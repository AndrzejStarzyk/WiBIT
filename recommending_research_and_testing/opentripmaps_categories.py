import json
from typing import Union, List

import requests


class CategoriesProvider:
    def __init__(self):
        self.categories_list: List[str] = []
        self.categories_graph: List[List[int]] = []
        self.max_score = 0
        self.min_score = 0
        self.categories_fetched = False
        self.categories_url = "https://opentripmap.io/catalog.en.json"
        self.fetch_categories()

    def fetch_categories(self):
        response = requests.get(self.categories_url)

        catalog = json.loads(response.text)
        self.categories_list = ['everything']
        self.categories_graph = [[]]

        def dfs(node: dict):
            id_ = 0
            if 'id' in node:
                self.categories_list.append(node.get('id'))
                self.categories_graph.append([])
                id_ = len(self.categories_list) - 1
            if 'children' in node:
                for child in node.get('children'):
                    child_id = dfs(child)
                    self.categories_graph[id_].append(child_id)
                    self.categories_graph[child_id].append(id_)
            return id_

        dfs(catalog)
        self.get_max_distance()
        self.categories_fetched = True

    def get_categories(self) -> List[str]:
        if not self.categories_fetched:
            self.fetch_categories()
        return self.categories_list

    def distance(self, place1: str, place2: str) -> int:
        if not self.categories_fetched:
            self.fetch_categories()
        try:
            start = self.categories_list.index(place1)
            dest = self.categories_list.index(place2)

            def dfs(i: int, dist: int, parent: Union[int, None]):
                if i == dest:
                    return dist, True

                for j in self.categories_graph[i]:
                    if parent is None or j != parent:
                        d, found = dfs(j, dist + 1, i)
                        if found:
                            return d, True
                return dist, False

            distance, reached = dfs(start, 0, None)
            if not reached:
                return -1

            return distance

        except ValueError:
            print("No such place on the list of categories", place1, place2)
        return -1

    def get_max_distance(self):
        def max_dist(node: int, parent: Union[int, None]):
            if len(self.categories_graph[node]) == 1:
                return 0, 0
            max_in_this_subtree = 0
            max_paths = []
            for child in self.categories_graph[node]:
                if parent is None or child != parent:
                    max_from_node, max_in_subtree = max_dist(child, node)
                    max_paths.append(max_from_node)
                    max_in_this_subtree = max(max_in_this_subtree, max_in_subtree)

            max_from_this_node = max(max_paths) + 1
            max_via_this_node = max_from_this_node
            if len(max_paths) > 1:
                max_paths.sort(reverse=True)
                max_via_this_node = max_paths[0] + max_paths[1] + 2
            max_in_this_subtree = max(max_in_this_subtree, max_via_this_node)
            return max_from_this_node, max_in_this_subtree

        _, res = max_dist(0, None)
        self.max_score = res

    def to_score(self, dist):
        if not self.categories_fetched:
            self.fetch_categories()
        return self.max_score - dist

    def get_score(self, preferences: List[str], categories: List[str]):
        if len(preferences) == 0 or len(categories) == 0:
            return 0

        score = 0
        for preference in preferences:
            total_dist = 0
            for category in categories:
                dist = self.distance(preference, category)
                if dist > -1:
                    total_dist += dist
            score += self.to_score(total_dist / len(categories))
        return score / len(preferences)


if __name__ == "__main__":
    provider = CategoriesProvider()
    provider.get_categories()
    print(provider.get_score(['historic', 'archaeology'], ['canyons', 'cinemas', 'stone_bridges']))
