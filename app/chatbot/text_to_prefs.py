import joblib
import re
import string
from stop_words import get_stop_words
from pyMorfologik import Morfologik
from pyMorfologik.parsing import ListParser
# from keras.models import load_model
import random

parser = ListParser()
stemmer = Morfologik()

stopwords_pl = get_stop_words("pl")


class TextProcessor:
    categories = ['amusement_parks', 'ferris_wheels', 'water_parks', 'miniature_parks',
                  'baths_and_saunas', 'climbing', 'stadiums', 'winter_sports',
                  'natural_springs', 'water', 'nature_reserves', 'beaches',
                  'railway_stations', 'dams', 'mints', 'mineshafts', 'science_museums',
                  'churches', 'cathedrals', 'monasteries', 'synagogues', 'hindu_temples',
                  'mosques', 'archaeology', 'castles', 'fortified_towers', 'bunkers',
                  'military_museums', 'battlefields', 'war_graves', 'cemeteries',
                  'mausoleums', 'crypts', 'monuments', 'tumuluses', 'wall_painting',
                  'fountains', 'sculptures', 'gardens_and_parks',
                  'archaeological_museums', 'art_galleries', 'biographical_museums',
                  'history_museums', 'local_museums', 'national_museums',
                  'fashion_museums', 'planetariums', 'zoos', 'aquariums', 'skyscrapers',
                  'towers', 'historic_architecture', 'bridges']

    vectorizer = joblib.load('./chatbot/models/tfidf_vectorizer_wibit.joblib')

    # model = load_model('./chatbot/models/tfidf_bigger_nn')

    def predict_classes(self, text):
        """prep_text = [self.preprocess_text(text)]
        vec_text = self.vectorizer.transform(prep_text)
        vec_text = vec_text.toarray()
        poi_pred_frac = self.model.predict(vec_text)
        poi_pred = self.get_attr_from_vector(poi_pred_frac[0], threshold=0.5)

        liked_categories = []
        for i in range(len(poi_pred)):
            if poi_pred[i] == 1:
                liked_categories.append(self.categories[i])"""

        liked_categories = random.sample(self.categories, random.randint(5, 15))

        return liked_categories

    @classmethod
    def preprocess_text(cls, text):
        translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
        new_text = text.translate(translator)
        new_text = re.sub(r'\d+', '', new_text)
        new_text = re.sub(r'\s+', ' ', new_text)
        new_text = new_text.strip()
        new_text = new_text.lower()

        stems = stemmer.stem([new_text], parser)
        tokens = [(list(stems[i][1].keys())[0] if len(list(stems[i][1].keys())) > 0 else stems[i][0]) for i in
                  range(len(stems))]

        filtered_tokens = [token for token in tokens if token not in stopwords_pl]
        filtered_tokens = [token for token in filtered_tokens if token != '']
        processed_text = " ".join(filtered_tokens)

        return processed_text

    @classmethod
    def get_attr_from_vector(cls, vector, threshold=0.5):
        return [1 if elem >= threshold else 0 for elem in vector]
