# coding: utf-8

import os
import io
import re
import string
import requests
import urllib
import ipa_unicode
from BeautifulSoup import BeautifulSoup
import ipa_learn
from ipa_transcribe import *


LEMMA_TYPES = {"Noun": 1, "Verb": 2, "Adjective": 3, "Adverb": 4, "Preposition": 5,
               "Conjunction": 6, "Interjection": 7, "Morpheme": 8, "Pronoun": 9,
               "Phrase": 10, "Numeral": 11, "Particle": 12, "Participle": 13,
               "Prefix": 14, "Suffix": 15}
PATH = os.path.dirname(os.path.realpath(__file__))


class IPAWord:
    """
    A class for representing and operating on words and their IPA pronunciations.
    """
    def __init__(self, word, ipa, parser, pos=None):
        self.word = word
        self.pos = pos
        self.ipa = ipa
        self.parser = parser
        self.lang = self.parser.get_lang()
        self.phoneme_dict = {}

    def get_dict(self):
        res = {}
        res["word"] = self.word
        #res["pos"] = self.pos
        #res["ipa"] = self.ipa
        res["phonemes"] = " ".join(self.find_ipa_phonemes())
        return res

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

    def get_pos_num(self):
        """
        Returns an integer representing this IPAWord's pos.

        :return: int, this IPAWord's pos integer
        """
        return LEMMA_TYPES[self.pos]

    def get_ipa(self):
        """
        Returns this IPAWord's pronunciation in IPA.

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

    def init_phoneme_dict(self):
        """
        Initializes this IPAWord's phoneme dictionary.

        :return: dict, where...
            key (str) - >=1 letters in a native language alphabet
            val (Set(str)) - list of >=1 IPA symbols corresponding to key
        """
        self.phoneme_dict = self.find_phoneme_dict()
        self.parser.merge_phoneme_dicts(self.phoneme_dict)

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

    def break_syllables(self, ipa):
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
        :return: List[tuple((all unicode) str, str, str)], the given
            syllables' onsets, rhymes, and codas, respectively
        """
        return self.parser.break_syllables(ipa)

    def split_syllables(self, syllables):
        """
        Splits the given IPA word into its constituent
        syllables.
        ~
        e.g. split_syllables("ɔˈba.lat͡ɕ") -> ["ɔ", "ba", "lat͡ɕ"]

        :param ipa: (unicode) str, IPA word to break into syllables
        :return: List[(unicode) str], list of given ipa's syllables
        """
        return self.parser.split_syllables(syllables)

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
        cleaned_ipa = self.get_ipa()
        phonemes = []

        size = len(cleaned_ipa)
        start = 0   # inclusive
        end = 1     # exclusive

        while end <= size:
            if end != size and cleaned_ipa[end] in ipa_unicode.SYMBOLS:
                if cleaned_ipa[end] in ipa_unicode.AFFRICATES:
                    end += 1  # skip 2 for affricates
                end += 1      # skip 1 for diacritics
            else:
                phoneme = cleaned_ipa[start:end]
                phonemes.append(phoneme)
                start = end
                end = start + 1

        return phonemes

    def find_ipa_phonemes(self):
        """
        Returns this IPAWord's phonemes as a list of IPA unicode strings.
        ~
        Phonemes are calculated from this IPAWord's self.ipa.
        ~
        e.g. cat = IPAWord("cat", "Noun", "kæt", IPAParser("English"))
             cat.find_ipa_phonemes() -> ["k", "æ", "t"]

             text = IPAWord("text", "Noun", "tɛkst", IPAParser("English"))
             text.find_ipa_phonemes() -> ["t", "ɛ", "ks", "t"]

        :return: List[(unicode) str], this IPAWord's phonemes in IPA
        """
        cleaned_ipa = self.get_ipa()
        phonemes = []

        size = len(cleaned_ipa)
        start = 0   # inclusive
        end = 1     # exclusive

        while end <= size:
            if end != size and cleaned_ipa[end] in ipa_unicode.SYMBOLS:
                if cleaned_ipa[end] in ipa_unicode.AFFRICATES:
                    end += 1  # skip 2 for affricates
                end += 1      # skip 1 for diacritics
            else:
                phoneme = cleaned_ipa[start:end]
                phonemes.append(phoneme)
                start = end
                end = start + 1

        return phonemes

    def find_phoneme_dict(self):
        """
        Returns a dictionary representing this IPAWord's phonemes,
        with native alphabet letters as keys and IPA symbols as values.
        ~
        Phonemes are calculated from this IPAWord's self.ipa.

        :return: dict, where...
            key (str) - >=1 letters in a native language alphabet
            val (Set(str)) - list of >=1 IPA symbols corresponding to key
        """
        word = self.get_word()
        phonemes = self.find_ipa_phonemes()
        alphabet = self.parser.get_phoneme_dict()
        print word + "\t\t",
        print "  ".join(phonemes)

        # more phonemes than letters
        if len(word) < len(phonemes):
            start_word, start_phone = 0, 0
            end_word, end_phone = 1, 1
            while end_phone <= len(phonemes):
                # TODO: sort phonemes when word is shorter
                pass
        # more letters than phonemes
        elif len(word) > len(phonemes):
            start_word, start_phone = 0, 0
            end_word, end_phone = 1, 1
            while end_word <= len(word):
                # TODO: sort phonemes when word is longer
                if all(char in alphabet for char in word):
                    pass
        # same no. of letters & phonemes
        elif len(word) == len(phonemes):
            phoneme_dict = {}
            for i in range(len(word)):
                char = word[i]
                phoneme_dict.setdefault(char, set())
                phoneme_dict[char].add(phonemes[i])

        self.parser.merge_phoneme_dicts(phoneme_dict)
        return phoneme_dict

    def find_phoneme_dict_syllables(self):
        """
        Returns a dictionary representing this IPAWord's ipa_phonemes,
        with native alphabet letters as keys and IPA symbols as values.
        ~
        Phonemes are calculated from this IPAWord's self.ipa_phonemes.

        :return: dict, where...
            key (str) - >=1 letters in a native language alphabet
            val (Set(str)) - list of >=1 IPA symbols corresponding to key
        """
        phoneme_dict = {}

        word = self.word
        ipa_phonemes = self.find_ipa_phonemes()

        clean_ipa = self.get_ipa()
        syllables = self.split_syllables(self.ipa)
        broken_syllables = self.break_syllables(self.ipa)



        for onset, rhyme, coda in broken_syllables:
            pass





        ipa_vowels = self.count_ipa_vowels()
        ipa_consonants = self.count_ipa_consonants()
        # same no. of letters & ipas
        if len(word) == len(ipa_phonemes) and ipa_vowels + ipa_consonants == len(ipa_phonemes):
            for i in range(len(word)):
                char = word[i]
                phoneme_dict.setdefault(char, set())
                phoneme_dict[char].add(ipa_phonemes[i])
                self.parser.add_dict_entry(char, ipa_phonemes[i])
        else:
            if len(self.parser.get_phoneme_dict()) == 0:
                return phoneme_dict

            clean_ipa = self.get_ipa()
            syllables = self.split_syllables(self.ipa)
            broken_syllables = self.break_syllables(syllables)

            word_idx = 0
            ipa_idx = 0

            print self.ipa, syllables
            print
            print word

            loop = 0


            for sy in range(len(syllables)):
                syllable = syllables[sy]
                ipa_syllable = self.break_syllable(syllable)
                ipa_idx += len(syllable)

                c1 = str()
                v = str()
                c2 = str()

                ipa_onset, ipa_rhyme, ipa_coda = ipa_syllable

                pre_word_v = True
                pre_ipa_v = True

                if len(ipa_onset) != 0:  # syllable starts with consonant
                    for i in range(word_idx, len(word)):
                        if self.is_letter_vowel(word[i]):
                            word_idx = i
                            break
                        else:
                            c1 += word[i]
                            continue

                if len(ipa_rhyme) != 0:
                    for i in range(word_idx, len(word)):
                        if self.is_letter_vowel(word[i]):
                            v += word[i]
                            continue
                        else:
                            word_idx = i
                            break

                if len(ipa_coda) != 0:
                    for i in range(word_idx, len(word)):
                        if self.is_letter_vowel(word[i]):
                            word_idx = i
                            break
                        else:
                            c2 += word[i]
                            if sy != len(syllables)-1 and not self.is_ipa_vowel(syllables[sy+1][0]):
                                # if the next syllable begins with a consonant,
                                break

                print c1, v, c2
                print ipa_onset, ipa_rhyme, ipa_coda

                if len(c1) != 0:
                    phoneme_dict.setdefault(c1, set())
                    phoneme_dict[c1].add(ipa_onset)
                    self.parser.add_dict_entry(c1, ipa_onset)
                if len(v) != 0:
                    phoneme_dict.setdefault(v, set())
                    phoneme_dict[v].add(ipa_rhyme)
                    self.parser.add_dict_entry(v, ipa_rhyme)
                if len(c2) != 0:
                    phoneme_dict.setdefault(c2, set())
                    phoneme_dict[c2].add(ipa_coda)
                    self.parser.add_dict_entry(c2, ipa_coda)

        return phoneme_dict

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

    def count_syllables(self):
        """
        Returns number of syllables in this IPAWord.

        :return: int, number of syllables in word with given IPA
        """
        periods = self.ipa.count(u".")
        primary_stress = self.ipa.count(u"ˈ")
        secondary_stress = self.ipa.count(u"ˌ")
        addn = 0 if self.ipa[0] in u"ˈˌ" else 1
        return periods + primary_stress + secondary_stress + addn

    def count_word_vowels(self):
        """
        Returns number of vowels in this IPAWord's word.

        :return: int, number of vowels in word
        """
        count = 0
        for char in self.word:
            if self.is_letter_vowel(char):
                count += 1
        return count

    def count_word_consonants(self):
        """
        Returns number of consonants in this IPAWord's word.

        :return: int, number of consonants in word
        """
        count = 0
        for char in self.word:
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
        symbols = set(ipa_unicode.SYMBOLS)
        ipas = set(self.ipa)
        sims = symbols.intersection(ipas)
        return len(sims) == 0

    def has_diacritics(self):
        """
        Returns True if this IPAWord's IPA pronunciation contains
        diacritical or affricate symbols.

        :return: bool, whether this IPAWord's IPA contains symbols
        """
        symbols = set(ipa_unicode.SYMBOLS)
        ipas = set(self.ipa)
        sims = symbols.intersection(ipas)
        return len(sims) != 0

    def strip_syllables(self):
        """
        Removes syllable markers (i.e., '.', a period) from given IPA.

        :param ipa: str, IPA pronunciation to remove syllable markers from
        :return: str, IPA pronunciation with syllable markers removed
        """
        return self.ipa.replace(".", "")

    def destress(self, ipa):
        """
        Returns the given IPA pronunciation with stress marks removed.

        :param ipa: (unicode) str, IPA to remove stress marks from
        :return: (unicode) str, given ipa with stress marks removed
        """
        return re.sub(u"[" + self.parser.STRESS_MARKS + u"]", u"", ipa)

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

    def __int__(self):
        """
        Returns this IPAWord as an integer sequence.

        :return: int, this IPAWord as an int
        """
        alphabet = self.parser.get_alphabet()
        word = self.get_word()
        digits = len(str(max(alphabet.values())))
        nums = []
        for char in word:
            num = str(self.get_pos_num()) + str(alphabet[char]).zfill(digits)
            nums.append(num)
        num = int("".join(nums))
        print num
        return num

    def __len__(self):
        """
        Returns the length of this IPAWord's cleaned word.

        :return: int, length of this IPAWord's word
        """
        return len(self.get_word())

    def __unicode__(self):
        return self.word + u"\t" + self.ipa


