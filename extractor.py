from number import NUMBER
from natasha.extractors import Extractor
import re

NON_SUMMABLE_FIRST_NUMBERS = [10]


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
        mask = []
        if text:
            new_text = ""
            start = 0

            # correct span counting
            text = f" {text} "

            matches = self.parser.findall(text)
            for match in matches:
                span_text = text[start : match.span.start]                
                mask = self.update_first_mask(span_text, mask) 

                if match.fact.multiplier:
                    num = match.fact.int * match.fact.multiplier
                    mask.append(2)
                else:
                    num = match.fact.int
                    mask.append(1)

                new_text += text[start : match.span.start] + str(num)
                start = match.span.stop

            new_text += text[start:]

            mask = self.update_first_mask(text[start:], mask)

            if start == 0:
                return text.strip(), mask
            else:
                return new_text.strip(), mask
        else:
            return "", mask


    def update_first_mask(self, span_text, mask):
        append_to_mask_count = self.get_words_count(span_text)
        if append_to_mask_count < 0:
            mask = mask[:-1]
        elif append_to_mask_count > 0:
            for _ in range(append_to_mask_count):
                mask.append(1)
        return mask


    def squash_spaces(self, text):
        return re.sub(" +", " ", text)


    def get_words_count(self, text):
        text = self.squash_spaces(text)
        if not text:
            return 0
        space_count = text.count(" ")
        if space_count == 0:
            return -1
        return space_count - 1


    def regroup_numbers(self, text):
        replaced, counter_mask = self.replace(text)
        print("REPLACED:", replaced, "words counter:", counter_mask)
        res = regroup_numbers(replaced, counter_mask)
        return res


    def is_summable(self, num1, num2):
        if num1 == 10 or num2 == 0:
            return False
        place = len(str(num2))
        str1 = str(num1)
        if len(str1) > place and str1[-place] == "0":
            return True
        return False


    def can_be_merged(self, num1, num2):
        if num2 > num1:
            m = self.get_multiplexer(num2)
            num = int(num2 / m)
            if self.is_summable(num1, num):
                return True
        return False


    def get_multiplexer(self, num):
        m = 1
        while num % 10 == 0:
            num = num / 10
            m *= 10
        return m



def regroup_numbers(text, first_mask):
    res = ""
    if text:
        start = 0
        handled_matches = set()
        retry = True
        debug_counter = 0

        while True:
            start = 0
            debug_counter += 1

            if debug_counter > 4:
                break

            if not retry:
                break
            omit_end = False
            match_amount = len(re.findall("\d+[ \d]+\d+", text))

            for i,m in enumerate(re.finditer("\d+[ \d]+\d+", text)):
                
                if i+1 == match_amount and not omit_end:
                    retry = False

                if m.span(0) in handled_matches:
                    continue
                elif omit_end:
                    continue
                else:
                    handled_matches.add(m.span(0))

                if m.group(0).strip():
                    span_start = m.span(0)[0]
                    span_end = m.span(0)[1]

                    span_text = text[:span_end]

                    mask_index = len(span_text.split())
                    mask_part = first_mask[:mask_index]

                    res += text[start:span_start]
                    start = span_end

                    regrouped, squashed_idxs = regroup_after_replace(m.group(0))

                    res += regrouped

                    curr_part = update_mask(mask_part, squashed_idxs)
                    first_mask = merge_masks(first_mask, mask_part, curr_part)
                    new_text = merge_texts(text, res, span_end)

                    if new_text != text:
                        omit_end = True

                    text = new_text

            glob_res = res
            res = ""
    return text, first_mask

def merge_texts(old, new, span_end):
    res = new + old[span_end:]
    return res



def merge_masks(first_mask, mask_part, curr_part):
    res = curr_part + first_mask[len(mask_part):]
    return res


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


def regroup_after_replace(text):
    squashed_idxs = []
    if text:
        nums = [int(x) for x in text.split()]
        new_nums = [nums[0]]
        acc = 1
        for i, n in enumerate(nums[1:]):
            if extractor.is_summable(new_nums[-1], n):
                new_nums[-1] = new_nums[-1] + n
                acc += 1
            elif extractor.can_be_merged(new_nums[-1], n):
                m = extractor.get_multiplexer(n)
                extracted = int(n / m)
                new_nums[-1] = (new_nums[-1] + extracted) * m
                acc += 1
            else:
                new_nums.append(n)
                squashed_idxs.append(acc)
                acc = 1
        squashed_idxs.append(acc)
        new_text = " ".join([str(n) for n in new_nums])
        assert sum(squashed_idxs) == len(text.split())
        return new_text, squashed_idxs
    else:
        return ""


extractor = NumberExtractor()


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


# text = "один, ,два три, четыре, пять"

# text = "один,двадцать два какой то текст"

text = "один два, тридцать три, пятьдесят пять,шестьдесят шесть сто двадцать четыре, привет как дела"

text = ""

replaced, counter_mask = extractor.replace(text)

print("INPUT:", text)

print("REPLACED:", replaced)

print(counter_mask)

text, mask = regroup_numbers(replaced, counter_mask)

print("RESULT:", text, mask)
