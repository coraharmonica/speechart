# coding: utf-8

from ipa_parser import *
import unittest

LANGUAGE = "Dutch"

parser = IPAParser(LANGUAGE)

phonemes = parser.common_phonemes(50)
#print "MORPHEMES", parser.filter_morphemes(parser.all_ipa_words())


class TestIPAWord(unittest.TestCase):
    WORDS = dict()  # word-pronunciation dict in LANGUAGE and IPA

    if LANGUAGE == "Polish":
        WORD = u"obalać"
        IPA = u"ɔbalat͡ɕ"
        WORDS[WORD] = IPA
        WORDS[u"jestem"] = u"jɛs̪t̪ɛm"
        IPA_WORD = IPAWord(WORD, IPA, parser)
    elif LANGUAGE == "Dutch":
        WORD = u"kleintje"
        IPA = u"klɛi̯ntjə"
        WORDS[WORD] = IPA
        IPA_WORD = IPAWord(WORD, IPA, parser)

    def test_break_syllable(self):
        if LANGUAGE == "Polish":
            syllable = u"lat͡ɕ"
            ans = (u"l", u"a", u"t͡ɕ")
        else:
            syllable = u"tjə"
            ans = (u"t", u"jə", u"")
        self.assertEqual(self.IPA_WORD.break_syllable(syllable), ans)

    def test_break_syllables(self):
        if LANGUAGE == "Polish":
            ans = [(u"", u"ɔ", u""),
                   (u"b", u"a", u""),
                   (u"l", u"a", u"t͡ɕ")]
        else:
            ans = [(u"kl", u"ɛi", u"̯n"),
                   (u"t", u"jə", u"")]
        self.assertEqual(self.IPA_WORD.break_syllables(self.IPA, use_syllables=False), ans)

    def test_extract_syllable(self):
        if LANGUAGE == "Polish":
            num = 2
            ans = (u"l", u"a", u"t͡ɕ")
        else:
            num = 0
            ans = (u"kl", u"ɛi̯", u"n")
        self.assertEqual(self.IPA_WORD.extract_syllable(self.IPA, num, use_syllables=False), ans)

    def test_add_syllables(self):
        if LANGUAGE == "Polish":
            ans = u"ɔ.ba.lat͡ɕ"
        else:
            ans = u"klɛi̯n.tjə"
        self.assertEqual(self.IPA_WORD.add_syllables(self.IPA), ans)

    def test_next_phoneme(self):
        ans1 = u"ɔ" if LANGUAGE == "Polish" else u"k"
        ans2 = u"b" if LANGUAGE == "Polish" else u"l"
        ans3 = u"a" if LANGUAGE == "Polish" else u"ɛi"
        next_phoneme, next_ipa = self.IPA_WORD.next_phoneme(self.IPA, use_syllables=False)
        self.assertEqual(next_phoneme, ans1)
        next_phoneme, next_ipa = self.IPA_WORD.next_phoneme(next_ipa, use_syllables=False)
        self.assertEqual(next_phoneme, ans2)
        self.assertEqual(self.IPA_WORD.next_phoneme(next_ipa, remove=False, use_syllables=False), ans3)

    def test_next_syllable(self):
        next_syllable, rest_ipa = self.IPA_WORD.next_syllable(self.IPA)
        ans1 = u"ɔ" if LANGUAGE == "Polish" else u"klɛi̯n"
        ans2 = u"ba" if LANGUAGE == "Polish" else u"tjə"
        ans3 = u"lat͡ɕ" if LANGUAGE == "Polish" else u""
        self.assertEqual(next_syllable, ans1)
        next_syllable, rest_ipa = self.IPA_WORD.next_syllable(rest_ipa)
        self.assertEqual(next_syllable, ans2)
        self.assertEqual(self.IPA_WORD.next_syllable(rest_ipa, remove=False), ans3)

    def test_split_syllables(self):
        ans = [u"ɔ", u"ba", u"lat͡ɕ"] if LANGUAGE == "Polish" else [u"klɛi̯n", u"tjə"]
        self.assertEqual(self.IPA_WORD.split_syllables(self.IPA, use_syllables=False), ans)

    def test_find_ipa_vowels(self):
        ans = (u"ɔ", u"balat͡ɕ") if LANGUAGE == "Polish" else (u"ɛi", u"̯ntjə")
        self.assertEqual(self.IPA_WORD.find_ipa_vowels(self.IPA), ans)

    def test_find_ipa_consonants(self):
        ans = (u"b", u"alat͡ɕ") if LANGUAGE == "Polish" else (u"kl", u"ɛi̯ntjə")
        self.assertEqual(self.IPA_WORD.find_ipa_consonants(self.IPA), ans)


if __name__ == '__main__':
    unittest.main()
    #pass

#print parser.get_phoneme_dict()