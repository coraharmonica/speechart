# coding: utf-8
"""
IPA_PARSER:

    Contains IPAParser class for parsing IPA pronunciation data.
"""
from ipa_word import *
from morpheme_parser import *


class IPAParser(MorphemeParser):
    """
    A class for parsing IPA data from Wiktionary in a given language.
    """
    STRESS_MARKS = u"ˈˌ"

    def __init__(self, language):
        MorphemeParser.__init__(self, language)
        self.ipas = set()        # this language's IPA symbols
        self.vowels = OrderedSet([])
        self.consonants = OrderedSet([])
        self.phoneme_dict = {}

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

    # LEMMAS
    # ------
    def lemmatize(self, word, language=None):
        """
        Returns the lemma for this word in this language.
        ~
        If word has no lemma, this method returns the given word.
        ~
        e.g. lemmatize("drove", "English") -> "drive"
             lemmatize("yeux", "French") -> "œil"

        :param word: str, word to find lemma for
        :param language: str, language of given word
        :return: str, lemma for given word
        """
        if len(word) != 0:
            language = self.verify_language(language)

            inflection = self.lookup_inflection(word, language)
            if len(inflection) != 0:
                return inflection[0]

            page = self.word_page(word)

            table = self.find_table(page, language)
            if table:
                return word

            page = self.find_page_language(page, language)

            try:
                page = page.findNext("ol")
                links = page.findAll("a")
            except AttributeError:
                pass
            else:
                links = {link.text for link in links}
                for base_form in links:
                    if 0 < len(base_form) <= len(word) and base_form != word:
                        form_chars = set(base_form)
                        if len(form_chars.intersection(word)) > len(form_chars)/2:
                            if self.in_lexicon(base_form, language):
                                print base_form, "IS LEMMA OF INFLECTION", word
                                return self.lemmatize(base_form, language)

        return word

    def find_lemmas(self, word, language=None):
        """
        Returns the lemmas for this word in this language.
        ~
        e.g. lemmatize("driven", "English") -> ["drive", "driven"]

        :param word: str, word to find lemmas for
        :param language: str, language of given word
        :return: List[str], lemmas for given word
        """
        if len(word) == 0:
            return [word]

        language = self.verify_language(language)
        page = self.word_page(word)
        lemmas = OrderedSet()
        inflections = self.lookup_inflection(word, language)
        ipa = self.page_ipa(page)
        page = self.find_page_language(page, language)

        if ipa:
            return [word]
        elif inflections:
            return inflections
        elif page:
            page = page.findNext("ol")
            links = page.findAll("a")
            links = {link.text for link in links}
            for base_form in links:
                if base_form != word and self.in_lexicon(base_form, language):
                    self.add_inflection(word, base_form, language)
                    lemmas.update(self.find_lemmas(base_form, language))
            return lemmas.items
        else:
            return [word]

    # HOMOPHONES
    # ----------
    def nearest_homophones(self, word, language):
        """
        Returns the nearest homophones in the given language
        to the given word in this IPAParser's native language.

        :param word: str, word in IPAParser's native language
        :param language: str, language of desired output homophones
        :return: List[str], homophones for word in given language
        """
        word_ipas = self.word_to_ipas(word)
        word_ipas = [self.clean_ipa(word_ipa, scrub=True) for word_ipa in word_ipas]
        homophones = list()

        if len(word_ipas) > 0:
            foreign = self.fetch_lang_ipas(language)

            for word_ipa in word_ipas:
                homophone = None

                for fw in foreign:
                    ipas = foreign[fw]

                    if len(ipas) != 0:
                        ipa = ipas[0]
                        if homophone is None:
                            homophone = IPAWord(fw, ipa, self)
                            continue
                        homo = self.nearer_homophone(word_ipa, homophone.ipa, ipa)
                        if homo == ipa:
                            homophone = IPAWord(fw, ipa, self)
                        if word_ipa == ipa:
                            break

                if homophone is not None:
                    homophones.append(homophone.word)

        if len(homophones) == 0:
            homophones.append(None)

        return homophones

    def nearest_homophone(self, word, language):
        """
        Returns the nearest homophone in the given language
        to the given word in this IPAParser's native language.
        ~
        e.g. nearest_homophone("droit", "English") -> "draw"

        :param word: str, word in IPAParser's native language
        :param language: str, language of desired output homophone
        :return: str, homophone for word in given language
        """
        word_ipa = self.word_to_ipa(word)
        homophone = None

        if word_ipa is not None:
            word_ipa = self.clean_ipa(word_ipa, scrub=True)
            foreign = self.fetch_lang_ipas(language)

            for fw in foreign:
                ipas = foreign[fw]

                if len(ipas) != 0:
                    ipa = self.clean_ipa(ipas[0], scrub=True)
                    if homophone is None:
                        homophone = IPAWord(fw, ipa, self)
                        continue
                    if word_ipa == ipa:
                        return fw
                    else:
                        homo = self.nearer_homophone(word_ipa, homophone.ipa, ipa)
                        if homo == ipa:
                            homophone = IPAWord(fw, ipa, self)

            if homophone is not None:
                return homophone.word

        return homophone

    def nearer_homophone(self, ipa, ipa1, ipa2):
        """
        If ipa1 is closer to ipa than ipa2,
        return ipa1.  Otherwise, return ipa2.

        :param ipa: (unicode) str, IPA homophones are trying to be like
        :param ipa1: str, first IPA to compare to ipa
        :param ipa2: str, second IPA to compare to ipa
        :return: str, closest homophone to IPA from ipa1 and ipa2
        """
        if ipa == ipa1 or ipa == ipa2:
            return ipa
        else:
            sim1, sim2 = 20, 20
            ipa_chars = set(ipa)
            elt_diffs = lambda i: len(ipa_chars.symmetric_difference(i))/2.0
            sim1 -= elt_diffs(ipa1)
            sim2 -= elt_diffs(ipa2)
            elt_sims = lambda i: len(ipa_chars.intersection(i))/2.0
            sim1 += elt_sims(ipa1)
            sim2 += elt_sims(ipa2)
            sim1 += self.same_ipas(ipa, ipa1)
            sim2 += self.same_ipas(ipa, ipa2)

            print ipa, "vs", ipa1, ":\t", sim1
            print ipa, "vs", ipa2, ":\t", sim2

            if sim1 >= sim2:
                print "winner:", ipa1
                return ipa1
            else:
                print "winner:", ipa2
                return ipa2

    def same_ipas(self, ipa1, ipa2):
        """
        Returns an integer representing the number of IPA characters
        shared at the same indices by ipa1 and ipa2.

        :param ipa1: str, first string to compare
        :param ipa2: str, second string to compare
        :return: int, number of IPA characters shared by ipa1 and ipa2
        """
        sims = 0
        i = 0

        try:
            while True:
                char1 = ipa1[i]
                char2 = ipa2[i]

                letter1 = self.ipa_to_ipaletter(char1)
                letter2 = self.ipa_to_ipaletter(char2)

                if letter1 is None or letter2 is None:
                    sims += (ipa1[i] == ipa2[i])
                else:
                    add = letter1.compare(letter2)
                    sims += add

                i += 1
        except IndexError:
            pass

        sims -= abs(len(ipa1) - len(ipa2))
        return sims

    # COMMON IPAS/PHONEMES
    # --------------------
    def common_ipas(self, lim=50000):
        """
        Returns a list of the 50,000 most common morphemes
        in this IPAParser's language transcribed to IPA.

        :param lim: int, lim <= 50000, number of IPAs to retreive
        :return: Set(str), most common IPAs in IPAParser's language
        """
        morphemes = self.common_morphemes(lim)
        ipas = set()

        for morpheme in morphemes:
            ipa = self.word_to_ipa(morpheme)
            if ipa is not None:
                ipas.add(ipa)

        self.refresh_json()
        return ipas

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

    def common_ipa_pairs(self, lim=50000, only_top=False):
        """
        Returns a set of common IPA-pos pairs from Wordnet up to lim.
        ~
        If top is True, this method only adds the top IPA pronunciation
        for each word to the list.  Otherwise, adds all IPA pronunciations.

        :param lim: int, lim <= 50000, number of ipa pairs to retrieve
        :param only_top: bool, whether to output only top IPAs or all IPAs
        :return: Set(tuple(str,str)), common ipa pairs in MorphemeParser's language
        """
        word_pairs = self.common_word_pairs(lim)
        ipa_pairs = set()

        for word, pos in word_pairs:
            print
            print word
            ipas = self.word_to_ipas(word)
            if len(ipas) > 0:
                for ipa in ipas:
                    pair = (ipa, pos)
                    ipa_pairs.add(pair)
                    self.add_ipa(word, ipa)
                    if only_top:
                        break
            else:
                self.add_ipa(word, None)

        self.refresh_json()
        return ipa_pairs

    # IPA/PHONEME MANIPULATION
    # ------------------------
    def word_to_ipa(self, word, language=None):
        """
        Transcribes the given word to IPA.  Returns this word's
        IPA pronunciation and adds its transcription to the given
        language's IPA dictionary.

        :param word: str, word to transcribe to IPA
        :param language: str, word's language
        :return: (unicode) str, IPA transcription of word
        """
        if len(word) != 0:
            language = self.verify_language(language)
            word = self.unicodize(word)

            ipa_entry = self.lookup_word_ipa(word, language)
            if ipa_entry is not None:
                return ipa_entry

            etymology = self.lookup_etymology(word, language)
            if etymology is not None:
                ipas = [self.word_to_ipa(etym) for etym in etymology]
                if None not in ipas:
                    return "".join(ipas)

            page = self.word_page(word)
            ipa = self.page_ipa(page, language)

            if ipa is not None:
                self.add_ipa(word, ipa, language)
                return ipa
            else:
                etymology = self.page_etymology(page, self.language)
                if etymology:
                    etyms = etymology.split(" + ")
                    self.add_etymologies(word, etyms)
                    ipas = [self.word_to_ipa(etym) for etym in etyms]
                    if None not in ipas:
                        ipa = "".join(ipas)
                        self.add_ipa(word, ipa, language)
                        return ipa

                lemma = self.lemmatize(word)
                if lemma == word or not self.in_lexicon(lemma, language):
                    return ipa
                else:
                    self.add_inflection(word, lemma, language)
                    return self.word_to_ipa(lemma, language)

    def word_to_ipas(self, word, language=None):
        """
        Transcribes the given word to IPAs.

        :param word: str, word to transcribe to IPA
        :param language: str, word's language
        :return: List[(unicode) str], IPA transcriptions of word
        """
        if len(word) == 0:
            return list()

        language = self.verify_language(language)
        word = self.unicodize(word)
        ipas = self.lookup_word_ipas(word, language)

        if len(ipas) > 0:
            return ipas
        else:
            parsed_url = self.word_page(word)
            ipas = OrderedSet(self.page_ipas(parsed_url))

            if len(ipas) == 0:
                lemma = self.lemmatize(word)
                if lemma != word and self.in_lexicon(lemma, language):
                    self.add_inflection(word, lemma, language)
                    return self.word_to_ipas(lemma, language)
                else:
                    return list()
            else:
                ipas = [subipa.strip() for ipa in ipas.items for subipa in ipa.split(",")]
                self.add_ipas(word, ipas, language)
                return ipas

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

    def parse_declension(self, table):
        """
        Returns a declension dictionary for the given table.
        ~
        If table has multiple columns or rows, this method adds
        all column/row names in a tuple.

        :param table: Tag, BeautifulSoup table
        :return: dict[str, dict], where...
            key (str) - declension column (i.e., plural or sing.)
            val (dict[str, list]) - declension row (e.g., nominative) &
                list of words for given row & column
        """
        coords = self.table_dict(table)
        declension = dict()
        line_text = lambda line: " > ".join([l.lower().replace(" ", "_") for l in line])

        for coord in sorted(coords):
            cell = coords[coord]
            if self.is_content(cell):
                row = self.cell_rows(coord, coords)
                col = self.cell_cols(coord, coords)
                row_text = line_text(row)
                col_text = line_text(col)
                entry = self.cell_entry(cell)
                if len(entry) > 0:
                    declension.setdefault(col_text, dict())
                    declension[col_text].setdefault(row_text, list())
                    declension[col_text][row_text] += entry

        for d in sorted(declension):
            print d, ":"
            value = declension[d]

            for val in sorted(value):
                v = value[val]
                print "\t", val, v

        return declension

    def declension_words(self, table):
        """
        Returns a list of all declension words in the given table.

        :param table: Tag, BeautifulSoup table
        :return: List[str], all declension words in given table
        """
        return [self.clean_etymology(cell.prettify()) for cell in self.table_cells(table)]

    def word_declension(self, word, language=None):
        """
        Returns the declension for the word in the given language.
        ~
        A declension is a dictionary of word inflections, with the
        word lemma as the head and each type of inflection as a
        different key-value pair.

        :param word: str, word to find declension for
        :param language: str, language of declension
        :return: dict[], where...
            key (str) - declension type (e.g. nominative)
            val (List[str]) - all word's inflections for given type
        """
        print word
        word = self.unicodize(word)
        declension = self.lookup_declension(word, language)

        if declension is not None:
            return declension
        else:
            page = self.word_page(word)
            page_lang = self.find_page_language(page, language)

            if page_lang is not None:
                table = self.find_table(page)

                if table is None:
                    lemma = self.lemmatize(word, language)
                    if lemma != word:
                        return self.word_declension(lemma, language)
                    else:
                        return dict()
                else:
                    inflections = self.declension_words(table)
                    declension = self.parse_declension(table)
                    self.add_inflections(inflections, word, language)
                    self.add_declension(word, declension, language)
                    return declension

    def words_declensions(self, words, language=None):
        """
        Returns a list of declension dictionaries for each
        word (in the given language) in words.

        :param words: List[str], words to retrieve declensions for
        :param language: str, language of given words
        :return: List[dict], declension dictionaries for all words
        """
        declensions = []
        for word in words:
            declension = self.word_declension(word, language)
            if declension is not None:
                declensions.append(declension)
        return declensions

    def ipa_to_ipaletter(self, ipa):
        try:
            return IPALETTERS[ipa]
        except KeyError:
            return

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
            phoneme_dict = ipa_word.find_phoneme_dict()
            self.phoneme_dict = self.merge_dicts(self.phoneme_dict, phoneme_dict)

        return self.phoneme_dict

    def all_ipa_words(self):
        """
        Returns a set of IPAWords corresponding to all
        Wiktionary entries in this IPAParser's language.

        :return: Set(IPAWord), all IPAWords in this IPAParser's language
        """
        pages = self.all_page_defns()
        transcriptions = self.words_to_ipawords(pages)
        return transcriptions

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

    # VOWELS, CONSONANTS, & PHONEMES
    # ------------------------------
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

    def is_letter_phoneme(self, chars):
        """
        Returns True if the given chars is a phoneme in this
        IPAWord's native language, False otherwise.
        ~
        Returns None if this chars is not in this IPAParser's phoneme_dict.
        ~
        N.B. chars can be multiple letters long.

        :param chars: (unicode) str, character(s) to determine whether phoneme
        :return: bool, whether given character(s) are a phoneme
        """
        return chars in self.phoneme_dict

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
                ipa_phonemes = self.phoneme_dict.keys()
                if len(ipa_phonemes) == 0:
                    return
                elif ipa in ipa_phonemes:
                    return any(self.is_ipa_vowel(sym) for sym in ipa if sym in IPALETTERS)
            else:
                return
        else:
            return ipa_sym.is_vowel

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

