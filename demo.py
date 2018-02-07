# coding: utf-8
"""
DEMO:

    Used for demoing MorphemeParser, MorphemeDFA, and more.
"""
from dfa import *
from dfa_ipa import IPAMorphemeDFA


dfa = IPAMorphemeDFA(language="Dutch")
word_pairs = dfa.common_word_pairs(lim=500)
dfa.add_word_pairs(word_pairs)
img = dfa.chart_dfa()
img.save("out/dfa_nl_rainbow_chart.png")
dfa.clear()
ipa_pairs = dfa.common_ipa_pairs(lim=500)
dfa.add_word_pairs(ipa_pairs)
img = dfa.chart_dfa()
img.save("out/dfa_nl_rainbow_ipa_chart.png")

'''
dfa.set_language("English")
#dfa = IPAMorphemeDFA(language="English")
word_pairs = dfa.common_word_pairs(lim=200)
dfa.add_word_pairs(word_pairs)
img = dfa.chart_dfa()
img.save("dfa_eng_rainbow_chart.png")
dfa.clear()
ipa_pairs = dfa.common_ipa_pairs(lim=200)
dfa.add_word_pairs(ipa_pairs)
img = dfa.chart_dfa()
img.save("dfa_eng_rainbow_ipa_chart.png")
'''

