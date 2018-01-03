# coding: utf-8
"""
IPA_SYMBOLS:

    Stores classes for categorizing IPA symbols.
"""
from ipa_unicode import *
from enum import Enum


class IPASymbol:

    def __init__(self, symbol):
        self.symbol = symbol

    def get_is_vowel(self):
        return False

class IPACompound(IPASymbol):

    def __init__(self, symbols):
        IPASymbol.__init__(self, symbols)
        self.num_symbols = len(symbols)

    def get_dict(self):
        res = dict()
        res["symbol"] = self.symbol
        return res

    def get_diacritics(self):
        diacritics = "".join([sym for sym in self.symbol if sym in DIACRITICS])
        return diacritics

    def get_letters(self):
        letters = "".join([sym for sym in self.symbol if sym in IPASYMBOLS])
        return letters


class IPADiacritic(IPASymbol):

    def __init__(self, symbol, is_affricate=False):
        IPASymbol.__init__(self, symbol)
        self.is_affricate = is_affricate

    def get_dict(self):
        res = dict()
        res["symbol"] = self.symbol
        res["affricate"] = self.is_affricate
        return res

    def __int__(self):
        first = 3
        second = int(self.is_affricate)
        third = sorted(SYMBOLS).index(self.symbol)
        return int(str(first) + str(second) + str(third))


class IPALetter(IPASymbol):

    def __init__(self, symbol, is_vowel=False):
        IPASymbol.__init__(self, symbol)
        self.is_vowel = is_vowel

    def get_symbol(self):
        return self.symbol

    def get_is_vowel(self):
        return self.is_vowel

    def parse_part(self, part, name):
        """
        Returns the appropriate Openness for the given string.
        ~
        e.g. parse_openness("near close") -> Openness.NEAR_CLOSE

        :param part: str, part of vowel (Openness, Backness, or Roundness)
        :param name: str, name of value in part
        :return: Openness/Backness/Roundness, corresponding value for
            given name and part
        """
        res = None
        #try:
        exec("res = self." + part + "." + name.upper().replace(" ", "_"))
        #except AttributeError:
        #    pass
        return res


class IPAVowel(IPALetter):

    def __init__(self, symbol, openness, backness, roundness, lax=False, rhotacized=False):
        """
        Initializes this IPAVowel as a vowel with the
        given symbol, with the given openness, backness, and roundness.
        ~
        If lax is True then this vowel is lax,
        otherwise it is not.
        ~
        If rhotacized is True then this vowel is rhotacized,
        otherwise it is regular.

        :param symbol: (unicode) str, vowel symbol(s)
        :param openness: str, openness of vowel
        :param backness: str, backness of vowel
        :param roundness: str, roundness of vowel
        :param lax: bool, whether this vowel is lax
        :param rhotacized: bool, whether this vowel is rhotacized
        """
        IPALetter.__init__(self, symbol, True)
        self.openness = self.parse_part("Openness", openness)
        self.backness = self.parse_part("Backness", backness)
        self.roundness = self.parse_part("Roundness", roundness)
        self.lax = lax
        self.rhotacized = rhotacized

    def get_dict(self):
        res = dict()
        res["symbol"] = self.symbol
        res["vowel"] = self.is_vowel
        res["openness"] = self.openness
        res["backness"] = self.backness
        res["roundness"] = self.roundness
        res["lax"] = self.lax
        res["rhotacized"] = self.rhotacized
        return res

    def __int__(self):
        first = 1
        second = self.openness.value
        third = self.backness.value
        fourth = self.roundness.value
        fifth = int(self.lax)
        sixth = int(self.rhotacized)
        return int(str(first) +
                   str(second) +
                   str(third).zfill(2) +
                   str(fourth) +
                   str(fifth) +
                   str(sixth))

    class Openness(Enum):
        CLOSE = 1
        NEAR_CLOSE = 2
        CLOSE_MID = 3
        MID = 4
        OPEN_MID = 5
        NEAR_OPEN = 6
        OPEN = 7

    class Backness(Enum):
        FRONT = 1
        NEAR_FRONT = 2
        CENTRAL_FRONT = 3
        CENTRAL = 4
        CENTRAL_BACK = 5
        NEAR_BACK = 6
        BACK = 7

    class Roundness(Enum):
        UNROUNDED = 1
        ROUNDED = 2
        NEITHER = 3


