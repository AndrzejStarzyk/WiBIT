from typing import List

import folium
from flask import render_template
from recommending_v2.model.trajectory import Trajectory

map_center = (50.0619474, 19.9368564)


def create_map(trajectory: Trajectory) -> folium.Map:
    path = trajectory.pois
    m = folium.Map(location=map_center, zoom_start=12)
    if len(path) == 0:
        return m
    trail = []
    if len(trajectory.extra_info) == len(path):
        folium.Marker(
            location=(path[0].lat, path[0].lon),
            popup=render_template('popup.html',
                                  name=path[0].name,
                                  img=path[0].image,
                                  website=path[0].website,
                                  wiki=path[0].wiki,
                                  date=trajectory.extra_info[0][0],
                                  start=trajectory.extra_info[0][1],
                                  end=trajectory.extra_info[0][2]),
            icon=folium.Icon(color='orange')
        ).add_to(m)
    else:
        folium.Marker(
            location=(path[0].lat, path[0].lon),
            popup=render_template('popup.html',
                                  name=path[0].name,
                                  img=path[0].image,
                                  website=path[0].website,
                                  wiki=path[0].wiki),
            icon=folium.Icon(color='orange')
        ).add_to(m)
    trail.append((path[0].lat, path[0].lon))
    for idx in range(len(path)):
        if len(trajectory.extra_info) == len(path):
            folium.Marker(
                location=(path[idx].lat, path[idx].lon),
                popup=render_template('popup.html',
                                      name=path[idx].name,
                                      img=path[idx].image,
                                      website=path[idx].website,
                                      wiki=path[idx].wiki,
                                      date=trajectory.extra_info[idx][0],
                                      start=trajectory.extra_info[idx][1],
                                      end=trajectory.extra_info[idx][2]),
                icon=folium.Icon(color='red')
            ).add_to(m)
        else:
            folium.Marker(
                location=(path[idx].lat, path[idx].lon),
                popup=render_template('popup.html',
                                      name=path[idx].name,
                                      img=path[idx].image,
                                      website=path[idx].website,
                                      wiki=path[idx].wiki),
                icon=folium.Icon(color='red')
            ).add_to(m)
        trail.append((path[idx].lat, path[idx].lon))

    if len(trail) > 0:
        folium.PolyLine(trail).add_to(m)

    return m


if __name__ == '__main__':
    a = [1, 2, 3]
    for i in a[4: -1]:
        print(i)
