import json
import math
import queue
from queue import PriorityQueue
from tqdm import tqdm
from typing import List

# There are 3^5 (243) different possible feedbacks that we can get when we
# compare two strings. Here we enumerate all of them
feedbacks = ['11112', '11113', '11121', '11122', '11123', '11131', '11132', '11133', '11211', '11212', '11213', '11221', '11222', '11223', '11231', '11232', '11233', '11311', '11312', '11313', '11321', '11322', '11323', '11331', '11332', '11333', '12111', '12112', '12113', '12121', '12122', '12123', '12131', '12132', '12133', '12211', '12212', '12213', '12221', '12222', '12223', '12231', '12232', '12233', '12311', '12312', '12313', '12321', '12322', '12323', '12331', '12332', '12333', '13111', '13112', '13113', '13121', '13122', '13123', '13131', '13132', '13133', '13211', '13212', '13213', '13221', '13222', '13223', '13231', '13232', '13233', '13311', '13312', '13313', '13321', '13322', '13323', '13331', '13332', '13333', '21111', '21112', '21113', '21121', '21122', '21123', '21131', '21132', '21133', '21211', '21212', '21213', '21221', '21222', '21223', '21231', '21232', '21233', '21311', '21312', '21313', '21321', '21322', '21323', '21331', '21332', '21333', '22111', '22112', '22113', '22121', '22122', '22123', '22131', '22132', '22133', '22211', '22212', '22213', '22221', '22222', '22223', '22231', '22232', '22233', '22311', '22312', '22313', '22321', '22322', '22323', '22331', '22332', '22333', '23111', '23112', '23113', '23121', '23122', '23123', '23131', '23132', '23133', '23211', '23212', '23213', '23221', '23222', '23223', '23231', '23232', '23233', '23311', '23312', '23313', '23321', '23322', '23323', '23331', '23332', '23333', '31111', '31112', '31113', '31121', '31122', '31123', '31131', '31132', '31133', '31211', '31212', '31213', '31221', '31222', '31223', '31231', '31232', '31233', '31311', '31312', '31313', '31321', '31322', '31323', '31331', '31332', '31333', '32111', '32112', '32113', '32121', '32122', '32123', '32131', '32132', '32133', '32211', '32212', '32213', '32221', '32222', '32223', '32231', '32232', '32233', '32311', '32312', '32313', '32321', '32322', '32323', '32331', '32332', '32333', '33111', '33112', '33113', '33121', '33122', '33123', '33131', '33132', '33133', '33211', '33212', '33213', '33221', '33222', '33223', '33231', '33232', '33233', '33311', '33312', '33313', '33321', '33322', '33323', '33331', '33332', '33333']

# Load words from the dictionary into all_words
with open('words.json') as file:
    data = json.load(file)
    all_words = [word for word in data]


