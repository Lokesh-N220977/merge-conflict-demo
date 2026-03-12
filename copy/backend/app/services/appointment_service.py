from typing import Optional, Dict, Any, List, Tuple
from app.models.appointment_model import AppointmentModel
from app.models.doctor_model import DoctorModel


class AppointmentService:

    # ------------------------------------------------------------------
    # Booking
    # ------------------------------------------------------------------

    @staticmethod
    def book_appointment(
        user_id: str, data: Dict[str, Any]
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Book an appointment for a patient.

        Validates:
          1. Doctor exists.
          2. Requested slot is available (calls DoctorService to avoid
             circular import we use the model-level check here too).
          3. Slot not already taken (double-booking guard).

        Stores status = 'pending'.
        """
        doctor_id = data.get("doctor_id")
        appt_date = data.get("date") or data.get("appointment_date")
        appt_time = data.get("time") or data.get("appointment_time")

        # 1. Doctor must exist
        doctor = DoctorModel.get_by_id(doctor_id)
        if not doctor:
            return None, "Doctor not found"

        # 2. Double-booking guard (same doctor + date + time, non-cancelled)
        # Using database checking as requested for race condition prevention
        existing = AppointmentModel.find_one({
            "doctor_id": doctor_id,
            "appointment_date": appt_date,
            "appointment_time": appt_time,
            "status": {"$ne": "cancelled"},
        })
        if existing:
            return None, "Slot already booked. Please choose another time."

        # 3. Slot availability check (import here to avoid top-level circular dep)
        from app.services.doctor_service import DoctorService
        available_slots, err = DoctorService.get_available_slots(doctor_id, appt_date)
        if err:
            return None, err
        if available_slots is not None and appt_time not in available_slots:
            return None, "Requested slot is not available."

        new_appointment: Dict[str, Any] = {
            "user_id": user_id,
            "doctor_id": doctor_id,
            "doctor_name": doctor.get("name", "Doctor"),
            "department": data.get("department", doctor.get("specialization", "")),
            "appointment_date": appt_date,
            "appointment_time": appt_time,
            "reason": data.get("reason", ""),
            "status": "pending",
        }

        appointment_id = AppointmentModel.create(new_appointment)
        return appointment_id, None

    # ------------------------------------------------------------------
    # Patient appointment queries
    # ------------------------------------------------------------------

    @staticmethod
    def get_patient_appointments(user_id: str) -> List[Dict[str, Any]]:
        """All appointments for a patient (sorted newest first)."""
        return AppointmentModel.get_by_user(user_id)

    @staticmethod
    def get_upcoming_appointments(user_id: str) -> List[Dict[str, Any]]:
        """Today-onwards non-cancelled appointments (sorted soonest first)."""
        return AppointmentModel.get_upcoming_by_patient(user_id)

    @staticmethod
    def get_patient_history(user_id: str) -> List[Dict[str, Any]]:
        return AppointmentModel.get_history(user_id)

    # ------------------------------------------------------------------
    # Doctor appointment queries
    # ------------------------------------------------------------------

    @staticmethod
    def get_doctor_appointments(doctor_id: str) -> List[Dict[str, Any]]:
        return AppointmentModel.get_by_doctor(doctor_id)

    @staticmethod
    def get_today_appointments(doctor_id: str) -> List[Dict[str, Any]]:
        """All non-cancelled appointments for a doctor on today's date."""
        return AppointmentModel.get_by_doctor_today(doctor_id)

    # ------------------------------------------------------------------
    # Cancellation
    # ------------------------------------------------------------------

    @staticmethod
    def cancel_appointment(
        appointment_id: str, user_id: str, reason: str = ""
    ) -> Tuple[bool, Optional[str]]:
        """
        Soft-cancel: sets status to 'cancelled' and records the reason.
        Only the patient who booked can cancel via this method.
        """
        from bson import ObjectId
        try:
            oid = ObjectId(appointment_id)
        except Exception:
            return False, "Invalid appointment ID"

        appointment = AppointmentModel.find_one({"_id": oid, "user_id": user_id})
        if not appointment:
            return False, "Appointment not found"
        if appointment.get("status") == "cancelled":
            return False, "Appointment is already cancelled"

        # Soft-cancel: update status + store reason
        from app.database import database
        database.appointments.update_one(
            {"_id": oid},
            {"$set": {"status": "cancelled", "cancellation_reason": reason}},
        )
        return True, None

    # ------------------------------------------------------------------
    # Status management (confirm / reject)
    # ------------------------------------------------------------------

    @staticmethod
    def _update_status(
        appointment_id: str, doctor_id: str, new_status: str
    ) -> Tuple[bool, Optional[str]]:
        """Shared guard logic for confirm/reject. Only the assigned doctor can act."""
        from bson import ObjectId
        try:
            oid = ObjectId(appointment_id)
        except Exception:
            return False, "Invalid appointment ID"

        appointment = AppointmentModel.find_one({"_id": oid})
        if not appointment:
            return False, "Appointment not found"
        if appointment.get("doctor_id") != doctor_id:
            return False, "Not authorized to update this appointment"
        if appointment.get("status") == "cancelled":
            return False, "Cannot update a cancelled appointment"

        success = AppointmentModel.update_status(appointment_id, new_status)
        return (True, None) if success else (False, "Failed to update appointment status")

    @staticmethod
    def confirm_appointment(
        appointment_id: str, doctor_id: str
    ) -> Tuple[bool, Optional[str]]:
        return AppointmentService._update_status(appointment_id, doctor_id, "confirmed")

    @staticmethod
    def reject_appointment(
        appointment_id: str, doctor_id: str
    ) -> Tuple[bool, Optional[str]]:
        return AppointmentService._update_status(appointment_id, doctor_id, "rejected")

    # ------------------------------------------------------------------
    # Scheduling Engine & Slots
    # ------------------------------------------------------------------

    @staticmethod
    def get_available_slots(doctor_id: str, date: str) -> Tuple[Optional[List[str]], Optional[str]]:
        """
        Calculates available slots by:
        1. Fetching doctor working hours.
        2. Checking leave periods.
        3. Generating all possible slots.
        4. Removing booked slots.
        """
        from app.services.doctor_service import DoctorService
        
        # We delegate the actual sequence of these 4 steps to DoctorService 
        # because it already correctly hits the ScheduleModel & LeaveModel
        slots, error = DoctorService.get_available_slots(doctor_id, date)
        
        if error:
            return None, error
            
        return slots or [], None
