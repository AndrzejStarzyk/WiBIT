from typing import List, Tuple
from numpy import inf
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from pyvis.network import Network

from category import Category

very_low_score = 0


class CategoriesProvider:
    def __init__(self):
        self.categories_list: List[Category] = []
        self.categories_dict: dict[str: int] = {}
        self.categories_ids: List[int] = []
        self.categories_graph: List[List[Tuple[int, int]]] = []
        self.categories_distances: List[List[Tuple[int, int]]] = []
        self.max_score = 0
        self.min_score = 0
        self.categories_fetched = False
        self.distances_computed = False
        self.mongodb_uri = f"mongodb+srv://andrzej:passwordas@wibit.4d0e5vs.mongodb.net/?retryWrites=true&w=majority"

        self.fetch_categories()
        self.compute_shortest_paths()

    def fetch_categories(self):
        client = MongoClient(self.mongodb_uri, server_api=ServerApi('1'))
        try:
            client.admin.command('ping')
            print("Successfully connected to MongoDB!")
        except Exception as e:
            print(e)

        db = client["wibit"]
        collection = db["categories-graph"]
        edges = collection.find()

        collection2 = db["categories"]
        categories = collection2.find()

        for cat in categories:
            self.categories_list.append(Category(
                cat.get("name"),
                cat.get("code"),
                cat.get("visiting_time").get("hours"),
                cat.get("visiting_time").get("minutes"),
                cat.get("id")
            ))
            self.categories_ids.append(cat.get("id"))
            self.categories_graph.append([])
            self.categories_dict[cat.get("code")] = len(self.categories_ids) - 1

            if cat.get('additional_codes') is None:
                continue
            for code in cat.get('additional_codes'):
                self.categories_dict[code] = len(self.categories_ids) - 1

        for edge in edges:
            self.categories_graph[self.categories_ids.index(edge.get("from_id"))] \
                .append((self.categories_ids.index(edge.get("to_id")), edge.get("weight")))
            self.categories_graph[self.categories_ids.index(edge.get("to_id"))] \
                .append((self.categories_ids.index(edge.get("from_id")), edge.get("weight")))

        self.categories_fetched = True

    def compute_shortest_paths(self):
        n = len(self.categories_ids)
        self.categories_distances = [[inf for _ in range(n)] for _ in range(n)]
        for u in range(n):
            self.categories_distances[u][u] = 0
            for v, w in self.categories_graph[u]:
                self.categories_distances[u][v] = w

        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if self.categories_distances[i][j] > self.categories_distances[i][k] + \
                            self.categories_distances[k][j]:
                        self.categories_distances[i][j] = self.categories_distances[i][k] + \
                                                          self.categories_distances[k][j]
        self.distances_computed = True

    def distance(self, cat1, cat2):
        if cat1 not in self.categories_dict.keys() or cat2 not in self.categories_dict.keys():
            return None
        idx1 = self.categories_dict.get(cat1)
        idx2 = self.categories_dict.get(cat2)
        return self.categories_distances[idx1][idx2]

    def compute_score(self, preferences: List[str], categories: List[str]) -> float:
        if not self.distances_computed:
            self.compute_shortest_paths()

        if len(preferences) == 0 or len(categories) == 0:
            return very_low_score

        total_dist = 0
        only_nones = True
        for pref in preferences:
            sum_dist = 0
            for cat in categories:
                dist = self.distance(pref, cat)
                if dist is not None:
                    sum_dist += dist
                    only_nones = False

            total_dist += sum_dist / len(categories)
        if only_nones:
            return very_low_score
        return total_dist / len(preferences)

    def show_graph(self):
        if not self.categories_fetched:
            self.fetch_categories()
        N = Network()
        for cat in range(len(self.categories_ids)):
            N.add_node(self.categories_ids[cat], self.categories_list[cat].name, size=8)

        for u in range(len(self.categories_graph)):
            for v, _ in self.categories_graph[u]:
                N.add_edge(self.categories_ids[u], self.categories_ids[v])

        N.toggle_physics(True)
        N.show_buttons(True)
        N.force_atlas_2based()
        N.show("categories_graph.html", notebook=False)


if __name__ == "__main__":
    cp = CategoriesProvider()
    cp.show_graph()
