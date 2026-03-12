from bson import ObjectId
from config.db import db

class PatientModel:
    collection = db.patients

    @staticmethod
    def create(data: dict):
        result = PatientModel.collection.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def find(query: dict = None):
        if query is None:
            query = {}
        patients = list(PatientModel.collection.find(query))
        for pat in patients:
            pat["_id"] = str(pat["_id"])
        return patients

    @staticmethod
    def find_by_id(patient_id: str):
        pat = PatientModel.collection.find_one({"_id": ObjectId(patient_id)})
        if pat:
            pat["_id"] = str(pat["_id"])
        return pat

    @staticmethod
    def update(patient_id: str, data: dict):
        result = PatientModel.collection.update_one(
            {"_id": ObjectId(patient_id)}, {"$set": data}
        )
        return result.modified_count > 0

    @staticmethod
    def delete(patient_id: str):
        result = PatientModel.collection.delete_one({"_id": ObjectId(patient_id)})
        return result.deleted_count > 0