class IPAConsonant(IPALetter):

    def __init__(self, symbol, place, manner, voiced=False, velarized=False):
        """
        Initializes this IPAConsonant as a consonant with the
        given symbol and linguistic place and manner of articulation.
        ~
        If voiced is True then this consonant is voiced,
        otherwise it is voiceless.

        :param symbol: (unicode) str, consonant symbol(s)
        :param place: str, place of articulation
        :param manner: str, manner of articulation
        :param voiced: bool, whether this consonant is voiced
        :param velarized: bool, whether this consonant is velarized
        """
        IPALetter.__init__(self, symbol, False)
        self.symbol = symbol
        self.place = self.parse_part("Place", place)
        self.manner = self.parse_part("Manner", manner)
        self.voiced = voiced
        self.velarized = velarized

    def get_dict(self):
        res = dict()
        res["symbol"] = self.symbol
        res["vowel"] = self.is_vowel
        res["place"] = self.place
        res["manner"] = self.manner
        res["voiced"] = self.voiced
        res["velarized"] = self.velarized
        return res

    def __int__(self):
        """
        Returns an int representing this consonant's properties
        for a machine learning classifier.

        :return: int, an integer representing this consonant
        """
        first = 2
        second = 0
        third = self.place.value
        fourth = self.manner.value
        fifth = int(self.voiced)
        sixth = int(self.velarized)
        return int(str(first) +
                   str(second) +
                   str(third).zfill(2) +
                   str(fourth) +
                   str(fifth) +
                   str(sixth))

    class Place(Enum):
        LABIAL = 1
        CORONAL = 2
        DORSAL = 3
        LARYNGEAL = 4
        BILABIAL = 5
        LABIODENTAL = 6
        DENTAL = 7
        ALVEOLAR = 8
        POST_ALVEOLAR = 9
        RETROFLEX = 10
        PALATAL = 11
        VELAR = 12
        UVULAR = 13
        PHARYNGEAL = 14
        GLOTTAL = 15
        ALVEOLOPALATAL = 16

        def parse_place(self, name):
            """
            Returns the appropriate Place for the given string.
            ~
            e.g. parse_place("post-alveolar") -> Place.POST_ALVEOLAR

            :param name: str, the name of the Place value
            :return: Place, the Place value for the given name
            """
            place = None
            exec("place = Place." + name.upper().replace("-", "_"))
            return place

    class Manner(Enum):
        GLIDE = 0
        PLOSIVE = 1
        NASAL = 2
        FRICATIVE = 3
        #SIBILANT_FRICATIVE = 2
        #NON_SIBILANT_FRICATIVE = 3
        APPROXIMANT = 4
        FLAP_TAP = 5
        TRILL = 6
        LATERAL_FRICATIVE = 7
        LATERAL_APPROXIMANT = 8
        LATERAL_FLAP_TAP = 9

        def parse_manner(self, name):
            """
            Returns the appropriate Manner for the given string.
            ~
            e.g. parse_manner("lateral fricative") -> Manner.LATERAL_FRICATIVE

            :param name: str, the name of the Manner value
            :return: Manner, the Manner value for the given name
            """
            manner = None
            exec("manner = Manner." + name.upper().replace(" ", "_"))
            return manner


VOWEL_KEYS = VOWELS.keys()

