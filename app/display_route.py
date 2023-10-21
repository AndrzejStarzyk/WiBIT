import folium
from flask import render_template
from recommending_v2.model.trajectory import Trajectory

map_center = (50.0619474, 19.9368564)


def create_map(trajectory: Trajectory) -> folium.Map:
    m = folium.Map(location=map_center, zoom_start=12)
    path = trajectory.events
    if len(path) == 0:
        return m
    trail = []
    for idx in range(len(path)):
        folium.Marker(
            location=(path[idx].poi.lat, path[idx].poi.lon),
            popup=render_template('popup.html',
                                  name=path[idx].poi.name,
                                  img=path[idx].poi.image,
                                  website=path[idx].poi.website,
                                  wiki=path[idx].poi.wiki,
                                  start=path[idx].start,
                                  end=path[idx].end,
                                  icon=folium.Icon(color='red'))
        ).add_to(m)
        trail.append((path[idx].poi.lat, path[idx].poi.lon))

    if len(trail) > 0:
        folium.PolyLine(trail).add_to(m)

    return m


if __name__ == '__main__':
    a = [1, 2, 3]
    for i in a[4: -1]:
        print(i)
