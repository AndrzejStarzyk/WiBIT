from typing import List


def determine_kinds(tags):
    kinds: List[str] = []
    for mapping in mappings:
        kind = mapping.get("code")
        if kind is None or mapping.get("query_parameters") is None:
            continue
        for parameter in mapping.get("query_parameters"):
            if tags.get(parameter.get("key")) is not None and tags.get(parameter.get("key")) == parameter.get("value"):
                kinds.append(kind)
    return kinds


mappings = [
    {
        "code": "attraction",
        "query_parameters": [{
            "key": "tourist",
            "value": "attraction"
        }],
    }, {
        "code": "amusement_parks",
        "query_parameters": [{
            "key": "tourist",
            "value": "theme_park"
        }],
    }, {
        "code": "ferris_wheels",
        "query_parameters": [{
            "key": "attraction",
            "value": "big_wheel"
        }],
    }, {
        "code": "water_parks",
        "query_parameters": [{
            "key": "leisure",
            "value": "water_park"
        }],
    }, {
        "code": "miniature_parks"
    }, {
        "code": "baths_and_saunas",
        "query_parameters": [{
            "key": "leisure",
            "value": "sauna"
        }, {
            "key": "amenity",
            "value": "public_bath"
        }],
    }, {
        "code": "sport",
        "query_parameters": [{
            "key": "sport",
            "value": "*"
        }],
    }, {
        "code": "climbing",
        "query_parameters": [{
            "key": "route",
            "value": "hiking"
        }],
    }, {
        "code": "stadiums",
        "query_parameters": [{
            "key": "leisure",
            "value": "stadium"
        }],
    }, {
        "code": "winter_sports",
        "query_parameters": [{
            "key": "landuse",
            "value": "winter_sport"
        }],
    }, {
        "code": "natural",
        "query_parameters": [{
            "key": "natural",
            "value": "*"
        }],
    }, {
        "code": "natural_springs",
        "query_parameters": [{
            "key": "natural",
            "value": "spring"
        }],
    }, {
        "code": "water",
        "query_parameters": [{
            "key": "natural",
            "value": "water"
        }],
    }, {
        "code": "nature_reserves",
        "query_parameters": [{
            "key": "leisure",
            "value": "nature_reserve"
        }],
    }, {
        "code": "beaches",
        "query_parameters": [{
            "key": "natural",
            "value": "beach"
        }],
    }, {
        "code": "industrial_facilities"
    }, {
        "code": "railway_stations",
        "query_parameters": [{
            "key": "museum",
            "value": "railway"
        }],
    }, {
        "code": "dams",
        "query_parameters": [{
            "key": "waterway",
            "value": "dam"
        }],
    }, {
        "code": "mints"
    }, {
        "code": "mineshafts",
        "query_parameters": [{
            "key": "historic",
            "value": "mine"
        }],
    }, {
        "code": "science_museums",
        "additional_codes": ["museums_of_science_and_technology"],
        "query_parameters": [{
            "key": "museum",
            "value": "science"
        }, {
            "key": "museum",
            "value": "technology"
        }],
    }, {
        "code": "religion",
        "query_parameters": [{
            "key": "religion",
            "value": "*"
        }],
    }, {
        "code": "churches",
        "query_parameters": [{
            "key": "historic",
            "value": "church"
        }],
    }, {
        "code": "cathedrals",
        "query_parameters": [{
            "key": "building",
            "value": "cathedral"
        }],
    }, {
        "code": "monasteries",
        "query_parameters": [{
            "key": "historic",
            "value": "monastery"
        }],
    }, {
        "code": "synagogues",
        "query_parameters": [{
            "key": "building",
            "value": "synagogue"
        }],
    }, {
        "code": "hindu_temples",
        "query_parameters": [{
            "key": "religion",
            "value": "hindu"
        }],
    }, {
        "code": "mosques",
        "query_parameters": [{
            "key": "historic",
            "value": "mosque"
        }],
    }, {
        "code": "archaeology",
        "query_parameters": [{
            "key": "historic",
            "value": "archaeological_site"
        }, {
            "key": "archaeological_site",
            "value": "*"
        }],
    }, {
        "code": "historical_places",
        "additional_codes": ["fortifications", "historic"],
        "query_parameters": [{
            "key": "historic",
            "value": "*"
        }],
    }, {
        "code": "castles",
        "query_parameters": [{
            "key": "historic",
            "value": "castle"
        }],
    }, {
        "code": "fortified_towers",
        "query_parameters": [{
            "key": "historic",
            "value": "tower"
        }],
    }, {
        "code": "bunkers",
        "query_parameters": [{
            "key": "military",
            "value": "bunker"
        }],
    }, {
        "code": "military_museums",
        "query_parameters": [{
            "key": "museum",
            "value": "military"
        }],
    }, {
        "code": "battlefields",
        "query_parameters": [{
            "key": "historic",
            "value": "battlefield"
        }],
    }, {
        "code": "war_graves",
        "query_parameters": [{
            "key": "cemetery",
            "value": "war_cemetery"
        }],
    }, {
        "code": "war_memorials",
        "query_parameters": [{
            "key": "memorial",
            "value": "war_memorial"
        }],
    }, {
        "code": "burial_places"
    }, {
        "code": "cemeteries",
        "query_parameters": [{
            "key": "landuse",
            "value": "cemetery"
        }, {
            "key": "amenity",
            "value": "grave_yard"
        }],
    }, {
        "code": "necropolises",
        "query_parameters": [{
            "key": "archaeological_site",
            "value": "necropolis"
        }],
    }, {
        "code": "mausoleums",
        "query_parameters": [{
            "key": "tomb",
            "value": "mausoleum"
        }],
    }, {
        "code": "crypts",
        "query_parameters": [{
            "key": "amenity",
            "value": "crypt"
        }],
    }, {
        "code": "urban_environment"
    }, {
        "code": "wall_painting",
        "query_parameters": [{
            "key": "artwork_type",
            "value": "mural"
        }],
    }, {
        "code": "fountains",
        "query_parameters": [{
            "key": "fountain",
            "value": "decorative"
        }],
    }, {
        "code": "sculptures",
        "additional_codes": ["installations"],
        "query_parameters": [{
            "key": "artwork_type",
            "value": "sculpture"
        }],
    }, {
        "code": "gardens_and_parks",
        "query_parameters": [{
            "key": "leisure",
            "value": "garden"
        }, {
            "key": "leisure",
            "value": "park"
        }],
    }, {
        "code": "museums",
        "query_parameters": [{
            "key": "tourism",
            "value": "museum"
        }],
    }, {
        "code": "archaeological_museums",
        "query_parameters": [{
            "key": "museum",
            "value": "archaeological"
        }],
    }, {
        "code": "art_galleries",
        "query_parameters": [{
            "key": "tourism",
            "value": "gallery"
        }],
    }, {
        "code": "biographical_museums",
        "query_parameters": [{
            "key": "museum",
            "value": "person"
        }],
    }, {
        "code": "history_museums",
        "additional_codes": ["historic_house_museums"],
        "query_parameters": [{
            "key": "museum",
            "value": "history"
        }],
    }, {
        "code": "local_museums",
        "query_parameters": [{
            "key": "museum",
            "value": "local"
        }],
    }, {
        "code": "national_museums",
        "query_parameters": [{
            "key": "museum_type",
            "value": "national"
        }],
    }, {
        "code": "fashion_museums"
    }, {
        "code": "nature_museums",
        "query_parameters": [{
            "key": "museum",
            "value": "nature"
        }],
    }, {
        "code": "planetariums",
        "query_parameters": [{
            "key": "amenity",
            "value": "planetarium"
        }],
    }, {
        "code": "zoos",
        "query_parameters": [{
            "key": "tourism",
            "value": "zoo"
        }],
    }, {
        "code": "aquariums",
        "query_parameters": [{
            "key": "tourism",
            "value": "aquarium"
        }],
    }, {
        "code": "architecture",
        "query_parameters": [{
            "key": "artwork_type",
            "value": "architecture"
        }],
    }, {
        "code": "skyscrapers"
    }, {
        "code": "towers",
        "query_parameters": [{
            "key": "building",
            "value": "tower"
        }],
    }, {
        "code": "historic_architecture",
        "query_parameters": [{
            "key": "historic",
            "value": "building"
        }],
    }, {
        "code": "bridges",
        "query_parameters": [{
            "key": "building",
            "value": "bridge"
        }],
    }, {
        "code": "memorials",
        "query_parameters": [{
            "key": "historic",
            "value": "memorial"
        }],
    }, {
        "code": "monuments",
        "query_parameters": [{
            "key": "historic",
            "value": "monument"
        }],
    }, {
        "code": "tumuluses",
        "query_parameters": [{
            "key": "archaeological_site",
            "value": "tumulus"
        }],
    },
]

