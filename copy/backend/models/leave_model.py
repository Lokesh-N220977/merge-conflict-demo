from bson import ObjectId
from config.db import db

class LeaveModel:
    collection = db.doctor_leaves

    @staticmethod
    def create(data: dict):
        result = LeaveModel.collection.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def find(query: dict = None):
        if query is None:
            query = {}
        leaves = list(LeaveModel.collection.find(query))
        for leave in leaves:
            leave["_id"] = str(leave["_id"])
        return leaves

    @staticmethod
    def find_by_id(leave_id: str):
        leave = LeaveModel.collection.find_one({"_id": ObjectId(leave_id)})
        if leave:
            leave["_id"] = str(leave["_id"])
        return leave

    @staticmethod
    def update(leave_id: str, data: dict):
        result = LeaveModel.collection.update_one(
            {"_id": ObjectId(leave_id)}, {"$set": data}
        )
        return result.modified_count > 0

    @staticmethod
    def delete(leave_id: str):
        result = LeaveModel.collection.delete_one({"_id": ObjectId(leave_id)})
        return result.deleted_count > 0
