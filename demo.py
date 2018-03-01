# coding: utf-8
"""
DEMO:

    Used for demoing MorphemeParser, MorphemeDFA, and more.
"""
from language_dfas import *

# construct a MorphemeDFA to create a DFA for words in your desired language
dfa = MorphemeDFA("English")
dfa.add_words("hello there my friend how are you today")
img = dfa.chart_dfa()
img.save("out/en_word_chart.png")    # save chart to file

dfa = MorphemeDFA("Finnish")
dfa.word_declension("nuo")  # adds nuo's declension to this dfa
dfa.refresh_json()          # stores all changes from this DFA's data back to JSONs (in data)
dfa.clear()                 # resets this DFA's states
# fetch nearest homophones between languages
dfa.nearest_homophone("naapuri", "English")
dfa.nearest_homophone("kuulu", "English")

# supports Chinese, Japanese, and Korean chart visualization
dfa = MorphemeDFA("Chinese")
dfa.add_states(lim=500)
dfa.chart_dfa()

dfa = MorphemeDFA("Japanese")
dfa.add_states(lim=500)
dfa.chart_dfa()

dfa = MorphemeDFA("Korean")
dfa.add_states(lim=500)
dfa.chart_dfa()

