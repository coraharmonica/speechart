# Speechart
Speechart allows you to easily create artful charts for visualizing and analyzing linguistic features,
including morphemes and IPA pronunciations.

To create a Speechart, create a MorphemeDFA for displaying words or a PhonemeDFA for displaying IPA
pronunciations.  Both come with an add_states method that adds the most common words/IPA pronunciations
to their states.

Speechart is programmed in Python 2.7.1.
Initialize a MorphemeParser in your desired language to generate lists of common words as well as their morphemes and IPA transcriptions.  Refer to demo.py to see examples of how to visualize data.
