from bson import ObjectId
from config.db import db

class AppointmentModel:
    collection = db.appointments

    @staticmethod
    def create(data: dict):
        result = AppointmentModel.collection.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def find(query: dict = None):
        if query is None:
            query = {}
        appointments = list(AppointmentModel.collection.find(query))
        for apt in appointments:
            apt["_id"] = str(apt["_id"])
        return appointments

    @staticmethod
    def find_by_id(appointment_id: str):
        apt = AppointmentModel.collection.find_one({"_id": ObjectId(appointment_id)})
        if apt:
            apt["_id"] = str(apt["_id"])
        return apt

    @staticmethod
    def update(appointment_id: str, data: dict):
        result = AppointmentModel.collection.update_one(
            {"_id": ObjectId(appointment_id)}, {"$set": data}
        )
        return result.modified_count > 0

    @staticmethod
    def delete(appointment_id: str):
        result = AppointmentModel.collection.delete_one({"_id": ObjectId(appointment_id)})
        return result.deleted_count > 0
