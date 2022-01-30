import json
import math
import queue
from tqdm import tqdm
from typing import List

letters = "abcdefghijklmnopqrstuvwxyz"

# There are 3^5 (243) different possible feedbacks that we can get when we
# compare two strings. Here we enumerate all of them
feedbacks = ['11112', '11113', '11121', '11122', '11123', '11131', '11132', '11133', '11211', '11212', '11213', '11221', '11222', '11223', '11231', '11232', '11233', '11311', '11312', '11313', '11321', '11322', '11323', '11331', '11332', '11333', '12111', '12112', '12113', '12121', '12122', '12123', '12131', '12132', '12133', '12211', '12212', '12213', '12221', '12222', '12223', '12231', '12232', '12233', '12311', '12312', '12313', '12321', '12322', '12323', '12331', '12332', '12333', '13111', '13112', '13113', '13121', '13122', '13123', '13131', '13132', '13133', '13211', '13212', '13213', '13221', '13222', '13223', '13231', '13232', '13233', '13311', '13312', '13313', '13321', '13322', '13323', '13331', '13332', '13333', '21111', '21112', '21113', '21121', '21122', '21123', '21131', '21132', '21133', '21211', '21212', '21213', '21221', '21222', '21223', '21231', '21232', '21233', '21311', '21312', '21313', '21321', '21322', '21323', '21331', '21332', '21333', '22111', '22112', '22113', '22121', '22122', '22123', '22131', '22132', '22133', '22211', '22212', '22213', '22221', '22222', '22223', '22231', '22232', '22233', '22311', '22312', '22313', '22321', '22322', '22323', '22331', '22332', '22333', '23111', '23112', '23113', '23121', '23122', '23123', '23131', '23132', '23133', '23211', '23212', '23213', '23221', '23222', '23223', '23231', '23232', '23233', '23311', '23312', '23313', '23321', '23322', '23323', '23331', '23332', '23333', '31111', '31112', '31113', '31121', '31122', '31123', '31131', '31132', '31133', '31211', '31212', '31213', '31221', '31222', '31223', '31231', '31232', '31233', '31311', '31312', '31313', '31321', '31322', '31323', '31331', '31332', '31333', '32111', '32112', '32113', '32121', '32122', '32123', '32131', '32132', '32133', '32211', '32212', '32213', '32221', '32222', '32223', '32231', '32232', '32233', '32311', '32312', '32313', '32321', '32322', '32323', '32331', '32332', '32333', '33111', '33112', '33113', '33121', '33122', '33123', '33131', '33132', '33133', '33211', '33212', '33213', '33221', '33222', '33223', '33231', '33232', '33233', '33311', '33312', '33313', '33321', '33322', '33323', '33331', '33332', '33333']

# Load words from the dictionary into all_words
with open('words.json') as file:
    data = json.load(file)
    all_words = [word for word in data]

"""
Given a string and the feedback, what are all the possible next guesses.
Optionally exclude letters
"""
def possible_next_guesses(guess: str, feedback: str, excluded_letters: List[str] = []) -> List[str]:
    return [s for s in all_words if _is_possible_next_guess(guess, s, feedback, excluded_letters)]

"""
Given a guess, feedback, and excluded letters, determine whether a given
candidate string is a valid next choice
"""
def _is_possible_next_guess(guess: str, candidate: str, feedback: str, excluded_letters: List[str] = []) -> bool:
    for i in range(len(guess)):
        # Green
        if feedback[i] == '1' and guess[i] != candidate[i]:
            return False
        # Yellow
        if feedback[i] == '2' and (guess[i] == candidate[i] or not guess[i] in candidate):
            return False
        # Grey
        if feedback[i] == 3 and guess[i] in candidate:
            return False
        # Excluded letter
        if candidate[i] in excluded_letters:
            return False

    return True

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
Given a current path of guesses and the feedback on the most recent guess,
find the shortest path from the most recent guess to all possible words

