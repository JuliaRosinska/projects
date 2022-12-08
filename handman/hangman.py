import random

def construct_char_dict(word):
    """This func parse word and return dict with chars as keys and their indexes as values."""
    char_dict = {}
    for index, letter in enumerate(word):
        if letter not in char_dict:
            char_dict[letter] = [index]
        else:
            char_dict[letter].append(index)
    return char_dict

def game_status(word, attempts):
    """This func print string with actual game data."""
    print(f"{word}     |     {attempts} attempts left")

def main():
    words = ["luxury", "matrix", "rhythm"]
    used_words = []

    print("Hello! Time to play hangman!")
    print("I will choose a word and you have to guess it in 7 tries.")
    print("You can enter only one letter or a whole word if you have already guessed it.")
    print("----------------------------")

    word = random.choice(words)
    word_indexes = construct_char_dict(word)

    attempts = 7
    game_status(word, attempts)

main()
