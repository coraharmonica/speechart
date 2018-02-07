# coding: utf-8
"""
DFA:

    Stores classes for representing words with DFAs.
    ~
    Designed for (ideally) any language.
"""
from morpheme_parser import MorphemeParser
from images import *


class MorphemeDFA(MorphemeParser):
    """
    A class for constructing a DFA for morphemes from input words.
    """
    RADIUS = 24
    FONT_SIZE = RADIUS / 2
    PARTS_OF_SPEECH = ["CC", "CD", "DT", "EX", "FW", "IN", "JJ", "JJR", "JJS", "LS",
                       "MD", "NN", "NNS", "NNP", "NNPS", "PDT", "POS", "PRP", "PRP$",
                       "RB", "RBR", "RBS", "RP", "TO", "UH", "VB", "VBD", "VBG",
                       "VBN", "VBP", "VBZ", "WDT", "WP", "WP$", "WRB"]

    RGB = {'verbs': (225,   0,   0, 125),
           'nouns': (  0, 225,   0, 125),
           'adjs.': (  0,   0, 200, 125),
           'advs.': (175,   0, 175, 125),
           'other': (  0, 175, 175, 125),
           ' n + v':     (225, 225, 100, 125),
           ' v + adj':   (225, 100, 200, 125),
           ' adj + adv': (175,   0, 225, 125)}

    POS_ADDS = {"n": (  0, 225,   0, 125),
                "v": (250,   0,   0, 125),
                "a": (  0,   0, 200, 125),
                "s": (  0,   0, 200, 125),
                #"s": (  0, 175, 175, 125),
                "r": (175,   0, 175, 125),
                "o": (  0, 175, 175, 125)} #(100, 150,   0, 125)}

    POS_KEY = {"Noun": "n",
               "Verb": "v",
               "Adjective": "a",
               "Adverb": "r"}

    def __init__(self, language):
        MorphemeParser.__init__(self, language)
        self.alphabet = set()
        self.start_state = 0
        self.language = language
        self.states = {self.start_state}
        self.current_state = self.start_state
        self.start_states = self.states.copy()
        self.success_states = dict()
        self.success_colours = dict()
        self.transitions = dict()  # holds transition_all functions

    def state_colour(self, state):
        """
        Returns the colour corresponding to the given state.

        :param state: int, state to return colour for
        :return: 3-tuple(int,int,int), RGB colour for state
        """
        poses = self.success_states[state]

        if len(poses) == 0:
            return 'lightgray'
        else:
            return self.success_colours[state]

    def avg_colour(self, colours):
        """
        Returns a 3-tuple representing the average RBG value of
        the given colours.

        :param colours: List[3-tuple(int,int,int)], RGB values to average
        :return: 3-tuple(int,int,int), average RBG value
        """
        r = max([colour[0] for colour in colours])
        g = max([colour[1] for colour in colours])
        b = max([colour[2] for colour in colours])
        rgb = (r, g, b)
        return rgb

    def pos_add(self, pos):
        """
        Returns a 4-tuple representing an additive RGBA value for
        the given pos.

        :param pos: str, part-of-speech to retrieve additive RGBA value for
        :return: 4-tuple(int,int,int,int), additive RBGA value for given pos
        """
        try:
            return self.POS_ADDS[pos]
        except KeyError:
            try:
                return self.POS_ADDS[self.POS_KEY[pos]]
            except KeyError:
                return self.POS_ADDS['o']

    def new_state(self):
        """
        Adds one more state to this MorphemeDFA's states.
        ~
        Returns the integer representing the new state.

        :return: int, new state's number
        """
        state = len(self.states)
        self.states.add(state)
        return state

    def add_success_state(self, state, pos=None):
        """
        Adds this state and its part-of-speech as a success state
        to this MorphemeDFA's success_states.

        :param state: int, state to add as success state
        :param pos: str, part of speech to add as key
        :return: None
        """
        self.success_states.setdefault(state, set())
        self.success_states[state].add(pos)
        self.add_success_colour(state, pos)
        return

    def add_success_colour(self, state, pos):
        """
        Adds this state and its part-of-speech colour to success_colours.

        :param state: int, state to add as success state
        :param pos: str, part-of-speech to add to success_colours
        :return: None
        """
        self.success_colours.setdefault(state, (0, 0, 0, 0))
        colour = self.success_colours[state]
        pos_colour = self.pos_add(pos)
        avg_colour = lambda i: max(100, min(colour[i] + pos_colour[i], 225))
        colour = (avg_colour(0),
                  avg_colour(1),
                  avg_colour(2),
                  avg_colour(3))
        self.success_colours[state] = colour

    def add_word(self, word):
        """
        Adds the given word's characters as states to this MorphemeDFA's dfa.
        ~
        Adds the given word to success_states.

        :param word: str, word to add to DFA
        :return: None
        """
        self.current_state = self.transition_all(self.current_state, self.unicodize(word))
        self.add_success_state(self.current_state)
        self.current_state = 0
        return

    def add_words(self, words):
        """
        Adds the given words' characters as states to this MorphemeDFA's dfa.
        ~
        Adds the given words to success_states.

        :param words: Set(str), words to add to DFA
        :return: None
        """
        for word in sorted(words):
            self.add_word(word)

    def add_word_pair(self, word_pair):
        """
        Adds the given word-pos pair's characters as states to this MorphemeDFA's dfa.
        ~
        Adds the given word-pos pair to success_states.

        :param words: tuple(str, Set(str)), word-pos pair to add to DFA
        :return: None
        """
        word, pos = word_pair
        self.current_state = self.transition_all(self.current_state, self.unicodize(word))
        self.add_success_state(self.current_state, pos)
        self.current_state = 0
        return

    def add_word_pairs(self, word_pairs):
        """
        Adds the given word-pos pairs' characters as states to this MorphemeDFA's dfa.
        ~
        Adds the given word-pos pairs to success_states.

        :param words: Set(tuple(str, str)), word-pos pairs to add to DFA
        :return: None
        """
        for word_pair in sorted(word_pairs):
            self.add_word_pair(word_pair)

    def clear(self):
        """
        Clears this DFA's transitions and all states.

        :return: None
        """
        self.states = {self.start_state}
        self.start_states = self.states.copy()
        self.success_states = dict()
        self.success_colours = dict()
        self.transitions = dict()

    def transition(self, state, char):
        """
        Returns the result of the transition function from the given state
        and character.
        ~
        If the given state-char pair already exists, returns their output.
        Otherwise, creates a new transition pair from input state to a new
        state.

        :param state: int, state to transition from
        :param char: str, character in alphabet to transition with
        :return: int, next state
        """
        try:
            new_state = self.transitions[(state, char)]
            print "OLD STATE:\t", state, ",", char, "->", new_state
        except KeyError:
            new_state = self.new_state()
            self.transitions[(state, char)] = new_state
            print "NEW STATE:\t", state, ",", char, "->", new_state
        return new_state

    def transition_all(self, state, chars):
        """
        Returns the result of the transition function from the given state
        and all characters in chars.
        ~
        If the given state-char pair already exists, returns their output.
        Otherwise, creates a new transition pair from input state to a new
        state.

        :param state: int, state to transition from
        :param chars: Iterable(str), characters in alphabet to transition with
        :return: int, new state after all chars transitions
        """
        curr_state = state
        for char in chars:
            curr_state = self.transition(state, char)
        return curr_state

    def state_circle(self, state_num):
        """
        Returns a circle with state_num overlaid.
        ~
        If given state_num is a success state, output circle
        will be outlined.

        :param state_num: int, number for state circle
        :return: Image, circle with state_num overlaid
        """
        success = state_num in self.success_states
        img = circle(self.RADIUS, fill=None, outline='gray')
        if success:
            fill = self.state_colour(state_num)
            img = overlay(circle(self.RADIUS - 8, fill=fill, outline='gray'), img)
        img = overlay(text(str(state_num), size=self.FONT_SIZE/2, alpha=0), img)
        return img

    def empty_image(self):
        """
        Returns an invisible image of RADIUS * RADIUS dimensions.
        ~
        Used for holding the place of a future state circle.

        :return: Image, invisible placeholder image
        """
        return rectangle(self.RADIUS/2, self.RADIUS/2, fill=None)

    def connect_states(self, state1, state2, transition="", length=None, angle=0):
        """
        Connects state1 and state2 images with an arrow of given
        length and angle, with transition_all overlaid on the arrow.
        ~
        If length is None, set length to the larger of 50 and
        the length of transition_all's text image.

        :param state1: Image, arrow's outgoing state
        :param state2: Image, arrow's incoming state
        :param transition: str, transition_all function from state1 to state2
        :param length: int, length of arrow
        :param angle: int[0,360), angle of arrow between state1 and state2
        :return: Image, state1 connected to state2 with an arrow
        """
        font = load_default_font()

        if length is None:
            length = int(max(50,
                             round(font.getsize(transition)[0]*4, -2)))

        arro = arrow(length, 2, "lightgray", angle=angle, label=transition, font_size=self.FONT_SIZE)
        state0 = make_blank_img(1, state2.size[1]/2, alpha=0)

        if angle > 0:
            align1, align2 = 'bottom', 'top'
            arro = above(state0, arro)
        elif angle < 0:
            align1, align2 = 'top', 'bottom'
            arro = above(arro, state0)
        else:
            align1, align2 = 'center', 'center'

        s1 = trim(state1)
        s2 = beside(arro, state2, align=align2)
        dfa = beside(s1, s2, align=align1)
        return dfa

    def visualize(self):
        """
        Visualizes all this MorphemeDFA's transitions as an Image
        and returns the image.

        :return: Image, image of this DFA
        """
        start = sorted(self.states)[0]
        dfa = self.visualize_state(start)
        dfa.show()
        return dfa

    def visualize_state(self, state):
        """
        Visualizes the given state and its transitions as an Image
        and returns the image.

        :param state: int, state to visualize
        :return: Image, image of this state and its transitions
        """
        dfa = self.state_circle(state)
        state0 = make_blank_img(0, 0, alpha=0)
        transitions = [t for t in self.transitions if t[0] == state]
        destinations = dict()

        for statechar in transitions:
            dest = self.transitions[statechar]
            destinations.setdefault(dest, set())
            destinations[dest].add(statechar[1])

        if len(destinations) != 0:
            inc = 5
            apex = (len(destinations) - 1) * inc
            angle = apex / 2
            branch = state0

            for dest in sorted(destinations):
                msg = ", ".join(destinations[dest])
                circ = self.visualize_state(dest)
                twig = self.connect_states(state0, circ, msg, angle=angle, length=len(destinations)*self.FONT_SIZE/2)
                branch = above(branch, twig, align='left')
                angle -= inc

            dfa = self.connect_states(dfa, branch, length=0)

        return dfa

    def chart_dfa(self):
        dfa = self.visualize()
        title = self.language + " Language Chart"
        title = text(title, size=self.FONT_SIZE*2)
        space = self.empty_image()
        legend = space

        for colour in sorted(self.RGB):
            label = text(colour, size=self.FONT_SIZE)
            rgb = self.RGB[colour]
            state = circle(self.RADIUS/2, fill=rgb, outline='gray')
            line = beside(state, space, align='center')
            line = beside(line, label, align='center')
            legend = above(legend, line, align='left')
            legend = above(legend, space, align='left')

        legend = above(legend, space)
        legend = above(title, legend)
        img = above(legend, dfa)
        bg = make_blank_img(img.size[0], img.size[1], alpha=255)
        bg = overlay(img, bg)
        bg.show()
        return bg

