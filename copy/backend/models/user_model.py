from bson import ObjectId
from config.db import db

class UserModel:
    collection = db.users

    @staticmethod
    def create(data: dict):
        result = UserModel.collection.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def find(query: dict = None):
        if query is None:
            query = {}
        users = list(UserModel.collection.find(query))
        for user in users:
            user["_id"] = str(user["_id"])
        return users

    @staticmethod
    def find_by_id(user_id: str):
        user = UserModel.collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
        return user

    @staticmethod
    def update(user_id: str, data: dict):
        result = UserModel.collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": data}
        )
        return result.modified_count > 0

    @staticmethod
    def delete(user_id: str):
        result = UserModel.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
