from sklearn.model_selection import train_test_split
from surprise.dataset import Dataset, Reader
import pandas as pd
from surprise.prediction_algorithms.knns import KNNBasic
from random import randrange, choices
from copy import deepcopy
from typing import Dict, List
from reccomending_v1.opentripmaps_categories import CategoriesProvider
from reccomending_v1.opentripmap_api import OpenTripMapApiProvider


class Recommender:
    def __init__(self):
        self.categories_provider = CategoriesProvider()
        self.api_provider = OpenTripMapApiProvider()
        self.users = None
        self.places = None
        self.train_set = None
        self.test_set = None
        self.model = None

    def train(self):
        categories = self.categories_provider.get_categories()
        places = self.api_provider.get_places()
        self.places = places
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
            j = 0
            while j < len(places):
                data_dict['user'].append(i)
                data_dict['place'].append(j)
                data_dict['score'].append(self.categories_provider.get_score(user, places[j]['kinds'].split(',')))
                j += randrange(1, 5)

        self.users = users
        data_df = pd.DataFrame(data_dict)
        reader = Reader(rating_scale=(data_df['score'].min(), data_df['score'].max()))
        dataset = Dataset.load_from_df(data_df, reader=reader)

        X, y = train_test_split(
            dataset.raw_ratings, test_size=0.4, random_state=1
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

    def get_recommended(self, preferences: List[str]):
        user_to_sort = []
        for i in range(len(self.users)):
            user_to_sort.append((i, self.categories_provider.get_score(self.users[i], preferences)))
        user_to_sort.sort(key=lambda x: x[1], reverse=True)
        users_id = map(lambda x: x[0], user_to_sort[:3])
        print(user_to_sort)
        recommended: Dict[int, int] = {}
        for user_id in users_id:
            semi_recommended = []
            for i in range(len(self.api_provider.get_places())):
                semi_recommended.append((i, self.model.predict(user_id, i)[3]))
            semi_recommended.sort(key=lambda x: x[1], reverse=True)

            for item in semi_recommended[:5]:
                if item[0] in recommended:
                    recommended[item[0]] = recommended[item[0]] + item[1]
                else:
                    recommended[item[0]] = item[1]
        res = [(self.places[item[0]], item[1]) for item in recommended.items()]
        res.sort(key=lambda x: x[1], reverse=True)
        return map(lambda x: x[0], res[0:5])


if __name__ == "__main__":
    recommender = Recommender()
    recommender.train()
    recommender.get_recommended(['towers'])
