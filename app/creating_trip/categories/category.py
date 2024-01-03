from datetime import timedelta


class Category:
    def __init__(self, name: str, code: str, visiting_hours: int, visiting_minutes: int, graph_id: int, is_main: bool):
        self.name = name
        self.code = code
        self.visiting_time = timedelta(hours=visiting_hours, minutes=visiting_minutes)
        self.graph_id = graph_id
        self.is_main = is_main


categories = [
    {
        "name": "Obiekty rozrywkowe",
        "code": "attraction",
        "visiting_time": {
            "hours": 2,
            "minutes": 0
        },
        "sub_categories": [
            {
                "name": "Parki rozrywki",
                "code": "amusement_parks"
            }, {
                "name": "Koło widokowe",
                "code": "ferris_wheels"
            }, {
                "name": "Parki wodne",
                "code": "water_parks"
            }, {
                "name": "Parki miniatur",
                "code": "miniature_parks"
            }, {
                "name": "Baseny, termy i sauny",
                "code": "baths_and_saunas"
            }]},
    {
        "name": "Obiekty sportowe",
        "code": "sport",
        "visiting_time": {
            "hours": 2,
            "minutes": 0
        },
        "sub_categories": [
            {
                "name": "Ścianki wspinaczkowe",
                "code": "climbing"
            }, {
                "name": "Stadiony",
                "code": "stadiums"
            }, {
                "name": "Sporty zimowe",
                "code": "winter_sports"
            }]},
    {
        "name": "Atrakcje naturalne",
        "code": "natural",
        "visiting_time": {
            "hours": 2,
            "minutes": 0
        },
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
        "visiting_time": {
            "hours": 3,
            "minutes": 0
        },
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
            }, {
                "name": "Muzea nauki i techniki",
                "code": "science_museums",
                "additional_codes": ["museums_of_science_and_technology"]
            }]},
    {
        "name": "Obiekty religijne",
        "code": "religion",
        "visiting_time": {
            "hours": 1,
            "minutes": 0
        },
        "sub_categories": [
            {
                "name": "Kościoły",
                "code": "churches"
            }, {
                "name": "Katedry",
                "code": "cathedrals"
            }, {
                "name": "Klasztory",
                "code": "monasteries"
            }, {
                "name": "Synagogi",
                "code": "synagogues"
            }
            , {
                "name": "Świątynie Hinduizmu",
                "code": "hindu_temples"
            }
            , {
                "name": "Meczety",
                "code": "mosques"
            }]},
    {
        "name": "Obiekty archeologiczne",
        "code": "archaeology",
        "visiting_time": {
            "hours": 1,
            "minutes": 30
        }},
    {
        "name": "Obiekty historyczno-militarne",
        "code": "historical_places",
        "additional_codes": ["fortifications", "historic"],
        "visiting_time": {
            "hours": 2,
            "minutes": 0
        },
        "sub_categories": [
            {
                "name": "Zamki",
                "code": "castles"
            }, {
                "name": "Wieże obronne",
                "code": "fortified_towers"
            }, {
                "name": "Bunkry",
                "code": "bunkers"
            }, {
                "name": "Muzea militarne",
                "code": "military_museums"
            }, {
                "name": "Pola bitew",
                "code": "battlefields"
            }, {
                "name": "Cmentarze wojenne",
                "code": "war_graves",
                "additional_codes": ["war_memorials"]
            }]},
    {
        "name": "Miejsca pochówku",
        "code": "burial_places",
        "visiting_time": {
            "hours": 0,
            "minutes": 30
        },
        "sub_categories": [
            {
                "name": "Cmentarze",
                "code": "cemeteries",
                "additional_codes": ["necropolises"]
            }, {
                "name": "Mauzolea",
                "code": "mausoleums"
            }, {
                "name": "Krypty",
                "code": "crypts"
            }]},
    {
        "name": "Środowisko miejskie",
        "code": "urban_environment",
        "visiting_time": {
            "hours": 0,
            "minutes": 15
        },
        "sub_categories": [
            {
                "name": "Murale",
                "code": "wall_painting"
            }, {
                "name": "Fontanny",
                "code": "fountains"
            }, {
                "name": "Rzeźby",
                "code": "sculptures",
                "additional_codes": ["installations"]
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

if __name__ == "__main__":
    a = {"a": 1, "b": 2}
    print(a.get("a"))
