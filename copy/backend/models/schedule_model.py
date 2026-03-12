from bson import ObjectId
from config.db import db

class ScheduleModel:
    collection = db.doctor_schedule

    @staticmethod
    def create(data: dict):
        result = ScheduleModel.collection.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def find(query: dict = None):
        if query is None:
            query = {}
        schedules = list(ScheduleModel.collection.find(query))
        for sched in schedules:
            sched["_id"] = str(sched["_id"])
        return schedules

    @staticmethod
    def find_by_id(schedule_id: str):
        sched = ScheduleModel.collection.find_one({"_id": ObjectId(schedule_id)})
        if sched:
            sched["_id"] = str(sched["_id"])
        return sched

    @staticmethod
    def update(schedule_id: str, data: dict):
        result = ScheduleModel.collection.update_one(
            {"_id": ObjectId(schedule_id)}, {"$set": data}
        )
        return result.modified_count > 0

    @staticmethod
    def delete(schedule_id: str):
        result = ScheduleModel.collection.delete_one({"_id": ObjectId(schedule_id)})
        return result.deleted_count > 0
