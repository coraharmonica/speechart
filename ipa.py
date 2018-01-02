# coding: utf-8

# False denotes an impossible sound,
# while None only denotes a sound that no language uses.

NASAL = [u"m̥", u"m", None, u"ɱ", None,                                 # LABIAL
         u"n̼", None, None, u"n̥", u"n", None, None, u"ɳ̊", u"ɳ", None,   # CORONAL
         None, u"ɲ̊", u"ɲ", u"ŋ̊", u"ŋ", None,                           # DORSAL
         u"ɴ", False, False, False, False, False, False]               # LARYNGEAL
PLOSIVE = [u"p", u"b", u"p̪", u"b̪", u"t̼",
        u"d̼", None, None, u"t", u"d", None, None, u"ʈ", u"ɖ", None,
           None, u"c", u"ɟ", u"k", u"ɡ", u"q",
        u"ɢ", False, False, u"ʡ", None, u"ʔ", False]
SIBILANT_FRICATIVE = [False, False, False, False, False,
                      False, None, None, u"s", u"z", u"ʃ", u"ʒ", u"ʂ", u"ʐ", u"ɕ",
                      u"ʑ", False, False, False, False, False,
                      False, False, False, False, False, False, False]
NON_SIBILANT_FRICATIVE = [u"ɸ", u"β", u"f", u"v", u"θ̼",
                          u"ð̼", u"θ", u"ð", u"θ̠", u"ð̠", u"ɹ̠̊˔", u"ɹ̠˔", None, u"ɻ˔", None,
                          None, u"ç", u"ʝ", u"x", u"ɣ", u"χ",
                          u"ʁ", u"ħ", u"ʕ", None, u"ʢ", u"h", u"ɦ"]
APPROXIMANT = [None, None, u"ʋ̥", u"ʋ", None,
               None, None, None, u"ɹ̥", u"ɹ", None, None, u"ɻ̊", u"ɻ", None,
               None, u"j̊", u"j", u"ɰ̊", u"ɰ", None,
               None, None, None, None, None, None, u"ʔ̞"]
FLAP_TAP = [None, u"ⱱ̟", None, u"ⱱ", None,
            u"ɾ̼", None, None, u"ɾ̥", u"ɾ", None, None, u"ɽ̊", u"ɽ", False,
            False, False, False, False, False, None,
            u"ɢ̆", False, False, None, u"ʡ̮", False, False]
TRILL = [u"ʙ̥", u"ʙ", None, None, None,
         u"r̼", None, None, u"r̥", u"r", None, None, u"ɽ̊ɽ̊", u"ɽɽ", False,
         False, False, False, False, False, u"ʀ̥",
         u"ʀ", False, False, u"ʜ", u"ʢ", False, False]
LATERAL_FRICATIVE = [False, False, False, False, None,
                     None, None, None, u"ɬ", u"ɮ", None, None, u"ɭ̊˔", None, None,
                     None, u"ʎ̥˔", u"ʎ̝", u"ʟ̝̊", u"ʟ̝", None,
                     None, False, False, False, False, False, False]
LATERAL_APPROXIMANT = [False, False, False, False, None,
                       None, None, None, u"l̥", u"l", None, None, u"ɭ̊", u"ɭ", None,
                       None, u"ʎ̥", u"ʎ", u"ʟ̥", u"ʟ", None,
                       u"ʟ̠", False, False, False, False, False, False]
LATERAL_FLAP_TAP = [False, False, False, False, None,
                    None, None, None, None, u"ɺ", None, None, None, u"ɺ̢", None,
                    None, None, u"ʎ̮", None, u"ʟ̆", None,
                    None, False, False, False, False, False, False]

MANNERS = {"nasal": NASAL, "stop": PLOSIVE,
           "sibilant fricative": SIBILANT_FRICATIVE, "non-sibilant fricative": NON_SIBILANT_FRICATIVE,
           "approximant": APPROXIMANT, "flap/tap": FLAP_TAP, "trill": TRILL,
           "lateral fricative": LATERAL_FRICATIVE,
           "lateral approximant": LATERAL_APPROXIMANT,
           "lateral flap/tap": LATERAL_FLAP_TAP}

LABIAL = [manner[:5] for manner in MANNERS]
CORONAL = [manner[5:15] for manner in MANNERS]
DORSAL = [manner[-13:-7] for manner in MANNERS]
LARYNGEAL = [manner[-7:] for manner in MANNERS]


IPA = (NASAL +
       PLOSIVE +
       SIBILANT_FRICATIVE +
       NON_SIBILANT_FRICATIVE +
       APPROXIMANT +
       FLAP_TAP +
       TRILL +
       LATERAL_FRICATIVE +
       LATERAL_APPROXIMANT +
       LATERAL_FLAP_TAP)


def transcribe_to_ipa(phrase):
    """
    Returns the given phrase transcribed to IPA.
    ~
    Input phrase can be in either bytes or unicode.

    :param phrase: str, phrase to output as unicode
    :return: (unicode) str,
    """
    return phrase


print len(IPA)
print IPA
print len(set(IPA))
print [u"t̺ d̺"]