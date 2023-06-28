import math
from typing import List, Tuple

import folium

from recommending_v2.model.trajectory import Trajectory
from recommending_v2.model.point_of_interest import PointOfInterest

map_center = (50.0619474, 19.9368564)


def create_map(trajectory: Trajectory()) -> folium.Map:
    m = folium.Map(location=map_center, zoom_start=16)
    trail = []
    for coordinate in pretty_path(trajectory):
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
    graph = [[math.sqrt((coordinates1.lon - coordinates2.lon) * (coordinates1.lon - coordinates2.lon) +
                        (coordinates1.lat - coordinates2.lat) * (coordinates1.lat - coordinates2.lat))
              for coordinates2 in trajectory.pois] for coordinates1 in trajectory.pois]
    route = [trajectory.pois[0]]
    visited = [False for _ in range(dl)]

    def visit(node):
        visited[node] = True
        next_nodes = [(i, graph[node][i]) for i in range(dl)]
        next_nodes.sort(key=lambda x: x[1])
        for next_node in next_nodes:
            if not visited[next_node[0]]:
                route.append(trajectory.pois[next_node[0]])
                visit(next_node[0])

    visit(0)
    return route


if __name__ == '__main__':
    pass
