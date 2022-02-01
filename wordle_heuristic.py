import json
import math
import queue
from queue import PriorityQueue
from os.path import exists
from tqdm import tqdm
from typing import List

# There are 3^5 (243) different possible feedbacks that we can get when we
# compare two strings. Here we enumerate all of them
feedbacks = ['11112', '11113', '11121', '11122', '11123', '11131', '11132', '11133', '11211', '11212', '11213', '11221', '11222', '11223', '11231', '11232', '11233', '11311', '11312', '11313', '11321', '11322', '11323', '11331', '11332', '11333', '12111', '12112', '12113', '12121', '12122', '12123', '12131', '12132', '12133', '12211', '12212', '12213', '12221', '12222', '12223', '12231', '12232', '12233', '12311', '12312', '12313', '12321', '12322', '12323', '12331', '12332', '12333', '13111', '13112', '13113', '13121', '13122', '13123', '13131', '13132', '13133', '13211', '13212', '13213', '13221', '13222', '13223', '13231', '13232', '13233', '13311', '13312', '13313', '13321', '13322', '13323', '13331', '13332', '13333', '21111', '21112', '21113', '21121', '21122', '21123', '21131', '21132', '21133', '21211', '21212', '21213', '21221', '21222', '21223', '21231', '21232', '21233', '21311', '21312', '21313', '21321', '21322', '21323', '21331', '21332', '21333', '22111', '22112', '22113', '22121', '22122', '22123', '22131', '22132', '22133', '22211', '22212', '22213', '22221', '22222', '22223', '22231', '22232', '22233', '22311', '22312', '22313', '22321', '22322', '22323', '22331', '22332', '22333', '23111', '23112', '23113', '23121', '23122', '23123', '23131', '23132', '23133', '23211', '23212', '23213', '23221', '23222', '23223', '23231', '23232', '23233', '23311', '23312', '23313', '23321', '23322', '23323', '23331', '23332', '23333', '31111', '31112', '31113', '31121', '31122', '31123', '31131', '31132', '31133', '31211', '31212', '31213', '31221', '31222', '31223', '31231', '31232', '31233', '31311', '31312', '31313', '31321', '31322', '31323', '31331', '31332', '31333', '32111', '32112', '32113', '32121', '32122', '32123', '32131', '32132', '32133', '32211', '32212', '32213', '32221', '32222', '32223', '32231', '32232', '32233', '32311', '32312', '32313', '32321', '32322', '32323', '32331', '32332', '32333', '33111', '33112', '33113', '33121', '33122', '33123', '33131', '33132', '33133', '33211', '33212', '33213', '33221', '33222', '33223', '33231', '33232', '33233', '33311', '33312', '33313', '33321', '33322', '33323', '33331', '33332', '33333']

# Load words from the dictionary into all_words
with open('all_words.json') as file:
    data = json.load(file)
    all_words = [word for word in data]

# Load words from the dictionary into all_words
with open('solution_words.json') as file:
    data = json.load(file)
    solution_words = [word for word in data]


"""
Given the current guesses and feedback, determine whether a given candidate
string is a valid next choice
"""
def _is_possible_next_guess(guesses: List[str], feedbacks: List[str], candidate: str) -> bool:
    if candidate in guesses:
        return False

    # Valid candidates must match all of the following conditions. For every
    # guess and feedback:
    #  1. Must match guess[i] if feedback[i] == '1'
    #  2. candidate[i] must be in guess if feedback[i] == '2', but candidate[i]
    #     must NOT equal guess[i]
    #  3. candidate[i] must not be in guess if feedback[i] == '3'
    for i in range(len(guesses)):
        for j in range(len(guesses[i])):
         # Green
         if feedbacks[i][j] == '1' and guesses[i][j] != candidate[j]:
             return False
         # Yellow
         if feedbacks[i][j] == '2' and (guesses[i][j] == candidate[j] or not guesses[i][j] in candidate):
             return False
         # Grey
         if feedbacks[i][j] == '3' and guesses[i][j] in candidate:
             return False

    return True

