from typing import List, Tuple, Union, Dict
from numpy import inf

from pyvis.network import Network

from recommending_v2.categories.category import Category
from models.mongo_utils import MongoUtils

very_low_score = 0
subcategory_match_score = 2
main_category_match_score = 1


class CategoriesProvider:
    def __init__(self, db_connection: MongoUtils):
        self.db_connection = db_connection

        self.categories_list: List[Category] = []
        self.code_to_graph_id: Dict[str: int] = {}
        self.category_ids: List[int] = []
        self.categories_graph: List[List[Tuple[int, int]]] = []  # adjacency lists with weights
        self.categories_distances: List[List[Tuple[int, int]]] = []  # graph matrix with shortest distances

        self.additional_codes_mappings: Dict[str, str] = {}

        self.categories_fetched = False
        self.distances_computed = False

        self.fetch_categories()
        self.compute_shortest_paths()

    def fetch_categories(self):

        collection = self.db_connection.get_collection("categories-graph")
        edges = collection.find()

        collection2 = self.db_connection.get_collection("categories")
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
            additional = cat.get("additional_codes")
            if additional is not None:
                for code in additional:
                    self.additional_codes_mappings[code] = cat.get("code")

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

    def compute_score(self, preferences: List[str], kinds: List[str]) -> float:
        if not self.distances_computed:
            self.compute_shortest_paths()

        if len(preferences) == 0 or len(kinds) == 0:
            return very_low_score

        score = 0
        categories: List[str] = list(map(lambda x: x.code, self.get_categories()))
        subcategories: List[str] = list(map(lambda x: x.code, self.get_subcategories()))

        set_pref: set = set()
        set_cat: set = set()

        for pref in preferences:
            if pref in self.additional_codes_mappings.keys():
                set_pref.add(self.additional_codes_mappings[pref])
            elif pref in categories:
                set_pref.add(pref)
        for cat in kinds:
            if cat in self.additional_codes_mappings.keys():
                set_cat.add(self.additional_codes_mappings[cat])
            elif cat in categories:
                set_cat.add(cat)

        union = set_cat & set_pref
        for i in union:
            if i in subcategories:
                score += subcategory_match_score
                set_cat.remove(i)
                set_pref.remove(i)
        union.clear()

        for i in set_cat.copy():
            if i in subcategories:
                set_cat.remove(i)
                for j in self.get_super_of_categories(i):
                    set_cat.add(j)

        for i in set_pref.copy():
            if i in subcategories:
                set_pref.remove(i)
                for j in self.get_super_of_categories(i):
                    set_pref.add(j)

        union = set_cat & set_pref
        for i in union:
            score += main_category_match_score
            set_cat.remove(i)
            set_pref.remove(i)

        total_weight = 0
        total = 0
        for i in set_cat:
            i_id = self.code_to_graph_id[i]
            for j in set_pref:
                j_id = self.code_to_graph_id[j]
                for k, w in self.categories_graph[i_id]:
                    if k == j_id:
                        total_weight += w
                        total += 1

        if total != 0:
            score += 1 / (1 + total_weight / total)

        return score

    def get_super_of_categories(self, code: str, check_shortcuts: bool = True) -> List[str]:
        if not self.categories_fetched:
            self.fetch_categories()

        cat_id = self.code_to_graph_id[code]
        cat = self.categories_list[cat_id]
        if cat.is_main:
            return [code]

        res: List[str] = []
        main_categories: List[str] = list(map(lambda x: x.code, self.get_main_categories()))
        for v, w in self.categories_graph[cat_id]:
            neighbour = self.categories_list[v].code
            if check_shortcuts:
                for k in self.get_super_of_categories(neighbour, False):
                    res.append(k)
            elif neighbour in main_categories:
                res.append(neighbour)
        return res

    def get_categories(self):
        if not self.categories_fetched:
            self.fetch_categories()
        return self.categories_list

    def get_main_categories(self):
        if not self.categories_fetched:
            self.fetch_categories()
        return list(filter(lambda x: x.is_main, self.categories_list))

    def get_subcategories(self, main_categories: Union[None, List[str]] = None):
        if not self.categories_fetched:
            self.fetch_categories()
        if main_categories is None:
            return list(filter(lambda x: not x.is_main, self.categories_list))
        ids = [self.code_to_graph_id[code] for code in main_categories]
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
    cp = CategoriesProvider(MongoUtils())
    cp.show_graph()

