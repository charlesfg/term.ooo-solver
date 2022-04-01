import re
import operator
import random

from test_generator import CaseWriter


class Game:

    def __init__(self, word, tries):
        self.word = word
        self.tries = 5
        if len(word) != 5:
            raise ValueError("Only 5 Character files")

    def __split_word(self, word):
        l = []
        for i in range(len(word)):
            l.append((word[i], i))
        return sorted(l)

    def play(self, guess):
        if self.tries == 0:
            raise Exception("No more tries! End of Game!")
        self.tries += 1

        # The lisf of characters  (character, index in word)
        wl = self.__split_word(self.word)
        gl = self.__split_word(guess)

        pttrn = ["0" for i in range(5)]

        # The current candidates
        wi = 0
        gi = 0

        while gi < 5:
            if wi == 5:
                # we reached the end of the word, the following characters are not present
                while gi < 5:
                    pttrn[gl[gi][1]] = 'x'
                    gi += 1
                break

            # the character is the same?
            if wl[wi][0] == gl[gi][0]:
                # same character and index
                if wl[wi][1] == gl[gi][1]:
                    pttrn[gl[gi][1]] = '!'
                    wi += 1
                    gi += 1
                # The word indexer is greater
                elif wl[wi][1] > gl[gi][1]:
                    # if we find the current index in a following position this is an x
                    if self.__foward_check(wi, wl, gl):
                        pttrn[gl[gi][1]] = 'x'
                    else:
                        # otherwise is an ?
                        pttrn[gl[gi][1]] = '?'
                        wi += 1
                    gi += 1
                elif wl[wi][1] < gl[gi][1]:
                    # this word character has an index lower the current one,
                    # since they are sorted, this character is out of position
                    pttrn[gl[gi][1]] = '?'
                    gi += 1
                else:
                    raise ValueError("This Should be impossible!")
            elif wl[wi][0] > gl[gi][0]:
                # This character does not exist in the word
                pttrn[gl[gi][1]] = 'x'
                gi += 1

            elif wl[wi][0] < gl[gi][0]:
                wi += 1

            else:
                raise ValueError("This Should be impossible!")

        return "".join(pttrn)

    def __foward_check(self, wi, wl, gl):
        for j in range(wi, 5):
            if wl[wi][0] == gl[j][0]:
                if wl[wi][1] == gl[j][1]:
                    return True
        return False


# Model of 5 character words

vowel_f = {
    "a": 0.1564,
    "o": 0.1019,
    "e": 0.1009,
    "i": 0.0795,
    "u": 0.0465,
}

consonant_f = {
    "r": 0.0771,
    "s": 0.0725,
    "m": 0.0477,
    "t": 0.0404,
    "c": 0.0400,
    "l": 0.0376,
    "n": 0.0320,
    "d": 0.0278,
    "p": 0.0255,
    "g": 0.0220,
    "v": 0.0218,
    "b": 0.0197,
    "f": 0.0195,
    "h": 0.0086,
    "j": 0.0076,
    "z": 0.0074,
    "x": 0.0060,
    "q": 0.0014,
    "k": 0.0001,
}


class CharacterGenerator:
    def __init__(self, cc, vc, iv):
        self.cc = cc
        self.vc = vc
        self.back_chars = []
        self.i = 0
        self.wait = 0
        self.iv = iv
        self.vowel_added_back = 0
        pass

    def char_generator(self):
        while True:
            char_source = self.cc
            if self.i < self.iv:
                if self.vc:
                    char_source = self.vc
            if self.vowel_added_back:
                char_source = self.vc
                self.vowel_added_back = 0
            if not char_source:
                raise StopIteration
            tmp_c = [x for x in sorted(char_source.items(), key=operator.itemgetter(1), reverse=True)][0]
            # print(" tmp_c:",tmp_c)
            yield tmp_c[0]
            del char_source[tmp_c[0]]
            if self.wait:
                self.wait -= 1
            else:
                if self.back_chars:
                    self._add_back()
            self.i += 1
        pass

    def back(self, c):
        self.back_chars.append(c)
        self.wait += 2

    def _add_back(self):
        for c in self.back_chars:
            if c in consonant_f:
                self.cc[c] = consonant_f[c]
            elif c in vowel_f:
                self.vc[c] = vowel_f[c]
                self.vowel_added_back = 1
            else:
                raise ValueError("Character Unknow {}".format(c))
        pass


