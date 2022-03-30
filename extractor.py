from number import NUMBER
from natasha.extractors import Extractor
from collections import defaultdict


def squash_spaces(text):
    return re.sub(" +", " ", text)


def get_words_count(text):
    text = squash_spaces(text)
    if not text:
        return 0

    space_count = text.count(" ")

    if space_count == 0:
        return -1

    return space_count - 1


class NumberExtractor(Extractor):
    def __init__(self):
        super(NumberExtractor, self).__init__(NUMBER)

    def replace(self, text):
        """
        Замена чисел в тексте без их группировки

        Аргументы:
            text: исходный текст

        Результат:
            new_text: текст с замененными числами
        """

        # одна тысяча восемьсот тридцать пятый | тысяча девятьсот пятьдесят четвертый

        # mask showing amount of words before squashing
        counter_mask = []

        if text:
            new_text = ""
            start = 0

            # for correct span words counting
            text = f" {text} "

            matches = self.parser.findall(text)
            matches = self.handle_subsequent_numbers(matches)

            for match in matches:

                print("int", match.fact.int, "multiplier", match.fact.multiplier)

                print(
                    "match:",
                    match,
                )

                span_text = text[start : match.span.start]

                print("START:", start, "STOP:", match.span.start)
                print(f"span: |{span_text}|")

                append_to_mask_count = get_words_count(span_text)
                if append_to_mask_count < 0:
                    counter_mask = counter_mask[:-1]
                elif append_to_mask_count > 0:
                    for _ in range(append_to_mask_count):
                        counter_mask.append(1)

                print("CM1:", counter_mask)

                # if len(span_text) > 2:
                #     for _ in range(len(span_text.split()) - edge_coef(span_text)):
                #         counter_mask.append(1)
                # elif len(span_text) == 1 and span_text != " ":
                #     counter_mask.pop()

                if match.fact.multiplier:
                    num = match.fact.int * match.fact.multiplier
                    counter_mask.append(2)
                else:
                    num = match.fact.int
                    counter_mask.append(1)

                print("CM2:", counter_mask)

                new_text += text[start : match.span.start] + str(num)
                start = match.span.stop

            new_text += text[start:]

            # for _ in range(len(text[start:].split())):
            #     counter_mask.append(1)

            append_to_mask_count = get_words_count(text[start:])
            if append_to_mask_count < 0:
                counter_mask = counter_mask[:-1]
            elif append_to_mask_count > 0:
                for _ in range(append_to_mask_count):
                    counter_mask.append(1)

            print("counter_mask", counter_mask)

            if start == 0:
                return text.strip(), counter_mask
            else:
                return new_text.strip(), counter_mask
        else:
            return None, counter_mask

    def handle_subsequent_numbers(self, matches):
        return matches

    def replace_groups(self, text):
        """
        Замена сгруппированных составных чисел в тексте

        Аргументы:
            text: исходный текст

        Результат:
            new_text: текст с замененными числами
        """
        if text:
            start = 0
            matches = list(self.parser.findall(text))
            groups = []
            group_matches = []

            for i, match in enumerate(matches):
                if i == 0:
                    start = match.span.start
                if i == len(matches) - 1:
                    next_match = match
                else:
                    next_match = matches[i + 1]
                group_matches.append(match.fact)
                if (
                    text[match.span.stop : next_match.span.start].strip()
                    or next_match == match
                ):
                    groups.append((group_matches, start, match.span.stop))
                    group_matches = []
                    start = next_match.span.start

            new_text = ""
            start = 0

            for group in groups:
                num = 0
                nums = []
                new_text += text[start : group[1]]

                print("groups---------------------------------")

                for match in group[0]:

                    print("MATCH", match)

                    curr_num = (
                        match.int * match.multiplier if match.multiplier else match.int
                    )

                    # print("\ncurr_num", curr_num)
                    # print("nums", nums)

                    if match.multiplier:
                        num = (num + match.int) * match.multiplier
                        nums.append(num)
                        num = 0
                    elif num > curr_num or num == 0:
                        # print(f"{num} > {curr_num}")
                        num += curr_num
                    else:
                        # print(f"--------------кладем {num} в nums")
                        nums.append(num)
                        num = 0
                    # else:
                    #     nums.append(match.int)

                    # print("------num", num)

                if num > 0:
                    # print(f"кладем {num} в nums")
                    nums.append(num)

                # print("=============================nums", nums)

                # new_text += str(sum(nums))

                new_nums = [nums[0]]
                for i, n in enumerate(nums[1:]):
                    if is_summable(new_nums[-1], n):
                        new_nums[-1] = new_nums[-1] + n
                    else:
                        new_nums.append(n)

                new_text += " ".join([str(n) for n in new_nums])

                start = group[2]

                # print("group", group)

                # print("--------------------=> new_text", new_text)

            new_text += text[start:]

            if start == 0:
                print("return text")
                return text
            else:
                print("return new_text")
                return new_text
        else:
            return None

    def regroup_numbers(self, text):
        replaced, counter_mask = self.replace(text)
        print("REPLACED:", replaced, "words counter:", counter_mask)
        res = regroup_numbers(replaced, counter_mask)
        return res


