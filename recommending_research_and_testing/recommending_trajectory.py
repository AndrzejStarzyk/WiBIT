import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from torch import sigmoid

from opentripmaps_categories import *
from opentripmap_api import *


class Model(nn.Module):
    def __init__(self, input_size: int):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(input_size, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )

    def forward(self, x):
        return self.mlp(x)

    def predict_proba(self, x):
        return sigmoid(self(x))

    def predict(self, x):
        y_pred_score = self.predict_proba(x)
        return torch.argmax(y_pred_score, dim=1)


class Recommender:
    def __init__(self):
        self.trained = False
        self.labels_ids = {}
        self.n_parameters = 0
        self.learning_rate = 1e-3
        self.model = None
        self.optimizer = None

    def train(self):
        categories = CategoriesProvider().get_categories()
        places = OpenTripMapApiProvider().get_places()
        self.labels_ids = {}
        for i in range(len(categories)):
            self.labels_ids[categories[i]] = i

        for i in range(len(places)):
            self.labels_ids[places[i]['name']] = i + len(categories)

        length = len(categories) + len(places)
        self.n_parameters = length
        print(len(categories), len(places), length)
        X_list = []
        y_list = []
        for place in places:
            place_data = [0 for _ in range(length)]
            for cat in place['kinds'].split(','):
                place_data[self.labels_ids[cat]] = 1
            place_data[self.labels_ids[place['name']]] = 1
            X_list.append(place_data)
            y_list.append(1)

            place_data = [1 if i < len(categories) else 0 for i in range(length)]
            for cat in place['kinds'].split(','):
                place_data[self.labels_ids[cat]] = 0
            place_data[self.labels_ids[place['name']]] = 1
            X_list.append(place_data)
            y_list.append(0)

        X_train, X_test, y_train, y_test = train_test_split(X_list, y_list, test_size=0.2, random_state=0, shuffle=True)

        X_train, X_test, y_train, y_test = torch.tensor(X_train).float(), torch.tensor(X_test).float(), \
            torch.tensor(y_train).float().unsqueeze(-1), torch.tensor(y_test).float().unsqueeze(-1)
        print(y_train.shape)
        self.model = Model(input_size=X_train.shape[1])
        self.optimizer = torch.optim.SGD(self.model.parameters(), lr=self.learning_rate)

        loss_fn = torch.nn.BCEWithLogitsLoss()
        num_epochs = 2000
        evaluation_steps = 200
        loss = 0
        for i in range(num_epochs):
            y_pred = self.model(X_train)
            loss = loss_fn(y_pred, y_train)
            loss.backward()

            self.optimizer.step()
            self.optimizer.zero_grad()

            if i % evaluation_steps == 0:
                print(f"Epoch {i} train loss: {loss.item():.4f}")

        print(f"final loss: {loss.item():.4f}")
        self.trained = True

    def recommend(self, preferences):
        places = get_places()
        X = [0 for _ in range(self.n_parameters)]
        for category in preferences:
            X[self.labels_ids[category]] = 1
        self.model.predict()


if __name__ == "__main__":
    recommender = Recommender()
    recommender.train()
    print(recommender.recommend(['historic', 'architecture']))
