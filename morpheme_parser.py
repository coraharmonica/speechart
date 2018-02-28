# coding: utf-8
"""
MORPHEME_PARSER:

    Contains MorphemeParser class for parsing morpheme data
    in a given language from Wiktionary.
"""
from language_parser import *


class Morpheme:
    """
    A class for distinguishing morphemes.

    1) free (roots)
        PARTS OF SPEECH:
        1) noun - "NN"
        2) verb - "VB"
        3) adj  - "JJ"
        4) adv  - "RB"

    2) bound (affixes)
        AFFIXES:
        1) prefix    (*XXX)
        2) suffix    (XXX*)
        3) infix     (X**X)
        4) circumfix (*XX*)
        5) interfix  (XX*X)
    """
    PARTS_OF_SPEECH = {"NN", "VB", "JJ", "RB"}
    AFFIXES = {"prefix",
               "suffix",
               "infix",
               "circumfix",
               "interfix"}

    def __init__(self, word, language, is_free, type):
        self.word = word
        self.language = language.title()
        self._is_free = is_free
        self._type = type      # root part-of-speech or affix type

    @property
    def is_free(self):
        return self._is_free

    @is_free.setter
    def is_free(self, value):
        self._is_free = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    def __hash__(self):
        return hash(self.word + self.language[:3] + str(self.type))


