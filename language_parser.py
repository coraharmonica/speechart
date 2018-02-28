# coding: utf-8
"""
LANGUAGE_PARSER:

    Contains LanguageParser class for parsing data in
    a particular language from Wiktionary.
"""
import json
from ordered_set import OrderedSet
from wiktionary_parser import *


class LanguageParser(WiktionaryParser):
    ALPHABETS = {}
    LEXICA = {}

    def __init__(self, language):
        WiktionaryParser.__init__(self)
        self.language = language
        self.url = self.url % self.language
        # ALPHABETS
        self.alphabet = self.init_alphabet(self.language)  # all characters in language
        self.add_alphabet(self.language, self.alphabet)
        # LEXICA
        self.lexicon = self.init_lexicon(self.language)
        self.add_lexicon(self.language, self.lexicon)

        # LANGUAGE DICTIONARIES
        # --> IPA pronunciations
        self.langs_ipas = self.fetch_langs_ipas()
        self.lang_ipas = self.fetch_lang_ipas()
        # --> parts of speech
        self.langs_pos = self.fetch_langs_pos()
        self.lang_pos = self.fetch_lang_pos()
        # --> inflections
        self.langs_inflections = self.fetch_langs_inflections()
        self.lang_inflections = self.fetch_lang_inflections()
        # --> etymologies
        self.langs_etymologies = self.fetch_langs_etymologies()
        self.lang_etymologies = self.fetch_lang_etymologies()
        # --> declensions
        self.langs_declensions = self.fetch_langs_declensions()
        self.lang_declensions = self.fetch_lang_declensions()

        self.wordnet_words = self.get_wordnet_words()
        self.words = self.wordnet_words.intersection(self.lexicon)

    def verify_word(self, word, language=None):
        """
        Returns True if given word contains only characters from
        this LanguageParser's alphabet, False otherwise.

        :param word: str, word to verify whether in language
        :param language: str, language to verify word with
        :return: bool, whether word contains only characters from language
        """
        language = self.verify_language(language)
        word_chars = set(word)
        alphabet = self.fetch_alphabet(language)
        return len(word_chars.difference(alphabet)) == 0

    # LANGUAGES
    # ---------
    def set_language(self, language):
        """
        Sets this LanguageParser's language to the given language.

        :param language: str, language to change to
        :return: None
        """
        if self.language != language:
            self.refresh_json()
            self.__init__(language)

    def add_language(self, language):
        """
        Adds the given language to all language dictionaries in
        this LanguageParser.

        :param language: str, language to add to language dictionaries
        :return: None
        """
        self.langs_pos.setdefault(language, dict())
        self.langs_ipas.setdefault(language, dict())
        self.langs_inflections.setdefault(language, dict())
        self.langs_etymologies.setdefault(language, dict())

    def add_languages(self, languages):
        """
        Adds the given languages to all language dictionaries in
        this LanguageParser.

        :param languages: List[str], languages to add to language dictionaries
        :return: None
        """
        for language in languages:
            self.add_language(language)

    def find_page_languages(self, page):
        """
        Returns a list of the given page's languages.

        :param page: Tag, page to return languages from
        :return: List[str], all languages on this page
        """
        languages = WiktionaryParser.find_page_languages(self, page)
        self.add_languages(languages)
        return self.langs_ipas.keys()

    # LEXICA
    # ------
    def init_lexicon(self, language=None, lim=None):
        """
        Returns a set of all words in this language, up to lim.
        ~
        If lim is None, returns all words.

        :param language: str, language of lexicon to retrieve
        :param lim: int, number of words in lexicon to retrieve
        :return: List[str], words in LanguageParser's language
        """
        lang_code = self.get_lang_code(language)

        if lang_code is None:
            return

        words = list()
        path = self.PATH + "/resources/frequency_words/content/2016/%s/%s_full.txt" % (lang_code, lang_code)

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

    def add_lexicon(self, language, lexicon):
        """
        Adds the given lexicon to LEXICA under the given language.

        :param language: str, language of lexicon
        :param lexicon: List[str], all words in given language
        :return: None
        """
        self.LEXICA[language] = lexicon

    def fetch_lexicon(self, language, lim=100000):
        """
        Returns the lexicon for the given language.
        ~
        If no lexicon for this language exists, creates new
        lexicon for language, adds to LEXICA, and returns the result.

        :param language: str, language of lexicon
        :return: List[str], all words in given language
        """
        try:
            return self.LEXICA[language]
        except KeyError:
            lexicon = self.init_lexicon(language, lim)
            self.add_lexicon(language, lexicon)
            return lexicon

    def in_lexicon(self, word, language=None):
        return word in self.fetch_lexicon(language)

    def parse_lexicon(self, language):
        """
        Parses plaintext lexicon in given language.
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
        lexicon = self.fetch_lang_inflections(language)

        if len(lexicon) == 0:
            if language == "Polish":
                fn = self.parse_polish_lexicon
            elif language == "French":
                fn = self.parse_french_lexicon
            else:
                return lexicon

            filename = "/resources/lexica/" + language + ".txt"

            with open(self.PATH + filename, "rb") as lex:
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

        e.g. "grande, grand" -> {"grand": ["grand", "grande"]}

        :param lex: List[str], entries in French lexicon
        :return: dict, where...
            key (str) - word lemma
            val (List[str]) - all lexical forms of word lemma
        """
        lexicon = dict()

        for line in lex:
            line = line.strip("\n")
            line = self.unicodize(line)
            if line[-1] == "=":
                lemma = line[:-2]
                lexicon.setdefault(lemma, list())
                lexicon[lemma].append(lemma)
                self.add_inflection(lemma, lemma, "French")
            else:
                entry = line.split("\t")
                lemma = entry[1]
                lexeme = entry[0]
                lexicon.setdefault(lexeme, list())
                lexicon[lexeme].append(lemma)
                self.add_inflection(lexeme, lemma, "French")

        self.refresh_inflections()
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

        e.g. "kot, kota, kocie" -> {"kot": ["kot", "kota", "kocie"]}

        :param lex: List[str], entries in Polish lexicon
        :return: dict, where...
            key (str) - word lemma
            val (List[str]) - all lexical forms of word lemma
        """
        lexicon = dict()

        for line in lex:
            line = line.strip("\n")
            line = line.strip("\r")
            line = self.unicodize(line)
            lexemes = line.split(",")
            lexemes = [l.strip() for l in lexemes]
            lemma = lexemes[0]
            lexicon[lemma] = lexemes
            self.add_inflections(lexemes, lemma, "Polish")

        self.refresh_inflections()
        return lexicon

    # ALPHABET
    # --------
    def init_alphabet(self, language=None):
        """
        Returns a set of all characters in the given language.

        :param language: str, language of alphabet
        :return: Set(str), all characters in this language
        """
        words = self.fetch_lexicon(language, lim=1000)
        alphabet = set()

        for word in words:
            alphabet.update(word)

        return alphabet

    def add_alphabet(self, language, alphabet):
        """
        Adds the given alphabet to ALPHABETS under the given language.

        :param language: str, language of alphabet
        :param alphabet: List[str], all letters in given language's alphabet
        :return: None
        """
        self.ALPHABETS[language] = alphabet

    def fetch_alphabet(self, language):
        """
        Returns the alphabet for the given language.
        ~
        If no alphabet for this language exists, creates new
        alphabet for language, adds to ALPHABETS, and returns the result.

        :param language: str, language of alphabet
        :return: List[str], all letters in given language's alphabet
        """
        try:
            return self.ALPHABETS[language]
        except KeyError:
            alphabet = self.init_alphabet(language)
            self.add_alphabet(language, alphabet)
            return alphabet

    # JSON
    # ----
    def dump_json(self, data, filename):
        """
        Dumps data (prettily) to filename.json.

        :param data: X, data to dump to JSON
        :param filename: str, name of .json file to dump to
        :return: None
        """
        path = self.PATH + "/resources/data/" + filename + ".json"
        json.dump(data, open(path, 'w'), indent=1, sort_keys=True, encoding='utf-8')

    def fetch_json(self, filename):
        """
        Returns a dictionary corresponding to the given JSON file.

        :param filename: str, name of .json file to fetch
        :return: X, content of given .json file
        """
        return json.load(open(self.PATH + "/resources/data/" + filename + ".json"))

    def fetch_langs_ipas(self):
        """
        Returns a dictionary of words and their IPA transcriptions.

        :return: X, content of ipas.json file
        """
        return self.fetch_json("ipas")

    def fetch_lang_ipas(self, language=None):
        """
        Returns the IPA dictionary in this language.

        :param language: str, language of IPA dictionary
        :return: dict, where...
            key (str) - word in language
            val (str) - word's IPA transcription
        """
        language = self.verify_language(language)
        try:
            return self.langs_ipas[language]
        except KeyError:
            lang_ipas = dict()
            self.langs_ipas[language] = lang_ipas
            return lang_ipas

    def fetch_langs_pos(self):
        """
        Returns a dictionary of words and their parts of speech.

        :return: X, content of parts_of_speech.json file
        """
        return self.fetch_json("parts_of_speech")

    def fetch_lang_pos(self, language=None):
        """
        Returns the part-of-speech dictionary in this language.

        :param language: str, language of inflectional dictionary
        :return: dict, where...
            key (str) - word in native language
            val (str) - word's part of speech
        """
        language = self.verify_language(language)
        try:
            return self.langs_pos[language]
        except KeyError:
            lang_pos = dict()
            self.langs_pos[language] = lang_pos
            return lang_pos

    def fetch_langs_inflections(self):
        """
        Returns all inflectional dictionaries in every language.

        :return: dict(str, dict), where str is language and dict is...
            key (str) - lemma in native language
            val (List[str]) - lexemes of given lemma
        """
        return self.fetch_json("inflections")

    def fetch_lang_inflections(self, language=None):
        """
        Returns the inflectional dictionary in this LanguageParser's
        native language.

        :param language: str, language of inflectional dictionary
        :return: dict, where...
            key (str) - lemma in native language
            val (List[str]) - lexemes of given lemma
        """
        language = self.verify_language(language)
        try:
            return self.langs_inflections[language]
        except KeyError:
            inflections = dict()
            self.langs_inflections[language] = inflections
            return inflections

    def fetch_langs_etymologies(self):
        """
        Returns all etymological dictionaries in every language.

        :return: dict(str, dict), where str is language and dict is...
            key (str) - lexeme in language
            val (List[str]) - morphemic decomposition of lexeme
        """
        return self.fetch_json("etymologies")

    def fetch_lang_etymologies(self, language=None):
        """
        Returns the etymological dictionary for this language.

        :return: dict, where...
            key (str) - lexeme in language
            val (List[str]) - morphemic decomposition of lexeme
        """
        language = self.verify_language(language)
        try:
            return self.langs_etymologies[language]
        except KeyError:
            etymologies = dict()
            self.langs_etymologies[language] = etymologies
            return etymologies

    def fetch_langs_declensions(self):
        """
        Returns all declension dictionaries in every language.

        :return: dict(str, dict), where str is language and dict is...
            key (str) - declension column name
            val (dict(str, List[str])) - row names & values
        """
        return self.fetch_json("declensions")

    def fetch_lang_declensions(self, language=None):
        """
        Returns the declension dictionary for this language.

        :return: dict(str, dict), where str is declension column and dict is...
            key (str) - declension row name
            val (List[str]) - inflection of lexeme
        """
        language = self.verify_language(language)
        try:
            return self.langs_declensions[language]
        except KeyError:
            declensions = dict()
            self.langs_declensions[language] = declensions
            return declensions

    def refresh_json(self):
        """
        Dumps this LanguageParser's data from...
            langs_ipas to ipas.json,
            langs_pos to parts_of_speech.json,
            langs_inflections to inflections.json,
            langs_etymologies to etymologies.json, and
            langs_declensions to declensions.json.

        :return: None
        """
        self.refresh_pos()
        self.refresh_ipas()
        self.refresh_inflections()
        self.refresh_etymologies()
        self.refresh_declensions()

    def refresh_ipas(self):
        """
        Dumps this LanguageParser's langs_ipas data to ipas.json.

        :return: None
        """
        self.langs_ipas[self.language] = self.lang_ipas
        self.dump_json(self.langs_ipas, "ipas")

    def refresh_pos(self):
        """
        Dumps this LanguageParser's langs_pos to parts_of_speech.json.

        :return: None
        """
        self.langs_pos[self.language] = self.lang_pos
        self.dump_json(self.langs_pos, "parts_of_speech")

    def refresh_inflections(self):
        """
        Dumps this LanguageParser's langs_inflections data to inflections.json.

        :return: None
        """
        self.langs_inflections[self.language] = self.lang_inflections
        self.dump_json(self.langs_inflections, "inflections")

    def refresh_etymologies(self):
        """
        Dumps this LanguageParser's langs_etymologies data to etymologies.json.

        :return: None
        """
        self.langs_etymologies[self.language] = self.lang_etymologies
        self.dump_json(self.langs_etymologies, "etymologies")

    def refresh_declensions(self):
        """
        Dumps this LanguageParser's langs_declensions data to declensions.json.

        :return: None
        """
        self.langs_declensions[self.language] = self.lang_declensions
        self.dump_json(self.langs_declensions, "declensions")

    # LOOKUPS
    # -------
    def lookup_word_ipa(self, word, language=None):
        """
        Returns the given word's IPA pronunciation from this language's
        IPA dictionary.
        ~
        If no pronunciation exists, returns None.

        :param word: str, word to lookup IPA pronunciation for
        :return: (unicode) str, word's IPA pronunciation
        """
        try:
            return self.lookup_word_ipas(word, language)[0]
        except IndexError:
            return

    def lookup_word_ipas(self, word, language=None):
        """
        Returns the given word's IPA pronunciations from this language's
        IPA dictionary.
        ~
        Returns empty list if word has no existing IPA pronunciation.

        :param word: str, word to lookup IPA pronunciations for
        :return: List[(unicode) str], word's IPA pronunciations
        """
        lang_ipas = self.fetch_lang_ipas(language)
        try:
            word_ipas = lang_ipas[word]
        except KeyError:
            try:
                word_ipas = lang_ipas[word.lower()]
            except KeyError:
                word_ipas = list()
        return word_ipas

    def lookup_word_pos(self, word, language=None):
        """
        Returns this word's part of speech from this language's
        parts-of-speech dictionary.
        ~
        If no part of speech exists, returns None.

        :param word: str, word to lookup part of speech for
        :return: (unicode) str, word's part of speech
        """
        try:
            return self.lookup_word_poses(word, language)[0]
        except IndexError:
            return

    def lookup_word_poses(self, word, language=None):
        """
        Returns all this word's parts of speech from this language's
        parts-of-speech dictionary.

        :param word: str, word to lookup parts of speech for
        :return: List[(unicode) str], word's parts of speech
        """
        poses = self.fetch_lang_pos(language)
        try:
            return poses[word]
        except KeyError:
            try:
                return poses[word.lower()]
            except KeyError:
                return list()

    def lookup_inflection(self, inflection, language=None):
        """
        Returns all this inflection's lemmas from this language's
        IPA dictionary.

        :param inflection: str, word to lookup lemmas for
        :return: List[(unicode) str], inflection's lemmas
        """
        inflections = self.fetch_lang_inflections(language)
        try:
            return inflections[inflection]
        except KeyError:
            try:
                return inflections[inflection.lower()]
            except KeyError:
                return list()

    def lookup_etymology(self, word, language=None):
        """
        Returns this word's etymology from this language's
        IPA dictionary.
        ~
        If no etymology exists, returns None.

        :param word: str, word to lookup etymology for
        :return: List[(unicode) str], word's etymology
        """
        etymologies = self.fetch_lang_etymologies(language)
        try:
            return etymologies[word]
        except KeyError:
            return

    def lookup_declension(self, word, language=None):
        """
        Returns this word's declension from this language's
        IPA dictionary.
        ~
        If no declension exists, returns None.

        :param word: str, word to lookup declension for
        :return: dict[str, list], word's declension
        """
        declension = self.fetch_lang_declensions(language)
        try:
            return declension[word]
        except KeyError:
            return

    def uninflect(self, inflection, language=None):
        """
        Returns this inflection's lemma from this language's
        IPA dictionary.
        ~
        If no lemma exists, returns None.

        :param inflection: str, word to lookup lemma for
        :return: (unicode) str, inflection's lemma
        """
        language = self.verify_language(language)
        try:
            return self.lookup_inflection(inflection, language)[0]
        except IndexError:
            return inflection

    # BULK LOOKUPS
    # ------------
    def all_etymologies(self):
        """
        Returns a dictionary of each word in this MorphemeParser's words
        and its corresponding etymology (according to Wiktionary).

        :return: dict, where...
            key (str) - word with etymology
            val (List[str]) - given word's etymology (as a combination of words)
        """
        return self.words_etymologies(self.words, self.language)

    def all_page_defns(self):
        """
        Returns all Wiktionary definitions in this LanguageParser's language.

        :return: Set((unicode) str), set of all word definitions
        """
        defns = set()
        next_pgs = self.all_ipa_pages()

        for next_pg in next_pgs:
            defns.update(self.page_defns(next_pg))

        return defns

    def all_lemma_pages(self):
        """
        Returns list of webpages for all Wiktionary entries for
        lemmas in this LanguageParser's language.

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
        IPA pronunciations in this LanguageParser's language.

        :return: List[Tag], given page's next pages
        """
        url = self.url + self.IPA_URL + sorted(self.alphabet)[0].upper()
        next_pg = self.parse_url(url)
        pgs = []

        while next_pg is not None:
            pgs.append(next_pg)
            next_pg = self.next_page(next_pg)

        return pgs

    # ADDITIONS
    # ---------
    def add_ipas(self, word, ipas, language=None):
        """
        Adds the given word as a key to this language's IPA
        dictionary, with IPA pronunciations as values.

        :param word: str, word to add as key
        :param ipas: List[str], IPAs to add as values
        :param language: str, language of IPAs/word
        :return: None
        """
        for ipa in ipas:
            self.add_ipa(word, ipa, language)

    def add_ipa(self, word, ipa, language=None):
        """
        Adds the given word as a key to this language's IPA
        dictionary, appending IPA pronunciation to its values.

        :param word: str, word to add as key
        :param ipa: str, IPA pronunciation to add to values
        :param language: str, language of IPAs/word
        :return: None
        """
        language = self.verify_language(language)
        ipa_dict = self.fetch_lang_ipas(language)
        ipas = ipa_dict.setdefault(word, list())

        if ipa is not None:
            ipas.append(ipa)
            ipa_dict[word] = OrderedSet(ipas).items
            self.langs_ipas[language] = ipa_dict

    def add_etymologies(self, word, etymologies, language=None):
        """
        Adds the given word as a key to this language's etymological
        dictionary, with etymologies as values.

        :param word: str, word to add as key
        :param etymologies: List[str], etymologies to add as values
        :param language: str, language of etymologies/word
        :return: None
        """
        for etymology in etymologies:
            self.add_etymology(word, etymology, language)

    def add_etymology(self, word, etymology, language=None):
        """
        Adds the given word as a key to this language's etymological
        dictionary, adding etymology to its values.

        :param word: str, word to add as key
        :param etymology: str, etymology to add to values
        :param language: str, language of etymology/word
        :return: None
        """
        language = self.verify_language(language)
        etym_dict = self.fetch_lang_etymologies(language)
        etyms = etym_dict.setdefault(word, list())

        if etymology is not None:
            etyms.append(etymology)
            etym_dict[word] = OrderedSet(etyms).items
            self.langs_etymologies[language] = etym_dict

    def add_inflections(self, inflections, lemma, language=None):
        """
        Adds the given inflections as keys to this language's
        inflectional dictionary, with lemma as their values.

        :param inflections: List[str], inflections to add as keys
        :param lemma: str, lemmatized form of inflections to add as value
        :param language: str, language of inflections/lemma
        :return: None
        """
        for inflection in inflections:
            self.add_inflection(inflection, lemma, language)

    def add_inflection(self, inflection, lemma, language=None):
        """
        Adds the given inflection as a key to this language's
        inflectional dictionary, with lemma as its value.

        :param inflections: str, inflection to add as key
        :param lemma: str, lemmatized form of inflection to add as value
        :param language: str, language of inflection/lemma
        :return: None
        """
        inflection, lemma = inflection.strip(), lemma.strip()
        language = self.verify_language(language)
        inflections = self.fetch_lang_inflections(language)

        if lemma is not None:
            for subinflection in inflection.split("/"):
                subinflection = subinflection.strip()
                lemmas = inflections.setdefault(subinflection, list())
                lemmas.append(lemma)
                inflections[subinflection] = list(set(lemmas))
            self.langs_inflections[language] = inflections

    def add_declensions(self, word, declensions, language=None):
        """
        Adds the given word as a key to this language's declension
        dictionary, with declensions as values.

        :param word: str, word to add as key
        :param declensions: List[str], declensions to add as values
        :param language: str, language of declensions/word
        :return: None
        """
        for declension in declensions:
            self.add_declension(word, declension, language)

    def add_declension(self, word, declension, language=None):
        """
        Adds the given word as a key to this language's declension
        dictionary, adding declension to its values.

        :param word: str, word to add as key
        :param declension: dict(str, List[str]), declension to add to values
        :param language: str, language of declension/word
        :return: None
        """
        language = self.verify_language(language)
        declensions = self.fetch_lang_declensions(language)
        dec = declensions.setdefault(word, dict())

        if declension is not None:
            dec.update(declension)
            declensions[word] = dec
            self.langs_declensions[language] = declensions

    # WORDNET
    # -------
    def get_wordnet_words(self):
        """
        Returns a set of all words in Wordnet.

        :return: Set(str), Wordnet word
        """
        lexicon = self.parse_lexicon(self.language)

        if len(lexicon) != 0:
            return set(lexicon.keys())
        else:
            entries = set()
            if self.language == "English":
                path = self.PATH + "/resources/wordnet/wn_s.txt"

                with open(path, "r") as synsets:
                    for synset in synsets:
                        synset = synset[2:-3]
                        info = synset.split(",")
                        name = info[2]
                        name = name[1:-1]
                        if " " not in name:
                            entries.add(name)

            return entries

    def get_wordnet_word_pairs(self):
        """
        Returns a list of 2-tuples consisting of a Wordnet word and
        its corresponding parts of speech.

        :return: Set(tuple(str,str)), Wordnet word and pos
        """
        path = self.PATH + "/resources/wordnet/wn_s.txt"
        entries = set()

        with open(path, "r") as synsets:
            for synset in synsets:
                synset = synset[2:-3]
                info = synset.split(",")
                name = info[2]
                name = name[1:-1]
                pos = info[3]
                if " " not in name:
                    pair = (self.unicodize(name), self.unicodize(pos))
                    entries.add(pair)

        return entries

    # COMMON WORDS
    # ------------
    def common_words(self, lim=50000):
        """
        Returns a list of the 50,000 most common words
        in this LanguageParser's language.

        :param lim: int, lim <= 50000, number of words to retreive
        :return: List[str], 50k most common words in LanguageParser's language
        """
        lang_code = self.get_lang_code()

        if lang_code is None:
            return

        words = list()
        path = self.PATH + "/resources/frequency_words/content/2016/%s/%s_50k.txt" % (lang_code, lang_code)

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

    def common_word_pairs(self, lim=50000):
        """
        Returns a set of common word-pos pairs, up to lim.

        :param lim: int, number of common words to return
        :return: List[tuple(str, str)], Wordnet word and pos
        """
        common_words = self.common_morphemes(lim)

        if self.language == "English":
            word_pairs = self.get_wordnet_word_pairs()
            return [word_pair for word_pair in word_pairs if word_pair[0] in common_words]
        else:
            inflections = self.parse_lexicon(self.language)
            if len(inflections) == 0:
                lemmas = common_words
            else:
                lemmas = [self.uninflect(cw, self.language) for cw in common_words]

            poses = self.words_to_poses(lemmas)
            word_pairs = list()

            for i in range(len(common_words)):
                word = common_words[i]
                pos = poses[i]
                if len(pos) == 0:
                    pos.append(None)
                for p in pos:
                    pair = (self.unicodize(word), self.unicodize(p))
                    word_pairs.append(pair)

            return word_pairs

    def common_morphemes(self, lim=50000):
        """
        Returns a set of the 50,000 most common words
        in this LanguageParser's language, including their
        constituent words.

        :param lim: int, lim <= 50000, number of words to retrieve
        :return: Set(str), up to 50k most common words in LanguageParser's language
        """
        lexicon = self.lexicon
        common_words = lexicon[:lim]
        morphemes = common_words[:]
        common_words = set(common_words)
        all_words = self.wordnet_words.intersection(lexicon).difference(common_words)

        for word in all_words:
            # catch all derivative words
            if len(word) > 3: # or cw == word[:len(cw)]
                if any(word == cw[:len(word)]
                       for cw in common_words if (len(word)/4) < len(cw)):
                    word = self.unicodize(word)
                    print word, "is a derivative of a common word"
                    morphemes.append(word)

        return morphemes

    # WORD MANIPULATION
    # -----------------
    def word_to_pos(self, word):
        """
        Returns the given word's part of speech.

        :param word: str, word to get parts of speech of
        :return: str, word's part of speech
        """
        if word in self.lang_pos:
            return self.lang_pos[word]
        else:
            parsed_url = self.word_page(word)
            pos = self.page_pos(parsed_url)
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
            parsed_url = self.word_page(word)
            poses = self.page_poses(parsed_url)
            self.lang_pos[word] = poses
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
            print word
            poses.append(self.word_to_poses(word))
        return poses

