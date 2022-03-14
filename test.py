#%%
from extractor import NumberExtractor


def extractor():
    return NumberExtractor()


tests = [
    (
        "Я купил сорок пять килограмм картошки и 7 пудов моркови",
        "Я купил 45 килограмм картошки и 7 пудов моркови",
    ),
    (
        "Выплаты за второго-третьего ребенка выросли на девять сотых процента",
        "Выплаты за 2-3 ребенка выросли на 0.09 процента",
    ),
    (
        "Девятьсот восемьдесят семь тысяч шестьсот пятьдесят четыре минус 321",
        "987654 минус 321",
    ),
    (
        "Госдолг США в тысяча девятьсот пятидесятом году составил двести пятьдесят шесть миллиардов девятьсот миллионов долларов",
        "Госдолг США в 1950 году составил 256900000000 долларов",
    ),
    (
        "Один два три четыре пять",
        "1 2 3 4 5",
    ),
    (
        "Четыре три два один",
        "4 3 2 1",
    ),
    ("", ""),
    ("тридцать три", "33"),
    ("тридцать пять один", "35 1"),
    ("десять два", "10 2"),
    ("два десять", "2 10"),
    ("семьсот двадцать один тридцать", "721 30"),
    ("шестьсот одиннадцать два два три", "611 2 2 3"),
    (
        "семьсот миллиардов один рубль, один, два, три три",
        "700000000001 рубль, 1, 2, 3 3",
    ),
]


def test_extractor(extractor, test):
    text, etalon = test
    guess = extractor.regroup_numbers(text)
    assert guess == etalon


# %%
text = "Выплаты за второго-третьего ребенка выросли на пятьсот двадцать пять тысячных процента и составили 90 тысяч рублей"
extractor = NumberExtractor()

# %%
print(extractor.replace_groups(text))
# %%
for test in tests:
    test_extractor(extractor, test)