"""
Given the current guesses and feedbacks, what are all the possible next guesses
"""
def possible_next_guesses(guesses: List[str], feedbacks: List[str], word_list: List[str] = all_words) -> List[str]:
    # For each string, see if it is a valid next guess
    return [s for s in word_list if _is_possible_next_guess(guesses, feedbacks, s)]

"""
Given a guess and a solution, generate the feedback string
"""
def get_feedback_string(guess: str, solution: str) -> str:
    to_return = []

    # Check for each character whether it is in the string or not and if its
    # in the correct position
    for i in range(len(guess)):
        if guess[i] == solution[i]:
            to_return.append(str(1))
        elif guess[i] in solution:
            to_return.append(str(2))
        else:
            to_return.append(str(3))

    return "".join(to_return)

"""
Given a dictionary of word counts for each response, find the standard deviation
(technically the square of the std deviation) in the sizes of each bucket
"""
def dict_std_dev(data: dict) -> float:
    # Find what the average number of words for each bucket should be
    avg_num_words = 0
    for key in data:
        avg_num_words = avg_num_words + data[key]

    avg_num_words = avg_num_words/len(data)

    # Sum up the squares of the difference between actual and average
    std_dev = 0
    for key in data:
        std_dev = std_dev + (data[key] - avg_num_words) ** 2

    return std_dev

"""
Given a dict of words mapping to numeric values, find the n words with the
smallest counts
"""
def find_n_smallest(data: dict, n: int = 1) -> dict:
    # We're mapping words to numbers and we want to sort and look up by the
    # numbers, so we invert the mapping. We assume that all numbers are distinct
    inverted_dict = {}
    for key in data:
        if data[key] in inverted_dict:
            inverted_dict[data[key]].append(key)
        else:
            inverted_dict[data[key]] = [key]

    if n >= len(data):
        sorted_values = sorted(inverted_dict)
    else:
        sorted_values = sorted(inverted_dict)[:n]

    to_return = {}
    for key in sorted_values:
        to_return[key] = inverted_dict[key]

    return to_return


"""
Find the starting word that divides all other words into the most even buckets
by feedback. Calculation is pretty time consuming so it saves all standard
deviations to a file. Returns the string with the lowest standard deviation
"""
def best_dividing_word_std_dev(word_list: List[str] = all_words, file_name: str = "test_std_dev.json", num_results: int = 1) -> dict:
    # We will calculate the standard deviation for the bucketing of each
    # possible starting word
    std_devs = {}

    # Check if file exists. If so, don't recompute
    if exists(file_name):
        with open(file_name) as file:
            std_devs = json.load(file)
    else:
        # Go through every possible guess/solution pair
        for guess in tqdm(word_list):
            counts = {}

            # Initialize for every feedback. Even empty ones should be included in
            # standard deviation
            for feedback in feedbacks:
                counts[feedback] = 0

            # Every word is a possible solution
            for solution in word_list:
                # We don't include '11111' in feedbacks, so just skip this
                if guess == solution:
                    continue

                # Get feedback string and update sum
                curr_feedback = get_feedback_string(guess, solution)
                counts[curr_feedback] = counts[curr_feedback] + 1

            # Compute standard deviation
            std_devs[guess] = dict_std_dev(counts)

            with open(file_name, "w") as outfile:
                json.dump(std_devs, outfile)


    return find_n_smallest(std_devs, num_results)

"""
Find the starting word with the fewest number of letters not included in the
solution. Generates json file with the counts of '33333' feedback for each word
"""
def best_dividing_word_max_info(word_list: List[str] = all_words, file_name: str = "test_max_info.json", num_results: int = 1) -> dict:
    words = {}

    # Check if file exists. If so, don't recompute
    if exists(file_name):
        with open(file_name) as file:
            words = json.load(file)
    else:
        # For every guess/solution pair, see if the result is '33333' and if so
        # add it to the count
        for guess in tqdm(word_list):
            count = 0
            for solution in word_list:
                curr_feedback = get_feedback_string(guess, solution)
                if curr_feedback == "33333":
                    count = count+1

                words[guess] = count

        with open(file_name, "w") as outfile:
            json.dump(words, outfile)

    return find_n_smallest(words, num_results)

