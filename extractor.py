from number import NUMBER
from natasha.extractors import Extractor


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
        if text:
            new_text = ""
            start = 0

            for match in self.parser.findall(text):
                if match.fact.multiplier:
                    num = match.fact.int * match.fact.multiplier
                else:
                    num = match.fact.int

                new_text += text[start : match.span.start] + str(num)
                start = match.span.stop

            new_text += text[start:]

            if start == 0:
                return text
            else:
                return new_text
        else:
            return None

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

                    # print(match)

                    curr_num = (
                        match.int * match.multiplier if match.multiplier else match.int
                    )

                    print("\ncurr_num", curr_num)
                    print("nums", nums)

                    if match.multiplier:
                        num = (num + match.int) * match.multiplier
                        nums.append(num)
                        num = 0
                    elif num > curr_num or num == 0:
                        print(f"{num} > {curr_num}")
                        num += curr_num
                    else:
                        print(f"--------------кладем {num} в nums")
                        nums.append(num)
                        num = 0
                    # else:
                    #     nums.append(match.int)

                    # print("------num", num)

                if num > 0:
                    print(f"кладем {num} в nums")
                    nums.append(num)

                print("=============================nums", nums)

                # new_text += str(sum(nums))

                new_nums = [nums[0]]
                for i, n in enumerate(nums[1:]):
                    if is_summable(new_nums[-1], n):
                        new_nums[-1] = new_nums[-1] + n
                    else:
                        new_nums.append(n)

                new_text += " ".join([str(n) for n in new_nums])

                start = group[2]

                print("group", group)

                print("--------------------=> new_text", new_text)

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
        replaced = self.replace(text)
        print("REPLACED:", replaced)
        res = regroup_numbers(replaced)
        return res


def is_summable(num1, num2):
    print("sum", num1, num2)
    if num1 == 10:
        return False
    place = len(str(num2))
    str1 = str(num1)
    print(">", str1, place)
    if len(str1) > place and str1[-place] == "0":
        print("sum true")
        return True
    return False


def can_be_merged(num1, num2):
    print("merge", num1, num2)
    # extract multiplexer
    if num2 > num1:
        m = get_multiplexer(num2)
        num = int(num2 / m)
        if is_summable(num1, num):
            print("sum in merge")
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

print(extractor.replace(text))

# print(extractor.replace_groups("десять тысяча"))

# print(extractor.regroup_after_replace("900 80 7000 600 50 4"))

# print(get_multiplexer(600))

import re


def regroup_numbers(text):
    res = ""
    if text:
        start = 0
        for m in re.finditer("\d+[ \d]+\d+", text):
            if m.group(0).strip():
                print(m.group(0))
                print(m.span(0))
                span_start = m.span(0)[0]
                span_end = m.span(0)[1]
                res += text[start:span_start]
                start = span_end
                res += regroup_after_replace(m.group(0))
        res += text[start:]
    return res


def regroup_after_replace(text):
    if text:
        nums = [int(x) for x in text.split()]
        new_nums = [nums[0]]
        for i, n in enumerate(nums[1:]):
            if is_summable(new_nums[-1], n):
                print("summable")
                new_nums[-1] = new_nums[-1] + n
            elif can_be_merged(new_nums[-1], n):
                print("can be merged")
                m = get_multiplexer(n)
                extracted = int(n / m)
                new_nums[-1] = (new_nums[-1] + extracted) * m
            else:
                print("not")
                new_nums.append(n)
        new_text = " ".join([str(n) for n in new_nums])
        print("new_text", new_text)
        return new_text
    else:
        return ""


text = "Госдолг США в тысяча девятьсот пятидесятом году составил двести пятьдесят шесть миллиардов девятьсот миллионов долларов"

text = "Я купил 40 5 килограмм картошки и 7 пудов моркови"

replaced = extractor.replace(text)

print("INPUT:", text)

print("REPLACED:", replaced)

print("RESULT:", regroup_numbers(replaced))
