from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any, List
from bson import ObjectId
from app.database import database
from datetime import datetime


# --- Pydantic Schemas ---

class VisitHistoryCreate(BaseModel):
    """Payload for POST /visit-history/add (sent by doctor after a visit)."""
    appointment_id: str
    doctor_id: str
    patient_id: str
    diagnosis: str
    prescription: Optional[str] = None
    notes: Optional[str] = None


class VisitHistoryResponse(BaseModel):
    """Typed response for a single visit record."""
    id: str
    appointment_id: str
    doctor_id: str
    patient_id: str
    diagnosis: str
    prescription: Optional[str] = None
    notes: Optional[str] = None
    doctor_name: Optional[str] = None
    visit_date: Optional[str] = None     # stored as YYYY-MM-DD
    created_at: Optional[str] = None


# --- MongoDB Model ---

class VisitHistoryModel:

    @staticmethod
    def create(data: Dict[str, Any]) -> str:
        """Insert a visit record and return its id."""
        result = database.visit_history.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def get_by_patient(patient_id: str) -> List[Dict[str, Any]]:
        """Return all visits for a patient, most recent first."""
        records = list(
            database.visit_history
            .find({"patient_id": patient_id})
            .sort("created_at", -1)
        )
        for rec in records:
            rec["_id"] = str(rec["_id"])
        return records

    @staticmethod
    def get_by_appointment(appointment_id: str) -> Optional[Dict[str, Any]]:
        """Return the visit record linked to a specific appointment, if any."""
        doc = database.visit_history.find_one({"appointment_id": appointment_id})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    @staticmethod
    def get_by_doctor(doctor_id: str) -> List[Dict[str, Any]]:
        """Return all visits recorded by a doctor, most recent first."""
        records = list(
            database.visit_history
            .find({"doctor_id": doctor_id})
            .sort("created_at", -1)
        )
        for rec in records:
            rec["_id"] = str(rec["_id"])
        return records