"""
Given a feedback string, generate all possible next feedback strings. We assume
that if a letter is in the right position, it must stay there, so all 1s in the
feedback strings must remain 1s, but everything else can change
"""
def possible_feedbacks(curr_feedback: str) -> List[str]:
    feedbacks = []
    _possible_feedbacks_inner(curr_feedback, feedbacks)
    return feedbacks

def _possible_feedbacks_inner(curr_feedback: str, result: List[str], idx: int = 0, path: List[str] = []):
    if idx == len(curr_feedback):
        result.append("".join(path))
        return

    if curr_feedback[idx] >= '2':
        path.append('3')
        _possible_feedbacks_inner(curr_feedback, result, idx+1, path)
        path.pop()

    if curr_feedback[idx] >= '2':
        path.append('2')
        _possible_feedbacks_inner(curr_feedback, result, idx+1, path)
        path.pop()

    if curr_feedback[idx] >= '1':
        path.append('1')
        _possible_feedbacks_inner(curr_feedback, result, idx+1, path)
        path.pop()

"""
Given the current game state, determine the next best move that optimally splits
the answer space
"""
def best_next_guess_std_dev(curr_guesses: List[str], curr_feedbacks: List[str], word_list: List[str] = all_words) -> str:
    feedbacks = possible_feedbacks(curr_feedbacks[-1])
    possible_words = possible_next_guesses(curr_guesses, curr_feedbacks, word_list)
    std_devs = {}
    for guess in possible_words:
        counts = {}
        for feedback in feedbacks:
            counts[feedback] = 0

        for solution in possible_words:
            if guess == solution:
                continue

            curr_feedback = get_feedback_string(guess, solution)
            counts[curr_feedback] = counts[curr_feedback] + 1

        std_devs[guess] = dict_std_dev(counts)

    smallest = find_n_smallest(std_devs)
    return smallest[list(smallest.keys())[0]][0]

"""
Test using standard dev heuristic. For every starting word and every possible
solution word, count the length of every path
"""
def tester_std_dev(starting_words: List[str] = ["lares"], words: List[str] = all_words, result_file: str = "length_counts_std_dev.json") -> dict:
    lengths = {}
    for word in starting_words:
        lengths[word] = {}

    for word in words: #tqdm(words):
        for starting_word in starting_words:
            curr_word = starting_word
            result = [curr_word]
            feedback = []

            while curr_word != word:
                feedback_str = get_feedback_string(curr_word, word)
                feedback.append(feedback_str)
                curr_word = best_next_guess_std_dev(result, feedback, words)
                result.append(curr_word)

            if len(result) in lengths[starting_word]:
                lengths[starting_word][len(result)].append(word)
            else:
                lengths[starting_word][len(result)] = [word]

            print(result)

    with open(result_file, "w") as outfile:
        json.dump(lengths, outfile)

    return lengths

def best_next_guess_max_info(curr_guesses: List[str], curr_feedbacks: List[str], word_list: List[str] = all_words) -> str:
    if curr_feedbacks[-1].count('3') == 0:
         return best_next_guess_std_dev(curr_guesses, curr_feedbacks)

    feedbacks = possible_feedbacks(curr_feedbacks[-1])
    possible_words = possible_next_guesses(curr_guesses, curr_feedbacks, word_list)

    max_info_string = ""
    min_unmatching = float('inf')
    for guess in possible_words:
        count = 0
        for solution in possible_words:
            if guess == solution:
                continue

            curr_feedback = get_feedback_string(guess, solution)
            count = count+curr_feedback.count('3')

        if count < min_unmatching:
            min_unmatching = count
            max_info_string = guess

    return max_info_string

