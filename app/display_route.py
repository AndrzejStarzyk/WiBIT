import folium
from flask import render_template

from recommending_v2.algorythm_models.trajectory import Trajectory

map_center = (50.0619474, 19.9368564)


def create_map(trajectory: Trajectory) -> folium.Map:
    m = folium.Map(location=map_center, zoom_start=12)
    path = trajectory.events
    if len(path) == 0:
        return m
    trail = []
    for i in range(len(path)):
        folium.Marker(
            location=(path[i].poi.lat, path[i].poi.lon),
            popup=render_template('popup.html',
                                  name=path[i].poi.name,
                                  img=path[i].poi.image,
                                  website=path[i].poi.website,
                                  wiki=path[i].poi.wiki,
                                  start=path[i].start,
                                  end=path[i].end),
            icon=folium.Icon(color=color(i))
        ).add_to(m)
        trail.append((path[i].poi.lat, path[i].poi.lon))

    if len(trail) > 0:
        folium.PolyLine(trail).add_to(m)

    return m


def color(i):
    if i == 0:
        return "orange"
    else:
        return 'blue'


if __name__ == '__main__':
    a = [1, 2, 3]
    for i_ in a[4: -1]:
        print(i_)
