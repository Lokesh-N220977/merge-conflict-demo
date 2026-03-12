from fastapi import APIRouter, HTTPException, Depends
from app.models.user_model import UserCreate, UserProfileUpdate, UserLogin
from app.utils.auth import get_current_patient
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/register")
def register_user(user: UserCreate):
    user_id, error = AuthService.register_user(user.dict())
    if error:
        raise HTTPException(status_code=400, detail=error)

    return {"message": "User registered successfully", "id": user_id}


@router.post("/login")
def login_user(user: UserLogin):
    token_data, error = AuthService.login_user(user.email, user.password)
    
    if error:
        status_code = 404 if error == "User not found" else 401
        raise HTTPException(status_code=status_code, detail=error)

    return {
        "message": "Login successful",
        **token_data
    }


@router.get("/profile")
def get_profile(user_id: str = Depends(get_current_patient)):
    profile_data, error = AuthService.get_profile(user_id)
    
    if error:
        status_code = 404 if error == "User not found" else 400
        raise HTTPException(status_code=status_code, detail=error)

    return profile_data


@router.put("/profile")
def update_profile(
    profile_update: UserProfileUpdate,
    user_id: str = Depends(get_current_patient)
):
    success, error = AuthService.update_profile(user_id, profile_update.dict())
    
    if error:
        status_code = 400 if "data" in error else 404
        raise HTTPException(status_code=status_code, detail=error)
        
    return {"message": "Profile updated successfully"}
