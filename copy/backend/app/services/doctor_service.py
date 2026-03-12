from typing import Optional, Dict, Any, List, Tuple
from app.models.doctor_model import DoctorModel
from app.models.appointment_model import AppointmentModel
from app.models.leave_model import LeaveModel
from app.models.schedule_model import ScheduleModel
from datetime import datetime, timedelta


class DoctorService:

    # ------------------------------------------------------------------
    # Doctor read helpers
    # ------------------------------------------------------------------

    @staticmethod
    def get_all_doctors() -> List[Dict[str, Any]]:
        return DoctorModel.get_all()

    @staticmethod
    def get_doctor_by_id(
        doctor_id: str,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        doctor = DoctorModel.get_by_id(doctor_id)
        if not doctor:
            return None, "Doctor not found"
        return doctor, None

    # ------------------------------------------------------------------
    # Schedule management
    # ------------------------------------------------------------------

    @staticmethod
    def set_schedule(
        doctor_id: str, schedule_data: Dict[str, Any]
    ) -> Tuple[str, Optional[str]]:
        """Upsert (create-or-replace) a schedule for a doctor."""
        doctor = DoctorModel.get_by_id(doctor_id)
        if not doctor:
            return "", "Doctor not found"
        schedule_data["doctor_id"] = doctor_id
        schedule_id = ScheduleModel.upsert(doctor_id, schedule_data)
        return schedule_id, None

    @staticmethod
    def get_schedule(
        doctor_id: str,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Return the stored schedule for a doctor.
        Falls back to the doctor document's own timing fields if no schedule
        record exists (backwards-compatible for seeded doctors).
        """
        schedule = ScheduleModel.get_by_doctor(doctor_id)
        if schedule:
            return schedule, None

        doctor = DoctorModel.get_by_id(doctor_id)
        if not doctor:
            return None, "Doctor not found"

        fallback: Dict[str, Any] = {
            "_id": None,
            "doctor_id": doctor_id,
            "working_days": doctor.get("available_days", []),
            "start_time": doctor.get("start_time", "09:00"),
            "end_time": doctor.get("end_time", "17:00"),
            "slot_duration": doctor.get("slot_duration", 30),
            "break_start": doctor.get("break_start"),
            "break_end": doctor.get("break_end"),
        }
        return fallback, None

    # ------------------------------------------------------------------
    # Leave management
    # ------------------------------------------------------------------

    @staticmethod
    def set_leave(
        doctor_id: str, leave_data: Dict[str, Any]
    ) -> Tuple[Optional[str], Optional[str]]:
        """Create a leave record. Prevents duplicate entries for the same date."""
        doctor = DoctorModel.get_by_id(doctor_id)
        if not doctor:
            return None, "Doctor not found"

        leave_date = leave_data.get("leave_date")
        if LeaveModel.get_by_doctor_date(doctor_id, leave_date):
            return None, f"Leave already set for {leave_date}"

        leave_data["doctor_id"] = doctor_id
        leave_id = LeaveModel.create(leave_data)
        return leave_id, None

    @staticmethod
    def get_leaves(
        doctor_id: str,
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
        """Return all leave records for a doctor sorted by date."""
        doctor = DoctorModel.get_by_id(doctor_id)
        if not doctor:
            return None, "Doctor not found"
        return LeaveModel.get_by_doctor(doctor_id), None

    # ------------------------------------------------------------------
    # Slot generation (pure helper — no DB access)
    # ------------------------------------------------------------------

    @staticmethod
    def generate_slots(
        start_str: str,
        end_str: str,
        duration: int,
        break_start: Optional[str] = None,
        break_end: Optional[str] = None,
    ) -> List[str]:
        slots: List[str] = []
        try:
            start_time = datetime.strptime(start_str, "%H:%M")
            end_time = datetime.strptime(end_str, "%H:%M")
            b_start = datetime.strptime(break_start, "%H:%M") if break_start else None
            b_end = datetime.strptime(break_end, "%H:%M") if break_end else None

            current = start_time
            while current + timedelta(minutes=duration) <= end_time:
                in_break = (
                    b_start is not None
                    and b_end is not None
                    and b_start <= current < b_end
                )
                if not in_break:
                    slots.append(current.strftime("%I:%M %p"))
                current += timedelta(minutes=duration)
        except Exception as exc:
            print(f"Slot generation error: {exc}")
        return slots

    # ------------------------------------------------------------------
    # Available slots (used by both route and AppointmentService)
    # ------------------------------------------------------------------

    @staticmethod
    def get_available_slots(
        doctor_id: str, date: str
    ) -> Tuple[Optional[List[str]], Optional[str]]:
        """
        Steps:
          1. Validate date format.
          2. Check leave — return [] if doctor is on leave.
          3. Load schedule (schedules collection → doctor-doc fallback).
          4. Check working_days — return [] if that weekday is not scheduled.
          5. Generate all slots, subtract non-cancelled bookings.
          6. For today, drop slots within the 15-minute buffer window.
        """
        # 1. Validate date
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return None, "Invalid date format. Use YYYY-MM-DD."

        # 2. Leave check
        if LeaveModel.get_by_doctor_date(doctor_id, date):
            return [], None

        # 3. Load schedule
        schedule, err = DoctorService.get_schedule(doctor_id)
        if err:
            return None, err

        # 4. Working-day check
        day_name = target_date.strftime("%A").lower()
        working_days = [d.lower() for d in (schedule.get("working_days") or [])]
        if working_days and day_name not in working_days:
            return [], None

        # 5. Generate slots and subtract booked
        all_slots = DoctorService.generate_slots(
            schedule.get("start_time", "09:00"),
            schedule.get("end_time", "17:00"),
            int(schedule.get("slot_duration", 30)),
            schedule.get("break_start"),
            schedule.get("break_end"),
        )
        booked = {
            app.get("appointment_time")
            for app in AppointmentModel.get_by_doctor_date(doctor_id, date)
        }
        available = [s for s in all_slots if s not in booked]

        # 6. Drop near-past slots for today
        today_str = datetime.now().strftime("%Y-%m-%d")
        if date == today_str:
            cutoff = datetime.now() + timedelta(minutes=15)
            filtered = []
            for slot in available:
                try:
                    slot_dt = datetime.strptime(f"{date} {slot}", "%Y-%m-%d %I:%M %p")
                    if slot_dt > cutoff:
                        filtered.append(slot)
                except ValueError:
                    continue
            available = filtered

        return available, None

    # ------------------------------------------------------------------
    # Calendar status
    # ------------------------------------------------------------------

    @staticmethod
    def get_calendar_status(
        doctor_id: str, month: str
    ) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
        leaves = LeaveModel.get_by_doctor_month(doctor_id, month)
        leave_dates = [lv["leave_date"] for lv in leaves]

        doctor = DoctorModel.get_by_id(doctor_id)
        if not doctor:
            return None, "Doctor not found"

        all_slots = DoctorService.generate_slots(
            doctor.get("start_time", "09:00"),
            doctor.get("end_time", "17:00"),
            doctor.get("slot_duration", 30),
            doctor.get("break_start"),
            doctor.get("break_end"),
        )
        total_possible_slots = len(all_slots)

        pipeline = [
            {"$match": {
                "doctor_id": doctor_id,
                "appointment_date": {"$regex": f"^{month}"},
                "status": {"$ne": "cancelled"},
            }},
            {"$group": {"_id": "$appointment_date", "count": {"$sum": 1}}},
        ]
        booking_counts = AppointmentModel.aggregate_bookings(pipeline)

        status_map: Dict[str, str] = {}
        for date_info in booking_counts:
            if date_info["count"] >= total_possible_slots:
                status_map[date_info["_id"]] = "fully_booked"
        for l_date in leave_dates:
            status_map[l_date] = "leave"

        return status_map, None
