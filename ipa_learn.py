from sklearn.tree import DecisionTreeClassifier
from sklearn.feature_extraction import DictVectorizer


CLASSIFIER = DecisionTreeClassifier()
DICT_CLASSIFIER = DictVectorizer()


def train_classifier(questions, answers):
    CLASSIFIER.fit(questions, answers)


def train_dict_classifier(questions):  #, answers):
    DICT_CLASSIFIER.fit_transform(questions)  #, answers)


def test_classifier(questions, answers):
    hits = []
    misses = []
    for i in range(len(questions)):
        guess = CLASSIFIER.predict([questions[i]])
        ans = answers[i]
        if guess == ans:
            hits.append(guess)
        else:
            print guess
            misses.append(ans)
    print len(hits), " out of ", len(hits)+len(misses)


