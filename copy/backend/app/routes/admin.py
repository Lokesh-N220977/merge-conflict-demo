from fastapi import APIRouter, Depends, HTTPException
from app.utils.auth import get_current_admin
from app.services.admin_service import AdminService

router = APIRouter()

@router.get("/all-appointments")
def get_all_appointments(admin_id: str = Depends(get_current_admin)):
    return AdminService.get_all_appointments()

@router.get("/stats")
def get_dashboard_stats(admin_id: str = Depends(get_current_admin)):
    return AdminService.get_dashboard_stats()

@router.post("/add-doctor")
def add_doctor(data: dict, admin_id: str = Depends(get_current_admin)):
    doctor_id, error = AdminService.add_doctor(data)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
        
    return {"message": "Doctor added successfully", "doctor_id": doctor_id}

@router.delete("/remove-doctor/{doctor_id}")
def remove_doctor(doctor_id: str, admin_id: str = Depends(get_current_admin)):
    success, error = AdminService.delete_doctor(doctor_id)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return {"message": "Doctor removed successfully"}