IPAVOWELS = {
    # FRONT VOWELS
    u"i": IPAVowel(u"i", "close", "front", "unrounded"),
    u"y": IPAVowel(u"y", "close", "front", "rounded"),

    u"ɪ": IPAVowel(u"ɪ", "near close", "near front", "unrounded", lax=True),
    u"ʏ": IPAVowel(u"ʏ", "near close", "near front", "rounded", lax=True),

    u"e": IPAVowel(u"e", "close mid", "front", "unrounded"),
    u"ø": IPAVowel(u"ø", "close mid", "front", "rounded"),

    u"ɛ": IPAVowel(u"ɛ", "open mid", "front", "unrounded"),
    u"œ": IPAVowel(u"œ", "open mid", "front", "rounded"),

    u"æ": IPAVowel(u"æ", "near open", "front", "unrounded"),

    u"a": IPAVowel(u"a", "open", "front", "unrounded"),
    u"ɶ": IPAVowel(u"ɶ", "open", "front", "rounded"),

    # CENTRAL VOWELS
    u"ɨ": IPAVowel(u"ɨ", "close", "central", "unrounded"),
    u"ʉ": IPAVowel(u"ʉ", "close", "central", "rounded"),

    u"ɘ": IPAVowel(u"ɘ", "close mid", "central", "unrounded"),
    u"ɵ": IPAVowel(u"ɵ", "close mid", "central", "rounded"),

    u"ə": IPAVowel(u"ə", "mid", "central", "unrounded"),
    u"ɚ": IPAVowel(u"ɚ", "mid", "central", "unrounded", rhotacized=True),

    u"ɜ": IPAVowel(u"ɜ", "open mid", "central", "unrounded"),
    u"ɝ": IPAVowel(u"ɝ", "open mid", "central", "unrounded", rhotacized=True),
    u"ɞ": IPAVowel(u"ɞ", "open mid", "central", "rounded"),

    u"ɐ": IPAVowel(u"ɐ", "near open", "central", "unrounded"),

    # BACK VOWELS
    u"ɯ": IPAVowel(u"ɯ", "close", "back", "unrounded"),
    u"u": IPAVowel(u"u", "close", "back", "rounded"),

    u"ʊ": IPAVowel(u"ʊ", "near close", "near back", "rounded"),

    u"ɤ": IPAVowel(u"ɤ", "close mid", "back", "unrounded"),
    u"o": IPAVowel(u"o", "close mid", "back", "rounded"),

    u"ʌ": IPAVowel(u"ʌ", "open mid", "back", "unrounded"),
    u"ɔ": IPAVowel(u"ɔ", "open mid", "back", "rounded"),

    u"ɑ": IPAVowel(u"ɑ", "open", "back", "unrounded"),
    u"ɒ": IPAVowel(u"ɒ", "open", "back", "rounded"),
}

