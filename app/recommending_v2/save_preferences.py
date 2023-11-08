from typing import List

from recommending_v2.algorythm_models.constraint import Constraint, CategoryConstraint
from mongo_utils import MongoUtils
from models.objectid import PydanticObjectId


def save_preferences(user_id, constraints: List[Constraint], db_connection: MongoUtils):
    users = db_connection.get_collection("users")

    user = users.find_one({"_id": PydanticObjectId(user_id)})
    if user is None:
        return

    users.update_one(
        {"_id": PydanticObjectId(user_id)},
        [{"$set": {"preferences": [constraint.to_json() for constraint in constraints]}}]
    )


def delete_preferences(user_id, db_connection: MongoUtils):
    users = db_connection.get_collection("users")

    user = users.find_one({"_id": PydanticObjectId(user_id)})
    if user is None:
        return

    users.update_one(
        {"_id": PydanticObjectId(user_id)},
        [{"$unset": "preferences"}]
    )


def get_preferences_json(user_id, db_connection: MongoUtils):
    users = db_connection.get_collection("users")
    user = users.find_one({"_id": PydanticObjectId(user_id)})
    if user is None:
        return

    if 'preferences' in user:
        res = user['preferences']
        return res
    return []


if __name__ == '__main__':
    db = MongoUtils()
    save_preferences('65380a296f6d2ff66d8f2d4b', [CategoryConstraint(['amusement_parks'], db)], db)