"""
,
        "query_parameters": [{
            "key": "",
            "value": ""
        }],
{
    "attraction":,
    "amusement_parks":,
    "ferris_wheels":,
    "water_parks":,
    "miniature_parks":,
    "baths_and_saunas":,
    "sport":,
    "climbing":,
    "stadiums":,
    "winter_sports":,
    "natural":,
    "natural_springs":,
    "water":,
    "nature_reserves":,
    "beaches":,
    "industrial_facilities":,
    "railway_stations":,
    "dams":,
    "mints":,
    "mineshafts":,
    "science_museums":,
    "museums_of_science_and_technology":,
    "religion":,
    "churches":,
    "cathedrals":,
    "monasteries":,
    "synagogues":,
    "hindu_temples":,
    "mosques":,
    "archaeology":,
    "historical_places":,
    "fortifications"":,
    "historic":,
    "castles":,
    "fortified_towers":,
    "bunkers":,
    "military_museums":,
    "battlefields":,
    "war_graves":,
    "war_memorials":,
    "burial_places":,
    "cemeteries":,
    "necropolises":,
    "mausoleums":,
    "crypts":,
    "urban_environment":,
    "wall_painting":,
    "fountains":,
    "sculptures":,
    "installations":,
}

        "sub_categories": [
            {
                "name": "Murale",
                "code":
            }, {
                "name": "Fontanny",
                "code":
            }, {
                "name": "Rzeźby",
                "code":
                "additional_codes": []
            }, {
                "name": "Zieleń miejska",
                "code": "gardens_and_parks"
            }]},
    {
        "name": "Muzea i wystawy",
        "code": "museums",
        "visiting_time": {
            "hours": 3,
            "minutes": 0
        },
        "sub_categories": [
            {
                "name": "Muzea archeologiczne",
                "code": "archaeological_museums"
            }, {
                "name": "Galerie sztuki",
                "code": "art_galleries"
            }, {
                "name": "Muzea biografizcne",
                "code": "biographical_museums"
            }, {
                "name": "Muzea historyczne",
                "code": "history_museums",
                "additional_codes": ["historic_house_museums"]
            }, {
                "name": "Muzea lokalne",
                "code": "local_museums"
            }, {
                "name": "Muzea narodowe",
                "code": "national_museums"
            }, {
                "name": "Muzea mody",
                "code": "fashion_museums"
            }]},
    {
        "name": "Muzea, parki i obiekty związane z przyrodą",
        "code": "nature_museums",
        "visiting_time": {
            "hours": 3,
            "minutes": 0
        },
        "sub_categories": [
            {
                "name": "Planetaria",
                "code": "planetariums"
            }, {
                "name": "Zoo",
                "code": "zoos"
            }, {
                "name": "Akwaria",
                "code": "aquariums"
            }]},
    {
        "name": "Architektura",
        "code": "architecture",
        "visiting_time": {
            "hours": 0,
            "minutes": 15
        },
        "sub_categories": [
            {
                "name": "Drapacze chmur",
                "code": "skyscrapers"
            }, {
                "name": "Wieże (zegarowe, widokowe)",
                "code": "towers"
            }, {
                "name": "Budynki historyczne",
                "code": "historic_architecture"
            }, {
                "name": "Mosty",
                "code": "bridges"
            }]},
    {
        "name": "Miejsca pamięci",
        "code": "memorials",
        "visiting_time": {
            "hours": 0,
            "minutes": 20
        },
        "sub_categories": [
            {
                "name": "Pomniki",
                "code": "monuments"
            }, {
                "name": "Kopce/kurhan",
                "code": "tumuluses"
            },
        ]
    }
]
"""
