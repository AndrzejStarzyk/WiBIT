import math
from typing import List, Tuple

import folium

map_center = (50.0619474, 19.9368564)


def create_map(pois: [(float, float, str)]):
    m = folium.Map(location=map_center, zoom_start=16)
    trail = []
    for coordinate in pretty_path(pois):
        folium.Marker(
            location=(coordinate[1], coordinate[0]),
            popup=coordinate[2],
            icon=folium.Icon(color='red')
        ).add_to(m)
        trail.append((coordinate[1], coordinate[0]))
    if len(trail) > 0:
        folium.PolyLine(trail).add_to(m)
    m.save("./templates/map.html")


def pretty_path(places: List[Tuple[float, float]]):
    dl = len(places)
    graph = [[math.sqrt((coordinates1[0] - coordinates2[0]) * (coordinates1[0] - coordinates2[0]) +
                        (coordinates1[1] - coordinates2[1]) * (coordinates1[1] - coordinates2[1]))
              for coordinates2 in places] for coordinates1 in places]
    route = [places[0]]
    visited = [False for _ in range(dl)]

    def visit(node):
        visited[node] = True
        next_nodes = [(i, graph[node][i]) for i in range(dl)]
        next_nodes.sort(key=lambda x: x[1])
        for next_node in next_nodes:
            if not visited[next_node[0]]:
                route.append(places[next_node[0]])
                visit(next_node[0])

    visit(0)
    return route


if __name__ == '__main__':
    create_map([])
