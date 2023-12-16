import re
from string import punctuation
import nltk
import spacy
from stop_words import get_stop_words
from pyMorfologik import Morfologik
from pyMorfologik.parsing import ListParser
import string

parser = ListParser()
stemmer = Morfologik()

stopwords_pl = get_stop_words("pl")


def preprocess_text(text):
    translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    new_text = text.translate(translator)
    new_text = re.sub(r'\d+', '', new_text)
    new_text = re.sub(r'\s+', ' ', new_text)
    new_text = new_text.strip()
    new_text = new_text.lower()

    stems = stemmer.stem([new_text], parser)
    tokens = [(list(stems[i][1].keys())[0] if len(list(stems[i][1].keys())) > 0 else stems[i][0]) for i in range(len(stems))]

    filtered_tokens = [token for token in tokens if token not in stopwords_pl]
    filtered_tokens = [token for token in filtered_tokens if token!= '']
    processed_text = " ".join(filtered_tokens)

    return processed_text


test = preprocess_text("Za siedmioma górami, za siedmioma lasami, w dużym zamku mieszkała królewna z księciem.")
print(test)
print(lemmatize(pd.Series([test]))[0])



