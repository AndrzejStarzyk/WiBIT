import joblib
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

from chatbot.text_to_prefs import TextProcessor


class TextProcessorKnowledge:
    def __init__(self):
        self.vectorizer = joblib.load('./chatbot/models/tfidf_vectorizer_wibit_categories.joblib')
        self.df = pd.read_csv('./chatbot/models/tf_idf_categories.csv', index_col=0)
        self.categories = list(self.df.columns)
        self.categories_sparse_matrices = {category: self.get_category_vector_from_df(category) for category in self.categories}

    def predict_classes(self, text, n=10):
        prep_text = TextProcessor.preprocess_text(text)
        text_vector = self.vectorizer.transform([prep_text])

        calculated_metrics = {}

        for category in self.categories:
            category_vector = self.categories_sparse_matrices[category]
            calculated_metrics[category] = cosine_similarity(text_vector, category_vector)[0][0]

        metrics_values = list(calculated_metrics.values())
        threshold = (sorted(metrics_values))[-n]

        liked_categories = [category for category, score in calculated_metrics.items() if score >= threshold]
        return liked_categories

    def get_category_vector_from_df(self, category):
        return csr_matrix(self.df[category].values)