To find the optimal starting word, we would call this with every possible word
and feedback combination and find the word that gives us the best worst case
"""
def longest_path_to_every_word(guesses: List[str], current_feedback: str, excluded_letters: List[str] = []) -> int:
    # We have found the solution, so it takes us 0 more steps
    if current_feedback == "11111":
        return 0

    # We need to track which characters are excluded and keep a running list
    # across multiple guesses. We do this by updating excluded_letters. We will
    # also need to backtrack later, so count the number of excluded characters
    # that we added to our list
    count_excluded = 0
    for i in range(len(current_feedback)):
        if current_feedback[i] == '3':
            excluded_letters.append(guesses[-1][i])
            count_excluded = count_excluded + 1

    # We want to try every possible next guess and see which gives us the best
    # worst-case path. That is going to be our best next guess because it
    # minimizes the worst case. For our purposes, we're just counting what is
    # the length of the worst case path
    max_path = 0

    # Given the current guess and feedback, what are all the possible solutions?
    next_guesses = possible_next_guesses(guesses[-1], current_feedback, excluded_letters)

    # For every possible guess, find the worst case path
    for guess in next_guesses:
        # Avoid cycles
        if guess in guesses:
            continue

        # For every possible solution, find the longest path
        for solution in next_guesses:
            feedback = get_feedback_string(guess, solution)

            # Update our guess
            guesses.append(guess)
            max_path = max(max_path, longest_path_to_every_word(guesses, feedback, excluded_letters) + 1)

            # Backtrack
            guesses.pop()

    # Backtracking
    for _ in range(count_excluded):
        excluded_letters.pop()

    return max_path


# def longest_path_to_every_word_opt(current_guess, current_feedback: str, dp: dict, depth_count=100) -> int:
#     if depth_count < 0:
#         return -1
#
#     if current_feedback == "11111":
#         return 0
#
#     if not current_guess in dp:
#         dp[current_guess] = {}
#
#     if not current_feedback in dp[current_guess]:
#         max_path = -1
#
#         next_guesses = possible_next_guesses(current_guess, current_feedback)
#
#         for guess in next_guesses:
#             if current_guess == guess:
#                 continue
#
#             for solution in next_guesses:
#                 feedback = get_feedback_string(guess, solution)
#
#                 longest = longest_path_to_every_word_opt(guess, feedback, dp, depth_count-1)
#
#                 if longest >= 0:
#                     max_path = max(max_path, longest+1)
#
#         dp[current_guess][current_feedback] = max_path
#
#     return dp[current_guess][current_feedback]


def best_dividing_word():
    avg_num_words = len(all_words)/len(feedbacks)
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


        std_dev = 0
        for feedback in feedbacks:
            std_dev = std_dev + (counts[feedback] - avg_num_words) ** 2

        std_devs[guess] = math.sqrt(std_dev)

    return std_devs


def possible_feedbacks(curr_feedback: str, result: List[str], idx: int = 0, path: List[str] = []):
    if idx == len(curr_feedback):
        result.append("".join(path))
        return

    if curr_feedback[idx] >= '2':
        path.append('3')
        possible_feedbacks(curr_feedback, result, idx+1, path)
        path.pop()

    if curr_feedback[idx] >= '2':
        path.append('2')
        possible_feedbacks(curr_feedback, result, idx+1, path)
        path.pop()

    if curr_feedback[idx] >= '1':
        path.append('1')
        possible_feedbacks(curr_feedback, result, idx+1, path)
        path.pop()

def best_next_guess(curr_guess: str, curr_feedback: str, excluded_letters: List[str], excluded_words: List[str] = []) -> str:
    feedbacks = []
    possible_feedbacks(curr_feedback, feedbacks)
    possible_words = [s for s in all_words if _is_possible_next_guess(curr_guess, s, curr_feedback, excluded_letters)]
    avg_num_words = len(possible_words) / len(feedbacks)

    std_devs = {}
    for guess in possible_words: #tqdm(possible_words):
        if guess in excluded_words:
            continue

        counts = {}
        for feedback in feedbacks:
            counts[feedback] = 0

        for solution in possible_words:
            if guess == solution:
                continue

            curr_feedback = get_feedback_string(guess, solution)
            counts[curr_feedback] = counts[curr_feedback] + 1


        std_dev = 0
        for feedback in feedbacks:
            std_dev = std_dev + (counts[feedback] - avg_num_words) ** 2

        std_devs[guess] = math.sqrt(std_dev)

    min = float('inf')
    min_word = ""
    for key in std_devs:
        if std_devs[key] < min:
            min = std_devs[key]
            min_word = key

    return min_word


def tester(starting_word = "lares", words: List[str] = all_words) -> dict:
    lengths = {}
    for word in tqdm(words):
        curr_word = starting_word
        result = [curr_word]
        excluded_letters = []

        while curr_word != word:
            feedback_str = get_feedback_string(curr_word, word)
            for i in range(len(feedback_str)):
                if feedback_str[i] == '3':
                    excluded_letters.append(curr_word[i])

            curr_word = best_next_guess(curr_word, feedback_str, excluded_letters, result)
            result.append(curr_word)

        print(result)
        if len(result) in lengths:
            lengths[len(result)] = lengths[len(result)]+1
        else:
            lengths[len(result)] = 1

    return lengths



if __name__ == '__main__':



    # print(possible_next_guesses("abact", "11113"))
    # print(get_feedback_string("abbot", "abbey"))

    # print(longest_path_to_every_word(["abbot"], "11232"))

    # dp = {}
    # print(longest_path_to_every_word_opt("abbot", "11232", dp))
    # with open("test.json", "w") as outfile:
    #     json.dump(dp, outfile)

    # print(possible_next_guesses_2("abbot", "11233"))
    # std_devs = best_dividing_word()
    # with open("test.json", "w") as outfile:
    #     json.dump(std_devs, outfile)

    # with open('test.json') as file:
    #     data = json.load(file)

    # print(best_next_guess("adieu", "32332", ['a','i','e']))
    # print(best_next_guess("durns", "22333", ['a','i','e','n','r','s']))
    # print(best_next_guess("dumpy", "22333", ['a','i','e','n','r','s','m','p','y']))

    print(best_next_guess("adieu", "32332", ['a','i','e']))

    # print(tester()) #"lares", ["alley"]))
# adieu
# durns
