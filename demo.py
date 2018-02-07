# coding: utf-8
"""
DEMO:

    Used for demoing MorphemeParser, MorphemeDFA, and more.
"""
from dfa import *
from dfa_ipa import IPAMorphemeDFA


dfa = IPAMorphemeDFA(language="Polish")
word_pairs = dfa.common_ipa_pairs(lim=1000)
dfa.add_word_pairs(word_pairs)
#img = dfa.visualize()
#img.save("dfa_pol_rainbow.png")
img = dfa.chart_dfa()
img.save("dfa_pol_rainbow_chart.png")


dfa = IPAMorphemeDFA(language="English")
word_pairs = dfa.common_ipa_pairs(lim=1000)
dfa.add_word_pairs(word_pairs)
#img = dfa.visualize()
#img.save("dfa_eng_rainbow.png")
img = dfa.chart_dfa()
img.save("dfa_eng_rainbow_chart.png")