class IPAParser:
    """
    A class for parsing Wiktionary IPA data for a given language.

    1) visit all next pages & collect all pronunciation links
    2) visit all pronunciation links & fetch IPA pronunciation for each word
      - create dictionary
    3) map IPA pronunciations to word letters
    """
    WIKI_URL = "https://en.wiktionary.org"
    END_URL = "/w/index.php?title=Category:%s_terms_with_IPA_pronunciation&from="
    STRESS_MARKS = u"ˈˌ"
    ALPHABET_LETTERS = 0

    def __init__(self, language):
        self.lang = language
        self.alphabet = {}       # this language's alphabet
        self.ipas = set()        # this language's IPA symbols
        self.url = self.WIKI_URL + self.END_URL % self.lang  # + self.lang + self.END_URL
        self.urls = [self.url + chr(i) for i in range(ord("a"), ord("z")+1)]
        self.phoneme_dict = {}
        self.init_alphabet()

    def get_lang(self):
        """
        Returns this IPAParser's native language.

        :return: str, this IPAParser's language
        """
        return self.lang

    def get_alphabet(self):
        """
        Returns this IPAParser's native language alphabet.

        :return: str, this IPAParser's language's alphabet
        """
        return self.alphabet

    def init_alphabet(self):
        """
        Initializes this IPAParser's native language's alphabet.

        :return: None
        """
        url = self.url + "A"
        page = self.parse_url(url)
        self.find_alphabet(page)

    def add_alphabet_letter(self, letter):
        """
        Adds the given letter to this IPAParser's alphabet
        if it is not there already.

        :param letter: str, letter to add to alphabet
        :return: None
        """
        if letter not in self.alphabet:
            self.ALPHABET_LETTERS += 1
            self.alphabet[letter] = self.ALPHABET_LETTERS

    def get_url(self):
        """
        Returns this IPAParser's base Wiktionary URL.
        ~
        Used for all word lookups.

        :return: str, this IPAParser's Wiktionary URL
        """
        return self.url

    def get_phoneme_dict(self):
        """
        Returns this IPAParser's phoneme_dict, a dictionary linking letter
        sequences in a language to their IPA pronunciations.

        :return: dict, where...
            key ((unicode) str) - phoneme (i.e., short sequence of alphabetic letters)
            val (Set(str)) - IPA translations of this language's phoneme
        """
        return self.phoneme_dict

    def add_dict_entry(self, phoneme, ipas):
        """
        Adds the given phoneme-ipas pair to this IPAParser's
        phoneme_dict.

        :param phoneme: str, phoneme (i.e., short sequence of characters)
        :param ipas: Set(str), IPA translations of this language's phoneme
        :return: None
        """
        self.phoneme_dict[phoneme] = ipas

    def merge_phoneme_dicts(self, phoneme_dict):
        """
        Merges this IPAParser's self.phoneme_dict with the
        given phoneme_dict.

        :param phoneme_dict: dict, where...
            key (str) - phoneme (i.e., short sequence of characters)
            val (Set(str)) - IPA translations of this language's phoneme
        :return: None
        """
        self.phoneme_dict = self.merge_dicts(self.phoneme_dict, phoneme_dict)

    def merge_dicts(self, first, other):
        """
        Merges the first dict with the other dict.

        :param first: dict, where...
            key (str)
            val (Set(str))
        :param other: dict, where...
            key (str)
            val (Set(str))
        :return: dict, where...
            key (str)
            val (Set(str))
        """
        first = {phoneme: first[phoneme].union(other.pop(phoneme, "")) for phoneme in first}
        first.update(other)
        return first

    def write_lexicon(self):
        """
        Writes all words for Wiktionary entries in this
        IPAParser's language.
        ~
        Saves the file as [IPAParser language in lowercase]_lexicon.txt.
        ~
        e.g. parser = IPAParser("Polish")
             parser.write_lexicon() -> saved to "polish_lexicon.txt"

        :return: None
        """
        pronunciations = self.all_page_defns()

        dest = self.get_lang().lower() + "_lexicon.txt"
        dest_path = PATH + "/" + dest

        with open(dest_path, "w") as out:
            # replace each url with its IPA transcription
            for pron in sorted(pronunciations):
                out.write(unicode(pron).encode('utf-8') + "\n")

    def write_ipa_dict(self):
        """
        Writes a word-IPA dictionary for this IPAParser's language
        using Wiktionary entries.
        ~
        Saves the file as [IPAParser language in lowercase].txt.
        ~
        e.g. parser = IPAParser("Polish")
             parser.write_ipa_dict() -> saved to "polish.txt"

        :return: None
        """
        pronunciations = self.all_page_defns()

        dest = self.get_lang().lower() + ".txt"
        dest_path = PATH + "/" + dest

        with open(dest_path, "w") as out:
            # replace each url with its IPA transcription
            for pron in sorted(pronunciations):
                #print pron
                url = self.get_word_url(pron)
                parsed_url = self.parse_url(url)
                #pos = self.find_pos(parsed_url)
                #if pos is None:
                #    continue
                ipa = self.find_ipa(parsed_url)
                if ipa is None:
                    continue
                #text = pron + u"\t" + pos + u"\t" + ipa
                text = pron + u"\t" + ipa
                print text
                out.write(unicode(text).encode('utf-8') + "\n")

    def get_word_url(self, word):
        """
        Returns a Wiktionary URL for the given word.

        :param word: str, word to retrieve URL for
        :return: str, URL matching given word
        """
        url = self.WIKI_URL + "/wiki/%s#%s" % (word, self.get_lang())
        print url
        return url #self.WIKI_URL + "/wiki/%s#%s" % (word, self.get_lang())

    def parse_url(self, url):
        """
        Parses given URL string to a BeautifulSoup Tag.

        :param url: str, URL to parse to tags
        :return: Tag, parsed URL
        """
        session = requests.session()
        response = session.get(url)
        html = response.text
        parsed = BeautifulSoup(html)
        return parsed

    def next_page(self, page):
        """
        Returns given BeautifulSoup Tag page's next page,
        or None if no next page exists.

        :param page: Tag, page to find next page of
        :return: Tag, next page
        """
        pgs = (pg for pg in
               page.findAll(name='a', attrs={"title": "Category:"+self.lang+" terms with IPA pronunciation"}))
        try:
            pg = next(pgs)
        except StopIteration:
            return
        else:
            # fetch index of next page
            while pg.string != "next page":
                try:
                    pg = next(pgs)
                except StopIteration:
                    return
        # form wiki url from index
        url = self.WIKI_URL + pg['href']
        return self.parse_url(url)

    def all_pages(self):
        """
        Returns list of webpages for all Wiktionary entries under this
        IPAParser's language.

        :return: List[Tag], given page's next pages
        """
        url = self.url + sorted(self.alphabet)[0].upper()
        next_pg = self.parse_url(url)
        pgs = []

        while next_pg is not None:
            pgs.append(next_pg)
            next_pg = self.next_page(next_pg)

        return pgs

    def page_defns(self, page):
        """
        Returns given BeautifulSoup Tag page's definitions.

        :param page: Tag, page to find definitions from
        :return: Set((unicode) str), set of word definitions
        """
        defns = page.find(name='ul')
        defns = defns.findAll('a')
        # replace dashes & spaces w/ blanks
        defns = set(defn['title'] for defn in defns if defn['title'][0].islower()
                    and all(char not in defn['title'] for char in '.- '))
        return defns

    def all_page_defns(self):
        """
        Returns all Wiktionary definitions in this IPAParser's language.

        :return: Set((unicode) str), set of word definitions
        """
        defns = set()
        next_pgs = self.all_pages()

        for next_pg in next_pgs:
            defns.update(self.page_defns(next_pg))

        return defns

    def find_alphabet(self, page):
        """
        Returns alphabet for a language from this Wiktionary page.

        :param page: Tag, a parsed BeautifulSoup page
        :return: List[(unicode) str], a list of a language's alphabetic characters
        """
        adds = page.findAll('a', attrs={'class': 'external text'})[2:]
        for add in adds:
            letters = add.string.lower()
            if len(letters) != 1:
                letters = letters.split(" ")
                for letter in letters:
                    if len(letter) == 1:
                        self.add_alphabet_letter(letter)
            elif len(letters) == 1:
                self.add_alphabet_letter(letters)
        return self.alphabet.keys()

    def find_ipa(self, page):
        """
        Returns IPA pronunciation from given BeautifulSoup Tag page.
        ~
        This method finds the first pronunciation that does not begin
        with a dash (which denotes a rhyme ending rather than the word).

        :param page: Tag, page to find pronunciation from
        :return: (unicode) str, IPA pronunciation from given URL
        """
        spans = page.findAll('span', attrs={'class': "IPA"})
        if len(spans) > 1:
            for sp in spans:
                st = sp.string
                if st is not None and not st.startswith("-"):
                    ipa = st
                    break
            else:
                return None
        else:
            ipa = spans[0].string
        ipa = ipa.strip(u"[]/") if ipa is not None else ipa
        return ipa

    def find_pos(self, page):
        """
        Returns part-of-speech from given BeautifulSoup Tag page.

        :param page: Tag, page to find part-of-speech from
        :return: str, part-of-speech from given URL
        """
        spans = page.findAll('span', attrs={'class': "mw-headline"})

        for span in spans:
            span_id = span['id']
            if span_id in LEMMA_TYPES:
                return span_id
        else:
            return

    def transcribe_to_ipawords(self, defns):
        """
        Transcribes the words and URLs in the given definition
        dictionary to IPAWords.

        :param defns: Set((unicode) str), set of word definitions
        :return: Set(IPAWord), IPAWords corresponding to given definitions
        """
        prons = set()
        base_url = self.WIKI_URL + "/wiki/%s#%s"

        for defn in defns:
            print defn
            print
            url = base_url % (defn, self.lang)
            parsed_url = self.parse_url(url)
            ipa = self.find_ipa(parsed_url)
            #raw_input()
            prons.add(IPAWord(defn, ipa, self))

        return prons

    def clean_ipa(self, ipa):
        """
        Returns the given IPA pronunciation with stress marks and
        syllable markers removed.

        :param ipa: (unicode) str, IPA to remove stress/syllable marks from
        :return: (unicode) str, given ipa with stress/syllable marks removed
        """
        return re.sub(u"[ˈˌ\.\(\)]", u"", ipa)

    def clean_word(self, word):
        """
        Returns the given word in lowercase and with punctuation and
        whitespace removed.

        :param word: (unicode) str, word to clean
        :return: (unicode) str, cleaned word
        """
        return re.sub("[" + string.punctuation + "]", "", word.lower())

    def remove_parens(self, word):
        """
        Returns the given word with parentheses removed.

        :param word: str, word to remove parentheses from
        :return: str, word with parentheses removed
        """
        return re.sub(u"[\(\)]", "", word)

    def ipaword_phonemes(self, ipa_words):
        """
        Returns a dictionary representing all phonemes in ipa_words.
        ~
        N.B. Phonemes are in a language's native lettering system,
        while their forms are in IPA.

        :param ipa_words: Set(IPAWord), IPAWords to return phonemes of
        :return: dict, where...
            key (str) - phoneme (i.e., short sequence of >=1 characters)
            val (Set(str)) - IPA translations of this language's phoneme
        """
        phonemes = {}
        for ipa_word in ipa_words:
            print ipa_word.get_word()
            phoneme_dict = ipa_word.find_phoneme_dict()
            phonemes = {phoneme: phonemes[phoneme].union(phoneme_dict.pop(phoneme, "")) for phoneme in phonemes}
            phonemes.update(phoneme_dict)
        return phonemes

    def all_phonemes(self):
        """
        Returns a dictionary representing all ipa_phonemes
        in this language and each of the forms they take.

        :return: dict, where...
            key (str) - phoneme (i.e., short sequence of characters)
            val (Set(str)) - IPA translations of this language's phoneme
        """
        transcriptions = self.all_ipa_words()
        phoneme_dict = self.ipaword_phonemes(transcriptions)
        return phoneme_dict

    def all_ipa_words(self):
        """
        Returns a set of IPAWords corresponding all
        Wiktionary entries in this IPAParser's language.

        :return: Set(IPAWord), all IPAWords in this IPAParser's language
        """
        pages = self.all_page_defns()
        transcriptions = self.transcribe_to_ipawords(pages)
        return transcriptions

    def ipa_words_to_features(self, ipa_words):
        questions = []
        answers = []

        for ipa_word in ipa_words:
            ipas = ipa_word.find_ipa_phonemes()
            ipas_nums = get_ipas_nums(ipas)
            #word_num = get_word_num(word)
            pos_num = LEMMA_TYPES[ipa_word.get_pos()]
            word_num = int(ipa_word)
            if len(str(word_num)) > 20:
                continue
            word_feat = [word_num, pos_num]
            print
            print ipa_word.get_word(), ipa_word.get_pos()
            print word_feat
            print
            print "  ".join(ipas)
            print ipas_nums
            print
            #raw_input("continue?")
            questions.append(word_feat)
            answers.append(ipas_nums)

        return (questions, answers)

    def ipa_words_to_dict(self, ipa_words):
        """
        Returns the given set of IPAWords as a dictionary,
        where each IPAWord's word is a key with an associated
        IPA pronunciation value.

        :param ipa_words: Set(IPAWord)
        :return: dict, where...
            key ((unicode) str) - IPAWord's word
            val ((unicode) str) - IPA pronunciation of IPAWord
        """
        ipa_dict = {}

        word_count = 1  # start word numbers at 1

        for ipa_word in ipa_words:
            print(ipa_word.get_word())
            word_dict = ipa_word.get_dict()
            for key in word_dict:
                key_num = key + str(word_count)
                print key_num, word_dict[key]
                ipa_dict[key_num] = word_dict[key]
            print
            word_count += 1

        return ipa_dict

    def train(self):
        ipa_lexicon = self.all_ipa_words()  #self.get_ipa_lexicon().items()
        cutoff = int(len(ipa_lexicon) * 0.75)
        print cutoff
        ipa_lst = list(ipa_lexicon)
        train_set, test_set = ipa_lst[:cutoff], ipa_lst[cutoff:]

        train_qs, train_as = self.ipa_words_to_features(train_set)
        test_qs, test_as = self.ipa_words_to_features(test_set)
        print train_qs
        print
        print test_qs
        print len(test_qs)
        print
        print test_as
        print len(test_as)
        print

        ipa_learn.train_classifier(train_qs, train_as)
        ipa_learn.test_classifier(test_qs, test_as)

    def train_dict(self):
        ipa_lexicon = self.all_ipa_words()
        #for ipa_word in ipa_lexicon:
        #    print(ipa_word.find_phoneme_dict()) #_syllables())
        train = self.ipa_words_to_dict(ipa_lexicon)
        print train
        print

        ipa_learn.train_dict_classifier(train)
        print ipa_learn.DICT_CLASSIFIER.set_params()

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
        return

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
                    elif i+1 != len(word) and self.is_letter_vowel(word[i+1]) or True:
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

        for i in range(len(syllable)):
            ipa = syllable[i]

            if self.is_ipa_vowel(ipa) is None:
                if i != 0 and self.is_ipa_vowel(syllable[i-1]):
                    rhyme += ipa
                else:
                    if pre_rhyme:
                        onset += ipa
                    else:
                        coda += ipa
            elif self.is_ipa_vowel(ipa):
                pre_rhyme = False
                rhyme += ipa
            else:
                if pre_rhyme:
                    onset += ipa
                else:
                    coda += ipa

        return (onset, rhyme, coda)

    def break_syllables(self, ipa):
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
        :return: List[tuple((all unicode) str, str, str)], the given
            syllables' onsets, rhymes, and codas, respectively
        """
        return [self.break_syllable(syllable)
                for syllable in self.split_syllables(ipa)]

    def split_syllables(self, ipa):
        """
        Splits the given IPA word into its constituent
        syllables.
        ~
        e.g. split_syllables("ɔˈba.lat͡ɕ") -> ["ɔ", "ba", "lat͡ɕ"]

        :param ipa: (unicode) str, IPA word to break into syllables
        :return: List[(unicode) str], list of given ipa's syllables
        """
        subbed_ipa = re.sub(u"[ˈˌ]", u".", ipa)
        syllables = subbed_ipa.split(u".")
        return syllables

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
        phonemes = self.get_phoneme_dict()
        try:
            ipa = phonemes[char]
        except KeyError:
            return None
        else:
            return ipa in IPAVOWELS

    def is_ipa_vowel(self, ipa):
        """
        Returns True if the given IPA symbol is a vowel
        according to the IPA, False if a consonant.
        ~
        Returns None if this symbol is not an IPA letter.

        :param ipa: (unicode) str, IPA symbol to determine whether vowel
        :return: bool, whether given IPA symbol is a vowel
        """
        try:
            ipa_sym = IPALETTERS[ipa]
        except KeyError:
            return None
        else:
            return ipa_sym.get_is_vowel()


parser = IPAParser("Dutch")
#parser.train_dict()
#print parser.break_syllables(u"fʂɛxˈmɔt͡s.nɨ")
#print parser.split_word_syllables(u"wszechmocny")
#parser.write_lexicon()
#print parser.all_ipa_words()
print parser.all_phonemes()