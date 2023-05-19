import string
import folium

map_center = (50.0619474, 19.9368564)


def create_map(pois: [(float, float, string)]):
    m = folium.Map(location=map_center)

    for coordinate in pois:
        folium.Marker(
            location=(coordinate[0], coordinate[1]),
            popup=coordinate[2],
            icon=folium.Icon(color='red')
        ).add_to(m)
    m.save("./templates/index.html")


if __name__ == '__main__':
    create_map([])
