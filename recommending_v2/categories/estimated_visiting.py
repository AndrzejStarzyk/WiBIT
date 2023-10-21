from datetime import timedelta

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from typing import Dict

from recommending_v2.model.point_of_interest import PointOfInterest
from recommending_v2.poi_provider import PoiProvider


class VisitingTimeProvider:
    def __init__(self):
        self.code_to_time: Dict[str, timedelta] = {}
        self.fetched = False
        self.mongodb_uri = f"mongodb+srv://andrzej:passwordas@wibit.4d0e5vs.mongodb.net/?retryWrites=true&w=majority"

    def fetch_visiting_times(self):
        client = MongoClient(self.mongodb_uri, server_api=ServerApi('1'))
        try:
            client.admin.command('ping')
            print("Successfully connected to MongoDB!")
        except Exception as e:
            print(e)

        db = client["wibit"]
        collection = db["categories"]

        categories = collection.find()

        for cat in categories:
            visiting_time = cat.get("visiting_time")
            self.code_to_time.setdefault(cat.get("code"),
                                         timedelta(hours=visiting_time.get("hours"), minutes=visiting_time.get("minutes")))

        self.fetched = True

    def get_visiting_time(self, poi: PointOfInterest) -> timedelta:
        if not self.fetched:
            self.fetch_visiting_times()
        avg_time: timedelta = timedelta()
        total = 0
        for code in poi.kinds:
            if code not in self.code_to_time:
                continue
            avg_time += self.code_to_time[code]
            total += 1

        avg_time /= total
        return avg_time


if __name__ == "__main__":
    poi_provider = PoiProvider()
    poi_provider.fetch_pois()
    provider = VisitingTimeProvider()
    print(poi_provider.pois[0])
    print(provider.get_visiting_time(poi_provider.pois[0]))

"""categories = [
    {
        "name": "Atrakcje naturalne",
        "code": "natural",
        "visiting_time": timedelta(minutes=30),
        "sub_categories": [
            {
                "name": "Źródła",
                "code": "natural_springs"
            }, {
                "name": "Rzeki, kanały, wodospady",
                "code": "water"
            }, {
                "name": "Rezerwaty przyrody",
                "code": "nature_reserves"
            }, {
                "name": "Plaże",
                "code": "beaches"
            }]},
    {
        "name": "Obiekty przemysłowe",
        "code": "industrial_facilities",
        "visiting_time": timedelta(hours=2),
        "sub_categories": [
            {
                "name": "Stacje kolejowe",
                "code": "railway_stations"
            }, {
                "name": "Zapory",
                "code": "dams"
            }, {
                "name": "Mennice",
                "code": "mints"
            }, {
                "name": "Kopalnie",
                "code": "mineshafts"
            }]
    },
    {
        "name": "Obiekty religijne",
        "code": "religion",
        "visiting_time": timedelta(hours=1),
        "sub_categories": [
            {
                "name": "Kościoły",
                "code": "churches"
            },
            {
                "name": "Katedry",
                "code": "cathedrals"
            },
            {
                "name": "Klasztory",
                "code": "monasteries"
            },
            {
                "name": "Synagogi",
                "code": "synagogues"
            }
        ]
    },
    {
        "name": "Obiekty archeologiczne",
        "code": "archeaology",
        "visiting_time": timedelta(hours=1),
        "sub_categories": [{
            "name": "Malarstwo jaskiniowe",
            "code": "cave_paintings"
        }]
    },
    {
        "name": "Fortyfikacje",
        "code": "fortifications",
        "visiting_time": timedelta(hours=2),
        "sub_categories": [
            {
                "name": "Zamki",
                "code": "castles"
            },
            {
                "name": "Wieże obronne",
                "code": "fortified_towers"
            },
            {
                "name": "Bunkry",
                "code": "bunkers"
            }
        ]
    },
    {
        "name": "Miejsca historyczne",
        "code": "historical_places",
        "visiting_time": timedelta(hours=1),
        "sub_categories": [{
            "name": "Pola bitew",
            "code": "battlefields"
        }]
    },
    {
        "name": "Miejsca pochówku",
        "code": "burial_places",
        "visiting_time": timedelta(minutes=30),
        "sub_categories": [
            {
                "name": "Cmentarze",
                "code": "cemeteries"
            },
            {
                "name": "Nekropolie",
                "code": "necropolises"
            },
            {
                "name": "Mauzolea",
                "code": "mausoleums"
            },
            {
                "name": "Krypty",
                "code": "crypts"
            },
            {
                "name": "Kopce/kurhany",
                "code": "tumuluses"
            },
            {
                "name": "Cmentarze wojenne",
                "code": "war_graves"
            },
            {
                "name": "Pomiki wojenne",
                "code": "war_memorials"
            }
        ]
    },
    {
        "name": "Środowisko miejskie",
        "code": "urban_environment",
        "visiting_time": timedelta(minutes=10),
        "sub_categories": [
            {
                "name": "Murale",
                "code": "wall_painting"
            },
            {
                "name": "Instalacie artystyczne",
                "code": "installation"
            },
            {
                "name": "Fontanny",
                "code": "fountains"
            },
            {
                "name": "Rzeźby",
                "code": "sculptures"
            }]
    },
    {
        "name": "Muzea",
        "code": "museums",
        "visiting_time": timedelta(hours=2),
        "sub_categories": [
            {
                "name": "Akwaria",
                "code": "aquariums"
            },
            {
                "name": "Muzea archeologiczne",
                "code": "archaeological_museums"
            },
            {
                "name": "Galerie sztuki",
                "code": "art_galleries"
            },
            {
                "name": "Muzea biografizcne",
                "code": "biographical_museums"
            },
            {
                "name": "Muzea historii",
                "code": "history_museums"
            },
            {
                "name": "Budynki historyczne",
                "code": "historic_house_museums"
            },
            {
                "name": "Muzea lokalne",
                "code": "local_museums"
            },
            {
                "name": "Muzea militarne",
                "code": "military_museums"
            },
            {
                "name": "Muzea mody",
                "code": "fashion_museums"
            },
            {
                "name": "Planetaria",
                "code": "planetariums"
            },
            {
                "name": "Zoo",
                "code": "zoos"
            }
        ]
    },
    {
        "name": "Architektura",
        "code": "architecture",
        "visiting_time": timedelta(minutes=10),
        "sub_categories": [{
            "name": "Drapacze chmur",
            "code": "skyscrapers"
        },
            {
                "name": "Wieże",
                "code": "towers"
            },
            {
                "name": "Architektura historyczna",
                "code": "historic_architecture"
            },
            {
                "name": "Mosty",
                "code": "bridges"
            }
        ]
    }
]"""
