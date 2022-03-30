#%%
import re


def squash_spaces(text):
    return re.sub(" +", " ", text)


def get_words_count(text):
    text = squash_spaces(text)

    space_count = text.count(" ")

    if space_count == 0:
        return -1

    return space_count - 1


text = "1,,,,,,s ,,,,,,,2"

get_words_count(text)

# %%
