from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from app.models.visit_history_model import VisitHistoryModel
from app.models.appointment_model import AppointmentModel
from app.models.doctor_model import DoctorModel


class VisitHistoryService:

    @staticmethod
    def add_visit(
        user_id_from_token: str, data: Dict[str, Any]
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Create a visit history record.

        Validations:
          1. Resolve the doctor document ID from the token's user ID.
          2. The appointment must exist.
          3. The calling doctor must be the one assigned to the appointment.
          ...
        """
        from bson import ObjectId

        # 1. Resolve actual doctor document
        doctor = DoctorModel.get_by_user_id(user_id_from_token)
        if not doctor:
            # Fallback: maybe the ID is already a doctor_id? 
            # (useful for some tests or if the token was minted differently)
            doctor = DoctorModel.get_by_id(user_id_from_token)
            
        if not doctor:
            return None, "Current caller is not a registered doctor"
            
        doctor_id = doctor["_id"]
        appointment_id = data.get("appointment_id")
        patient_id = data.get("patient_id")

        # 2. Appointment must exist
        try:
            appt = AppointmentModel.find_one({"_id": ObjectId(appointment_id)})
        except Exception:
            return None, "Invalid appointment_id format"

        if not appt:
            return None, "Appointment not found"

        # 2. Calling doctor must own the appointment
        if appt.get("doctor_id") != doctor_id:
            return None, "Not authorized: you are not the assigned doctor for this appointment"

        # 3. No duplicate
        if VisitHistoryModel.get_by_appointment(appointment_id):
            return None, "Visit history already recorded for this appointment"

        # 4. Enrich record
        doctor = DoctorModel.get_by_id(doctor_id)
        now = datetime.now()

        record: Dict[str, Any] = {
            "appointment_id": appointment_id,
            "doctor_id": doctor_id,
            "doctor_name": doctor.get("name", "Doctor") if doctor else "Doctor",
            "patient_id": patient_id,
            "diagnosis": data.get("diagnosis", ""),
            "prescription": data.get("prescription"),
            "notes": data.get("notes"),
            "visit_date": appt.get("appointment_date", now.strftime("%Y-%m-%d")),
            "created_at": now.isoformat(),
        }

        visit_id = VisitHistoryModel.create(record)

        # Also mark the appointment as completed
        AppointmentModel.update_status(appointment_id, "completed")

        return visit_id, None

    @staticmethod
    def get_patient_history(
        patient_id: str,
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Return all visit records for a patient."""
        records = VisitHistoryModel.get_by_patient(patient_id)
        return records, None

    @staticmethod
    def get_doctor_history(
        doctor_id: str,
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Return all visit records created by a doctor."""
        records = VisitHistoryModel.get_by_doctor(doctor_id)
        return records, None