class Guesser:
    """
    This class is to solve word guessing games in Portugues like:
     - https://term.ooo/
     - https://www.gabtoschi.com/letreco/

     It have some strategies that can be chosed in Constructor

     == Strategies ==

     'charfreq' -> Character'  Frequency
        - This strategy you should specify how many initial vowels (2 or 3) and it will suggest
        a initial list of words  with the most frequent character in the 5 character words.
          After the initial iteration you enter the result and it will suggest new set of words.
          It will add one vowel (if available) and consonants by those left and in frequency order.
          If no word is possible (by the combinations of the letters), it will drop the latest character
        added to the pool and than suggest any possible. This last step is happens recursively
        until a list is available or it will end in error.


        Usage:

        - After the constructor being called the Guesser will suggest a word list and wait for new information.
        - The Guesser is stateful and keep track of previous words used. For that you should call the method
        nextGuess with the choosen word and the result from the game. The format is:
            `nextGuest("WordChose","ResultFormat")`
        - The ResultFormat is:
            : 'x' - the character is not present in the word
            : '!' - the character is present and in the right place
            : '?' - the character is present but in the wrong place

    """

    STRATEGY_CHARFREQ = "charfreq"
    STRATEGY_CHARFREQ_WITH_AVOID_KNOW = "charfreqavoidknow"

    # def __init__(self, strategy, *args, **kwargs):
    def __init__(self, startVowels=3, incVowels=1):

        self.word = ['0' for i in range(5)]
        # used to hold characters for the exclusion [^`x`] regex
        self.wrong_place = [[] for i in range(5)]
        self.not_in_word = []
        self.in_word = []
        self.startVowels = startVowels
        self.incVowels = incVowels
        self.tryies = []
        self.test_case_generator = CaseWriter()
        self.end = None

        assert self.startVowels == 3 or self.startVowels == 2
        assert incVowels == 1 or incVowels == 2

        self.words5char = []
        self.loadWords()
        pass

    def nextGuess(self, str, pttr, ret=False):
        raise ValueError("Should not be called. Maybe a problem in constructor")

    def print_candidates_trained(self, in_word, out_of_word, word_regex):
        # raise ValueError("Should not be called. Maybe a problem in constructor")
        pass

    def loadWords(self):
        import json
        with open('words5char.json') as f:
            self.words5char = json.load(f)
            print("Loaded the {} words of our database".format(len(self.words5char)))
        pass

    def print_candidates(self, in_word, out_of_word, word_regex, ret=False):
        """
        in_word       - characters that must exist in the word
        out_of_word   - characters that can't exist in the word
        word_regex    - regex describing the word (which characters and in
              which position), ex. '^.a..s$' for 'patos'
        """
        candidates = []
        for w in self.words5char:
            if word_regex:
                if not re.match(word_regex, w):
                    continue
            if not self.check(in_word, w, "in"):
                continue
            if not self.check(out_of_word, w, "out"):
                continue

            candidates.append(w)

        if ret:
            return candidates

        for i in candidates:
            print(i)

    def check(self, test_chars, word_str, relations):
        """
            Given a set of test characteres it will test if they relates to the word_str
            returning trues if this relation holds.

            Ex.  check('ab',"colegio","in") ==> False
                 check('ab',"colegio","out") ==> True
                 check('ab',"colegio","biro") ==> TypeError
            """
        if relations == "in":
            for i in test_chars:
                if i not in word_str:
                    return False
            return True
        if relations == "out":
            for i in test_chars:
                if i in word_str:
                    return False
            return True
        raise TypeError("relations should be in/out")


