from dfa import *
from ipa_symbols import IPADIACRITICS


class IPAMorphemeDFA(MorphemeDFA):

    def __init__(self, language):
        MorphemeDFA.__init__(self, language)

    def transition_all(self, state, chars):
        ipas = self.clean_ipa(chars)
        # "".join([char for char in chars if char not in IPADIACRITICS and char not in "()."])
        # ipas = self.split_ipas(chars)
        curr_state = state
        for ipa in ipas:
            curr_state = self.transition(curr_state, ipa)
        return curr_state

    def split_ipas(self, ipas):
        strings = []
        string = str()
        next_ipa = lambda i: ipas[i] if i < len(ipas) else None
        in_parens = False

        for i in range(len(ipas)):
            ipa = ipas[i]
            if ipa in "()":
                in_parens = not in_parens
                string += ipa
            elif in_parens or ipa in IPADIACRITICS or next_ipa(i+1) in IPADIACRITICS:
                string += ipa
            else:
                string += ipa
                strings.append(string)
                string = str()

        if len(string) != 0:
            strings.append(string)

        return strings
