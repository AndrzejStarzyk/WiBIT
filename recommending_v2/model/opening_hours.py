from typing import List


class BeginningOrEnding:
    def __init__(self, day, time):
        self.day = day
        self.time = time


class Period:
    def __init__(self, opening: BeginningOrEnding, closing: BeginningOrEnding):
        self.open = opening
        self.close = closing

    def __str__(self):
        if self.open.day == self.close.day:
            return str(self.open) + " - " + str(self.close.time)
        return str(self.open) + " - " + str(self.close)


class OpeningHours:
    def __init__(self, periods: List[Period]):
        self.periods = periods

    def __str__(self):
        res = "Opening hours: "
        for period in self.periods:
            res += str(period) + ", "

        return res[0:-2]

def parse_opening_hours(opening_hours):
    pass


if __name__ == "__main__":
    from pymongo.mongo_client import MongoClient
    from pymongo.server_api import ServerApi
    client = MongoClient( "mongodb+srv://andrzej:passwordas@wibit.4d0e5vs.mongodb.net/?retryWrites=true&w=majority", server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    db = client["wibit"]
    collection = db["cracow-attractions-popular"]

    attraction = collection.find_one()

    opening_hours = OpeningHours(attraction['opening_hours'])
    print(attraction)
    print(opening_hours)