class GuesserCharFrequencyNaive(Guesser):

    def __init__(self, startVowels=3, incVowels=1, initialGuess=True):
        super().__init__(startVowels=startVowels, incVowels=incVowels)
        if initialGuess:
            self.print_candidates_trained("", "", "")
        pass

    def nextGuess(self, usedword, pttr, ret=False):
        if pttr == "!!!!!":
            for t, r in self.tryies:
                self.test_case_generator.add_case(t, r)
            self.test_case_generator.finish(usedword)
            print("Word is =>  {}".format(usedword))
            self.end = usedword
            return []
        else:
            self.tryies.append((usedword, pttr))

        # ! has the most priority, should be evaluated first to avoid errors
        # (eg. removing a character of the pool after ensuring its position)
        for i in range(5):
            c = pttr[i]
            if c == '!':
                if usedword[i] not in self.word[i]:
                    self.word[i] = usedword[i]
                    self.in_word.append(usedword[i])

        for i in range(5):
            c = pttr[i]
            if c == 'x':
                if usedword[i] not in self.word and usedword[i] not in [z for x in self.wrong_place for z in x]:
                    self.not_in_word.append(usedword[i])
                else:
                    if usedword[i] not in self.wrong_place[i]:
                        self.wrong_place[i].append(usedword[i])
            elif c == '?':
                if usedword[i] not in self.wrong_place[i]:
                    self.wrong_place[i].append(usedword[i])
                    self.in_word.append(usedword[i])
            else:
                ValueError("Pattern should only have x ! or ?")

        arr_reg = [[] for i in range(5)]
        for i in range(5):
            c = self.word[i]
            if c == '0' and bool(self.wrong_place[i]):
                arr_reg[i] = '[^{}]'.format(''.join(self.wrong_place[i]))
            else:
                arr_reg[i] = c

        cur_reg = "".join([x if x != '0' else '.' for x in arr_reg])

        return self.print_candidates_trained("".join(set(self.in_word)), "".join(self.not_in_word), cur_reg, ret=ret)
        pass

    def print_candidates_trained(self, in_word, out_of_word, word_regex, ret=False):
        iw_l = len(in_word)

        vc = vowel_f.copy()
        cc = consonant_f.copy()
        candidates = None

        # No space for more characters
        if iw_l == 5:
            candidates = self.print_candidates(in_word, out_of_word, word_regex, ret=ret)
            if ret:
                return candidates
            else:
                print(candidates)

        # Removing chars that will not be included in the next pool
        for o in out_of_word + in_word:
            if o in vc:
                del vc[o]
                # print("removing ",o)
            if o in cc:
                del cc[o]
                # print("removing ",o)

        # We do not have any clue, first try
        if iw_l == 0:
            tmp_inw = "".join(
                [x[0] for x in sorted(vc.items(), key=operator.itemgetter(1), reverse=True)][0:self.startVowels])
            tmp_inw += "".join(
                [x[0] for x in sorted(cc.items(), key=operator.itemgetter(1), reverse=True)][0:5 - self.startVowels])
            candidates = self.print_candidates(tmp_inw, out_of_word, word_regex, ret=ret)
            if ret:
                return candidates
            else:
                print(candidates)

            return

        new_chars = ""

        # print("-",in_word)

        gen = CharacterGenerator(cc, vc, self.incVowels)
        char_gen = gen.char_generator()

        for i in range(5 - iw_l):
            new_chars += next(char_gen)

        print("-", in_word + new_chars)

        candidates = self.print_candidates(in_word + new_chars, out_of_word, word_regex, True)

        while not candidates:
            print("Failed! With sequence '{}'".format(in_word + new_chars))
            if new_chars:
                rollback = new_chars[-1]
                new_chars = new_chars[:-1]
                gen.back(rollback)
                try:
                    new_chars += next(char_gen)
                except StopIteration:
                    print("Ignoring last charcter")
            else:
                in_word = in_word[:-1]
            print("Retrying with '{}'".format(in_word + new_chars))
            candidates = self.print_candidates(in_word + new_chars, out_of_word, word_regex, True)

        if ret:
            return candidates
        else:
            print(candidates)

    pass


