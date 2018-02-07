# coding: utf-8
"""
MORPHEME_PARSER:

    Stores classes for extracting and analyzing morphemes.
    ~
    Designed for (ideally) any language.
"""
from ipa_parser import *
import re
import os

PATH = os.path.dirname(os.path.realpath(__file__))


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


class MorphemeParser(IPAParser):
    """
    A class for extracting and analyzing morphemes in a
    given language.
    """
    def __init__(self, language):
        IPAParser.__init__(self, language)
        self.wordnet_words = self.get_wordnet_words()
        self.lexicon = self.get_lexicon()
        self.words = self.wordnet_words.intersection(self.lexicon[:1000])
        self.affixes = set()
        self.morphemes = set()
        self.html_pattern = re.compile("(<.+?>|\n|\d)")
        self.quote_pattern = re.compile("\"[^\+]*?\"")
        self.paren_pattern = re.compile("\([^\(]*?\)")
        self.deriv_pattern = re.compile("(\S+ ?(\".+\")? ?\+ ?)+\S+ ?(\".+?\")?")
        self.space_pattern = re.compile("( )+")

    def clean(self, s):
        """
        Returns s with \xe2\x80\x8e removed.

        :param s: str, string to clean
        :return: str, s cleaned
        """
        return s.replace("‎", "")

    def clean_etymology(self, etymology):
        """
        Returns etymology fully cleaned, i.e., without
        HTML, parentheticals, duplicate spaces or irregular characters.

        :param etymology: str, etymology to clean
        :return: str, etymology cleaned
        """
        return self.clean_spaces(self.clean_parentheticals(self.clean_quotes(self.clean_html(self.clean(etymology)))))

    def clean_spaces(self, s):
        """
        Returns s with no more than 1 consecutive space and with
        whitespace stripped from ends.
        ~
        e.g. clean_spaces("  how  are   you  ") -> "how are you"

        :param s: str, string with spaces to clean
        :return: str, s cleaned
        """
        return self.space_pattern.sub(" ", s).strip()

    def clean_html(self, html):
        """
        Removes all HTML gunk from the given etymology string.

        :param html: str, HTML string to remove HTML gunk from
        :return: str, html without HTML gunk
        """
        return self.html_pattern.sub("", html)

    def clean_parentheticals(self, s):
        """
        Returns s with all parentheticals removed.
        ~
        e.g. clean_parentheticals("cat (noun) - animal") -> "cat - animal"

        :param s: str, string to remove parentheticals frosm
        :return: str, s without parentheticals
        """
        last = s
        new = self.paren_pattern.sub("", s)
        while last != new:
            last = new
            new = self.paren_pattern.sub("", new)
        return new

    def clean_quotes(self, s):
        """
        Returns s with all quotes removed.
        ~
        e.g. clean_parentheticals("cat ("cat")") -> "cat ()"

        :param s: str, string to remove parentheticals from
        :return: str, s without parentheticals
        """
        return self.quote_pattern.sub("", s)

    def description_etymology(self, description):
        """
        Returns the etymology of a word from the given description.

        :param description: str, description to find etymology from
        :return: str, a word's etymology from given description
        """
        '''
        etymologies = description.split("valent to ")

        if len(etymologies) > 1:
            etymology = etymologies[-1]
            etymology = etymology.split(".", 1)[0]
            etymology = etymology.split(",", 1)[0]
            etymology = etymology.split(";", 1)[0]
        else:
        '''
        if description[:5] == "From ":
            description = description[5:]

        etymology = self.deriv_pattern.match(description)

        #if etymology is None:
        #    etymology = self.deriv_pattern.search(description)

        etymology = etymology.group()

        try:
            etymology = etymology.rstrip(" .")
        except AttributeError:
            pass

        return etymology.strip()

    def page_etymologies(self, page, derivations=True):
        """
        Returns all etymologies from this Wiktionary page.
        ~
        If no etymology exists, returns None.
        ~
        If derivations is False, this method returns the given page's
        etymology no matter what.
        Otherwise, if derivations is True, this method returns this
        page's etymology only if it is derivational (i.e., consisting
        only of additive morphemes).

        :param page: Tag, page to extract etymology from
        :param derivations: bool, whether to only extract derivational etymologies
        :return: List[str], etymologies for given page
        """
        etymologies = list()

        try:
            headers = page.findAll('span', attrs={'class': 'mw-headline'})
            etyms = [h.findNext('p') for h in headers
                     if h['id'][:4] == "Etym"]

            for etym in etyms:
                etym = self.clean_parentheticals(self.clean_html(etym.prettify()))
                if derivations:
                    if any(char.isupper() or char == "." for char in etym):
                        continue
                etymologies.append(etym)

        except AttributeError or TypeError:
            return

        return etymologies

    def page_etymology(self, page, derivational=True):
        """
        Returns the etymology from this Wiktionary page belonging to this
        MorphemeParser's language.
        ~
        If no etymology exists, returns None.
        ~
        If derivational is False, this method returns the given page's
        etymology no matter what.
        Otherwise, if derivational is True, this method returns this
        page's etymology only if it is derivational (i.e., consisting
        only of additive morphemes).

        :param page: Tag, page to extract etymology from
        :param derivational: bool, whether to only extract derivational etymologies
        :return: str, etymology for given page
        """
        etymology = self.find_page_language(page)

        try:
            while etymology['id'][:4] != 'Etym':
                etymology = etymology.findNext('span', attrs={'class': "mw-headline"})
            etymology = etymology.findNext('p')
            etymology = self.clean_etymology(etymology.prettify())
            if derivational:
                etymology = self.description_etymology(etymology)

        except AttributeError:
            return
        except TypeError:
            return

        return etymology

    def word_etymology(self, word, derivational=True):
        """
        Returns the etymology of the given word in this
        MorphemeParser's language (according to Wiktionary).

        :param word: str, word to find etymology of
        :param derivational: bool, whether to only extract derivational etymologies
        :return: str, word's etymology
        """
        base_url = self.WIKI_URL + "/wiki/%s"
        url = base_url % word
        parsed_url = self.parse_url(url)
        etymology = self.page_etymology(parsed_url, derivational)
        return etymology

    def word_etymologies(self, word):
        """
        Returns all etymologies for the given word
        (according to Wiktionary).

        :param word: str, word to find etymologies of
        :return: List[str], word's etymologies
        """
        base_url = self.WIKI_URL + "/wiki/%s"
        url = base_url % word
        parsed_url = self.parse_url(url)
        etymologies = self.page_etymologies(parsed_url)
        return etymologies

    def words_etymologies(self, words, strict=True):
        """
        Returns a dictionary of each word in words and its corresponding
        etymology (according to Wiktionary).
        ~
        If strict is set to True, this method only adds words whose etymologies
        are purely strict, e.g. happiness -> happy + -ness, but not
        pardon -> per- + donare.

        :param words: Iterable[str], list of words to lookup etymologies for
        :param strict: bool, whether to only add purely derivational etymologies
        :return: dict, where...
            key (str) - word with etymology
            val (str) - given word's etymology
        """
        etymologies = dict()

        for word in words:
            etymology = self.word_etymology(word, derivational=strict)
            if etymology is not None:
                derivations = [e.strip() for e in etymology.split("+")]
                if strict and not self.derivative_word(word, derivations):
                    continue
                #print word, "has the etymology", etymology,
                #print "and morphemes", "+".join(derivations)
                etymologies[word] = derivations
            #else:
                #print word, "has no etymology"
            #print

        return etymologies

    def derivative_word(self, word, derivations):
        """
        Returns True if the given word is derivative
        (i.e., a composite of its derivations), False otherwise.
        ~
        e.g. derivative_word("happiness", ["happy", "-ness"]) -> True
             derivative_word("pardon", ["per-", "donare"]) -> False

        :param word: str, word to determine whether derivative
        :param derivations: List[str], derivations of word
        :return: bool, whether given word is derivative
        """
        derivations = [d.replace("-", "") for d in derivations]
        derivation = "".join(derivations)
        if word == derivation:
            return True
        else:
            return any(d in word for d in derivations) and \
                   len(set(word).difference(derivation)) < 2 and \
                   len(word) in range(len(derivation)-1, len(derivation)+2)

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

    def all_etymologies(self):
        """
        Returns a dictionary of each word in this MorphemeParser's words
        and its corresponding etymology (according to Wiktionary).

        :return: dict, where...
            key (str) - word with etymology
            val (List[str]) - given word's etymology (as a combination of words)
        """
        return self.words_etymologies(self.words)

    def flatten(self, lst):
        """
        Flattens the given list of lists to a list.
        ~
        e.g. flatten([[1, 2], [3, 4]]) -> [1, 2, 3, 4]

        :param derivations: List[List[X]], list of lists to flatten
        :return: List[X], input list flattened
        """
        return [item for sublst in lst for item in sublst]

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

    def get_wordnet_words(self):
        """
        Returns a set of all words in Wordnet.

        :return: Set(str), Wordnet word
        """
        lexicon = self.parse_lexicon(self.language)

        if lexicon is not None:
            return set(lexicon.keys())
        else:
            path = PATH + "/resources/wordnet/wn_s.txt"
            entries = set()

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
        path = PATH + "/resources/wordnet/wn_s.txt"
        entries = set()

        with open(path, "r") as synsets:
            for synset in synsets:
                synset = synset[2:-3]
                info = synset.split(",")
                name = info[2]
                name = name[1:-1]
                pos = info[3]
                if " " not in name:
                    entries.add((name, pos))

        return entries

    def common_word_pairs(self, lim=50000):
        """
        Returns a set of common word-pos pairs, up to lim.

        :param lim: int, number of common words to return
        :return: List[tuple(str, str)], Wordnet word and pos
        """
        common_words = self.common_words(lim)

        if self.language == "English":
            word_pairs = self.get_wordnet_word_pairs()
            return [word_pair for word_pair in word_pairs if word_pair[0] in common_words]
        else:
            poses = self.words_to_poses(common_words)
            word_pairs = list()
            for i in range(len(common_words)):
                word = common_words[i]
                pos = poses[i]
                for p in pos:
                    pair = (word, p)
                    word_pairs.append(pair)
            return word_pairs

    def common_morphemes(self, lim=50000):
        """
        Returns a list of the 50,000 most common words
        in this IPAParser's language, including their
        constituent words.

        :param lim: int, lim <= 50000, number of words to retreive
        :return: List[str], 50k most common words in IPAParser's language
        """
        lexicon = self.lexicon
        common_words = lexicon[:lim]
        all_words = self.wordnet_words.intersection(lexicon).difference(common_words)
        morphemes = common_words[:]

        for word in all_words:
            # catch all derivative words
            if len(word) > 3:
                if any(word == cw[:len(word)] or cw == word[:len(cw)] for cw in common_words if len(cw) > 3):
                    morphemes.append(word)

        return sorted(morphemes)

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

    def common_ipa_pairs(self, lim=50000):
        """
        Returns a set of common word-pos pairs from Wordnet, up to lim,
        with each word transcribed to IPA.

        :param lim: int, lim <= 50000, number of ipa pairs to retreive
        :return: List[str], common ipa pairs in MorphemeParser's language
        """
        word_pairs = self.common_word_pairs(lim)
        ipas = set()

        for word, pos in word_pairs:
            ipa = self.word_to_ipa(word)
            if ipa is not None:
                ipas.add((ipa, pos))
        self.refresh_json()
        return ipas