def is_summable(num1, num2):
    # print("sum", num1, num2)
    if num1 == 10 or num2 == 0:
        return False
    place = len(str(num2))
    str1 = str(num1)
    # print(">", str1, place)
    if len(str1) > place and str1[-place] == "0":
        # print("sum true")
        return True
    return False


def can_be_merged(num1, num2):
    # print("merge", num1, num2)
    # extract multiplexer
    if num2 > num1:
        m = get_multiplexer(num2)
        num = int(num2 / m)
        if is_summable(num1, num):
            # print("sum in merge")
            return True
    return False


def get_multiplexer(num):
    m = 1
    while num % 10 == 0:
        num = num / 10
        m *= 10
    return m


NON_SUMMABLE_FIRST_NUMBERS = [10]

extractor = NumberExtractor()

# text = "один, два, три, три два один, четыре пять шесть, тысяча девяносто пять, две тысячи шесть, семьсот двадцать один, пятьдесят шестьдесят, два два два, семь умножить на семь"
# text = "четыре пять шесть, две тысячи три, десять два"

text = "Это случилось в Девятьсот восемьдесят семь тысяч шестьсот пятьдесят четыре, это один два три по полудни"

# print(extractor.replace(text))

# print(extractor.replace_groups("десять тысяча"))

# print(extractor.regroup_after_replace("900 80 7000 600 50 4"))

# print(get_multiplexer(600))

import re


def regroup_numbers(text, prev_mask):
    res = ""
    # merged_indices = []
    counter_mask = []

    print("prev_mask", prev_mask)

    if text:
        start = 0
        counter_start = 0
        for m in re.finditer("\d+[ \d]+\d+", text):
            if m.group(0).strip():
                print("group:", m.group(0))
                print(m.span(0))
                span_start = m.span(0)[0]
                span_end = m.span(0)[1]

                span_start_ix = len(text[:span_start].split())

                # for _ in range(len(text[start:span_start].split())):
                for c in prev_mask[counter_start:span_start_ix]:
                    counter_mask.append(c)

                res += text[start:span_start]
                start = span_end

                counter_start = len(text[:span_end].split())

                regrouped, squashed_idxs = regroup_after_replace(
                    m.group(0), span_start_ix, prev_mask
                )
                res += regrouped
                # if indices:
                # merged_indices.extend(indices)

                print("squashed_idxs", squashed_idxs)

                counter_mask.extend(squashed_idxs)

        # for _ in range(len(text[start:].split())):
        #     counter_mask.append(1)

        for c in prev_mask[counter_start:]:
            counter_mask.append(c)

        res += text[start:]
    return res, counter_mask


def regroup_after_replace(text, start_ix, counter_mask):
    # merged_indices = []
    squashed_idxs = []
    if text:
        print("number group:", text, "start_ix", start_ix)
        # indices = []
        nums = [int(x) for x in text.split()]
        new_nums = [nums[0]]
        # indices.append(start_ix)
        submask = counter_mask[start_ix : start_ix + len(nums)]
        start = 0
        acc = submask[0]
        for i, n in enumerate(nums[1:]):
            if is_summable(new_nums[-1], n):
                # print("summable")
                new_nums[-1] = new_nums[-1] + n
                # indices.append(i + 1 + start_ix)
                acc += submask[i + 1]

            elif can_be_merged(new_nums[-1], n):
                # print("can be merged")
                m = get_multiplexer(n)
                extracted = int(n / m)
                new_nums[-1] = (new_nums[-1] + extracted) * m
                # indices.append(i + 1 + start_ix)
                acc += submask[i + 1]

            else:
                # print("not")
                new_nums.append(n)

                print("submask", submask)
                print("submask[start : i + 1]", submask[start : i + 1])

                squashed_idxs.append(acc)
                start = i + 1

                acc = submask[i + 1]

                # if len(indices) > 1:
                # merged_indices.append(indices)
                # indices = [i + 1 + start_ix]
        # if len(indices) > 1:
        # merged_indices.append(indices)

        squashed_idxs.append(acc)

        new_text = " ".join([str(n) for n in new_nums])
        print("new_text", new_text)
        return new_text, squashed_idxs
    else:
        return ""


# fix long numbers
text = "Госдолг США в тысяча девятьсот пятидесятом году составил двести пятьдесят шесть миллиардов девятьсот миллионов долларов"

# fix 0
text = "пять шесть ноль ноль ноль семь двадцать ноль"

# we need to return word indices
text = "годы его правления одна тысяча восемьсот тридцать пятый и две тысячи девятьсот пятьдесят четвертый годы"

text = "семьсот миллиардов один рубль, один, два, три три"

# text = "Выплаты за второго-третьего ребенка выросли на девять сотых процента"

# text = "Я купил сорок пять килограмм картошки и 7 пудов моркови"

# text = "один, ,два"

# text = "Я купил сорок пять килограмм картошки и 7 пудов моркови"


text = "один, ,два три, четыре, пять"

replaced, counter_mask = extractor.replace(text)

print("INPUT:", text)

print("REPLACED:", replaced)

print(counter_mask)

text, mask = regroup_numbers(replaced, counter_mask)

print("RESULT:", text, mask)
