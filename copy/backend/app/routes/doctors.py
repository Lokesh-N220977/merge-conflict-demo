from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import datetime
from app.models.doctor_model import DoctorCreate, DoctorModel
from app.models.schedule_model import ScheduleSet
from app.models.leave_model import DoctorLeave
from app.utils.auth import get_current_admin, get_current_doctor
from app.utils.hash import hash_password
from app.services.doctor_service import DoctorService
from app.services.appointment_service import AppointmentService

router = APIRouter()


# ──────────────────────────────────────────────────────────────────────
# Doctor listing
# ──────────────────────────────────────────────────────────────────────

@router.get(
    "",
    summary="List all doctors",
    description="Returns doctors with specialization, experience, and consultation fee. Passwords are never included.",
)
def get_doctors(
    specialization: Optional[str] = Query(None, description="Filter by specialization"),
):
    doctors = DoctorService.get_all_doctors()
    if specialization:
        doctors = [
            d for d in doctors
            if d.get("specialization", "").lower() == specialization.lower()
        ]
    return doctors


@router.get(
    "/today-appointments",
    summary="Today's appointments for the authenticated doctor",
    description=(
        "Returns all non-cancelled appointments for the logged-in doctor on today's date, "
        "sorted by appointment time. Requires doctor (or admin) JWT token."
    ),
)
def get_today_appointments(
    doctor_id: str = Depends(get_current_doctor),
):
    appointments = AppointmentService.get_today_appointments(doctor_id)
    today = datetime.now().strftime("%Y-%m-%d")
    return {"appointments": appointments, "total": len(appointments), "date": today}


@router.get(
    "/{doctor_id}",
    summary="Get a single doctor",
    description="Returns 404 if not found, 400 if the ID format is invalid.",
)
def get_doctor(doctor_id: str):
    if len(doctor_id) != 24:
        raise HTTPException(status_code=400, detail="Invalid doctor ID format")
    doctor, error = DoctorService.get_doctor_by_id(doctor_id)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return doctor


# ──────────────────────────────────────────────────────────────────────
# Schedule
# ──────────────────────────────────────────────────────────────────────

@router.post(
    "/set-schedule",
    summary="Set (or update) a doctor's schedule",
    description=(
        "Creates or replaces the working schedule for a doctor. "
        "Only one schedule document is kept per doctor (upsert). "
        "Requires admin auth."
    ),
)
def set_schedule(
    schedule: ScheduleSet,
    _admin: str = Depends(get_current_admin),
):
    schedule_id, error = DoctorService.set_schedule(
        schedule.doctor_id, schedule.dict()
    )
    if error:
        status_code = 404 if "not found" in error else 400
        raise HTTPException(status_code=status_code, detail=error)
    return {"message": "Schedule saved successfully", "id": schedule_id}


@router.get(
    "/{doctor_id}/schedule",
    summary="Get a doctor's schedule",
    description=(
        "Returns the doctor's stored schedule. "
        "Falls back to the doctor document's own timing fields if no schedule record exists."
    ),
)
def get_schedule(doctor_id: str):
    if len(doctor_id) != 24:
        raise HTTPException(status_code=400, detail="Invalid doctor ID format")
    schedule, error = DoctorService.get_schedule(doctor_id)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return schedule


# ──────────────────────────────────────────────────────────────────────
# Leave
# ──────────────────────────────────────────────────────────────────────

@router.post(
    "/set-leave",
    summary="Mark a doctor as on leave for a date",
    description=(
        "Records a leave day for a doctor. "
        "Returns 409 if the date is already marked. "
        "Requires admin auth."
    ),
)
def set_leave(
    leave: DoctorLeave,
    _admin: str = Depends(get_current_admin),
):
    leave_id, error = DoctorService.set_leave(leave.doctor_id, leave.dict())
    if error:
        status_code = 409 if "already set" in error else 404
        raise HTTPException(status_code=status_code, detail=error)
    return {"message": "Leave recorded successfully", "id": leave_id}


@router.get(
    "/{doctor_id}/leaves",
    summary="Get all leave records for a doctor",
    description="Returns all leave dates sorted ascending.",
)
def get_leaves(doctor_id: str):
    if len(doctor_id) != 24:
        raise HTTPException(status_code=400, detail="Invalid doctor ID format")
    leaves, error = DoctorService.get_leaves(doctor_id)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return {"leaves": leaves, "total": len(leaves)}


# ──────────────────────────────────────────────────────────────────────
# Available slots
# ──────────────────────────────────────────────────────────────────────

@router.get(
    "/{doctor_id}/available-slots",
    summary="Get available appointment slots",
    description=(
        "Generates available time slots for a doctor on a given date. "
        "Returns [] if the doctor is on leave or the date is not a working day. "
        "Already-booked and within-15-min slots are excluded."
    ),
)
def get_available_slots(
    doctor_id: str,
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
):
    if len(doctor_id) != 24:
        raise HTTPException(status_code=400, detail="Invalid doctor ID format")

    slots, error = DoctorService.get_available_slots(doctor_id, date)
    if error:
        status_code = 400 if "format" in error else 404
        raise HTTPException(status_code=status_code, detail=error)

    return {"doctor_id": doctor_id, "date": date, "available_slots": slots}
