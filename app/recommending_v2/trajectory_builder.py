from datetime import timedelta, datetime
from queue import PriorityQueue
from typing import List, Tuple

from recommending_v2.categories.estimated_visiting import VisitingTimeProvider
from recommending_v2.algorythm_models.point_of_interest import PointOfInterest
from recommending_v2.algorythm_models.schedule import Day
from recommending_v2.algorythm_models.trajectory import Trajectory
from recommending_v2.utils import dist, estimated_time, round_time


def build_trajectory(day: Day, pois_score: List[Tuple[PointOfInterest, float]],
                     time_provider: VisitingTimeProvider) -> Trajectory:
    # TODO: edge cases, check every poi on list before finishing schedule and 2-opt again
    if len(pois_score) == 0:
        return Trajectory()
    graph = [[dist(i, j) for i, _ in pois_score] for j, _ in pois_score]
    mst_graph = get_mst(graph)
    path = estimated_shp_from_mst(mst_graph)
    path2 = opt_2(path, graph)
    better_path = opt_1(path2, graph)

    visiting_time_provider = time_provider
    trajectory = Trajectory()

    curr: datetime = day.start
    travel_time: timedelta = timedelta()
    next_visiting: timedelta = visiting_time_provider.get_visiting_time(pois_score[better_path[0]][0])
    for n in range(len(path)):
        if curr + travel_time + next_visiting < day.end:
            trajectory.add_event(
                pois_score[better_path[n]][0],
                round_time(curr + travel_time),
                round_time(curr + travel_time + next_visiting))
            if n+1 >= len(path):
                break
            curr += travel_time + next_visiting
            curr = round_time(curr)
            travel_time = timedelta(seconds=estimated_time(graph[path[n]][path[n+1]]))
            next_visiting = visiting_time_provider.get_visiting_time(pois_score[better_path[n+1]][0])

    return trajectory


def get_mst(graph) -> List[List[int]]:
    dl = len(graph)
    mst = [[0 for _ in range(len(graph))] for _ in range(dl)]
    visited = [False for _ in range(dl)]
    queue = PriorityQueue()

    visited[0] = True
    for u in range(dl):
        if graph[0][u] > 0:
            queue.put((graph[0][u], (0, u)))
    vertices_left = dl - 1

    while vertices_left > 0:
        w, (v, u) = queue.get()
        if not visited[u]:
            visited[u] = True
            vertices_left -= 1
            mst[v][u] = 1
            mst[u][v] = 1
            for t in range(dl):
                if t != u and not visited[t]:
                    queue.put((graph[u][t], (u, t)))
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
                v_next = path[i + 1]
                u = path[j]
                u_prev = path[j - 1]
                d = -graph[v][v_next] - graph[u_prev][u] + graph[v][u_prev] + graph[v_next][u]
                if d < -10:
                    improvement = True
                    new_path = [path[k] for k in range(0, i + 1)]
                    for k in range(j - 1, i, -1):
                        new_path.append(path[k])
                    for m in range(j, len(path)):
                        new_path.append(path[m])
                    path = new_path

        n += 1
    return path


def opt_1(path, graph):
    dl = len(path)
    max_dist = 0
    new_start = 0
    for i in range(dl):
        if graph[path[i]][path[(i + 1) % dl]] > max_dist:
            max_dist = graph[path[i]][path[(i + 1) % dl]]
            new_start = (i + 1) % dl

    new_path = []
    for i in range(new_start, dl):
        new_path.append(path[i])
    for i in range(new_start):
        new_path.append(path[i])
    return new_path


if __name__ == "__main__":
    a = 'cat_amusement_parks'
    print(a[4:-1])
