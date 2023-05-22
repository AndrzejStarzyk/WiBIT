import string

from sklearn.model_selection import train_test_split
from surprise.dataset import Dataset, Reader
import pandas as pd
from surprise.prediction_algorithms.knns import KNNBasic
from random import randrange, choices

from copy import deepcopy
from opentripmaps_categories import CategoriesProvider
from opentripmap_api import OpenTripMapApiProvider


class Recommender:
    def __init__(self):
        self.categories_provider = CategoriesProvider()
        self.api_provider = OpenTripMapApiProvider()
        self.train_set = None
        self.test_set = None
        self.model = None

    def train(self):
        categories = self.categories_provider.get_categories()
        places = self.api_provider.get_places()

        data_dict = {
            'user': [],
            'place': [],
            'score': []
        }

        users = []
        length = 10
        max_preferences_len = 10
        min_preferences_len = 2
        for _ in range(length):
            user = choices(categories, k=randrange(min_preferences_len, max_preferences_len + 1))
            users.append(user)
            i = len(users)
            for j in range(len(places)):
                data_dict['user'].append(i)
                data_dict['place'].append(j)
                data_dict['score'].append(self.categories_provider.get_score(user, places[j]['kinds'].split(',')))

        data_df = pd.DataFrame(data_dict)
        print(data_df)
        reader = Reader(rating_scale=(0, 1))
        dataset = Dataset.load_from_df(data_df, reader=reader)

        X, y = train_test_split(
            dataset.raw_ratings, test_size=0.2, random_state=1
        )

        data_train = deepcopy(dataset)
        data_train.raw_ratings = X

        self.train_set = data_train.build_full_trainset()
        self.test_set = data_train.construct_testset(y)

        self.model = KNNBasic()
        self.model.fit(self.train_set)

    def test(self):
        pred_knn_basic = self.model.test(self.test_set)
        print(pred_knn_basic[:5])

    def get_recommended(self, preferences: [string]):
        pass


if __name__ == "__main__":
    recommender = Recommender()
    recommender.train()
    recommender.test()
