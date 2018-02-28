# coding: utf-8
"""
DEMO:

    Used for demoing MorphemeParser, MorphemeDFA, and more.
"""
from language_dfas import *


dfa = MorphemeDFA("Polish")
dfa.add_states(lim=1000)
dfa.chart_dfa()


dfa = MorphemeDFA("Chinese")
dfa.add_states(lim=1000)
dfa.add_words()
dfa.chart_dfa()


dfa = MorphemeDFA("Japanese")
dfa.add_states(lim=1000)
dfa.chart_dfa()


dfa = MorphemeDFA("Korean")
dfa.add_states(lim=500)
dfa.chart_dfa()

'''
#dfa.words_declensions(dfa.common_words(1000))
#dfa.refresh_json()
dfa = PhonemeDFA("Finnish")
dfa.word_declension("nuo")
dfa.words_declensions(dfa.common_words(1000))
dfa.refresh_json()
#ipas = dfa.word_to_ipa("druga", "Polish")
#print dfa.nearest_homophone("naapuri", "English")
#dfa.refresh_json()
dfa = PhonemeDFA(language="Finnish")
#print dfa.nearest_homophone("kuulu", "English")
word_pairs = dfa.common_word_pairs(lim=1000)
dfa.add_word_pairs(word_pairs)
img = dfa.chart_dfa()
#img.save("out/dfa_nl_rainbow_chart.png")
#dfa.clear()
#ipa_pairs = dfa.common_ipa_pairs(lim=1000)
#dfa.add_word_pairs(ipa_pairs)
#dfa.chart_dfa()
#img.save("out/pol_ipa_chart.png")

dfa = PhonemeDFA("Chinese")
word_pairs = dfa.common_word_pairs(lim=100)
dfa.add_word_pairs(word_pairs)
img = dfa.chart_dfa()
dfa.clear()

dfa = MorphemeDFA("Chinese")
dfa.add_states(1000)
img = dfa.chart_dfa()

dfa = MorphemeDFA("Japanese")
dfa.add_states(1000)
img = dfa.chart_dfa()
'''


'''
dfa.set_language("English")
#dfa = PhonemeDFA(language="English")
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