def tester_max_info(starting_words: List[str] = ["lares"], words: List[str] = all_words, result_file: str = "length_counts_max_info.json") -> dict:
    lengths = {}
    for word in starting_words:
        lengths[word] = {}

    for word in words: #tqdm(words):
        for starting_word in starting_words:
            curr_word = starting_word
            result = [curr_word]
            feedback = []

            while curr_word != word:
                feedback_str = get_feedback_string(curr_word, word)
                feedback.append(feedback_str)
                curr_word = best_next_guess_max_info(result, feedback, words)
                result.append(curr_word)

            if len(result) in lengths[starting_word]:
                lengths[starting_word][len(result)].append(word)
            else:
                lengths[starting_word][len(result)] = [word]

            print(result)

    with open(result_file, "w") as outfile:
        json.dump(lengths, outfile)

    return lengths

if __name__ == '__main__':
    # Result: ["lares", "rales", "tares", "soare", "reais"]
    print(best_dividing_word_std_dev(all_words, "std_devs.json", 5))

    # Result: ["stoae", "toeas","aloes","aeons","aeros", "arose", 'soare"]
    print(best_dividing_word_max_info(all_words, "max_infos.json", 5))

    starting_words = ["lares", "rales", "tares", "soare", "reais", "stoae", "toeas","aloes","aeons","aeros", "adieu"]
    # print(tester_std_dev(starting_words, all_words, "length_counts_std_devs.json"))
    # print(tester_max_info(starting_words, all_words, "length_counts_max_info.json"))


    # Result: ['raise','arise','irate','arose','alter']
    print(best_dividing_word_std_dev(solution_words, "std_devs_solutions_only.json", 5))

    # Result: ['arise', 'raise','alone','arose','audio'.'atone']
    print(best_dividing_word_max_info(solution_words, "max_infos_solutions_only.json", 5))

    merged_starting_words = ["lares","rales","tares","soare","reais","stoae","toeas","aloes","aeons","aeros", "adieu","raise","arise","irate","arose","alter","alone","audio","atone"]
    # print(tester_std_dev(merged_starting_words, solution_words, "length_counts_std_dev_solutions.json"))
    # print(tester_max_info(merged_starting_words, solution_words, "length_counts_max_info_solutions.json"))

    """
    # Sample of how to use this for an actual puzzle with subsequent guesses and
    # feedback
    print(best_next_guess_std_dev(["irate"], ["32332"]))
    print(best_next_guess_std_dev(["irate", "sored"], ["32332", "31113"]))
    print(best_next_guess_std_dev(["irate", "sored", "borel"], ["32332", "31113", "31113"]))
    """


    with open('length_counts_std_dev_solutions.json') as file:
        length_counts = json.load(file)

    # filtered_length_counts = {}
    # for word in length_counts:
    #     filtered_length_counts[word] = {}
    #     for length in length_counts[word]:
    #         filtered_length_counts[word][length] = []
    #         for solution in length_counts[word][length]:
    #             if solution in solution_words:
    #                 filtered_length_counts[word][length].append(solution)
    # length_counts = filtered_length_counts

    result = {}
    for word in length_counts:
        sum = 0
        max = 0
        max_words = []
        count = 0
        losing_words = []
        for counts in length_counts[word]:
            sum = sum + int(counts) * len(length_counts[word][counts])
            if int(counts) > max:
                max = int(counts)
                max_words = length_counts[word][counts]
            count = count + len(length_counts[word][counts])
            if int(counts) > 6:
                losing_words.extend(length_counts[word][counts])

        print(word)
        print("Average: " + str(sum/count))
        print("Max Guesses: " + str(max))
        print("Max Words: " + str(max_words))
        print("Losing Words: " + str(losing_words))
        print("Num Losting Words: " + str(len(losing_words)))
        print()


    """
    tares
    Average: 3.594816414686825
    Max Guesses: 8
    Max Words: ['boxer', 'hound', 'match']
    """
