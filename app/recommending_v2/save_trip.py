from pymongo import MongoClient
from pymongo.server_api import ServerApi

from objectid import PydanticObjectId
from schedule import Schedule

mongodb_uri = f"mongodb+srv://andrzej:passwordas@wibit.4d0e5vs.mongodb.net/?retryWrites=true&w=majority"

# TODO: _id of trip


def save_trip(user_id, schedule: Schedule):
    client = MongoClient(mongodb_uri, server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        print("Successfully connected to MongoDB from save trip!")
    except Exception as e:
        print(e)

    db = client["wibit"]
    users = db["users"]

    user = users.find_one()
    if user is None:
        return

    days = [{
                "schedule": {
                    "date": schedule.schedule[i].date_str,
                    "start":schedule.schedule[i].start,
                    "end":schedule.schedule[i].end
                },
                "trajectory": [{
                    "poi_id": event.poi.xid,
                    "from": event.start,
                    "to": event.end
                } for event in schedule.trajectories[i].get_events()]} for i in range(schedule.days)]

    users.aggregate([
        {"$match": {"_id": PydanticObjectId(user_id)}},
        {"$set": {"trips": {"$concatArrays": [{
            "user_id": user_id,
            "nr_days": schedule.days,
            "days": days
            }]}}}])
