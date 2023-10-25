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
        self.code_to_graph_id: dict[str: int] = {}
        self.category_ids: List[int] = []
        self.categories_graph: List[List[Tuple[int, int]]] = []
        self.categories_distances: List[List[Tuple[int, int]]] = []

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
            self.category_ids.append(cat.get("id"))
            self.categories_graph.append([])
            self.code_to_graph_id[cat.get("code")] = len(self.category_ids) - 1

            if cat.get('additional_codes') is None:
                continue
            for code in cat.get('additional_codes'):
                self.code_to_graph_id[code] = len(self.category_ids) - 1

        for edge in edges:
            v = self.category_ids.index(edge.get("from_id"))
            u = self.category_ids.index(edge.get("to_id"))
            self.categories_graph[v].append((u, edge.get("weight")))
            self.categories_graph[u].append((v, edge.get("weight")))

        categories.rewind()
        for cat in categories:
            self.categories_list.append(Category(
                cat.get("name"),
                cat.get("code"),
                cat.get("visiting_time").get("hours"),
                cat.get("visiting_time").get("minutes"),
                cat.get("id"),
                len(self.categories_graph[self.category_ids.index(cat.get("id"))]) > 1
            ))

        self.categories_fetched = True

    def compute_shortest_paths(self):
        n = len(self.category_ids)
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
        if cat1 not in self.code_to_graph_id.keys() or cat2 not in self.code_to_graph_id.keys():
            return None
        idx1 = self.code_to_graph_id.get(cat1)
        idx2 = self.code_to_graph_id.get(cat2)
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

    def get_categories(self):
        if not self.categories_fetched:
            self.fetch_categories()
        return self.categories_list

    def get_main_categories(self):
        if not self.categories_fetched:
            self.fetch_categories()
        return list(filter(lambda x: x.is_main, self.categories_list))

    def get_subcategories(self, main_categories=None):
        if not self.categories_fetched:
            self.fetch_categories()
        if main_categories is None:
            return list(filter(lambda x: not x.is_main, self.categories_list))
        ids = [self.code_to_graph_id[code] for code, checked in main_categories if checked == "on"]
        return list(
            filter(lambda x: not x.is_main and self.categories_graph[self.code_to_graph_id[x.code]][0][0] in ids,
                   self.categories_list))

    def show_graph(self):
        if not self.categories_fetched:
            self.fetch_categories()
        N = Network()
        for cat in range(len(self.category_ids)):
            N.add_node(self.category_ids[cat], self.categories_list[cat].name, size=8)

        for u in range(len(self.categories_graph)):
            for v, _ in self.categories_graph[u]:
                N.add_edge(self.category_ids[u], self.category_ids[v])

        N.toggle_physics(True)
        N.show_buttons(True)
        N.force_atlas_2based()
        N.show("categories_graph.html", notebook=False)


if __name__ == "__main__":
    cp = CategoriesProvider()
    cp.show_graph()