class GuesserCharFrequencyAvoidKnown(GuesserCharFrequencyNaive):

    def __init__(self, startVowels=3, incVowels=1, initialGuess=True):
        super().__init__(startVowels=startVowels, incVowels=incVowels, initialGuess=initialGuess)


    def nextGuess(self, usedword, pttr, ret=False, avoidKnown=False):
        if pttr == "!!!!!":
            for t, r in self.tryies:
                self.test_case_generator.add_case(t, r)
            self.test_case_generator.finish(usedword)
            print("Word is =>  {}".format(usedword))
            self.end = usedword
            return []
        else:
            self.tryies.append((usedword, pttr))

        # ! has the most priority, should be evaluated first to avoid errors
        # (eg. removing a character of the pool after ensuring its position)
        for i in range(5):
            c = pttr[i]
            if c == '!':
                if usedword[i] not in self.word[i]:
                    self.word[i] = usedword[i]
                    self.in_word.append(usedword[i])

        for i in range(5):
            c = pttr[i]
            if c == 'x':
                if usedword[i] not in self.word and usedword[i] not in [z for x in self.wrong_place for z in x]:
                    self.not_in_word.append(usedword[i])
                else:
                    if usedword[i] not in self.wrong_place[i]:
                        self.wrong_place[i].append(usedword[i])
            elif c == '?':
                if usedword[i] not in self.wrong_place[i]:
                    self.wrong_place[i].append(usedword[i])
                    self.in_word.append(usedword[i])
            else:
                ValueError("Pattern should only have x ! or ?")

        arr_reg = [[] for i in range(5)]
        for i in range(5):
            c = self.word[i]
            if c == '0' and bool(self.wrong_place[i]):
                arr_reg[i] = '[^{}]'.format(''.join(self.wrong_place[i]))
            else:
                arr_reg[i] = c

        cur_reg = "".join([x if x != '0' else '.' for x in arr_reg])

        if avoidKnown:
            cand = []
            sz = len(self.in_word)
            i = -1
            while i <= sz and not cand:
                i += 1
                cand = self.print_candidates_trained("".join(set(self.in_word[sz - i:sz])),
                                                     "".join((self.not_in_word + self.in_word[0:sz - i])), ".....",
                                                     ret=True)

            return self.print_candidates_trained("".join(set(self.in_word[sz - i:sz])),
                                                 "".join((self.not_in_word + self.in_word[0:sz - i])), ".....",
                                                 ret=ret)

        else:
            return self.print_candidates_trained("".join(set(self.in_word)), "".join(self.not_in_word), cur_reg,
                                                 ret=ret)


class DualGuesser:
    def __init__(self, startVowels=3):

        self.g1 = GuesserFactory.guesser(Guesser.STRATEGY_CHARFREQ, startVowels=startVowels)
        self.g2 = GuesserFactory.guesser(Guesser.STRATEGY_CHARFREQ, startVowels=startVowels, initialGuess=False)
        self.g1_end = False
        self.g2_end = False

    def nextGuess(self, w, g1a, g2a):
        g1c = self.g1.nextGuess(w, g1a, ret=True)
        g2c = self.g2.nextGuess(w, g2a, ret=True)

        self.g1_end = bool(g1c)
        self.g2_end = bool(g2c)

        u = [z for z in g1c if z in g2c]
        if u:
            print(u)
            return
        else:
            if g1c:
                if g2c:
                    g1c.extend(g2c)
                print(g1c)
        pass


class GuesserFactory:

    @classmethod
    def guesser(cls, strategy=Guesser.STRATEGY_CHARFREQ, startVowels=3, initialGuess=True) -> Guesser:
        if strategy == Guesser.STRATEGY_CHARFREQ:
            return GuesserCharFrequencyNaive(startVowels, incVowels=1, initialGuess=initialGuess)
        elif strategy == Guesser.STRATEGY_CHARFREQ_WITH_AVOID_KNOW:
            return GuesserCharFrequencyAvoidKnown(startVowels, incVowels=1, initialGuess=initialGuess)
        else:
            raise ValueError("Unknown Strategy {}".format(strategy))
        pass


if __name__ == '__main__':
    wg = GuesserFactory.guesser(Guesser.STRATEGY_CHARFREQ_WITH_AVOID_KNOW, 3)
    # Test this sequence
    # wg.nextGuess("morsa","x!xx?")
    # wg.nextGuess("boate","x!?xx")
    # wg.nextGuess("colai","?!?!x")
    # wg.nextGuess("locao","?!!!x")
    #wg.nextGuess("serao", "x!!x!", avoidKnown=True)
    # wg.nextGuess("boate", "x!?xx")
    # wg.nextGuess("colai","?!?!x")
    # wg.nextGuess("local", "x!!!!")
    # dg.nextGuess("ramos", "xxx?x", "!!xxx")
    # dg = DualGuesser(2, 2)
    # dg.nextGuess("ralei","xxxx?", "!!xxx")
    # dg.nextGuess("intuo","?xx?!", "xxxxx")
