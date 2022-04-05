# Denormalize numbers in Russian

Inverse text normalization for numbers in Russian language. Optimized for ASR task.

## Intro

This tool handles complicated denormalization cases such as:

```python
INPUT:  "семьсот миллиардов один рубль, один, два, три три",
RESULT: "700000000001 рубль, 1, 2, 3 3"
```

```python
INPUT:  "мой телефон девятьсот десять ноль девяносто пять пятьдесят шесть десять",
RESULT: "мой телефон 910 0 95 56 10"
```

```python
INPUT:  "одна тысяча восемьсот тридцать первый и тысяча девятьсот пятьдесят четвертый",
RESULT: "1831 и 1954"
```

### Mapping

It also can produce mapping for the squashed numbers. This mapping can be further used in the ASR pipeline — e.g., to recalculate the word-level time offsets after the denormalization task.

```python
INPUT:   "семьсот миллиардов один рубль, один, два, три три",
RESULT:  "700000000001 рубль, 1, 2, 3 3"
MASK:    [3, 1, 1, 1, 1, 1]
```

```python
INPUT:   "мой телефон девятьсот десять ноль девяносто пять пятьдесят шесть десять",
RESULT:  "мой телефон 910 0 95 56 10",
MASK:    [1, 1, 2, 1, 2, 2, 1],
```

```python
INPUT:   "одна тысяча восемьсот тридцать первый и тысяча девятьсот пятьдесят четвертый",
RESULT:  "1831 и 1954",
MASK:    [5, 1, 4],
```

## Usage

In the following example note that "пятьдесят пять,шестьдесят шесть" are 3 words to squash.

```python
text = "один два, тридцать три, пятьдесят пять,шестьдесят шесть сто двадцать четыре, привет как дела"
extractor = NumberExtractor()

res, mask = extractor.replace(text, apply_regrouping=True)
```

Result:

```python
TEXT:  "1 2, 33, 55,66 124, привет как дела",
MASK:  [1, 1, 2, 3, 3, 1, 1, 1],
```
