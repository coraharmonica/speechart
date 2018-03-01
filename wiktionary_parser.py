# coding: utf-8
"""
WIKTIONARY_PARSER:

    Contains WiktionaryParser class for parsing Wiktionary entries in any language.
"""
import os
import re
import string
import requests
from BeautifulSoup import BeautifulSoup
from ipa_symbols import *


class WiktionaryParser:
    PATH = os.path.dirname(os.path.realpath(__file__))
    LANG_CODES = {"Afrikaans": "af",
                  "Albanian": 'sq',
                  "Arabic": "ar",
                  "Armenian": "hy",
                  "Basque": 'eu',
                  "Bengali": "bn",
                  "Bosnian": 'bs',
                  "Breton": 'br',
                  "Bulgarian": 'bg',
                  "Catalan": 'ca',
                  "Chinese": "zh",
                  "Croatian": 'hr',
                  "Danish": 'da',
                  "Dutch": 'nl',
                  "English": 'en',
                  "Esperanto": 'eo',
                  "Georgian": 'ka',
                  "German": 'de',
                  "Greek": 'el',
                  "Finnish": 'fi',
                  "French": 'fr',
                  "Galician": 'gl',
                  "Hebrew": 'he',
                  "Hindi": 'hi',
                  "Hungarian": "hu",
                  "Icelandic": 'is',
                  "Indonesian": 'id',
                  "Italian": 'it',
                  "Japanese": 'ja',
                  "Kazakh": 'kk',
                  "Korean": 'ko',
                  "Latvian": "lv",
                  "Lithuanian": "lt",
                  "Macedonian": "mk",
                  "Malayan": "ml",
                  "Malay": "ms",
                  "Norwegian": 'no',
                  "Persian": 'fa',
                  "Polish": 'pl',
                  "Portuguese": 'pt',
                  "Romanian": 'ro',
                  "Russian": 'ru',
                  "Serbian": 'sr',
                  "Sinhala": 'si',
                  "Slovak": 'sk',
                  "Slovenian": 'sl',
                  "Spanish": 'es',
                  "Swedish": 'sv',
                  "Tamil": 'ta',
                  "Telugu": 'te',
                  "Thai": 'th',
                  "Tagalog": 'tl',
                  "Turkish": 'tr',
                  "Ukrainian": 'uk',
                  "Vietnamese": 'vi'}
    LEMMA_TYPES = {"Noun": 1, "Verb": 2, "Adjective": 3, "Adverb": 4, "Preposition": 5,
                   "Conjunction": 6, "Interjection": 7, "Morpheme": 8, "Pronoun": 9,
                   "Phrase": 10, "Numeral": 11, "Particle": 12, "Participle": 13,
                   "Prefix": 14, "Suffix": 15, "Circumfix": 16, "Interfix": 17, "Infix": 18}
    WIKI_URL = "https://en.wiktionary.org"
    END_URL = "/w/index.php?title=Category:%s"
    BASE_URL = WIKI_URL + "/wiki/%s#%s"
    IPA_URL = "_terms_with_IPA_pronunciation&from="
    LEMMA_URL = "_lemmas"

    def __init__(self):
        self.session = requests.session()
        self.url = self.WIKI_URL + self.END_URL
        self.language = None

        # REGEXES
        self.html_pattern = re.compile("(<.+?>|\n)") # used to include |\d
        self.quote_pattern = re.compile("\"[^\+]*?\"")
        self.paren_pattern = re.compile("\([^\(]*?\)")
        self.deriv_pattern = re.compile("(\S+ ?(\".+\")? ?\+ ?)+\S+ ?(\".+?\")?")
        self.space_pattern = re.compile("( )+")

    def verify_language(self, language):
        """
        If given language is None, returns self.language.
        Otherwise, returns given language.

        :param language: str, language to verify
        :return: str, verified language
        """
        if language is None:
            return self.language
        else:
            return language

    def get_lang_code(self, language=None):
        """
        Returns the language code associated with the given language.
        ~
        e.g. get_lang_code("Polish") -> "pl"

        :param language: str, language to retrieve language code for
        :return: str, language code for given language
        """
        language = self.verify_language(language)
        return self.LANG_CODES.get(language, None)

    # PAGE RETRIEVAL
    # --------------
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

    def word_page(self, word):
        """
        Returns a BeautifulSoup Tag corresponding to the Wiktionary
        page for the given word.

        :param word: str, word to retrieve page for
        :return: Tag, BeautifulSoup tag matching given word's page
        """
        return self.parse_url(self.word_url(word))

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

    # PAGE PARSING
    # ------------
    def find_page_language(self, page, language=None):
        """
        Returns the subset of the given BeautifulSoup Tag page in
        the given language.

        :param page: Tag, page to return language section from
        :param language: str, desired language section from page
        :return: Tag, child of page in this IPAParser's language
        """
        language = self.verify_language(language)
        headers = page.findAll("h2")

        for header in headers:
            text = header.getText()
            if language in text:
                break
        else:
            return

        curr_tag = header.nextSibling
        next_sibling = curr_tag.nextSiblingGenerator()
        children = []

        while not (getattr(curr_tag, 'name', False) == "h2"):
            if curr_tag is not None:
                tag_str = str(curr_tag)
                if tag_str[:4] == "<!--":
                    break
                children.append(str(curr_tag))
            try:
                curr_tag = next(next_sibling)
            except StopIteration:
                break

        html = "".join(children)
        pg = BeautifulSoup(html)
        return pg

    def page_etymologies(self, page, language=None, derivational=True):
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
        :param derivational: bool, whether to only extract derivational etymologies
        :return: List[str], etymologies for given page
        """
        language = self.verify_language(language)
        pg = self.find_page_language(page, language)
        etymologies = list()

        if pg is not None:
            headers = pg.findAll(['h3', 'h4', 'h5'])
            paras = [header.findNext('p') for header in headers
                     if getattr(header, 'text', '')[:4] == "Etym"]

            for para in paras:
                if para is not None:
                    if derivational:
                        etym = self.tag_etymology(para, language)
                    else:
                        etym = self.clean_spaces(self.clean_parentheticals(para.getText(' ')))

                    etymologies.append(etym)

        return etymologies

    def page_etymology(self, page, language=None, derivational=True):
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
        :param language: str, language of etymology
        :param derivational: bool, whether to only extract derivational etymologies
        :return: str, etymology for given page
        """
        etyms = self.page_etymologies(page, language, derivational)

        try:
            return etyms[0]
        except IndexError:
            return

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

    def find_page_languages(self, page):
        """
        Returns a list of the given page's languages.

        :param page: Tag, page to return languages from
        :return: List[str], all languages on this page
        """
        headers = page.findAll("h2")
        langs = [header.getText()[:-6] for header in headers[1:-1]]
        return langs

    def page_ipa(self, page, language=None):
        """
        Returns IPA pronunciation in the given language from the given
        BeautifulSoup Tag page.
        ~
        This method finds the first pronunciation that does not begin
        with a dash (which denotes a rhyme ending rather than the word).
        ~
        If no IPA pronunciation exists on the given page, returns None.

        :param page: Tag, page to find pronunciation from
        :param language: str, language of IPA to find
        :return: (unicode) str, IPA pronunciation from given URL
        """
        language = self.verify_language(language)
        ipas = self.page_ipas(page, language)
        if len(ipas) > 0:
            return ipas[0]

    def page_ipas(self, page, language=None):
        """
        Returns all IPA pronunciations in the given language from the given
        BeautifulSoup Tag page.
        ~
        This method finds the all pronunciations that do not begin
        with a dash (which denotes a rhyme ending rather than the word).

        :param page: Tag, page to find pronunciations from
        :param language: str, language of IPAs
        :return: List[(unicode) str], IPA pronunciations from given URL
        """
        language = self.verify_language(language)
        pg = self.find_page_language(page, language)
        ipas = list()
        clean = lambda h: self.ipaize(self.remove_superscripts(h).getText().split(u"→")[0])

        if pg is not None:
            headers = pg.findAll("span", attrs={"class": "IPA"})
            ipas = [clean(header) for header in headers if header.getText()[0] != "-"]

        return ipas

    def page_pos(self, page, language=None):
        """
        Returns part of speech from given BeautifulSoup Tag page.

        :param page: Tag, page to find part of speech from
        :param language: str, language of part of speech
        :return: str, part of speech from given URL
        """
        language = self.verify_language(language)
        return self.page_poses(page, language)[0]

    def page_poses(self, page, language=None):
        """
        Returns parts of speech in given language from given BeautifulSoup Tag page.

        :param page: Tag, page to find parts of speech from
        :param language: str, language of parts of speech
        :return: List[str], parts of speech from given URL
        """
        language = self.verify_language(language)
        pg = self.find_page_language(page, language)
        poses = list()

        if pg is not None:  # given page has section in language
            headers = pg.findAll(['h3', 'h4', 'h5'])

            for header in headers:
                header_text = header.getText()[:-6]

                if header_text in self.LEMMA_TYPES:
                    poses.append(header_text)

        return poses

    # ETYMOLOGIES
    # -----------
    def word_etymology(self, word, language=None, derivational=True):
        """
        Returns the etymology of the given word in this
        language (according to Wiktionary).

        :param word: str, word to find etymology of
        :param language: str, language of etymology
        :param derivational: bool, whether to only extract derivational etymologies
        :return: str, word's etymology
        """
        language = self.verify_language(language)
        parsed_url = self.word_page(word)
        etymology = self.page_etymology(parsed_url, language, derivational)
        return etymology

    def word_etymologies(self, word):
        """
        Returns all etymologies for the given word
        (according to Wiktionary), irrespective of
        language.

        :param word: str, word to find etymologies of
        :return: List[str], word's etymologies
        """
        parsed_url = self.word_page(word)
        etymologies = self.page_etymologies(parsed_url)
        return etymologies

    def words_etymologies(self, words, language=None, derivational=True):
        """
        Returns a dictionary of each word in words and its corresponding
        etymology in the given language (according to Wiktionary).
        ~
        If derivational is set to True, this method only adds derivational
        (excluding descriptive) etymologies.

        :param words: Iterable[str], list of words to lookup etymologies for
        :param language: str, language of etymologies
        :param strict: bool, whether to only add purely derivational etymologies
        :return: dict, where...
            key (str) - word with etymology
            val (str) - given word's etymology
        """
        language = self.verify_language(language)
        etymologies = dict()

        for word in words:
            etymology = self.word_etymology(word, language, derivational)
            if etymology is not None:
                if derivational:
                    etymologies[word] = etymology.split(" + ")
                else:
                    etymologies[word] = etymology

        return etymologies

    def tag_etymology(self, tag, language=None):
        """
        Returns the etymology of a word from the given tag for
        the given language.

        :param tag: Tag, BeautifulSoup tag to find etymology from
        :param language: str, language of etymology to find
        :return: str, a word's etymology from given description
        """
        language = self.verify_language(language)
        etym_tags = tag.findAll("i", attrs={"lang": self.get_lang_code(language)})
        etyms = [etym_tag.text for etym_tag in etym_tags]
        etym = " + ".join(etyms)
        return etym

    # TABLES
    # ------
    def is_header(self, cell):
        """
        Returns True if the given cell is a (row or column) header,
        False otherwise.

        :param cell: Tag, BeautifulSoup cell in table to check if header
        :return: bool, whether given cell is a (row or column) header
        """
        return False if cell is None else cell.name == "th"

    def is_content(self, cell):
        """
        Returns True if the given cell is a cell containing content,
        False otherwise.

        :param cell: Tag, BeautifulSoup cell in table to check if content
        :return: bool, whether given cell contains content
        """
        # if cell begins w/ superscript, it's not content
        try:
            next = cell.contents[0]
            next_name = next.name
        except (IndexError, AttributeError):
            next = cell
            next_name = next.name

        return False if cell is None else (cell.name == "td" and next_name != "sup" and cell.find("p") is None)

    def cell_text(self, cell):
        """
        Returns the given cell (from a table)'s text.

        :param cell: Tag, BeautifulSoup Tag to get text from
        :return: str, given cell's text
        """
        try:
            self.remove_superscripts(cell)
            spans = cell.findAll("span")
            if len(spans) == 0:
                text = cell.getText(" ")
            else:
                spans_text = [span.getText(" ") for span in spans]
                text = "\n".join(spans_text)
            cleaned = self.clean_text(text.replace(" , ", ","))
            return cleaned
        except AttributeError:
            return ""

    def cell_entry(self, cell):
        """
        Returns a list of the words in the given cell (from a table).

        :param cell: Tag, BeautifulSoup tag to retrieve entry from
        :return: List[str], list of words in given cell
        """
        text = self.cell_text(cell)

        if len(text) != 0:
            delimiters = re.compile("[,/\n]")
            entry = [e.strip() for e in delimiters.split(text)]
            return entry
        else:
            return list()

    def cell_rows(self, coord, table_dict):
        """
        Returns a tuple of the given coordinate
        (from the given table, table_dict)'s row names.

        :param coord: Tuple(int, int), coordinate to get row names for
        :param table_dict: dict[tuple, Tag], where...
            key (Tuple[int, int]) - given table's row and column number
            val (Tag) - cell for given row and column
        :return: Tuple(str), given cell's row names
        """
        row_num, col_num = coord
        prev_rows = [c for c in sorted(table_dict) if c[0] == row_num
                     and c[1] < col_num]

        rows = []
        header_yet = False

        for row_coord in reversed(prev_rows):
            cell = table_dict[row_coord]
            if self.is_header(cell):
                header_yet = True
                text = self.cell_text(cell)
                if text not in rows:
                    rows.insert(0, text)
            elif header_yet:
                break

        return tuple(rows)

    def cell_cols(self, coord, table_dict):
        """
        Returns a tuple of the given coordinate
        (from the given table, table_dict)'s column names.

        :param coord: Tuple(int, int), coordinate to get row names for
        :param table_dict: dict[tuple, Tag], where...
            key (Tuple[int, int]) - given table's row and column number
            val (Tag) - cell for given row and column
        :return: Tuple(str), given cell's column names
        """
        row_num, col_num = coord
        prev_cols = [c for c in sorted(table_dict) if c[1] == col_num
                     and c[0] < row_num]

        cols = []
        header_yet = False

        for col_coord in reversed(prev_cols):
            cell = table_dict[col_coord]
            if self.is_header(cell):
                header_yet = True
                text = self.cell_text(cell)
                cols.insert(0, text)
            elif header_yet:
                break

        return tuple(cols)

    def is_table_declension(self, table, language):
        """
        Returns True if this table is a declension in the given language,
        False otherwise.

        :param table: Tag, Tag, BeautifulSoup tag for HTML table
        :param language: str, language of table
        :return: bool, whether given table is declension
        """
        #language = self.verify_language(language)
        prev_header = table.findPrevious("h4")

        if prev_header is None:
            return
        else:
            cells = self.table_cells(table)
            links = [cell.find("a") for cell in cells if cell.find("a") is not None]
            hrefs = [link.get("href") for link in links if link.get("href") is not None]
            all_langs = all([href[-len(language):] == language or
                             href[-21:] == "action=edit&redlink=1" for href in hrefs])
            header_text = prev_header.getText(" ")
            is_declension = False if prev_header is None else (u"Declension" in header_text) or \
                                                              (u"Conjugation" in header_text)
            return is_declension and all_langs

    def find_table(self, page, language=None):
        """
        Returns the first table on the given page in the given language.
        ~
        If language is None, returns the first table on the given page
        (regardless of language).

        :param page: Tag, BeautifulSoup tag to extract table from
        :param language: str, language of table
        :return: Tag, BeautifulSoup tag for table on page in language
        """
        if language is not None:
            page = self.find_page_language(page, language)
        else:
            language = self.verify_language(language)

        try:
            tables = page.findAll("table")
        except AttributeError:
            return

        for table in tables:
            if self.is_table_declension(table, language):
                return table
        else:
            return

    def table_cells(self, table):
        """
        Returns all (content) cells from the given table.

        :param table: Tag, BeautifulSoup tag for an HTML table
        :return: List[Tag], tags for all cells in given table
        """
        return [cell for cell in table.findAll("td") if self.is_content(cell)]

    def table_rows(self, table):
        """
        Returns the given table separated into rows.

        :param table: Tag, BeautifulSoup tag to get rows of
        :return: List[Tag], rows of given table
        """
        lines = table.findAll("tr", attrs={"class": "vsHide"})
        if len(lines) != 0:
            return lines
        else:
            return table.findAll("tr")

    def table_dict(self, table):
        """
        Returns a dictionary representing the given table Tag.

        :param table: Tag, BeautifulSoup tag for an HTML table
        :return: dict[tuple, Tag], where...
            key (tuple[int, int]) - given table's row and column number
            val (Tag) - cell for given row and column
        """
        table_dict = dict()

        if table is not None:
            lines = self.table_rows(table)
            num_rows = len(lines)
            num_cols = self.num_cols(table)
            row_iter = iter(range(num_rows))

            for r in row_iter:
                row = lines[r]
                cells = row.findAll(["th", "td"])
                cells_iter = iter(cells)
                col_iter = iter(range(num_cols))

                for c in col_iter:
                    coord = r, c
                    try:
                        cell = cells_iter.next()
                    except StopIteration:
                        continue

                    while coord in table_dict:
                        try:
                            col_iter.next()
                            c += 1
                        except StopIteration:
                            try:
                                row_iter.next()
                                r += 1
                            except StopIteration:
                                break

                        coord = r, c
                    else:
                        make_int = lambda x: 1 if x is None else int(x)
                        rowspan = make_int(cell.get("rowspan"))
                        colspan = make_int(cell.get("colspan"))

                        if colspan != 1 or rowspan != 1:
                            rs = 0

                            while rs < rowspan:
                                coord = r + rs, c
                                table_dict[coord] = cell
                                cs = 1

                                while cs < colspan:
                                    coord = r + rs, c + cs
                                    table_dict[coord] = cell
                                    cs += 1
                                rs += 1

                            for i in range(1, colspan):
                                col_iter.next()

                            continue
                        else:
                            table_dict[coord] = cell

        self.visualize_declension(table_dict)
        return table_dict

    def num_cols(self, table):
        """
        Returns the number of columns in the given HTML table.

        :param table: Tag, BeautifulSoup table in HTML from webpage
        :return: int, number of columns in given table
        """
        num_cols = 0
        col1 = table.find("tr")             # 1st row
        cells = col1.findAll(["th", "td"])  # all headers/cells in 1st row
        make_int = lambda x: 1 if x is None else int(x)

        for cell in cells:
            colspan = make_int(cell.get("colspan"))
            num_cols += colspan

        return num_cols

    def visualize_declension(self, declension):
        """
        Prints the given declension to the user as a table.

        :param declension: dict[tuple], row-col int keys with cell values
        :return: None
        """
        bold = '\033[1m'
        end = '\033[0m'

        add_spaces = lambda s, n: s + (" " * n)
        col_width = min(30, len(max(declension.values(), key=lambda v: len(v.text)).text)) + 5

        print "Declension:\n"
        col_intro = " "*(col_width - 5)
        col_space = " "*col_width
        max_col = max(declension, key=lambda d: d[1])[1]
        print col_intro, col_space.join([str(i) for i in range(max_col + 1)])

        for coord in sorted(declension):
            x, y = coord
            if y == 0:
                print
                print bold, coord[0], end, "\t\t\t",
            val = declension[coord]
            is_header = self.is_header(val)
            text = self.clean_text(val.getText(" "))
            offset = col_width - len(text)
            if is_header:
                text = bold + text + end
            print add_spaces(text, offset),
        print

    # TEXT CLEANUP / HELPERS
    # ----------------------
    def clean(self, s):
        """
        Returns s in unicode with \xe2\x80\x8e removed.

        :param s: str, string to clean
        :return: (unicode) str, s cleaned
        """
        return self.unicodize(s.replace("‎", ""))

    def clean_etymology(self, etymology):
        """
        Returns etymology fully cleaned, i.e., without
        HTML, parentheticals, duplicate spaces or irregular characters.

        :param etymology: str, etymology to clean
        :return: str, etymology cleaned
        """
        return self.clean_spaces(self.clean_parentheticals(self.clean_quotes(self.clean_html(self.clean(etymology)))))

    def clean_text(self, text):
        return self.clean_spaces(re.sub("&.{3,4};", " ", text))

    def clean_ipa(self, ipa, scrub=False):
        """
        Returns the given IPA pronunciation with stress marks,
        syllable markers, and parentheses removed.
        ~
        If scrub is True, clean_ipa() also removes given ipa's diacritics.

        :param ipa: (unicode) str, IPA to remove stress/syllable marks from
        :param scrub: bool, whether to also remove diacritics
        :return: (unicode) str, given ipa with stress/syllable marks removed
        """
        cleaned = re.sub(u"[ˈˌ.]", u"", self.clean_word(ipa))
        if scrub:
            cleaned = self.remove_diacritics(cleaned)
        return cleaned

    def clean_word(self, word):
        """
        Returns the given word in lowercase and with punctuation and
        whitespace removed.

        :param word: (unicode) str, word to clean
        :return: (unicode) str, cleaned word
        """
        return re.sub("[" + string.punctuation + "]", u"", word.lower())

    def clean_header(self, header):
        return self.clean_text(header).split("[", 1)[0].strip()

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

    def ipaize(self, s):
        return u"".join([char for char in s if char in IPASYMBOLS or char in ", "])

    def remove_digits(self, s):
        return u"".join([char for char in s if not char.isdigit() and char not in u"⁻⁽⁾"])

    def remove_parens(self, word):
        """
        Returns the given word with parentheses removed.

        :param word: (unicode) str, word to remove parentheses from
        :return: (unicode) str, word with parentheses removed
        """
        return re.sub("\(|\)", "", word)

    def remove_superscripts(self, tag):
        """
        Removes all superscript tags from the given BeautifulSoup Tag.

        :param tag: Tag, BeautifulSoup tag to remove superscripts from
        :return: Tag, tag with superscripts removed
        """
        try:
            tag.sup.decompose()
        except AttributeError:
            pass
        return tag

    def remove_diacritics(self, ipa):
        """
        Returns the given IPA pronunciation with diacritics removed.

        :param ipa: (unicode) str, IPA to remove stress/syllable marks from
        :return: (unicode) str, given ipa with stress/syllable marks removed
        """
        return "".join([c for c in ipa if c not in IPADIACRITICS])

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
                text = text.decode("utf-8")
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

    def fill_list(self, lst, limit, item=None):
        """
        Adds item to given list until it reaches length limit.

        :param lst: List[X], list to fill with item
        :param limit: int, desired length of list
        :param item: X, item to fill list with
        :return: List[X], original list with item added until limit
        """
        return self.add_item(lst, limit - len(lst), item)

    def add_item(self, lst, times, item=None):
        """
        Adds the given item to the given list the given number of times.
        ~
        e.g. add_item([1,2,3], 2) -> [1,2,3,None,None]

        :param lst: List[X], list to add item to repeatedly
        :param times: int, number of times to add item
        :param item: X, item to add to given lst
        :return: List[X], lst with item added up to times
        """
        lst += [item] * times
        return lst

    def safe_execute(self, default, exception, function, *args):
        """
        Returns the result of the given function with the given arguments.
        If exception is raised, return default.

        :param default: Any, default value to return if exception
        :param exception: Exception, exception to catch
        :param function: function, function to safely execute
        :param args: Any, arguments of given function to execute
        :return: Any, output of given function or default if exception
        """
        try:
            return function(*args)
        except exception:
            return default