class MorphemeParser(LanguageParser):
    """
    A class for extracting and analyzing morphemes in a
    given language.
    """
    def __init__(self, language):
        LanguageParser.__init__(self, language)
        self.affixes = set()
        self.morphemes = set()

    def init_morphemes(self):
        words = self.words
        self.morphemes.update(words)

        for word in words: #sorted(words, key=lambda w: len(w)):
            word_morphemes = self.strip_affixes(word)
            print word, "has morphemes", word_morphemes
            print
            self.morphemes.update(word_morphemes)
            continue

        print "MorphemeParser's morphemes", len(self.morphemes), self.morphemes
        return self.morphemes

    def all_morphemes(self):
        """
        Returns a frequency dictionary of morphemes in this
        MorphemeParser's language.

        :return: dict, where...
            key (str) - morpheme in this MP's language
            val (int) - given morpheme's frequency
        """
        etymologies = self.all_etymologies()
        etymologies = self.compress_etymologies(etymologies)
        etymologies = etymologies.values()
        etymologies = self.flatten(etymologies)
        keys = set(etymologies)
        return {key: etymologies.count(key) for key in keys}

    def get_word_morphemes(self, word):
        subwords = [word]

        for morpheme in sorted(self.morphemes, key=lambda m: len(m), reverse=True):
            if morpheme in word and morpheme != word:
                new_subwords = subwords
                for subword in subwords:
                    if morpheme in subword:
                        new_subword = filter(lambda s: s != "", re.split("("+morpheme+")", subword))
                        idx = new_subwords.index(subword)
                        new_subwords = new_subwords[:idx] + new_subword + new_subwords[idx+1:]
                subwords = new_subwords

        print subwords
        self.morphemes.update(subwords)
        return subwords

    def get_morphemes(self, words):
        morphemes = set()

        for word in words:
            word_morphemes = self.strip_affixes(word)
            print word, "has morphemes", word_morphemes
            print
            morphemes.update(word_morphemes)
            continue

        print "MorphemeParser's morphemes", len(morphemes), morphemes
        return morphemes

    def strip_affixes(self, word):
        words = self.morphemes.union(self.words)
        morphemes = []
        new_word = word
        last_morpheme = str()

        while len(new_word) != 0:
            for morpheme in sorted(words, key=lambda m: len(m), reverse=True):
                if morpheme != word and len(morpheme) > 1:
                    if morpheme == new_word[:len(morpheme)] and len(last_morpheme) > 1 and last_morpheme in words:
                        morphemes.append(last_morpheme)
                        morphemes.append(morpheme)
                        new_word = new_word[len(morpheme):]
                        last_morpheme = str()
                        break
            else:
                last_morpheme += new_word[0]
                new_word = new_word[1:]
                if len(new_word) == 0:
                    morphemes.append(last_morpheme)

        return filter(lambda m: m != "", morphemes)

    def compress_etymologies(self, etymologies):
        """
        Returns the given dictionary of etymologies with each
        non-atomic etymology replaced with atomic etymologies.

        :param etymologies: dict, where...
            key (str) - word with etymology
            val (List[str]) - given word's etymology (as a combination of words)
        :return: dict, where...
            key (str) - word with etymology
            val (List[str]) - given word's etymology (as a combination of words)
        """
        compressed = dict()

        for word in etymologies:
            etymology = etymologies[word]
            morphemes = etymology[:]
            while any(m in etymologies for m in morphemes):
                for i in range(len(morphemes)):
                    morpheme = morphemes[i]
                    if morpheme in etymologies:
                        derivs = etymologies[morpheme]
                        if not all(d in morphemes for d in derivs):
                            morphemes = morphemes[:i] + derivs + morphemes[i+1:]
                            break
                else:
                    break
            compressed[word] = morphemes
            print "compressed", etymology, "to", morphemes

        return compressed

    def flatten(self, lst):
        """
        Flattens the given list of lists to a list.
        ~
        e.g. flatten([[1, 2], [3, 4]]) -> [1, 2, 3, 4]

        :param derivations: List[List[X]], list of lists to flatten
        :return: List[X], input list flattened
        """
        return [item for sublst in lst for item in sublst]

    # SYLLABLES
    # ---------
    def break_word_syllable(self, syllable):
        """
        Breaks the given word syllable into its constituent
        consonants and vowels.
        ~
        N.B. In a syllable...
            1) The first set of consonants is called the ONSET.
            2) The set of vowels is called the RHYME.
            3) The second set of consonants is called the CODA.
        ~
        e.g. break_syllable("wszech") -> ("wsz", "e", "ch")

        :param syllable: (unicode) str, syllable to break
        :return: tuple((all unicode) str, str, str), the given
            syllable's onset, rhyme, and coda, respectively
        """
        onset = ""
        rhyme = ""
        coda = ""

        pre_rhyme = True

        for i in range(len(syllable)):
            char = syllable[i]

            if self.is_letter_vowel(char) is None:
                return ("", "", "")
            elif self.is_letter_vowel(char):
                pre_rhyme = False
                rhyme += char
            else:
                if pre_rhyme:
                    onset += char
                else:
                    coda += char

        return (onset, rhyme, coda)

    def break_word_syllables(self, word):
        """
        Breaks the given word into its constituent syllables'
        consonants and vowels.
        ~
        N.B. In a syllable...
            1) The first set of consonants is called the ONSET.
            2) The set of vowels is called the RHYME.
            3) The second set of consonants is called the CODA.
        ~
        e.g. break_word_syllables("wszechmocny") -> [("wsz", "e", "ch"),
                                                     ("m", "o", "c"),
                                                     ("n", "y", "")]

        :param syllable: (unicode) str, syllable to break
        :return: List[tuple((all unicode)] str, str, str), the given
            word's syllables' onsets, rhymes, and codas, respectively
        """
        return [self.break_word_syllable(syllable) for syllable in self.split_word_syllables(word)]

    def split_word_syllables(self, word):
        """
        Splits the given word into its constituent
        syllables.
        ~
        e.g. split_word_syllables("wszechmocny") -> ["wszech", "moc", "ny"]

        :param word: (unicode) str, word to break into syllables
        :return: List[(unicode) str], list of given word's syllables
        """
        syllables = []
        onset, rhyme, coda = "", "", ""
        pre_rhyme = True

        for i in range(len(word)):
            letter = word[i]

            if self.is_letter_vowel(letter):
                pre_rhyme = False
                rhyme += letter
            else:
                if pre_rhyme:
                    onset += letter
                else:
                    if not any(self.is_letter_vowel(char) for char in word[i:]):
                        coda += word[i:]
                        break
                    elif i+1 < len(word) and self.is_letter_vowel(word[i+1]):
                        coda += word[i]
                    triplet = (onset, rhyme, coda)
                    syllables.append(triplet)
                    onset, rhyme, coda = "", "", ""
                    pre_rhyme = True

        return syllables

    def break_syllable(self, syllable):
        """
        Breaks the given IPA syllable into its constituent
        consonants and vowels.
        ~
        N.B. In a syllable...
            1) The first set of consonants is called the ONSET.
            2) The set of vowels is called the RHYME.
            3) The second set of consonants is called the CODA.
        ~
        e.g. break_syllable("lat͡ɕ") -> ("l", "a", "t͡ɕ")

        :param syllable: (unicode) str, syllable to break
        :return: tuple((all unicode) str, str, str), the given
            syllable's onset, rhyme, and coda, respectively
        """
        onset = ""
        rhyme = ""
        coda = ""
        pre_rhyme = True
        next_syllable = syllable

        while len(next_syllable) != 0:
            next_phoneme, next_syllable = self.next_phoneme(next_syllable)
            is_vowel = self.is_ipa_vowel(next_phoneme)
            if pre_rhyme:
                if is_vowel:
                    pre_rhyme = False
                    rhyme += next_phoneme
                else:
                    onset += next_phoneme
            else:
                if is_vowel or self.is_ipa_semivowel(next_phoneme):
                    rhyme += next_phoneme
                else:
                    coda += next_phoneme + next_syllable
                    break

        return (onset, rhyme, coda)

    def break_syllables(self, ipa, use_syllables=True):
        """
        Breaks the given IPA word into its syllables' constituent
        consonants and vowels.
        ~
        N.B. In a syllable...
            1) The first set of consonants is called the ONSET.
            2) The set of vowels is called the RHYME.
            3) The second set of consonants is called the CODA.
        ~
        e.g. break_syllables("ɔˈba.lat͡ɕ") -> [("", "ɔ", ""),
                                              ("b", "a", ""),
                                              ("l", "a", "t͡ɕ")]

        :param ipa: (unicode) str, IPA word to break into constituents
        :param use_syllables: bool, whether to break syllables with IPA markers
        :return: List[tuple((all unicode) str, str, str)], the given
            syllables' onsets, rhymes, and codas, respectively
        """
        return [self.break_syllable(syllable)
                for syllable in self.split_syllables(ipa, use_syllables)]

    def extract_syllable(self, ipa, idx=0, use_syllables=True):
        """
        Returns the given ipa's syllable at the given idx.
        ~
        If the index is out of bounds, this method returns a
        3-tuple of all empty strings.
        ~
        e.g. extract_syllable("ɔˈba.lat͡ɕ", 2) -> ("l", "a", "t͡ɕ")
             extract_syllable("ɔbalat͡ɕ", 2, False) -> ("l", "a", "t͡ɕ")

        :param ipa: (unicode) str, IPA word to return syllable at idx
        :param idx: int, syllable to retrieve from IPA word
        :param use_syllables: bool, whether to calculate phonemes with ipa's syllables
        :return: tuple((all unicode) str, str, str), the given
            syllable's onsets, rhymes, and codas, respectively
        """
        syllables = self.split_syllables(ipa, use_syllables)
        try:
            syllable = syllables[idx]
        except IndexError:
            return "", "", ""
        else:
            return self.break_syllable(syllable)

    def remove_syllable(self, ipa, idx=0):
        """
        Returns given ipa with the syllable at given index idx removed.
        ~
        If the index is out of bounds, this method returns the input ipa.
        ~
        e.g. remove_syllable("ɔˈba.lat͡ɕ", 2) -> "ɔ.lat͡ɕ"

        :param ipa: (unicode) str, IPA word to remove syllable at idx
        :param idx: int, syllable to remove from IPA word
        :return: (unicode) str, given ipa without syllable at idx
        """
        syllables = self.split_syllables(ipa)
        syllables.pop(idx)
        return ".".join(syllables)

    def split_syllables(self, ipa, use_syllables=True):
        """
        Splits the given IPA word into its constituent
        syllables.
        ~
        e.g. split_syllables("ɔˈba.lat͡ɕ") -> ["ɔ", "ba", "lat͡ɕ"]
             split_syllables("ɔˈba.lat͡ɕ", use_syllables=False) -> ["ɔ", "ba", "lat͡ɕ"]

        :param ipa: (unicode) str, IPA word to break into syllables
        :param use_syllables: bool, whether to calculate phonemes with ipa's syllables
        :return: List[(unicode) str], list of given ipa's syllables
        """
        if len(ipa) == 0:
            return
        else:
            if use_syllables:
                subbed_ipa = re.sub(u"[ˈˌ]", u".", ipa)
                subbed_ipa = subbed_ipa.strip(u".")
                syllables = subbed_ipa.split(u".")
                return syllables
            else:
                ipa = self.clean_ipa(ipa)
                syllables = []

                while len(ipa) != 0:
                    syllable, ipa = self.next_syllable(ipa, remove=True)
                    syllables.append(syllable)

                return syllables

    def next_syllable(self, ipa, remove=True):
        """
        Returns the given ipa's next syllable.
        ~
        Assumes given ipa does not contain syllabic markers.
        ~
        If remove is set to True, this method finds and
        removes ipa's first syllable, returning a 2-tuple of
        1) the syllable and 2) given ipa with syllable removed.
        ~
        e.g. next_syllable("ɔˈba.lat͡ɕ") -> ("ɔ", "ba.lat͡ɕ")
             next_syllable("ɔˈba.lat͡ɕ", remove=False) -> "ɔ"

        :param ipa: (unicode) str, IPA word to return next syllable of
        :param remove: bool, whether to return ipa with syllable removed
        :return: tuple((both unicode) str, str), ipa's next syllable and rest of IPA
        """
        ipa = self.clean_ipa(ipa)
        syllable = []
        pre_vowel = True

        while len(ipa) != 0:
            phoneme, ipa = self.next_phoneme(ipa, remove=True, use_syllables=False)
            is_vowel = self.is_ipa_vowel(phoneme)

            if pre_vowel:
                if is_vowel:
                    pre_vowel = False
                syllable.append(phoneme)
            else:
                if is_vowel:
                    syllable.append(phoneme)
                else:
                    if len(ipa) == 0:
                        syllable.append(phoneme)
                    else:
                        new_phoneme, new_ipa = self.next_phoneme(ipa, remove=True, use_syllables=False)
                        if self.is_ipa_vowel(new_phoneme) is False:
                            syllable.append(phoneme)
                        else:
                            ipa = phoneme + ipa
                        break

        syllable = "".join(syllable)
        syllable = (syllable, ipa) if remove else syllable
        return syllable

