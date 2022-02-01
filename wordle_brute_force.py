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
with open('all_words.json') as file:
    data = json.load(file)
    all_words = [word for word in data]

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
def longest_path_to_every_word(guesses: List[str], feedbacks: List[str]) -> int:
    # We have found the solution, so it takes us 0 more steps
    if feedbacks[-1] == "11111":
        print(guesses)
        return 0

    # We want to try every possible next guess and see which gives us the best
    # worst-case path. That is going to be our best next guess because it
    # minimizes the worst case. For our purposes, we're just counting what is
    # the length of the worst case path
    max_path = 0

    # Given the current guess and feedback, what are all the possible solutions?
    next_guesses = possible_next_guesses(guesses, feedbacks)

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
            feedbacks.append(feedback)
            max_path = max(max_path, longest_path_to_every_word(guesses, feedbacks) + 1)

            # Backtrack
            guesses.pop()
            feedbacks.pop()

    return max_path


if __name__ == '__main__':

    print(longest_path_to_every_word(["rates"], ["11331"]))
