from typing import Optional, Dict, Any, Tuple
from app.models.user_model import UserModel
from app.utils.hash import hash_password, verify_password
from app.utils.jwt_handler import create_access_token

class AuthService:
    
    @staticmethod
    def register_user(data: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
        existing_user = UserModel.get_by_email(data.get("email"))
        if existing_user:
            return None, "Email already registered"

        hashed_pw = hash_password(data.get("password"))
        new_user = {
            "name": data.get("name"),
            "fullName": data.get("name"),
            "email": data.get("email"),
            "password": hashed_pw,
            "phone": data.get("phone", ""),
            "gender": data.get("gender", ""),
            "role": data.get("role", "patient")
        }

        user_id = UserModel.create(new_user)
        return user_id, None

    @staticmethod
    def login_user(email: str, password: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        db_user = UserModel.get_by_email(email)
        if not db_user:
            return None, "User not found"

        if not verify_password(password, db_user["password"]):
            return None, "Invalid password"

        token = create_access_token({
            "user_id": str(db_user["_id"]),
            "role": db_user.get("role", "patient")
        })

        return {
            "access_token": token,
            "token_type": "bearer"
        }, None

    @staticmethod
    def get_profile(user_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        try:
            user = UserModel.get_by_id(user_id)
            if not user:
                return None, "User not found"
                
            profile_data = {
                "id": str(user["_id"]),
                "fullName": user.get("fullName", user.get("name", "User")),
                "email": user.get("email", ""),
                "phone": user.get("phone", ""),
                "dob": user.get("dob", ""),
                "gender": user.get("gender", ""),
                "bloodGroup": user.get("bloodGroup", ""),
                "emergencyContact": user.get("emergencyContact", ""),
                "address": user.get("address", ""),
                "profilePic": user.get("profilePic", "")
            }
            return profile_data, None
        except Exception:
            return None, "Invalid user ID format"

    @staticmethod
    def update_profile(user_id: str, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        update_data = {k: v for k, v in data.items() if v is not None}
        
        if "fullName" in update_data:
            update_data["name"] = update_data["fullName"]
        elif "name" in update_data:
            update_data["fullName"] = update_data["name"]

        if not update_data:
            return False, "No data provided to update"
            
        success = UserModel.update(user_id, update_data)
        if success:
            return True, None
        return False, "User not found or error updating profile"
