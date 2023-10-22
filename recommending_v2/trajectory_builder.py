from datetime import timedelta, datetime
from typing import List, Tuple

from recommending_v2.categories.estimated_visiting import VisitingTimeProvider
from recommending_v2.model.point_of_interest import PointOfInterest
from recommending_v2.model.schedule import Day
from recommending_v2.model.trajectory import Trajectory
from recommending_v2.utils import dist, estimated_time


def build_trajectory(day: Day, pois_score: List[Tuple[PointOfInterest, float]]) -> Trajectory:
    # TODO: edge cases, check every poi on list before finishing schedule and 2-opt again
    if len(pois_score) == 0:
        return Trajectory()
    graph = [[dist(i, j) for i, _ in pois_score] for j, _ in pois_score]
    mst_graph = get_mst(graph)
    path = estimated_shp_from_mst(mst_graph)
    better_path = opt_2(path, graph)

    visiting_time_provider = VisitingTimeProvider()
    trajectory = Trajectory()
    n = 0
    curr: datetime = day.start
    travel_time: timedelta = timedelta()
    next_visiting: timedelta = visiting_time_provider.get_visiting_time(pois_score[better_path[0]][0])
    while curr + travel_time + next_visiting < day.end:
        trajectory.add_event(pois_score[better_path[n]][0], curr + travel_time, curr + travel_time + next_visiting)
        n += 1
        if n >= len(path):
            break

        curr += travel_time + next_visiting
        travel_time = timedelta(seconds=estimated_time(graph[path[n - 1]][path[n]]))
        next_visiting = visiting_time_provider.get_visiting_time(pois_score[better_path[n]][0])
        print(curr)
        print(travel_time)
        print(next_visiting)

    return trajectory


def get_mst(graph) -> List[List[int]]:
    root = [i for i in range(len(graph))]
    rank = [0 for _ in range(len(graph))]
    mst = [[0 for _ in range(len(graph))] for _ in range(len(graph))]

    def find(x) -> int:
        if x == root[x]:
            return x
        root[x] = find(root[x])
        return root[x]

    def union(x, y):
        root_x = find(x)
        root_y = find(y)
        if root_x == root_y:
            return
        if rank[root_x] > rank[root_y]:
            root[root_y] = root_x
        elif rank[root_y] > rank[root_x]:
            root[root_y] = root_x
        else:
            root[root_x] = root_y
            rank[root_y] += 1

    edges = []
    for row in range(len(graph)):
        for col in range(len(graph)):
            edges.append((graph[row][col], row, col))
    edges.sort(key=lambda x: x[0])
    v_left = len(graph)
    for d, u, v in edges:
        if find(u) == find(v):
            continue
        mst[u][v] = 1
        mst[v][u] = 1
        if rank[u] == 0:
            v_left -= 1
        if rank[v] == 0:
            v_left -= 1
        union(u, v)
        if v_left == 0:
            break
    return mst


def estimated_shp_from_mst(mst) -> List[int]:
    dl = len(mst)
    path = [0]
    deg = [2 * sum(mst[i]) for i in range(dl)]
    is_bridge = [[False for _ in range(dl)] for _ in range(dl)]

    def dfs(v):
        for u in range(dl):
            if mst[v][u] == 1 and deg[u] > 0 and not is_bridge[u][v]:
                path.append(u)
                deg[u] -= 1
                deg[v] -= 1
                is_bridge[u][v] = True
                is_bridge[v][u] = True
                dfs(u)
        for u in range(dl):
            if mst[v][u] == 1 and deg[u] > 0:
                deg[u] -= 1
                deg[v] -= 1
                dfs(u)

    dfs(0)
    return path


def opt_2(path, graph) -> List[int]:
    dl = len(path)
    improvement = True
    n = 0
    while improvement and n < 10:
        improvement = False
        for i in range(dl - 3):
            for j in range(i + 3, dl):
                v = path[i]
                v_next = path[i+1]
                u = path[j]
                u_prev = path[j-1]
                d = -graph[v][v_next] - graph[u_prev][u] + graph[v][u_prev] + graph[v_next][u]
                if d < -10:
                    improvement = True
                    new_path = [path[k] for k in range(0, i+1)]
                    for k in range(j - 1, i, -1):
                        new_path.append(path[k])
                    for m in range(j, len(path)):
                        new_path.append(path[m])
                    path = new_path

        n += 1
    return path


if __name__ == "__main__":
    for _i in range(5, 1, -1):
        print(_i)
