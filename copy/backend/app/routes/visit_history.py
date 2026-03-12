from fastapi import APIRouter, HTTPException, Depends
from app.models.visit_history_model import VisitHistoryCreate
from app.utils.auth import get_current_doctor
from app.services.visit_history_service import VisitHistoryService

router = APIRouter()


@router.post(
    "/add",
    summary="Record a visit / complete an appointment",
    description=(
        "Creates a visit history entry for a completed appointment. "
        "Only the doctor assigned to the appointment can add a record. "
        "Duplicate records for the same appointment are rejected. "
        "The appointment is automatically marked as 'completed'."
    ),
)
def add_visit(
    visit: VisitHistoryCreate,
    doctor_id: str = Depends(get_current_doctor),
):
    visit_id, error = VisitHistoryService.add_visit(doctor_id, visit.dict())
    if error:
        status_code = (
            403 if "Not authorized" in error
            else 409 if "already recorded" in error
            else 404 if "not found" in error.lower()
            else 400
        )
        raise HTTPException(status_code=status_code, detail=error)

    return {"message": "Visit history recorded successfully", "id": visit_id}


@router.get(
    "/patient/{patient_id}",
    summary="Get visit history for a patient",
    description=(
        "Returns all past visit records for the given patient, "
        "sorted most recent first. "
        "Includes diagnosis, prescription, notes, doctor name, and visit date."
    ),
)
def get_patient_history(patient_id: str):
    records, error = VisitHistoryService.get_patient_history(patient_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"history": records, "total": len(records)}


@router.get(
    "/doctor/{doctor_id}",
    summary="Get all visits recorded by a doctor",
    description="Returns all visit history entries created by the given doctor, sorted most recent first.",
)
def get_doctor_history(doctor_id: str):
    records, error = VisitHistoryService.get_doctor_history(doctor_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"history": records, "total": len(records)}
