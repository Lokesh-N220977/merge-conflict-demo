from bson import ObjectId
from config.db import db

class DoctorModel:
    collection = db.doctors

    @staticmethod
    def create(data: dict):
        result = DoctorModel.collection.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def find(query: dict = None):
        if query is None:
            query = {}
        doctors = list(DoctorModel.collection.find(query))
        for doc in doctors:
            doc["_id"] = str(doc["_id"])
        return doctors

    @staticmethod
    def find_by_id(doctor_id: str):
        doc = DoctorModel.collection.find_one({"_id": ObjectId(doctor_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    @staticmethod
    def update(doctor_id: str, data: dict):
        result = DoctorModel.collection.update_one(
            {"_id": ObjectId(doctor_id)}, {"$set": data}
        )
        return result.modified_count > 0

    @staticmethod
    def delete(doctor_id: str):
        result = DoctorModel.collection.delete_one({"_id": ObjectId(doctor_id)})
        return result.deleted_count > 0
