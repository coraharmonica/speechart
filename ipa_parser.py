# coding: utf-8

import os
import json
import string
import requests
from BeautifulSoup import BeautifulSoup
import ipa_learn
from ipa_word import *
from ipa_transcribe import *


LEMMA_TYPES = {"Noun": 1, "Verb": 2, "Adjective": 3, "Adverb": 4, "Preposition": 5,
               "Conjunction": 6, "Interjection": 7, "Morpheme": 8, "Pronoun": 9,
               "Phrase": 10, "Numeral": 11, "Particle": 12, "Participle": 13,
               "Prefix": 14, "Suffix": 15, "Circumfix": 16, "Interfix": 17, "Infix": 18}
PATH = os.path.dirname(os.path.realpath(__file__))
LEXICA_PATH = PATH + "/resources/lexica"


class IPAParser:
    """
    A class for parsing Wiktionary IPA data for a given language.

    1) visit all next pages & collect all pronunciation links
    2) visit all pronunciation links & fetch IPA pronunciation for each word
      - create dictionary
    3) map IPA pronunciations to word letters
    """
    LANG_CODES = {"Arabic": "arb",
                  "Bulgarian": 'bul',
                  "Catalan": 'cat',
                  "Danish": 'dan',
                  "Dutch": 'nld',
                  "German": 'deu',
                  "Greek": 'ell',
                  "English": 'eng',
                  "Basque": 'eus',
                  "Persian": 'fas',
                  "Finnish": 'fin',
                  "French": 'fra',
                  "Galician": 'glg',
                  "Hebrew": 'heb',
                  "Croatian": 'hrv',
                  "Indonesian": 'ind',
                  "Italian": 'ita',
                  "Japanese": 'jpn',
                  "Norwegian Nyorsk": 'nno',
                  "Norwegian Bokmal": 'nob',
                  "Polish": 'pl',
                  "Portuguese": 'por',
                  "Chinese": "qcn",
                  "Slovenian": 'slv',
                  "Spanish": 'spa',
                  "Swedish": 'swe',
                  "Thai": 'tha',
                  "Malay": 'zsm'}
    WIKI_URL = "https://en.wiktionary.org"
    END_URL = "/w/index.php?title=Category:%s"
    IPA_URL = "_terms_with_IPA_pronunciation&from="
    BASE_URL = WIKI_URL + "/wiki/%s#%s"
    LEMMA_URL = "_lemmas"
    STRESS_MARKS = u"ˈˌ"
    ALPHABET_LETTERS = 0

    def __init__(self, language):
        self.session = requests.session()
        self.language = language
        self.lang_code = self.LANG_CODES[self.language][:2] if self.language in self.LANG_CODES else None
        self.alphabet = {}       # this language's alphabet
        self.ipas = set()        # this language's IPA symbols
        self.url = self.WIKI_URL + self.END_URL % self.language  # + self.language + self.END_URL
        self.phoneme_dict = {}
        self.vowels = OrderedSet([])
        self.consonants = OrderedSet([])
        self.init_alphabet()
        self.langs_ipas = self.fetch_langs_ipas()
        self.lang_ipas = self.fetch_lang_ipas()
        self.langs_pos = self.fetch_langs_pos()
        self.lang_pos = self.fetch_lang_pos()

    def get_language(self):
        """
        Returns this IPAParser's native language.

        :return: str, this IPAParser's language
        """
        return self.language

    def set_language(self, language):
        if self.language != language:
            self.__init__(language)

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
        url = self.url + self.IPA_URL + "A"
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

    def dump_json(self, data, filename):
        """
        Dumps data (prettily) to filename.json.

        :param data: X, data to dump to JSON
        :param filename: str, name of .json file to dump to
        :return: None
        """
        path = PATH + "/resources/data/" + filename + ".json"
        json.dump(data, open(path, 'w'), indent=1, sort_keys=True, encoding='utf-8')

    def fetch_json(self, filename):
        """
        Returns a dictionary corresponding to the given JSON file.

        :param filename: str, name of .json file to fetch
        :return: X, content of given .json file
        """
        return json.load(open(PATH + "/resources/data/" + filename + ".json"))

    def refresh_json(self):
        """
        Dumps this IPAParser's langs_ipas data to ipas.json, and
        langs_pos to parts_of_speech.json.

        :return: None
        """
        self.langs_pos[self.language] = self.lang_pos
        self.langs_ipas[self.language] = self.lang_ipas
        self.dump_json(self.langs_pos, "parts_of_speech")
        self.dump_json(self.langs_ipas, "ipas")

    def fetch_langs_ipas(self):
        """
        Returns a dictionary of words and their IPA transcriptions.

        :return: X, content of ipas.json file
        """
        return self.fetch_json("ipas")

    def fetch_lang_ipas(self):
        """
        Returns the IPA dictionary in this IPAParser's native language.

        :return: dict, where...
            key (str) - word in native language
            val (str) - word's IPA transcription
        """
        try:
            return self.langs_ipas[self.language]
        except KeyError:
            lang_ipas = dict()
            self.langs_ipas[self.language] = lang_ipas
            return lang_ipas

    def fetch_langs_pos(self):
        """
        Returns a dictionary of words and their parts of speech.

        :return: X, content of parts_of_speech.json file
        """
        return self.fetch_json("parts_of_speech")

    def fetch_lang_pos(self):
        """
        Returns the part-of-speech dictionary in this IPAParser's
        native language.

        :return: dict, where...
            key (str) - word in native language
            val (str) - word's part of speech
        """
        try:
            return self.langs_pos[self.language]
        except KeyError:
            lang_pos = dict()
            self.langs_pos[self.language] = lang_pos
            return lang_pos

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
            val (OrderedSet(str)) - IPA translations of this language's phoneme
        """
        return self.phoneme_dict

    def all_ipa_phonemes(self):
        """
        Returns an OrderedSet with each IPA value
        in this IPAParser's phoneme_dict.

        :return: OrderedSet(str) - IPAs for all this language's phonemes
        """
        phoneme_dict = self.phoneme_dict
        ipa_phonemes = None

        for chars in phoneme_dict:
            if ipa_phonemes is None:
                ipa_phonemes = phoneme_dict[chars]
            else:
                ipa_phonemes.update(phoneme_dict[chars])

        if ipa_phonemes is None:
            return OrderedSet([])
        else:
            return ipa_phonemes

    def add_vowel(self, chars):
        """
        Adds the given chars to this IPAParser's
        list of vowels.

        :param chars: str, phoneme (i.e., short sequence of characters)
        :return: None
        """
        self.vowels.add(chars)

    def add_consonant(self, chars):
        """
        Adds the given chars to this IPAParser's
        list of consonants.

        :param chars: str, phoneme (i.e., short sequence of characters)
        :return: None
        """
        self.consonants.add(chars)

    def add_phoneme_entry(self, chars, ipas):
        """
        Adds the given chars-ipas pair to this IPAParser's
        phoneme_dict.

        :param chars: str, phoneme (i.e., short sequence of characters)
        :param ipas: str, IPA translation of this language's phoneme
        :return: None
        """
        self.phoneme_dict.setdefault(chars, OrderedSet([]))
        self.phoneme_dict[chars].add(ipas)

    def merge_phoneme_dicts(self, phoneme_dict):
        """
        Merges this IPAParser's self.phoneme_dict with the
        given phoneme_dict.

        :param phoneme_dict: dict, where...
            key (str) - phoneme (i.e., short sequence of characters)
            val (OrderedSet(str)) - IPA translations of this language's phoneme
        :return: None
        """
        self.phoneme_dict = self.merge_dicts(self.phoneme_dict, phoneme_dict)

    def merge_dicts(self, first, other):
        """
        Merges the first dict with the other dict.

        :param first: dict, to merge with other, where...
            key (X)
            val (OrderedSet(X))
        :param other: dict, to merge with first, where...
            key (X)
            val (OrderedSet(X))
        :return: dict, first merged with other, where...
            key (X)
            val (OrderedSet(X))
        """
        first = {phoneme: first[phoneme].union(other.pop(phoneme).pop(phoneme))
                 for phoneme in first if phoneme in other}
        first.update(other)
        return first

    def common_words(self, lim=50000):
        """
        Returns a list of the 50,000 most common words
        in this IPAParser's language.

        :param lim: int, lim <= 50000, number of words to retreive
        :return: List[str], 50k most common words in IPAParser's language
        """
        if self.lang_code is None:
            return

        words = list()
        path = PATH + "/resources/frequency_words/content/2016/%s/%s_50k.txt" % (self.lang_code, self.lang_code)

        with open(path, 'r') as fifty_k:
            line_no = 0
            for line in fifty_k:
                word = line.split(" ", 1)[0]
                word = self.unicodize(word)
                words.append(word)
                if line_no > lim:
                    break
                line_no += 1

        return words

    def common_ipa_words(self, lim=50000):
        """
        Returns a set of IPAWords corresponding to the
        Wiktionary entries of this IPAParser's language's most
        common words (up to 50,000).

        :param lim: int, lim <= 50000, number of words to retrieve
        :return: Set(IPAWord), common IPAWords in this IPAParser's language
        """
        pages = self.pages_common_defns(self.all_ipa_pages(), lim)
        transcriptions = self.words_to_ipawords(pages)
        return transcriptions

    def common_phonemes(self, lim=50000):
        """
        Returns a dictionary representing ipa_phonemes
        for up to the 50,000 most common words in this language
        and each of the forms they take.

        :param lim: int, lim <= 50000, number of words to retreive
        :return: dict, where...
            key (str) - phoneme (i.e., short sequence of characters)
            val (List[str]) - IPA translations of this language's phoneme
        """
        transcriptions = self.common_ipa_words(lim=lim)
        phoneme_dict = self.ipa_words_phonemes(transcriptions)
        return phoneme_dict

    def all_phonemes(self):
        """
        Returns a dictionary representing all ipa_phonemes
        in this language and each of the forms they take.

        :return: dict, where...
            key (str) - phoneme (i.e., short sequence of characters)
            val (Set(str)) - IPA translations of this language's phoneme
        """
        transcriptions = self.all_ipa_words()
        phoneme_dict = self.ipa_words_phonemes(transcriptions)
        return phoneme_dict

    def all_ipa_words(self):
        """
        Returns a set of IPAWords corresponding to all
        Wiktionary entries in this IPAParser's language.

        :return: Set(IPAWord), all IPAWords in this IPAParser's language
        """
        pages = self.all_page_defns()
        transcriptions = self.words_to_ipawords(pages)
        return transcriptions

    def ipa_words_phonemes(self, ipa_words):
        """
        Returns a dictionary representing all phonemes in ipa_words.
        ~
        N.B. Phonemes are in a language's native lettering system,
        while their forms are in IPA.

        :param ipa_words: Set(IPAWord), IPAWords to return phonemes of
        :return: dict, where...
            key (str) - phoneme (i.e., short sequence of >=1 characters)
            val (List[str]) - IPA translations of this language's phoneme
        """
        ipa_words = sorted(ipa_words, key=lambda iw: iw.get_difficulty())

        for ipa_word in ipa_words:
            print ipa_word.get_word()
            print "-"*8
            phoneme_dict = ipa_word.find_phoneme_dict()
            self.merge_phoneme_dicts(phoneme_dict)

        return self.phoneme_dict

    def get_lexicon(self, lim=None):
        """
        Returns a set of all words in this IPAParser's language, up to lim.
        ~
        If lim is None, returns all words.

        :param lim: int, number of words to retrieve
        :return: List[str], words in IPAParser's language
        """
        if self.lang_code is None:
            return

        words = list()
        path = PATH + "/resources/frequency_words/content/2016/%s/%s_full.txt" % (self.lang_code, self.lang_code)

        with open(path, 'r') as lexicon:
            line_no = 0
            for line in lexicon:
                word = line.split(" ", 1)[0]
                words.append(self.unicodize(word))
                if lim:
                    if line_no > lim:
                        break
                    line_no += 1

        return words

    def parse_lexicon(self, language):
        """
        Parses plaintext file for given language.
        Returns a dict with all words in lexicon
        as keys and corresponding lemma forms as values.
        ~
        Each new lexical entry should be separated by "\n",
        while inflected forms should be separated by ",".
        ~
        Assumes first word on every line is the lemma form
        of all subsequent words on the same line.
        ~
        N.B. The same lemma value will often belong to multiple keys.

        e.g. "kota, kocie, kot" -> {"kota":"kota", "kocie":"kota", "kot":"kota"}

        :param language: str, language of .txt file for lexicon
        :return: dict, where...
            key (str) - inflected form of a word
            val (str) - lemma form of inflected word
        """
        lexicon = None

        if language == "Polish":
            fn = self.parse_polish_lexicon
        elif language == "French":
            fn = self.parse_french_lexicon
        else:
            return lexicon

        filename = "/resources/lexica/" + language + ".txt"

        with open(PATH + filename, "rb") as lex:
            lexicon = fn(lex)

        return lexicon

    def parse_french_lexicon(self, lex):
        """
        Parses plaintext file for French lexicon with
        given filename.  Returns a dict with all lexemes
        in French lexicon as keys and corresponding
        lemma forms as values.
        ~
        Each new lexical entry should be separated by "\n",
        while inflected forms should be separated by ",".
        ~
        Assumes second word on every line is the lemma form
        of previous words on the same line.
        ~
        N.B. The same lemma value will often belong to
        multiple lexemes.

        e.g. "grande, grand" -> {"grande":"grand", "grand":"grand"}

        :param lex: List[str], entries in French lexicon
        :return: dict, where...
            key (str) - any lexical form of a word
            val (str) - lemmatized form of lemma
        """
        lexicon = {}

        for line in lex:
            line = line.decode("utf-8")
            line = line.strip("\n")
            if line[-1] == "=":
                lemma = line[:-2]
                lexicon[lemma] = lemma
            else:
                entry = line.split("\t")
                lemma = entry[1]
                lexeme = entry[0]
                lexicon[lexeme] = lemma

        return lexicon

    def parse_polish_lexicon(self, lex):
        """
        Parses plaintext file for Polish lexicon with
        given filename.  Returns a dict with all lexemes
        in Polish lexicon as keys and corresponding
        lemma forms as values.
        ~
        Inflected forms in each lexical entry should be
        separated by ",".
        ~
        Assumes first word on every line is the lemma form
        of following words on the same line.
        ~
        N.B. The same lemma value will often belong to
        multiple lexemes.

        e.g. "kota, kot, kocie" -> {"kota":"kota", "kot":"kota", "kocie":"kota"}

        :param lex: List[str], entries in Polish lexicon
        :return: dict, where...
            key (str) - any lexical form of a word
            val (str) - lemmatized form of lemma
        """
        lexicon = {}

        for line in lex:
            line = line.decode("utf-8")
            line = line.strip("\n")
            line = line.strip("\r")
            inflexions = line.split(",")
            lemma = inflexions[0]

            for inflexion in inflexions:
                lexicon[inflexion.strip()] = lemma

        return lexicon

    def word_url(self, word):
        """
        Returns a Wiktionary URL for the given word.

        :param word: str, word to retrieve URL for
        :return: str, URL matching given word
        """
        return self.BASE_URL % (word, self.language)

    def parse_url(self, url):
        """
        Parses given URL string to a BeautifulSoup Tag.

        :param url: str, URL to parse to tags
        :return: Tag, parsed URL
        """
        response = self.session.get(url)
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
        pg = page.find(name='a', attrs={"title": "Category:" + self.language + " terms with IPA pronunciation"})
        # fetch index of next page
        if pg.string != "next page":
            pgs = (pg for pg in
                   page.findAll(name='a', attrs={"title": "Category:" + self.language + " terms with IPA pronunciation"}))
            while pg.string != "next page":
                try:
                    pg = next(pgs)
                except StopIteration:
                    return
        # form wiki url from index
        url = self.WIKI_URL + pg['href']
        return self.parse_url(url)

    def all_lemma_pages(self):
        """
        Returns list of webpages for all Wiktionary entries for
        lemmas in this IPAParser's language.

        :return: List[Tag], given page's next pages
        """
        url = self.url + self.LEMMA_URL + sorted(self.alphabet)[0].upper()
        next_pg = self.parse_url(url)
        pgs = []

        while next_pg is not None:
            pgs.append(next_pg)
            next_pg = self.next_page(next_pg)

        return pgs

    def all_ipa_pages(self):
        """
        Returns list of webpages for all Wiktionary entries with
        IPA pronunciations in this IPAParser's language.

        :return: List[Tag], given page's next pages
        """
        url = self.url + self.IPA_URL + sorted(self.alphabet)[0].upper()
        next_pg = self.parse_url(url)
        pgs = []

        while next_pg is not None:
            pgs.append(next_pg)
            next_pg = self.next_page(next_pg)

        return pgs

    def page_common_defns(self, page, lim=50000):
        """
        Returns given BeautifulSoup Tag page's common definitions.

        :param page: Tag, page to find definitions from
        :param lim: int, lim <= 50000, number of words to retreive
        :return: Set((unicode) str), set of word definitions
        """
        defns = page.find(name='ul')
        defns = defns.findAll('a')
        common_words = self.common_words(lim)
        defns = set(defn['title'] for defn in defns if defn['title'] in common_words and
                    not defn['title'].istitle() and all(char not in defn['title'] for char in '.- '))
        return defns

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

    def pages_common_defns(self, pages, lim=50000):
        """
        Returns pages filtered to include only the most common definitions.

        :param pages: List[Tag], list of pages to filter by common definitions
        :param lim: int, lim <= 50000, number of words to retrieve
        :return: Set((unicode) str), set of common word definitions
        """
        defns = set()
        for next_pg in pages:
            defns.update(self.page_common_defns(next_pg, lim))
        return defns

    def all_page_defns(self):
        """
        Returns all Wiktionary definitions in this IPAParser's language.

        :return: Set((unicode) str), set of all word definitions
        """
        defns = set()
        next_pgs = self.all_ipa_pages()

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

    def find_page_language(self, page):
        """
        Returns the subset of the given BeautifulSoup Tag page in
        this IPAParser's language.

        :param page: Tag, page to return language section from
        :return: Tag, child of page in this IPAParser's language
        """
        pg = page.find('span', attrs={'id': self.language})
        return pg

    def find_ipa(self, page):
        """
        Returns IPA pronunciation from given BeautifulSoup Tag page.
        ~
        This method finds the first pronunciation that does not begin
        with a dash (which denotes a rhyme ending rather than the word).
        ~
        If no IPA pronunciation exists on the given page, returns None.

        :param page: Tag, page to find pronunciation from
        :return: (unicode) str, IPA pronunciation from given URL
        """
        pg = self.find_page_language(page)
        if pg is not None:
            spans = pg.findAllNext('span', attrs={'class': "IPA"})
            if len(spans) > 0:
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
        Returns part of speech from given BeautifulSoup Tag page.

        :param page: Tag, page to find part of speech from
        :return: str, part of speech from given URL
        """
        pg = self.find_page_language(page)
        if pg is None:
            pg = page
        spans = pg.findAllNext('span', attrs={'class': "mw-headline"})

        for span in spans:
            span_id = span['id']
            if span_id in LEMMA_TYPES:
                return span_id

    def findall_pos(self, page):
        """
        Returns parts of speech from given BeautifulSoup Tag page.

        :param page: Tag, page to find parts of speech from
        :return: List[str], parts of speech from given URL
        """
        pg = self.find_page_language(page)
        if pg is None:
            pg = page
        spans = pg.findAllNext('span', attrs={'class': "mw-headline"})

        poses = list()

        for span in spans:
            span_id = span['id']
            if span_id in LEMMA_TYPES:
                poses.append(span_id)

        if len(poses) == 0:
            poses.append(None)

        return poses

    def get_pos_num(self, pos):
        """
        Returns an integer representing this IPAWord's pos.

        :return: int, this IPAWord's pos integer
        """
        return LEMMA_TYPES[pos]

    def word_to_ipaword(self, word):
        """
        Returns the given word as an IPAWord.

        :param word: str, word to turn into IPAWord
        :return: IPAWord, IPAWord corresponding to given word
        """
        ipa = self.word_to_ipa(word)
        if ipa is not None:
            return IPAWord(word, self.remove_parens(ipa), self)

    def words_to_ipawords(self, words):
        """
        Transcribes the words in the given set of words to IPAWords.

        :param words: Set((unicode) str), set of word definitions
        :return: Set(IPAWord), IPAWords corresponding to given definitions
        """
        ipa_words = set()

        for word in words:
            ipa_word = self.word_to_ipaword(word)
            if ipa_word is not None:
                ipa_words.add(ipa_word)

        return ipa_words

    def word_to_ipa(self, word):
        """
        Transcribes the given word to IPA.

        :param word: str, word to transcribe to IPA
        :return: (unicode) str, IPA transcription of word
        """
        word = self.unicodize(word)
        if word in self.lang_ipas:
            return self.lang_ipas[word]
        else:
            url = self.word_url(word)
            parsed_url = self.parse_url(url)
            ipa = self.find_ipa(parsed_url)
            ipa = self.unicodize(ipa)
            self.lang_ipas[word] = ipa
            return ipa

    def words_to_ipa(self, words):
        """
        Transcribes the given words to IPA.

        :param word: List[str], words to transcribe to IPA
        :return: List[(unicode) str], IPA transcriptions of words
        """
        ipas = list()

        for word in words:
            ipa = self.word_to_ipa(word)
            if ipa is not None:
                ipas.append(ipa)

        return ipas

    def word_to_pos(self, word):
        """
        Returns the given word's part of speech.

        :param word: str, word to get parts of speech of
        :return: str, word's part of speech
        """
        if word in self.lang_pos:
            return self.lang_pos[word]
        else:
            url = self.word_url(word)
            parsed_url = self.parse_url(url)
            pos = self.find_pos(parsed_url)
            self.lang_pos[word] = pos
            return pos

    def word_to_poses(self, word):
        """
        Returns the given word's parts of speech.

        :param word: str, word to get parts of speech of
        :return: Set(str), word's part of speech
        """
        if word in self.lang_pos:
            return self.lang_pos[word]
        else:
            url = self.word_url(word)
            parsed_url = self.parse_url(url)
            poses = self.findall_pos(parsed_url)
            #poses = filter(None, poses)
            self.lang_pos[word] = poses
            print word, poses
            return poses

    def words_to_pos(self, words):
        """
        Returns a list of the given words' parts of speech.

        :param word: List[str], words to get parts of speech of
        :return: List[str], words' parts of speech
        """
        pos = list()
        for word in words:
            pos.append(self.word_to_pos(word))
        return pos

    def words_to_poses(self, words):
        """
        Returns a list of the given words' parts of speech.

        :param word: List[str], words to get parts of speech of
        :return: List[Set(str)], words' parts of speech
        """
        poses = list()
        for word in words:
            poses.append(self.word_to_poses(word))
        return poses

    def clean_ipa(self, ipa):
        """
        Returns the given IPA pronunciation with stress marks,
        syllable markers, and parentheses removed.

        :param ipa: (unicode) str, IPA to remove stress/syllable marks from
        :return: (unicode) str, given ipa with stress/syllable marks removed
        """
        return re.sub(u"[ˈˌ\.]", u"", self.remove_parens(ipa))

    def clean_word(self, word):
        """
        Returns the given word in lowercase and with punctuation and
        whitespace removed.

        :param word: (unicode) str, word to clean
        :return: (unicode) str, cleaned word
        """
        return re.sub("[" + string.punctuation + "]", u"", word.lower())

    def remove_parens(self, word):
        """
        Returns the given word with parentheses removed.

        :param word: (unicode) str, word to remove parentheses from
        :return: (unicode) str, word with parentheses removed
        """
        return word.split("(", 1)[0]

    def ipa_words_to_features(self, ipa_words):
        questions = []
        answers = []

        for ipa_word in ipa_words:
            ipas = ipa_word.find_ipa_phonemes(ipa_word.get_ipa())
            ipas_nums = get_ipas_nums(ipas)
            pos_num = LEMMA_TYPES[ipa_word.get_pos()]
            word_num = int(ipa_word)
            if len(str(word_num)) > 20:
                continue
            word_feat = [word_num, pos_num]
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
            word_dict = ipa_word.get_dict()
            for key in word_dict:
                key_num = key + str(word_count)
                ipa_dict[key_num] = word_dict[key]
            word_count += 1

        return ipa_dict

    def train(self):
        ipa_lexicon = self.all_ipa_words()
        cutoff = int(len(ipa_lexicon) * 0.75)
        ipa_lst = list(ipa_lexicon)
        train_set, test_set = ipa_lst[:cutoff], ipa_lst[cutoff:]
        train_qs, train_as = self.ipa_words_to_features(train_set)
        test_qs, test_as = self.ipa_words_to_features(test_set)
        ipa_learn.train_classifier(train_qs, train_as)
        ipa_learn.test_classifier(test_qs, test_as)

    def train_dict(self):
        ipa_lexicon = self.all_ipa_words()
        train = self.ipa_words_to_dict(ipa_lexicon)
        ipa_learn.train_dict_classifier(train)

    def unicodize(self, text):
        """
        Returns the given text in unicode.
        ~
        Ensures all text is in unicode for parsing.

        :param text: str (byte), text to return in unicode
        :return: str (unicode), text in unicode
        """
        if text is not None:
            if not isinstance(text, unicode):
                text = text.decode("utf-8") #, errors='ignore')
        return text

    def deunicodize(self, text):
        """
        Returns the given text decoded from unicode.
        ~
        Ensures all text is in bytes for printing.

        :param text: str (unicode), text to decode from unicode
        :return: str (byte), text in unicode
        """
        if text is not None:
            if isinstance(text, unicode):
                text = text.encode("utf-8")
        return text

    def destress(self, ipa):
        """
        Returns the given IPA pronunciation with stress marks removed.

        :param ipa: (unicode) str, IPA to remove stress marks from
        :return: (unicode) str, ipa with stress marks removed
        """
        return re.sub(u"[" + self.STRESS_MARKS + u"]", u"", ipa)

    def restress(self, ipa):
        """
        Returns the given IPA pronunciation with all stress marks
        replaced with periods.

        :param ipa: (unicode) str, IPA to replace stress marks with periods
        :return: (unicode) str, ipa with stress marks replaced with periods
        """
        restressed = re.sub(u"[" + self.STRESS_MARKS + u"]", u".", ipa)
        return restressed.strip(u".")

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

    def next_phoneme(self, ipa, remove=True, use_syllables=True):
        """
        Returns the given ipa's next phoneme.
        ~
        If remove is set to True, this method finds and
        removes ipa's first phoneme, returning a 2-tuple of
        1) the phoneme and 2) given ipa with phoneme removed.
        ~
        e.g. next_phoneme("ɔˈba.lat͡ɕ") -> ("ɔ", "balat͡ɕ")

        :param ipa: (unicode) str, IPA word to return next phoneme of
        :param remove: bool, whether to return ipa with vowels removed
        :param use_syllables: bool, whether to calculate next phoneme with ipa's syllables
        :return: tuple((both unicode) str, str), IPA's first phoneme and rest of IPA
        """
        phoneme = str()  # next phoneme so far

        if len(ipa) == 0:
            next_phoneme = (phoneme, ipa) if remove else phoneme
            return next_phoneme

        if use_syllables:
            # ensure uniform stress marks
            new_ipa = self.restress(ipa)
            # end ipa @ 1st syllable marker
            new_ipa = new_ipa.split(u".", 1)[0]
        else:
            new_ipa = self.clean_ipa(ipa)

        # search for polyphonemes first
        end = 1
        # TODO: change to end <= min([longest IPA phoneme in phoneme_dict], len(new_ipa))
        while end <= 3:
            new_sym = new_ipa[:end]
            filtered_sym = "".join(filter((lambda x: x if x not in SEMIVOWELS else ""), new_sym))
            # check to make sure phonemes are all vowels xor all consonants
            are_vowels = self.is_ipa_vowel(filtered_sym)
            if are_vowels is None:
                end -= 1
                break
            elif self.is_ipa_phoneme(new_sym):
                phoneme = new_sym
            end += 1

        # if no polyphonemes found,
        # set phoneme to first IPA character
        if len(phoneme) == 0:
            phoneme = new_ipa[0]
            end = 1

        next_phoneme = (phoneme, ipa[end:]) if remove else phoneme
        return next_phoneme

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

    def is_letter_vowel(self, chars):
        """
        Returns True if the given chars is a vowel in this
        IPAWord's native language, False if a consonant.
        ~
        Returns None if chars is not in this IPAParser's phoneme_dict.
        ~
        N.B. chars can be multiple letters long.

        :param chars: (unicode) str, character(s) to determine whether vowel
        :return: bool, whether given character(s) are a vowel
        """
        if chars in self.phoneme_dict:
            return chars in self.vowels.get_items()

    def is_letter_consonant(self, chars):
        """
        Returns True if the given chars is a consonant in this
        IPAWord's native language, False if a vowel.
        ~
        Returns None if this chars is not in this IPAParser's phoneme_dict.
        ~
        N.B. chars can be multiple letters long.

        :param chars: (unicode) str, character(s) to determine whether consonant
        :return: bool, whether given character(s) are a consonant
        """
        if chars in self.phoneme_dict:
            return chars in self.consonants.get_items()

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
            if len(ipa) > 1:
                ipa_phonemes = self.phoneme_dict.keys() #all_ipa_phonemes()
                if len(ipa_phonemes) == 0:
                    print "phonemes are NONE"
                    return
                elif ipa in ipa_phonemes:
                    return any(self.is_ipa_vowel(sym) for sym in ipa if sym in IPALETTERS)
            else:
                return
        else:
            return ipa_sym.get_is_vowel()

    def is_ipa_semivowel(self, ipa):
        """
        Returns True if the given IPA symbol is a semivowel
        according to the IPA, False otherwise.
        ~
        Returns None if this symbol is not an IPA letter.

        :param ipa: (unicode) str, IPA symbol to determine whether vowel
        :return: bool, whether given IPA symbol is a vowel
        """
        try:
            IPALETTERS[ipa]
        except KeyError:
            return None
        else:
            return ipa in SEMIVOWELS

    def is_ipa_phoneme(self, ipa):
        """
        Returns True if the given IPA symbol is a phoneme in the
        IPA or in this IPAParser's language, False otherwise.

        :param ipa: (unicode) str, IPA symbol to determine whether phoneme
        :return: bool, whether given IPA symbol is a phoneme
        """
        for phoneme in self.phoneme_dict:
            items = self.phoneme_dict[phoneme]
            for item in iter(items):
                if ipa == item:
                    return True
        else:
            if self.is_ipa_vowel(ipa) is not None:
                return True
            else:
                return False

    def filter_morphemes(self, ipa_words):
        """
        Returns a list of IPAWord words from ipa_words
        that are classified as "Morpheme" by Wiktionary.

        :param ipa_words: List[IPAWord], list of IPAWords to get morphemes of
        :return: List[str], only IPAWord words that are morphemes
        """
        morphemes = set()
        for ipa_word in ipa_words:
            if ipa_word.get_pos() == "Morpheme":
                morphemes.add(ipa_word.word)
        return morphemes
