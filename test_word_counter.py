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
def update_mask(mask_part, squashed_idxs):
    res = []
    shift = 0
    for count in squashed_idxs[::-1]:
        val = 0
        for i in range(count):
            val += mask_part[-1-i-shift]
        res.insert(0, val)
        shift += count
    while shift < len(mask_part):
        res.insert(0, mask_part[-1-shift])
        shift+=1
    return res

update_mask([2,1,2,1], [2])
# %%

def merge_texts(old, new, span_end):
    res = new + old[span_end:]
    return res


old = "1, 20 2, привет"
new = "1, 22"

merge_texts(old, new, 7)
# %%