IPACONSONANTS = {
    # PLOSIVES
    u"p": IPAConsonant(u"p", "bilabial", "plosive", voiced=False),  # vl bilabial plosive
    u"b": IPAConsonant(u"b", "bilabial", "plosive", voiced=True),   # vd bilabial plosive

    u"t": IPAConsonant(u"t", "alveolar", "plosive", voiced=False),  # vl alveolar plosive
    u"d": IPAConsonant(u"d", "alveolar", "plosive", voiced=True),   # vd alveolar plosive

    u"ʈ": IPAConsonant(u"ʈ", "retroflex", "plosive", voiced=False), # vl retroflex plosive
    u"ɖ": IPAConsonant(u"ɖ", "retroflex", "plosive", voiced=True),  # vd retroflex plosive

    u"c": IPAConsonant(u"c", "palatal", "plosive", voiced=False),   # vl palatal plosive
    u"ɟ": IPAConsonant(u"ɟ", "palatal", "plosive", voiced=True),    # vd palatal plosive

    u"k": IPAConsonant(u"k", "velar", "plosive", voiced=False),     # vl velar plosive
    u"ɡ": IPAConsonant(u"ɡ", "velar", "plosive", voiced=True),      # vd velar plosive

    u"q": IPAConsonant(u"q", "uvular", "plosive", voiced=False),    # vl uvular plosive
    u"ɢ": IPAConsonant(u"ɢ", "uvular", "plosive", voiced=True),     # vd uvular plosive

    u"ʔ": IPAConsonant(u"ʔ", "glottal", "plosive", voiced=True),    # vd glottal plosive

    # NASALS
    u"m": IPAConsonant(u"m", "labiodental", "nasal", voiced=True),  # vd bilabial nasal

    u"ɱ": IPAConsonant(u"ɱ", "labiodental", "nasal", voiced=True),  # vd labiodental nasal

    u"n": IPAConsonant(u"n", "alveolar", "nasal", voiced=True),     # vd alveolar nasal

    u"ɳ": IPAConsonant(u"ɳ", "retroflex", "nasal", voiced=True),    # vd retroflex nasal

    u"ɲ": IPAConsonant(u"ɲ", "palatal", "nasal", voiced=True),      # vd palatal nasal

    u"ŋ": IPAConsonant(u"ŋ", "velar", "nasal", voiced=True),        # vd velar nasal

    u"ɴ": IPAConsonant(u"ɴ", "uvular", "nasal", voiced=True),       # vd uvular nasal

    # TRILL
    u"ʙ": IPAConsonant(u"ʙ", "bilabial", "trill", voiced=True),    # vd bilabial trill

    u"r": IPAConsonant(u"r", "alveolar", "trill", voiced=True),    # vd alveolar trill

    u"ʀ": IPAConsonant(u"ʀ", "uvular", "trill", voiced=True),    # vd uvular trill

    # FLAP/TAP
    u"ⱱ": IPAConsonant(u"ⱱ", "labiodental", "flap tap", voiced=True),    # voiced labiodental flap

    u"ɾ": IPAConsonant(u"ɾ", "alveolar", "flap tap", voiced=True),    # vd alveolar tap

    u"ɽ": IPAConsonant(u"ɽ", "retroflex", "flap tap", voiced=True),    # vd retroflex flap

    # FRICATIVE
    u"ɸ": IPAConsonant(u"ɸ", "bilabial", "fricative", voiced=False),   # vl bilabial fricative
    u"β": IPAConsonant(u"β", "bilabial", "fricative", voiced=True),    # vd bilabial fricative

    u"f": IPAConsonant(u"f", "labiodental", "fricative", voiced=False),   # vl labiodental fricative
    u"v": IPAConsonant(u"v", "labiodental", "fricative", voiced=True),    # vd labiodental fricative

    u"θ": IPAConsonant(u"θ", "dental", "fricative", voiced=False),   # vl dental fricative
    u"ð": IPAConsonant(u"ð", "dental", "fricative", voiced=True),    # vd dental fricative

    u"s": IPAConsonant(u"s", "alveolar", "fricative", voiced=False),   # vl alveolar fricative
    u"z": IPAConsonant(u"z", "alveolar", "fricative", voiced=True),    # vd alveolar fricative

    u"ʃ": IPAConsonant(u"ʃ", "post alveolar", "fricative", voiced=False),   # vl postalveolar fricative
    u"ʒ": IPAConsonant(u"ʒ", "post alveolar", "fricative", voiced=True),    # vd postalveolar fricative

    u"ʂ": IPAConsonant(u"ʂ", "retroflex", "fricative", voiced=False),   # vl retroflex fricative
    u"ʐ": IPAConsonant(u"ʐ", "retroflex", "fricative", voiced=True),    # vd retroflex fricative

    u"ç": IPAConsonant(u"ç", "palatal", "fricative", voiced=False),   # vl palatal fricative
    u"ʝ": IPAConsonant(u"ʝ", "palatal", "fricative", voiced=True),    # vd palatal fricative

    u"x": IPAConsonant(u"x", "velar", "fricative", voiced=False),   # vl velar fricative
    u"ɣ": IPAConsonant(u"ɣ", "velar", "fricative", voiced=True),    # vd velar fricative

    u"χ": IPAConsonant(u"χ", "uvular", "fricative", voiced=False),   # vl uvular fricative
    u"ʁ": IPAConsonant(u"ʁ", "uvular", "fricative", voiced=True),    # vd uvular fricative

    u"ħ": IPAConsonant(u"ħ", "pharyngeal", "fricative", voiced=False),   # vl pharyngeal fricative
    u"ʕ": IPAConsonant(u"ʕ", "pharyngeal", "fricative", voiced=True),    # vd pharyngeal fricative

    u"h": IPAConsonant(u"h", "glottal", "fricative", voiced=False),   # vl glottal fricative
    u"ɦ": IPAConsonant(u"ɦ", "glottal", "fricative", voiced=True),    # vd glottal fricative

    # APPROXIMANT
    u"w": IPAConsonant(u"w", "bilabial", "approximant", voiced=True),       # vd bilabial approximant

    u"ʋ": IPAConsonant(u"ʋ", "labiodental", "approximant", voiced=True),    # vd labiodental approximant

    u"ɹ": IPAConsonant(u"ɹ", "post alveolar", "approximant", voiced=True),  # vd (post)alveolar approximant

    u"ɻ": IPAConsonant(u"ɻ", "retroflex", "approximant", voiced=True),      # vd retroflex approximant

    u"j": IPAConsonant(u"j", "palatal", "approximant", voiced=True),        # vd palatal approximant

    u"ɰ": IPAConsonant(u"ɰ", "velar", "approximant", voiced=True),          # vd velar approximant

    # LATERAL FRICATIVE
    u"ɬ": IPAConsonant(u"ɬ", "alveolar", "lateral fricative", voiced=False),  # vl alveolar lateral fricative
    u"ɮ": IPAConsonant(u"ɮ", "alveolar", "lateral fricative", voiced=True),   # vd alveolar lateral fricative
    u"ɫ": IPAConsonant(u"ɫ", "alveolar", "lateral fricative",                 # vd alveolar lateral (velarized) [dark l]
                       voiced=True, velarized=True),

    # LATERAL APPROXIMANT
    u"l": IPAConsonant(u"l", "alveolar", "lateral approximant", voiced=True),   # vd alveolar lateral approximant
    u"ɭ": IPAConsonant(u"ɭ", "retroflex", "lateral approximant", voiced=True),  # vd retroflex lateral approximant
    u"ʟ": IPAConsonant(u"ʟ", "velar", "lateral approximant", voiced=True),      # vd velar lateral approximant

    # LATERAL FLAP/TAP
    u"ɺ": IPAConsonant(u"ɺ", "alveolar", "lateral flap tap", voiced=True),    # vd alveolar lateral flap

    # ALVEOLOPALATAL
    u"ɕ": IPAConsonant(u"ɕ", "alveolopalatal", "fricative", voiced=False),   # vl alveolopalatal fricative
    u"ʑ": IPAConsonant(u"ʑ", "alveolopalatal", "fricative", voiced=True),    # vd alveolopalatal fricative

    # MISC (TBD)
    #u"ɓ": IPAConsonant(u"ɓ", "bilabial", "plosive", voiced=True),    # vd bilabial implosive
    #u"ɗ": IPAConsonant(u"ɗ", "alveolar", "plosive", voiced=True),    # vd alveolar implosive
    #u"ħ": IPAConsonant(u"ɧ", "", voiced=False),    # vl multiple-place fricative
    #u"ʜ": IPAConsonant(u"ʜ", voiced=False),    # vl epiglottal fricative
    #u"ʤ": IPAConsonant(u"ʤ", "post-alveolar", "affricate", voiced=True),    # vd postalveolar affricate
    #u"ʄ": IPAConsonant(u"ʄ", "palatal", "plosive", voiced=True),    # vd palatal implosive
    #u"ɠ": IPAConsonant(u"ɠ", "velar", "plosive", voiced=True),    # vd velar implosive
    #u"ʛ": IPAConsonant(u"ʛ", "uvular", "plosive", voiced=True),    # vd uvular implosive
    #u"ɥ": IPAConsonant(u"ɥ", ""),    # labial-palatal approximant
    #u"ʘ": IPAConsonant(u"ʘ", "bilabial", "click"),    # bilabial click
    #u"ʧ": IPAConsonant(u"ʧ", voiced=False),    # vl postalveolar affricate
    #u"ʍ": IPAConsonant(u"ʍ", voiced=False),    # vl labial-velar fricative
    #u"ʎ": IPAConsonant(u"ʎ", "palatal", voiced=True),    # vd palatal lateral
    #u"ʡ": IPAConsonant(u"ʡ", voiced=True),    # vd epiglottal plosive
    #u"ʢ": IPAConsonant(u"ʢ", voiced=True)     # vd epiglottal fricative
}


