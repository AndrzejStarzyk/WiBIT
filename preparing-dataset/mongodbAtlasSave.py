from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from keysAndPasswords import mongodb_password, mongodb_user


uri = f"mongodb+srv://{mongodb_user}:{mongodb_password}@wibit.4d0e5vs.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["wibit"]
# db.create_collection("cracow-attractions")
collection = db["cracow-attractions"]







