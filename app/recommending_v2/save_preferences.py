from typing import List

from pymongo import MongoClient
from pymongo.server_api import ServerApi

from recommending_v2.algorythm_models.constraint import Constraint
from models.objectid import PydanticObjectId

mongodb_uri = f"mongodb+srv://andrzej:passwordas@wibit.4d0e5vs.mongodb.net/?retryWrites=true&w=majority"


def save_preferences(user_id, constraints: List[Constraint]):
    client = MongoClient(mongodb_uri, server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        print("Successfully connected to MongoDB from save preferences!")
    except Exception as e:
        print(e)

    db = client["wibit"]
    users = db["users"]

    user = users.find_one()
    if user is None:
        return

    users.aggregate([
        {"$match": {"_id": PydanticObjectId(user_id)}},
        {"$set": {"preferences": {"$concatArrays": [{
          "user_id": PydanticObjectId(user_id),
          "preferences": [constraint.to_json() for constraint in constraints]
        }]}}}])