IPADIACRITICS = {
    # AFFRICATES
    u"͡": IPADiacritic(u"͡", is_affricate=True),     # combining double inverted breve
    u"͜": IPADiacritic(u"͜", is_affricate=True),     # combining double breve below

    # DIACRITICS
    u"ˈ": IPADiacritic(u"ˈ", is_affricate=False),    # (primary) stress mark
    u"ˌ": IPADiacritic(u"ˌ", is_affricate=False),    # secondary stress
    u"ː": IPADiacritic(u"ː", is_affricate=False),    # length mark (alt: colon)
    u"ˑ": IPADiacritic(u"ˑ", is_affricate=False),    # half-length
    u"ʼ": IPADiacritic(u"ʼ", is_affricate=False),    # ejective
    u"ʴ": IPADiacritic(u"ʴ", is_affricate=False),    # rhotacized
    u"ʰ": IPADiacritic(u"ʰ", is_affricate=False),    # aspirated
    u"ʱ": IPADiacritic(u"ʱ", is_affricate=False),    # breathy-voice-aspirated
    u"ʲ": IPADiacritic(u"ʲ", is_affricate=False),    # palatalized
    u"ʷ": IPADiacritic(u"ʷ", is_affricate=False),    # labialized
    u"ˠ": IPADiacritic(u"ˠ", is_affricate=False),    # velarized
    u"ˤ": IPADiacritic(u"ˤ", is_affricate=False),    # pharyngealized
    u"˞": IPADiacritic(u"˞", is_affricate=False),    # rhotacized
    u"̥": IPADiacritic(u"̥", is_affricate=False),     # voiceless
    u"̊": IPADiacritic(u"̊", is_affricate=False),     # voiceless (use if character has descender)
    u"̤": IPADiacritic(u"̤", is_affricate=False),     # breathy voiced
    u"̪": IPADiacritic(u"̪", is_affricate=False),     # dental
    u"̬": IPADiacritic(u"̬", is_affricate=False),     # voiced
    u"̰": IPADiacritic(u"̰", is_affricate=False),     # creaky voiced
    u"̺": IPADiacritic(u"̺", is_affricate=False),     # apical
    u"̼": IPADiacritic(u"̼", is_affricate=False),     # linguolabial
    u"̻": IPADiacritic(u"̻", is_affricate=False),     # laminal
    u"̚": IPADiacritic(u"̚", is_affricate=False),     # not audibly released
    u"̹": IPADiacritic(u"̹", is_affricate=False),     # more rounded
    u"̃": IPADiacritic(u"̃", is_affricate=False),     # nasalized
    u"̜": IPADiacritic(u"̜", is_affricate=False),     # less rounded
    u"̟": IPADiacritic(u"̟", is_affricate=False),     # advanced
    u"̠": IPADiacritic(u"̠", is_affricate=False),     # retracted
    u"̈": IPADiacritic(u"̈", is_affricate=False),     # centralized
    u"̴": IPADiacritic(u"̴", is_affricate=False),     # velarized or pharyngealized
    u"̽": IPADiacritic(u"̽", is_affricate=False),     # mid-centralized
    u"̝": IPADiacritic(u"̝", is_affricate=False),     # raised
    u"̩": IPADiacritic(u"̩", is_affricate=False),     # syllabic consonant
    u"̞̞": IPADiacritic(u"̞", is_affricate=False),     # lowered
    u"̯": IPADiacritic(u"̯", is_affricate=False),     # non-syllabic
    u"̘": IPADiacritic(u"̘", is_affricate=False),     # advanced tongue root
    u"̙": IPADiacritic(u"̙", is_affricate=False),     # retracted tongue root
    u"̆": IPADiacritic(u"̆", is_affricate=False),     # extra-short
    u"̋": IPADiacritic(u"̋", is_affricate=False),     # extra high tone
    u"́": IPADiacritic(u"́", is_affricate=False),     # high tone
    u"̄": IPADiacritic(u"̄", is_affricate=False),     # mid tone
    u"̀": IPADiacritic(u"̀", is_affricate=False),     # low tone
    u"̏": IPADiacritic(u"̏", is_affricate=False)      # extra low tone
}

IPALETTERS = dict(IPACONSONANTS.items() + IPAVOWELS.items())

IPASYMBOLS = dict(IPALETTERS.items() + IPADIACRITICS.items())

