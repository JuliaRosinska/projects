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

def hide_word(word):
    """This function returns a masked word for the player."""
    chars = random.sample(word, k = len(word) - 2)

    hide_word = word
    for char in word:
        if char in chars:
            hide_word = hide_word.replace(char, "*", 1)
            chars.remove(char)
        else:
            continue
    return hide_word

def unmask_letter(word_index, hide_word, letter):
    """This function accepts entered letter and unmaskin it in the word."""
    letter_index = word_index[letter]
    for i in letter_index:
        hide_word = hide_word[:i] + letter + hide_word[i + 1:]
    return hide_word

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
    game_word = hide_word(word)

    attempts = 7
    game_status(game_word, attempts)

    end = False
    while end == False:
        guess = input().lower()
        if guess in word:
            print("Cool!")
            game_word = unmask_letter(word_indexes, game_word, guess)
        else:
            if attempts == 0:
                print("Sorry, you lost :c")
                end = True

            print("Meh..")
            attempts -= 1
        game_status(game_word, attempts)
        print()

main()
