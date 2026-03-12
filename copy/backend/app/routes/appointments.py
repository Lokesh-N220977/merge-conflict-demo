from fastapi import APIRouter, Depends, HTTPException
from app.models.appointment_model import AppointmentBook, AppointmentCreate
from app.utils.auth import get_current_patient, get_current_doctor
from app.services.appointment_service import AppointmentService

router = APIRouter()


# ──────────────────────────────────────────────────────────────────────
# Booking
# ──────────────────────────────────────────────────────────────────────

@router.post(
    "/book",
    summary="Book an appointment",
    description=(
        "Books a slot for the authenticated patient. "
        "Validates slot availability and prevents double booking. "
        "Status starts as 'pending'."
    ),
)
def book_appointment(
    appointment: AppointmentBook,
    user_id: str = Depends(get_current_patient),
):
    appointment_id, error = AppointmentService.book_appointment(
        user_id, appointment.dict()
    )
    if error:
        status_code = (
            409 if "already booked" in error or "not available" in error else 400
        )
        raise HTTPException(status_code=status_code, detail=error)
    return {"message": "Appointment booked successfully", "id": appointment_id}


# ──────────────────────────────────────────────────────────────────────
# Patient appointment queries
# ──────────────────────────────────────────────────────────────────────

@router.get(
    "/patient/{patient_id}",
    summary="All appointments for a patient",
    description="Returns all appointments (any status) sorted newest first. Includes doctor name, date, time, and status.",
)
def get_patient_appointments(patient_id: str):
    appointments = AppointmentService.get_patient_appointments(patient_id)
    return {"appointments": appointments, "total": len(appointments)}


@router.get(
    "/upcoming/{patient_id}",
    summary="Upcoming appointments for a patient",
    description="Today-onwards non-cancelled appointments, sorted soonest first.",
)
def get_upcoming_appointments(patient_id: str):
    appointments = AppointmentService.get_upcoming_appointments(patient_id)
    return {"appointments": appointments, "total": len(appointments)}


# ──────────────────────────────────────────────────────────────────────
# Doctor appointment queries
# ──────────────────────────────────────────────────────────────────────

@router.get(
    "/doctor/{doctor_id}",
    summary="All appointments assigned to a doctor",
    description="Returns all appointments for the given doctor, sorted newest first.",
)
def get_doctor_appointments(doctor_id: str):
    appointments = AppointmentService.get_doctor_appointments(doctor_id)
    return {"appointments": appointments, "total": len(appointments)}


# ──────────────────────────────────────────────────────────────────────
# Status management — patient cancels
# ──────────────────────────────────────────────────────────────────────

@router.post(
    "/cancel",
    summary="Cancel an appointment (patient)",
    description=(
        "Soft-cancels an appointment by setting status to 'cancelled'. "
        "Accepts an optional 'reason' field. "
        "Only the patient who booked can cancel."
    ),
)
def cancel_appointment(
    payload: dict,
    user_id: str = Depends(get_current_patient),
):
    appointment_id = payload.get("appointment_id")
    if not appointment_id:
        raise HTTPException(status_code=400, detail="Missing appointment_id in payload")

    reason = payload.get("reason", "")
    success, error = AppointmentService.cancel_appointment(appointment_id, user_id, reason)
    if error:
        status_code = 404 if "not found" in error.lower() else 400
        raise HTTPException(status_code=status_code, detail=error)
    return {"message": "Appointment cancelled successfully"}


# ──────────────────────────────────────────────────────────────────────
# Status management — doctor confirms / rejects
# ──────────────────────────────────────────────────────────────────────

@router.post(
    "/confirm",
    summary="Confirm an appointment (doctor)",
    description=(
        "Marks an appointment as 'confirmed'. "
        "Only the assigned doctor can confirm. "
        "Cancelled appointments cannot be confirmed."
    ),
)
def confirm_appointment(
    payload: dict,
    doctor_id: str = Depends(get_current_doctor),
):
    appointment_id = payload.get("appointment_id")
    if not appointment_id:
        raise HTTPException(status_code=400, detail="Missing appointment_id in payload")

    success, error = AppointmentService.confirm_appointment(appointment_id, doctor_id)
    if error:
        status_code = 403 if "Not authorized" in error else (
            404 if "not found" in error.lower() else 400
        )
        raise HTTPException(status_code=status_code, detail=error)
    return {"message": "Appointment confirmed successfully"}


@router.post(
    "/reject",
    summary="Reject an appointment (doctor)",
    description=(
        "Marks an appointment as 'rejected'. "
        "Only the assigned doctor can reject. "
        "Cancelled appointments cannot be rejected."
    ),
)
def reject_appointment(
    payload: dict,
    doctor_id: str = Depends(get_current_doctor),
):
    appointment_id = payload.get("appointment_id")
    if not appointment_id:
        raise HTTPException(status_code=400, detail="Missing appointment_id in payload")

    success, error = AppointmentService.reject_appointment(appointment_id, doctor_id)
    if error:
        status_code = 403 if "Not authorized" in error else (
            404 if "not found" in error.lower() else 400
        )
        raise HTTPException(status_code=status_code, detail=error)
    return {"message": "Appointment rejected successfully"}


# ──────────────────────────────────────────────────────────────────────
# Available slots (legacy route — kept for frontend compatibility)
# ──────────────────────────────────────────────────────────────────────

@router.get(
    "/available-slots",
    summary="Available slots based on Schedule & Leaves",
    description="Returns available slots strictly checked against schedule, bookings, and leaves.",
)
def get_available_slots(doctor_id: str, date: str):
    slots, error = AppointmentService.get_available_slots(doctor_id, date)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"available_slots": slots}
