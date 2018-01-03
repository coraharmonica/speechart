from ipa_symbols import *


def get_word_num(word):
    nums = [str(ord(char)) for char in word]
    num = int("".join(nums))
    print num
    return num


def get_phrase_nums(phrase):
    nums = [get_word_num(word) for word in phrase]
    return nums


def get_ipa_num(ipa):
    ipa_sym = ""
    for char in ipa:
        ipa_sym += str(int(IPASYMBOLS[char]))
    return int(ipa_sym)


def get_ipas_nums(ipas):
    nums = [str(get_ipa_num(ipa)) for ipa in ipas]  # if ipa not in SYMBOLS]
    return " ".join(nums)


def get_ipa_phrase_nums(ipa_phrase):
    nums = [get_ipas_nums(ipas) for ipas in ipa_phrase.split(" ")]
    return nums