"""
Given a guess, feedback, and excluded letters, determine whether a given
candidate string is a valid next choice
"""
def _is_possible_next_guess(guesses: List[str], feedbacks: List[str], candidate: str) -> bool:
    if candidate in guesses:
        return False

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
Given a string and the feedback, what are all the possible next guesses.
Optionally exclude letters
"""
def possible_next_guesses(guesses: List[str], feedbacks: List[str]) -> List[str]:
    # excluded_letters = []
    # for i in range(len(guesses)):
    #     for j in range(len(guesses[i])):
    #         if feedbacks[i][j] == '3':
    #             excluded_letters.append(guesses[i][j])
    #
    # unfiltered = precomputed_data[guesses[-1]][feedbacks[-1]]
    #
    # to_return = []
    # for word in unfiltered:
    #     valid = True
    #     for i in range(len(word)):
    #         if word[i] in excluded_letters:
    #             valid = False
    #     if valid:
    #         to_return.append(word)
    #
    # return to_return
    #
    #
    #
    return [s for s in all_words if _is_possible_next_guess(guesses, feedbacks, s)]



"""
Given a guess and a solution, generate the feedback string
"""
def get_feedback_string(guess: str, solution: str) -> str:
    to_return = []
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
    avg_num_words = 0
    for key in data:
        avg_num_words = avg_num_words + data[key]

    avg_num_words = avg_num_words/len(data)

    std_dev = 0
    for key in data:
        std_dev = std_dev + (data[key] - avg_num_words) ** 2

    return std_dev

"""
Find the starting word that divides all other words into the most even buckets
by feedback. Calculation is pretty time consuming so it saves all standard
deviations to a file. Returns the string with the lowest standard deviation
"""
def best_dividing_word_std_dev(file_name: str = "test_std_dev.json"):
    std_devs = {}
    for guess in tqdm(all_words):
        counts = {}
        for feedback in feedbacks:
            counts[feedback] = 0

        for solution in all_words:
            if guess == solution:
                continue

            curr_feedback = get_feedback_string(guess, solution)
            counts[curr_feedback] = counts[curr_feedback] + 1

        std_devs[guess] = dict_std_dev(counts)

    min = float('inf')
    min_word = ""
    for key in std_devs:
        if std_devs[key] < min:
            min = std_devs[key]
            min_word = key

    with open(file_name, "w") as outfile:
        json.dump(std_devs, outfile)

    return min_word

"""
Find the starting word with the fewest number of letters not included in the
solution
"""
def best_dividing_word_max_info():
    words = {}
    best_word = ""
    min_nonmatching_words = float('inf')
    for guess in tqdm(all_words):
        count = 0
        for solution in all_words:
            curr_feedback = get_feedback_string(guess, solution)
            if curr_feedback == "33333":
                count = count+1

        if count in words:
            words[count].append(guess)
        else:
            words[count] = [guess]

        if count < min_nonmatching_words:
            min_nonmatching_words = count
            best_word = guess

    sorted_words = sorted(words)
    for i in range(10):
        print(words[sorted_words[i]])
    return guess



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
def best_next_guess(curr_guesses: List[str], curr_feedbacks: List[str]) -> str:
    feedbacks = possible_feedbacks(curr_feedbacks[-1])
    possible_words = possible_next_guesses(curr_guesses, curr_feedbacks)
    std_devs = {}
    for guess in possible_words: #tqdm(possible_words):
        counts = {}
        for feedback in feedbacks:
            counts[feedback] = 0

        for solution in possible_words:
            if guess == solution:
                continue

            curr_feedback = get_feedback_string(guess, solution)
            counts[curr_feedback] = counts[curr_feedback] + 1

        std_devs[guess] = dict_std_dev(counts)

    min = float('inf')
    min_word = ""
    for key in std_devs:
        if std_devs[key] < min:
            min = std_devs[key]
            min_word = key

    return min_word


def tester(starting_words: List[str] = ["lares"], words: List[str] = all_words) -> dict:

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
                curr_word = best_next_guess(result, feedback)
                result.append(curr_word)

            # print(result)
            if len(result) in lengths:
                lengths[starting_word][len(result)] = lengths[starting_word][len(result)]+1
            else:
                lengths[starting_word][len(result)] = 1

            print(result)

    with open("length_counts.json", "w") as outfile:
        json.dump(lengths, outfile)

    return lengths



if __name__ == '__main__':
    """
    with open('std_devs.json') as file:
        data = json.load(file)
    inverted = {}
    std_devs = []
    for key in data:
        inverted[data[key]] = key
        std_devs.append(data[key])

    std_devs.sort()

    for i in range(10):
        print(inverted[std_devs[i]])

    # Result: ["lares", "rales", "tares", "soare", "reais"]
    """

    """
    best_dividing_word_max_info()
    # Result: ["stoae", "toeas","aloes","aeons","aeros", "arose", 'soare"]
    """

    print(tester(["lares", "rales", "tares", "soare", "reais", "stoae", "toeas","aloes","aeons","aeros", "adieu"]))

    """
    print(best_next_guess(["lares"], ["33233"]))
    print(best_next_guess(["lares", "tronc"], ["33233", "31313"]))
    print(best_next_guess(["lares", "tronc", "bring"], ["33233", "31313", "31311"]))
    """
