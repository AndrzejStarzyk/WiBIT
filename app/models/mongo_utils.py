from pymongo import MongoClient
from pymongo.server_api import ServerApi
from constants import MONGODB_LOGIN, MONGODB_PASSWORD


class MongoUtils:
    def __init__(self):
        self.mongo_client = None
        self.mongo_database = None

    def get_db(self):
        if self.mongo_database is None:
            self.connect_to_db()

        return self.mongo_database

    def get_client(self):
        if self.mongo_client is None:
            self.connect_to_db()

        return self.mongo_client

    def connect_to_db(self):
        uri = f"mongodb+srv://{MONGODB_LOGIN}:{MONGODB_PASSWORD}@wibit.4d0e5vs.mongodb.net/?retryWrites=true&w=majority"

        self.mongo_client = MongoClient(uri, server_api=ServerApi('1'))

        try:
            self.mongo_client.admin.command('ping')
        except Exception as e:
            print(f"EXCEPTION while connecting mongodb atlas: {e}")

        self.mongo_database = self.mongo_client["wibit"]


mu = MongoUtils()
mu.connect_to_db()
