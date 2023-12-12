import joblib
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

from chatbot.text_to_prefs import TextProcessor


class TextProcessorKnowledge:
    vectorizer = joblib.load('./chatbot/models/tfidf_vectorizer_wibit_categories.joblib')
    df = pd.read_csv('./chatbot/models/tf_idf_categories.csv', index_col=0)

    def predict_classes(self, text, n=10):
        prep_text = TextProcessor.preprocess_text(text)
        text_vector = self.vectorizer.transform([prep_text])
        categories = list(self.df.columns)
        calculated_metrics = {}

        for category in categories:
            category_vector = self.get_category_vector_from_df(category)
            calculated_metrics[category] = cosine_similarity(text_vector, category_vector)[0][0]

        metrics_values = list(calculated_metrics.values())
        threshold = (sorted(metrics_values))[-n]

        liked_categories = [category for category, score in calculated_metrics.items() if score >= threshold]
        return liked_categories

    def get_category_vector_from_df(self, category):
        return csr_matrix(self.df[category].values)


