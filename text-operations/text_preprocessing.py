import re
from string import punctuation
from stop_words import get_stop_words
import spacy
import pandas as pd

spcay_nlp = spacy.load("pl_core_news_sm")
stopwords_pl = get_stop_words("pl")


def preprocess_text(text):
    translator = str.maketrans("", "", punctuation)
    new_text = text.translate(translator)
    new_text = re.sub(r'\d+', '', new_text)
    new_text = new_text.lower()
    new_text = re.sub(r'\s+', ' ', new_text)
    tokens = new_text.split(' ')

    filtered_tokens = [token for token in tokens if token not in stopwords_pl]
    filtered_tokens = [token for token in filtered_tokens if token!= '']
    processed_text = " ".join(filtered_tokens)

    return processed_text


def lemmatize(texts):
    texts_spacy = texts.map(spcay_nlp)
    lemmatized_texts = texts_spacy.map(lambda doc: [t.lemma_ for t in doc])
    return lemmatized_texts


test = preprocess_text("Za siedmioma górami, za siedmioma lasami, w dużym zamku mieszkała królewna z księciem.")
print(test)
print(lemmatize(pd.Series([test]))[0])



