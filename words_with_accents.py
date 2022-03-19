#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict

words5char = []


def print_5char_words():
    with open('br-utf8.txt', encoding='utf-8') as f:
        for line in f:
            w = line.strip()
            if len(w) == 5:
                print(repr(w))
                words5char.append(w)


import json

with open('words5char_utf-8.json', 'w', encoding='utf-8') as f:
    json.dump(words5char, f, indent=2, sort_keys=True)


def get_5wordchars() -> list:
    with open('words5char_utf-8.json', encoding='utf-8') as f:
        lero = json.load(f)
    return lero


def print_5char_words_with_accents():
    w5l = get_5wordchars()

    for line in w5l:
        w = line.strip()
        if len(w) == 5:
            print("-", repr(w))

    pass


def create_states_w5l_with_accents():
    with open('words5char_utf-8-syllables.json') as f:
        w5l = json.load(f)

    return w5l


import collections

import unicodedata


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


import pandas as pd
import numpy as np

if __name__ == '__main__':
    w5l = create_states_w5l_with_accents()
    syllables = defaultdict(int)
    for w in w5l.values():
        # Remove the accents ( this doesn't make difference in the puzzle)
        ss = strip_accents(w).split('-')
        for s in ss:
            syllables[s] += 1
    syll_values = np.array(list(syllables.values()))
    syll_tokens = np.array(list(syllables.keys()))
    tot = np.sum(syll_values)
    freq = syll_values/tot
    df = pd.DataFrame(data={"syllables": syll_tokens, "count": syll_values, "freq" : freq})

    df.sort_values()
    print(syllables)
