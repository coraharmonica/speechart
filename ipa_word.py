# coding: utf-8

import re
import ipas
from ordered_set import OrderedSet
from ipa_symbols import IPACONSONANTS, IPAVOWELS


class IPAWord:
    """
    A class for representing and operating on words and their IPA pronunciations.
    """
    def __init__(self, word, ipa, parser, pos=None):
        self.word = word
        self.pos = pos
        self.parser = parser
        self.vowels = OrderedSet([])
        self.consonants = OrderedSet([])
        self.ipa = ipa
        ipa_syllables = self.count_ipa_syllables(self.ipa)
        ipa_stresses = self.count_ipa_stresses(self.ipa)
        if ipa_syllables != ipa_stresses:
            self.ipa = self.equate_ipa_syllables(ipa)
        self.lang = self.parser.language
        self.phoneme_dict = {}
        self.word_model = self.build_word_model(self.word)
        self.ipa_model = self.build_ipa_model(self.ipa)
        self.difficulty = self.difficulty_score()
        self.find_phoneme_dict(self.word, self.ipa)

    def get_word(self):
        """
        Returns this IPAWord's word, in its native language's alphabet.

        :return: str, this IPAWord's word
        """
        return self.clean_word(self.word)

    def get_pos(self):
        """
        Returns this IPAWord's part-of-speech, pos.

        :return: str, this IPAWord's part-of-speech
        """
        return self.pos

    def get_ipa(self):
        """
        Returns this IPAWord's pronunciation in IPA.

        :return: str, this IPAWord's IPA pronunciation
        """
        return self.ipa

    def get_cleaned_ipa(self):
        """
        Returns this IPAWord's pronunciation in IPA,
        with no stress symbols.

        :return: str, this IPAWord's IPA pronunciation
        """
        return self.clean_ipa(self.ipa)

    def get_phoneme_dict(self):
        """
        Returns this IPAWord's phoneme dictionary.

        :return: dict, where...
            key (str) - >=1 letters in a native language alphabet
            val (Set(str)) - list of >=1 IPA symbols corresponding to key
        """
        return self.phoneme_dict

    def get_difficulty(self):
        return self.difficulty

    def init_phoneme_dict(self):
        """
        Initializes this IPAWord's phoneme dictionary.

        :return: dict, where...
            key (str) - >=1 letters in a native language alphabet
            val (Set(str)) - list of >=1 IPA symbols corresponding to key
        """
        self.phoneme_dict = self.find_phoneme_dict()

    def set_pos(self, pos):
        """
        Sets given pos to this IPAWord's part-of-speech.

        :param pos: str, this IPAWord's part-of-speech
        :return: None
        """
        self.pos = pos

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
        e.g. break_word_syllable("wszech") -> ("wsz", "e", "ch")

        :param syllable: (unicode) str, syllable to break
        :return: tuple((all unicode) str, str, str), the given
            syllable's onset, rhyme, and coda, respectively
        """
        return self.parser.break_word_syllable(syllable)

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
        return self.parser.break_word_syllable(word)

    def split_word_syllables(self, word):
        """
        Splits the given word into its constituent
        syllables.
        ~
        e.g. split_word_syllables("wszechmocny") -> ["wszech", "moc", "ny"]

        :param word: (unicode) str, word to break into syllables
        :return: List[(unicode) str], list of given word's syllables
        """
        return self.parser.split_word_syllables(word)

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
        return self.parser.break_syllable(syllable)

    def break_syllables(self, ipa, use_syllables):
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
        return self.parser.break_syllables(ipa, use_syllables)

    def extract_syllable(self, ipa, idx=0, use_syllables=True):
        """
        Returns the given ipa's syllable at the given idx.
        ~
        If the index is out of bounds, this method returns a
        3-tuple of all empty strings.
        ~
        e.g. extract_syllable("ɔˈba.lat͡ɕ", 2) -> ("l", "a", "t͡ɕ")

        :param ipa: (unicode) str, IPA word to return syllable at idx
        :param idx: int, syllable to retrieve from IPA word
        :param use_syllables: bool, whether to calculate phonemes with ipa's syllables
        :return: tuple((all unicode) str, str, str), the given
            syllable's onsets, rhymes, and codas, respectively
        """
        return self.parser.extract_syllable(ipa, idx, use_syllables)

    def remove_syllable(self, ipa, idx=0):
        """
        Returns given ipa with the syllable at given index idx removed.
        ~
        If the index is out of bounds, this method returns the input ipa.
        ~
        e.g. remove_syllable("ɔˈba.lat͡ɕ", 2) -> "ɔˈba"

        :param ipa: (unicode) str, IPA word to remove syllable at idx
        :param idx: int, syllable to remove from IPA word
        :return: (unicode) str, given ipa without syllable at idx
        """
        return self.parser.remove_syllable(ipa, idx)

    def split_syllables(self, ipa, use_syllables=True):
        """
        Splits the given IPA word into its constituent
        syllables.
        ~
        e.g. split_syllables("ɔˈba.lat͡ɕ") -> ["ɔ", "ba", "lat͡ɕ"]

        :param ipa: (unicode) str, IPA word to break into syllables
        :param use_syllables: bool, whether to calculate phonemes with ipa's syllables
        :return: List[(unicode) str], list of given ipa's syllables
        """
        return self.parser.split_syllables(ipa, use_syllables)

    def next_phoneme(self, ipa, remove=True, use_syllables=True):
        """
        Returns the given ipa's next phoneme.
        ~
        e.g. next_phoneme("ɔˈba.lat͡ɕ") -> "ɔ"

        :param ipa: (unicode) str, IPA word to return next phoneme of
        :param remove: bool, whether to return ipa with vowels removed
        :param use_syllables: bool, whether to calculate next phoneme with ipa's syllables
        :return: (unicode) str, given IPA's next phoneme
        """
        return self.parser.next_phoneme(ipa, remove, use_syllables)

    def next_syllable(self, ipa, remove=True):
        """
        Returns the given ipa's next syllable.
        ~
        Assumes given ipa does not contain syllabic markers.
        ~
        e.g. next_syllable("ɔˈba.lat͡ɕ") -> ("ɔ", "ba.lat͡ɕ")

        :param ipa: (unicode) str, IPA word to return next syllable of
        :param remove: bool, whether to return ipa with syllable removed
        :return: tuple((both unicode) str, str), ipa's next syllable and rest of IPA
        """
        return self.parser.next_syllable(ipa, remove)

    def add_phoneme_entry(self, chars, ipas):
        """
        Adds the given chars-ipas pair to this IPAWord and IPAParser's
        phoneme_dict.

        :param chars: str, phoneme (i.e., short sequence of characters)
        :param ipas: str, IPA translation of this language's phoneme
        :return: None
        """
        self.phoneme_dict.setdefault(chars, OrderedSet([]))
        self.phoneme_dict[chars].add(ipas)
        if self.is_ipa_vowel(ipas):
            self.add_vowel(chars)
        if self.is_ipa_vowel(ipas) is False or any(self.is_ipa_vowel(ipa) is False for ipa in ipas):
            self.add_consonant(chars)
        self.parser.add_phoneme_entry(chars, ipas)

    def add_vowel(self, chars):
        """
        Adds the given chars to this IPAWord and IPAParser's
        list of vowels.

        :param chars: str, phoneme (i.e., short sequence of characters)
        :return: None
        """
        self.vowels.add(chars)
        self.parser.add_vowel(chars)

    def add_consonant(self, chars):
        """
        Adds the given chars to this IPAWord and IPAParser's
        list of consonants.

        :param chars: str, phoneme (i.e., short sequence of characters)
        :return: None
        """
        self.consonants.add(chars)
        self.parser.add_consonant(chars)

    def find_vowels(self, phrase, remove=True):
        """
        Returns the first continuous string of vowels in
        the given phrase.
        ~
        If remove is set to True, this method finds and removes
        the first string of vowels, returning a tuple of the
        vowels and the given phrase after the vowels.
        ~
        e.g. find_vowels("stroop", remove=False) -> "oo"
             find_vowels("stroop", remove=True) -> ("oo", "p")

        :param phrase: str, phrase to extract vowels from
        :param remove: bool, whether to return phrase with vowels removed
        :return: str, first string of vowels in phrase
        """
        pre_vowels = True
        vowels = unicode(u"")
        char_idx = 0

        for char in phrase:
            if pre_vowels:
                if self.is_letter_vowel(char) is True:
                    pre_vowels = False
                    vowels += char
            else:
                if self.is_letter_vowel(char) is not False:
                    vowels += char
                else:
                    break

            char_idx += 1

        if remove:
            remainder = phrase[char_idx:]
            return (vowels, remainder)
        else:
            return vowels

    def find_consonants(self, phrase, remove=True):
        """
        Returns the first continuous string of consonants in
        the given phrase.
        ~
        If remove is set to True, this method finds and removes
        the first string of consonants, returning a tuple.
        ~
        e.g. find_consonants("stroop", remove=False) -> "str"
             find_consonants("stroop", remove=True) -> ("str", "oop")

        :param phrase: str, phrase to extract consonants from
        :param remove: bool, whether to return phrase with consonants removed
        :return: str, first string of consonants in phrase
              or tuple(str, str), first string of consonants in phrase and
              phrase with consonants removed
        """
        pre_consonants = True
        consonants = unicode()
        char_idx = 0

        for char in phrase:
            if pre_consonants:
                if self.is_letter_vowel(char) is False:
                    pre_consonants = False
                    consonants += char
            else:
                if self.is_letter_vowel(char) is True:
                    phoneme2 = consonants[-2:]
                    if self.is_letter_consonant(phoneme2):
                        consonants = consonants[:-2]
                        char_idx -= 2
                    else:
                        consonants = consonants[:-1]
                        char_idx -= 1
                    break
                else:
                    consonants += char

            char_idx += 1

        if remove:
            remainder = phrase[char_idx:]
            return (consonants, remainder)
        else:
            return consonants

    def find_ipa_vowels(self, ipa, remove=True):
        """
        Returns the first continuous string of vowels in
        the given IPA.
        ~
        If remove is set to True, this method finds and removes
        the first string of vowels, returning a tuple of the
        vowels and the given IPA after the vowels.
        ~
        e.g. find_vowels("twɔk", remove=False) -> "ɔ"
             find_vowels("twɔk", remove=True) -> ("ɔ", "k")

        :param ipa: (unicode) str, IPA to extract vowels from
        :param remove: bool, whether to return phrase with vowels removed
        :return: (unicode) str, first string of vowels in IPA
        """
        ipa = self.restress(ipa)
        pre_vowels = True
        vowels = unicode()
        sym_idx = 0

        for sym in ipa:
            if pre_vowels:
                if self.is_ipa_vowel(sym):
                    pre_vowels = False
                    vowels += sym
            else:
                if self.is_ipa_vowel(sym):
                    vowels += sym
                else:
                    if sym == u".":
                        sym_idx += 1
                    break

            sym_idx += 1

        if remove:
            remainder = ipa[sym_idx:]
            return (vowels, remainder)
        else:
            return vowels

    def find_ipa_consonants(self, ipa, remove=True):
        """
        Returns the first continuous string of consonants in
        the given IPA.
        ~
        If remove is set to True, this method finds and removes
        the first string of consonants, returning a tuple of the
        consonants and the given IPA after the consonants.
        ~
        e.g. find_consonants("twɔk", remove=False) -> "tw"
             find_consonants("twɔk", remove=True) -> ("tw", "ɔk")

        :param ipa: (unicode) str, IPA to extract consonants from
        :param remove: bool, whether to return phrase with consonants removed
        :return: (unicode) str, first string of consonants in IPA
        """
        ipa = self.restress(ipa)
        pre_consonants = True
        consonants = unicode()
        sym_idx = 0

        for sym in ipa:
            is_vowel = self.is_ipa_vowel(sym)

            if pre_consonants:
                if is_vowel is False:
                    pre_consonants = False
                    consonants += sym
            else:
                if is_vowel:
                    sym_idx -= 1
                    consonants = consonants[:sym_idx]
                    sym_idx += 1
                    break
                else:
                    if sym == u".":
                        sym_idx += 1
                        break
                    else:
                        consonants += sym

            sym_idx += 1

        if remove:
            remainder = ipa[sym_idx:]
            return (consonants, remainder)
        else:
            return consonants

    def find_letter_phonemes(self):
        """
        Returns this IPAWord's letter phonemes as a list of
        character strings.
        ~
        Phonemes are calculated from this IPAWord's word as well as ipa.
        ~
        e.g. cat = IPAWord("cat", "Noun", "kæt", IPAParser("English"))
             cat.find_letter_phonemes() -> ["c", "a", "t"]

             text = IPAWord("text", "Noun", "tɛkst", IPAParser("English"))
             text.find_letter_phonemes() -> ["t", "e", "x", "t"]

        :return: List[(unicode) str], this IPAWord's letter phonemes
        """
        cleaned_ipa = self.get_cleaned_ipa()
        phonemes = []

        size = len(cleaned_ipa)
        start = 0   # inclusive
        end = 1     # exclusive

        while end <= size:
            if end != size and cleaned_ipa[end] in ipas.SYMBOLS:
                if cleaned_ipa[end] in ipas.AFFRICATES:
                    end += 1  # skip 2 for affricates
                end += 1      # skip 1 for diacritics
            else:
                phoneme = cleaned_ipa[start:end]
                phonemes.append(phoneme)
                start = end
                end = start + 1

        return phonemes

    def extract_vowels(self, ipas):
        """
        Breaks the given ipas into a list of IPA vowels.
        ~
        Assumes ipas contains no consonants.

        :param ipas: (unicode) str, IPA to break into a list of vowels
        :return: List[(unicode) str], IPA broken into vowels
        """
        phonemes = []
        ipas_iter = iter(range(len(ipas)))

        for i in ipas_iter:
            try:
                ipas[i+2]
            except IndexError:
                pass
            else:
                phone_2 = ipas[i:i+2]
                if self.is_ipa_vowel(phone_2):
                    phonemes.append(phone_2)
                    next(ipas_iter)
                    continue

            phone_1 = ipas[i]

            if self.is_ipa_vowel(phone_1):
                phonemes.append(phone_1)
                continue

            try:
                ipas[i+3]
            except IndexError:
                pass
            else:
                phone_3 = ipas[i:i+3]
                if self.is_ipa_vowel(phone_3):
                    phonemes.append(phone_3)
                    next(ipas_iter)
                    next(ipas_iter)
                    continue

            phonemes.append(phone_1)

        return phonemes

    def extract_consonants(self, ipas):
        """
        Breaks the given ipas into a list of IPA consonants.
        ~
        Assumes ipas contains no vowels.

        :param ipas: (unicode) str, IPA to break into a list of consonants
        :return: List[(unicode) str], IPA broken into consonants
        """
        phonemes = []
        ipas_iter = iter(range(len(ipas)))

        for i in ipas_iter:
            try:
                phone_1 = ipas[i:i+1]
            except IndexError:
                pass
            else:
                if self.is_ipa_vowel(phone_1) is False:
                    phonemes.append(phone_1)
                    next(ipas_iter)
                    continue

            phone_0 = ipas[i]

            if self.is_ipa_vowel(phone_0) is False:
                phonemes.append(phone_0)
                continue

            try:
                phone_2 = ipas[i:i+2]
            except IndexError:
                pass
            else:
                if self.is_ipa_vowel(phone_2) is False:
                    phonemes.append(phone_2)
                    next(ipas_iter)
                    next(ipas_iter)
                    continue

            phonemes.append(phone_0)

        return phonemes

    def find_ipa_phonemes(self, ipa, use_syllables=True):
        """
        Returns this IPAWord's phonemes as a list of IPA unicode strings.
        ~
        Phonemes are calculated from this IPAWord's self.ipa.
        ~
        e.g. cat = IPAWord("cat", "Noun", "kæt", IPAParser("English"))
             cat.find_ipa_phonemes() -> ["k", "æ", "t"]

             text = IPAWord("text", "Noun", "tɛkst", IPAParser("English"))
             text.find_ipa_phonemes() -> ["t", "ɛ", "ks", "t"]

        :param ipa: (unicode) str, IPA to find phonemes of
        :param use_syllables: bool, whether to calculate phonemes with ipa's syllables
        :return: List[(unicode) str], this IPAWord's phonemes in IPA
        """
        if len(ipa) == 0:
            return []
        else:
            phonemes = []
            next_ipa = ipa

            while len(next_ipa) != 0:
                next_phoneme, next_ipa = self.next_phoneme(next_ipa, use_syllables)
                phonemes.append(next_phoneme)

            return phonemes

    def find_word_phonemes(self, word, ipa):
        """
        Finds this word-IPA pair's phonemes and
        adds them to this IPAWord's phoneme_dict.
        ~
        Returns None.
        ~
        N.B. For now, this method only works with 1-syllable words.

        :param word: (unicode) str, word to add phonemes of
        :param ipa: (unicode) str, IPA corresponding to word
        :return: None
        """
        parts = self.break_syllable(ipa)
        onset, rhyme, coda = parts
        vowel_start, vowel_end = 0, None
        clean_ipa = self.clean_ipa(ipa)

        if all(len(part) == 1 for part in parts) and len(word) == len(clean_ipa):
            self.add_phoneme_entry(word[0], onset)
            self.add_phoneme_entry(word[1], rhyme)
            self.add_phoneme_entry(word[2], coda)
            return

        if len(onset) != 0:
            # there MUST be consonant letter(s) @ beginning of word
            # at least 1st letter is consonant
            vowel_start += 1
            while all(self.is_letter_vowel(c) is False for c in word[:vowel_start+1]) \
                    and vowel_start+1 < len(word):
                vowel_start += 1
            char = word[:vowel_start]
            self.add_phoneme_entry(char, onset)
            self.add_consonant(char)

        if len(coda) != 0:
            # there MUST be consonant letter(s) @ end of word
            # at least last letter is consonant
            vowel_end = -1
            while all(self.is_letter_vowel(c) is not True for c in word[vowel_end-1:]) \
                    and vowel_end-1 > vowel_start:
                vowel_end -= 1
            char = word[vowel_end:]
            self.add_phoneme_entry(char, coda)
            self.add_consonant(char)

        if len(rhyme) != 0:
            # there MUST be vowel letter(s) @ middle of word
            char = word[vowel_start:vowel_end]
            self.add_phoneme_entry(char, rhyme)
            self.add_vowel(char)

    def find_hard_word_phonemes(self, word, ipa):
        """
        Finds this hard word-IPA pair's phonemes and
        adds them to this IPAWord's phoneme_dict.
        ~
        Returns None.
        ~
        N.B. This method is for words with >1 syllable.

        :param word: (unicode) str, word to add phonemes of
        :param ipa: (unicode) str, IPA corresponding to word
        :return: None
        """
        broken_syllables = self.break_syllables(ipa, use_syllables=True)
        rest_word = word

        for i in range(len(broken_syllables)):
            syllable = broken_syllables[i]
            onset, rhyme, coda = syllable

            if len(onset) != 0:
                consonants, rest_word = self.find_consonants(rest_word)
                if len(consonants) != 0:
                    self.add_phoneme_entry(consonants, onset)

            if len(rhyme) != 0:
                vowels, rest_word = self.find_vowels(rest_word)
                if len(vowels) != 0:
                    self.add_phoneme_entry(vowels, rhyme)

            if len(coda) != 0:
                consonants, rest_word = self.find_consonants(rest_word)
                if len(consonants) != 0:
                    self.add_phoneme_entry(consonants, coda)

    def find_phoneme_dict(self, word=None, ipa=None):
        """
        Returns a dictionary representing this IPAWord's ipa_phonemes,
        with native alphabet letters as keys and IPA symbols as values.
        ~
        Phonemes are calculated from this IPAWord's self.ipa_phonemes.

        :param word: (unicode) str, word to return phoneme dictionary for
        :param ipa: (unicode) str, IPA corresponding to word
        :return: dict, where...
            key (str) - >=1 letters in a native language alphabet
            val (OrderedSet(str)) - list of >=1 IPA symbols corresponding to key
        """
        word = self.word if word is None else word
        ipa = self.ipa if ipa is None else ipa
        ipa_phonemes = self.find_ipa_phonemes(ipa)
        #print "$$$\nIPA PHONEMES", ipa_phonemes

        if self.equal_word_ipa_syllables(word, ipa) == 1:
            # 1 syllable therefore only 1 set of onset/rhyme/coda
            if len(ipa_phonemes) == 1:
                self.add_phoneme_entry(word, ipa_phonemes[0])
            else:
                self.find_word_phonemes(word, ipa)

        elif not self.is_difficult(word, ipa_phonemes):
            for i in range(len(word)):
                char = word[i]
                phoneme = ipa_phonemes[i]
                self.add_phoneme_entry(char, phoneme)

        else:
            self.find_hard_word_phonemes(word, ipa)

        return self.phoneme_dict

    def build_word_model(self, word):
        """
        Builds a word model for the given word which
        organizes the word's characters into a dictionary of
        characters and a list of their common following characters.

        :param word: str, string to build model of
        :return: dict, where...
            key (str) - preceding character in word
            val (OrderedSet(str)) - characters following preceding character
        """
        word_model = {}
        word += " "
        for i in range(len(word)):
            try:
                after = word[i+1]
            except IndexError:
                break
            else:
                prev = word[i]
                word_model.setdefault(prev, OrderedSet([]))
                word_model[prev].add(after)
        return word_model

    def build_ipa_model(self, ipa):
        ipa_model = {}
        ipa_phonemes = self.find_ipa_phonemes(ipa)
        ipa_phonemes.append(u" ")

        for i in range(len(ipa_phonemes)):
            try:
                after = ipa_phonemes[i+1]
            except IndexError:
                break
            else:
                prev = ipa_phonemes[i]
                ipa_model.setdefault(prev, OrderedSet([]))
                ipa_model[prev].add(after)
        return ipa_model

    def is_letter_vowel(self, char):
        """
        Returns True if the given character is a vowel in this
        IPAWord's native language, False if a consonant.
        ~
        Returns None if this character is not yet linked to an
        IPA symbol.
        ~
        N.B. char can be multiple letters long.

        :param char: (unicode) str, character to determine whether vowel
        :return: bool, whether given character is a vowel
        """
        return self.parser.is_letter_vowel(char)

    def is_letter_consonant(self, char):
        """
        Returns True if the given character is a consonant in this
        IPAWord's native language, False if a vowel.
        ~
        Returns None if this character is not yet linked to an
        IPA symbol.
        ~
        N.B. char can be multiple letters long.

        :param char: (unicode) str, character to determine whether consonant
        :return: bool, whether given character is a consonant
        """
        return self.parser.is_letter_consonant(char)

    def is_ipa_vowel(self, ipa):
        """
        Returns True if the given IPA symbol is a vowel
        according to the IPA, False if a consonant.
        ~
        Returns None if this symbol is not an IPA letter.

        :param ipa: (unicode) str, IPA symbol to determine whether vowel
        :return: bool, whether given IPA symbol is a vowel
        """
        return self.parser.is_ipa_vowel(ipa)

    def is_ipa_phoneme(self, ipa):
        """
        Returns True if the given IPA symbol is a phoneme
        in this IPAParser's language, False otherwise.

        :param ipa: (unicode) str, IPA symbol to determine whether phoneme
        :return: bool, whether given IPA symbol is a phoneme
        """
        return self.parser.is_ipa_phoneme(ipa)

    def is_difficult(self, word, ipas):
        """
        Returns True if the given word-ipas pair is
        difficult to phonemize, False otherwise.
        ~
        Used to sort easy from difficult words.

        :param word: (unicode) str, word to determine whether difficult
        :param ipas: List[(unicode) str], IPAs of word to determine whether difficult
        :return: bool, whether given word-ipas pair is difficult to phonemize
        """
        return len(word) != len(ipas) or any(len(sym) > 1 for sym in ipas)

    def difficulty_score(self, word=None, ipas=None):
        """
        Returns an integer representing the difficulty of
        translating this word-ipas pair.
        ~
        Calculates difficulty score by subtracting the
        length of the word from the length of its IPAs.
        ~
        If word and/or ipas is None, this method replaces
        them with self.word and/or self.ipa respectively.
        ~
        Used to determine the difficulty of translating
        this word-ipas pair for sorting.

        :param word: (unicode) str, word to determine difficulty of
        :param ipas: List[(unicode) str], word's IPA pronunciations to score
        :return: int, number representing differences between word and ipas
        """
        word = self.word if word is None else word
        ipas = self.find_ipa_phonemes(self.ipa) if ipas is None else ipas
        score = (abs(len(word) - len(ipas)) + (max(0, len(word) - 2)))**2 + sum((len(sym)-1)**2 for sym in ipas)
        return score

    def add_syllables(self, ipa):
        """
        Adds most likely syllable marks to this IPA.
        ~
        Assumes given IPA has no syllable marks.
        ~
        This method does not account for primary/secondary stresses
        and thus only adds a period (".") to show stress.

        :param ipa: (unicode) str, IPA to add syllable marks to
        :return: (unicode) str, IPA with syllable marks added
        """
        syllables = []
        next_ipa = ipa

        while len(next_ipa) != 0:
            syllable, next_ipa = self.next_syllable(next_ipa)
            syllables.append(syllable)

        return u".".join(syllables)

    def equal_word_ipa_syllables(self, word, ipa):
        """
        If this word and its corresponding IPA pronunciation ipa share an equal
        number of syllables, this method returns their number of syllables.
        If they share an inequal number of syllables, this method returns False.
        ~
        False converts to integer 0 which ensures no overlap between bool vs int outputs.

        :param word: (unicode) str, word to count whether syllables equal to IPA
        :param ipa: (unicode) str, IPA to count whether syllables equal to word
        :return: int or bool, syllables in word and ipa if equal, False otherwise
        """
        word_syllables = self.count_word_syllables(word)
        ipa_syllables = self.count_ipa_syllables(ipa)

        if word_syllables == ipa_syllables:
            return word_syllables
        else:
            return False

    def equate_word_ipa_syllables(self, word, ipa):
        """
        If this word and its corresponding IPA pronunciation ipa share an equal
        number of syllables, this method returns the input ipa.
        ~
        Otherwise, if word and ipa share an inequal number of syllables, this method
        returns the input ipa modified to contain with the same number of syllables as
        the input word.
        ~
        This method was designed to correct Wiktionary IPA entries which have no
        syllable marks added as yet.

        :param word: (unicode) str, word to check whether syllables equal to IPA
        :param ipa: (unicode) str, IPA to check whether syllables equal to word
        :return: (unicode) str, input ipa containing same number of syllables as word
        """
        num_syllables = self.equal_word_ipa_syllables(word, ipa)

        if num_syllables != 0:
            return ipa
        else:
            ipa = self.clean_ipa(ipa)
            return self.add_syllables(ipa)

    def equate_ipa_syllables(self, ipa):
        """
        If this IPA pronunciation's stress marks appear not to match its
        number of syllables, this method returns the input ipa with stress marks added.
        ~
        Otherwise, if word and ipa share an inequal number of syllables, this method
        returns the input ipa modified to contain with the same number of syllables as
        the input word.
        ~
        This method was designed to correct Wiktionary IPA entries which have no
        syllable marks added as yet.

        :param word: (unicode) str, word to check whether syllables equal to IPA
        :param ipa: (unicode) str, IPA to check whether syllables equal to word
        :return: (unicode) str, input ipa containing same number of syllables as word
        """
        ipa = self.clean_ipa(ipa)
        return self.add_syllables(ipa)

    def count_ipa_stresses(self, ipa):
        """
        Returns number of stress marks in the given IPA.
        ~
        N.B. More precisely, this method returns the number of
        syllables implied by the number of stress marks in the given ipa.

        :param ipa: (unicode) str, IPA to count stress marks of
        :return: int, number of stress marks in word with given IPA
        """
        periods = ipa.count(u".")
        primary_stress = ipa.count(u"ˈ")
        secondary_stress = ipa.count(u"ˌ")
        addn = 0 if ipa[0] in u"ˈˌ" else 1  # accounts for missing initial stress mark
        return periods + primary_stress + secondary_stress + addn

    def count_ipa_syllables(self, ipa):
        """
        Returns number of syllables in the given IPA.

        :param ipa: (unicode) str, IPA to count syllables of
        :return: int, number of syllables in word with given IPA
        """
        syllables = 0
        ipa_iter = iter(range(len(ipa)))

        for i in ipa_iter:
            sym = ipa[i]

            if self.is_ipa_vowel(sym):
                while i < len(ipa)-1 and self.is_ipa_vowel(sym) is not False:
                    i = next(ipa_iter)
                    sym = ipa[i]

                syllables += 1

        if syllables is 0:
            syllables = 1

        return syllables

    def count_word_syllables(self, word):
        """
        Returns the number of vowel clusters in this word.

        :param word: str, word to count syllables of
        :return: int, number of syllables in word
        """
        syllables = 0
        new_word = word

        while len(new_word) != 0:
            vowels, new_word = self.find_vowels(new_word)
            syllables += 1
        # if word has no vowels, it has 1 syllable
        syllables = 1 if syllables == 0 else syllables

        return syllables

    def count_word_vowels(self, word):
        """
        Returns number of vowels in the given word.

        :param word: str, word to count vowels of
        :return: int, number of vowels in word
        """
        count = 0
        for char in word:
            if self.is_letter_vowel(char):
                count += 1
        return count

    def count_word_consonants(self, word):
        """
        Returns number of consonants in the given word.

        :param word: str, word to count consonants of
        :return: int, number of consonants in word
        """
        count = 0
        for char in word:
            if self.is_letter_vowel(char) is False:
                count += 1
        return count

    def count_ipa_vowels(self):
        """
        Returns number of vowels in this IPAWord's IPA.

        :return: int, number of vowels in IPA
        """
        count = 0
        for char in self.ipa:
            if char in IPAVOWELS:
                count += 1
        return count

    def count_ipa_consonants(self):
        """
        Returns number of consonants in this IPAWord's IPA.

        :return: int, number of consonants in IPA
        """
        count = 0
        for char in self.ipa:
            if char in IPACONSONANTS:
                count += 1
        return count

    def no_diacritics(self):
        """
        Returns True if this IPAWord's IPA pronunciation contains no
        diacritical or affricate symbols.

        :return: bool, whether this IPAWord's IPA contains no symbols
        """
        symbols = set(ipas.SYMBOLS)
        ipas = set(self.ipa)
        sims = symbols.intersection(ipas)
        return len(sims) == 0

    def has_diacritics(self):
        """
        Returns True if this IPAWord's IPA pronunciation contains
        diacritical or affricate symbols.

        :return: bool, whether this IPAWord's IPA contains symbols
        """
        symbols = set(ipas.SYMBOLS)
        ipas = set(self.ipa)
        sims = symbols.intersection(ipas)
        return len(sims) != 0

    def strip_syllables(self, ipa):
        """
        Removes syllable markers (i.e., '.', a period) from given IPA.

        :param ipa: (unicode) str, IPA pronunciation to remove syllable markers from
        :return: (unicode) str, IPA pronunciation with syllable markers removed
        """
        return re.sub(u"\.", u"", ipa)

    def destress(self, ipa):
        """
        Returns the given IPA pronunciation with stress marks removed.

        :param ipa: (unicode) str, IPA to remove stress marks from
        :return: (unicode) str, ipa with stress marks removed
        """
        return self.parser.destress(ipa)

    def restress(self, ipa):
        """
        Returns the given IPA pronunciation with all stress marks
        replaced with periods.

        :param ipa: (unicode) str, IPA to replace stress marks with periods
        :return: (unicode) str, ipa with stress marks replaced with periods
        """
        return self.parser.restress(ipa)

    def clean_ipa(self, ipa):
        """
        Returns the given IPA pronunciation with stress marks and
        syllable markers removed.

        :param ipa: (unicode) str, IPA to remove stress/syllable marks from
        :return: (unicode) str, given ipa with stress/syllable marks removed
        """
        return self.parser.clean_ipa(ipa)

    def clean_word(self, word):
        """
        Returns the given word in lowercase and with punctuation and
        whitespace removed.

        :param word: (unicode) str, word to clean
        :return: (unicode) str, cleaned word
        """
        return self.parser.clean_word(word)

    def __len__(self):
        """
        Returns the length of this IPAWord's cleaned word.

        :return: int, length of this IPAWord's word
        """
        return len(self.get_word())

    def __unicode__(self):
        return self.word + u"\t" + self.ipa

