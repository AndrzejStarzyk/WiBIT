import math
from typing import List, Tuple

import folium

from recommending_v2.model.trajectory import Trajectory
from recommending_v2.model.point_of_interest import PointOfInterest

map_center = (50.0619474, 19.9368564)


def create_map(path: List[PointOfInterest]) -> folium.Map:
    m = folium.Map(location=map_center, zoom_start=13)
    if len(path) == 0:
        return m
    trail = []
    folium.Marker(
        location=(path[0].lat, path[0].lon),
        popup=path[0].name,
        icon=folium.Icon(color='orange')
    ).add_to(m)
    trail.append((path[0].lat, path[0].lon))
    for coordinate in path[1:]:
        folium.Marker(
            location=(coordinate.lat, coordinate.lon),
            popup=coordinate.name,
            icon=folium.Icon(color='red')
        ).add_to(m)
        trail.append((coordinate.lat, coordinate.lon))

    if len(trail) > 0:
        folium.PolyLine(trail).add_to(m)

    return m


def pretty_path(trajectory: Trajectory()) -> List[PointOfInterest]:
    dl = len(trajectory.pois)
    if dl < 2:
        return trajectory.pois
    graph = [[math.sqrt((coordinates1.lon - coordinates2.lon) * (coordinates1.lon - coordinates2.lon) +
                        (coordinates1.lat - coordinates2.lat) * (coordinates1.lat - coordinates2.lat))
              for coordinates2 in trajectory.pois] for coordinates1 in trajectory.pois]

    shortest_paths: List[List[Tuple[float, int]]] = [[(0, -1) for _ in range(0, dl - 1)] for _ in range(0, 2 ** (dl - 1))]
    max_sum = sum([sum(graph[i]) for i in range(0, dl)])
    for i in range(0, dl-1):
        shortest_paths[0][i] = (graph[dl-1][i], 0)

    def number_to_permutation(n_: int) -> List[int]:
        res_: List[int] = []
        for i_ in range(0, dl-1):
            if n_ % 2 == 1:
                res_.append(i_)
            n_ = n_ // 2
        return res_

    def compute(row_, col_):

        perm = number_to_permutation(row_)

        shortest_ = max_sum
        pre_last_ = -1
        for i_ in perm:
            if shortest_paths[row_ - 2**i_][i_][1] == -1:
                compute(row_ - 2**i_, i_)
            if shortest_paths[row_ - 2**i_][i_][0] + graph[i_][col_] < shortest_:
                shortest_ = shortest_paths[row_ - 2**i_][i_][0] + graph[i_][col_]
                pre_last_ = i_
        shortest_paths[row_][col_] = (shortest_, pre_last_)

    shortest = max_sum
    last = -1
    for col in range(0, dl-1):
        row = 2**(dl-1) - 1 - 2**col
        if shortest_paths[row][col][1] == -1:
            compute(row, col)
        if shortest_paths[row][col][0] < shortest:
            shortest = shortest_paths[row][col][0]
            last = col

    path = []
    row = 2**(dl-1) - 1 - 2**last
    for i in range(0, dl-1):
        path.append(last)
        last = shortest_paths[row][last][1]
        row -= 2**last
    path.append(dl-1)

    longest = graph[path[0]][path[dl-1]]
    first = 0
    for i in range(0, dl-1):
        if graph[path[i]][path[i+1]] > longest:
            longest = graph[path[i]][path[i+1]]
            first = i

    res = []
    for i in range(first, dl):
        res.append(path[i])
    for i in range(0, first):
        res.append(path[i])

    return [trajectory.pois[i] for i in res]


if __name__ == '__main__':
    a = [1, 2, 3]
    for i in a[4: -1]:
        print(i)
