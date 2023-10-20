from flask_login import UserMixin
from models.mongo_utils import MongoUtils


class User(UserMixin):
    def __init__(self, login=None, hashed_password=None):
        self.login = login
        self.hashed_password = hashed_password
        self.id = None

    def get_id(self):
        return self.id

    @staticmethod
    def get_users_collection(mongo_utils: MongoUtils):
        return mongo_utils.get_collection('users')

    def get_user_by_id(self, user_id, mongo_utils: MongoUtils):
        tmp_user = User.get_users_collection(mongo_utils).find_one({'_id': user_id})
        if tmp_user is not None:
            self.login = tmp_user['login']
            self.hashed_password = tmp_user['password']
            self.id = str(tmp_user['_id'])

    def get_user_by_login(self, user_login, mongo_utils: MongoUtils):
        tmp_user = User.get_users_collection(mongo_utils).find_one({'login': user_login})
        if tmp_user is not None:
            self.login = tmp_user['login']
            self.hashed_password = tmp_user['password']
            self.id = str(tmp_user['_id'])

    def add_user_to_db(self, mongo_utils: MongoUtils):
        users_collection = User.get_users_collection(mongo_utils)
        new_user = {
            'login': self.login,
            'password': self.hashed_password
        }
        users_collection.insert_one(new_user)
