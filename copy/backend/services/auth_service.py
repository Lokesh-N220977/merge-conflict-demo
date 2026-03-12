from models.user_model import UserModel
from utils.auth_utils import get_password_hash, verify_password, create_access_token

class AuthService:
    
    @staticmethod
    def register_user(data: dict):
        # Check if email already exists
        existing_user = UserModel.find({"email": data.get("email")})
        if existing_user:
            return None, "Email already registered"

        # Ensure a valid role is provided, default to patient
        role = data.get("role", "patient")
        if role not in ["patient", "doctor", "admin"]:
            role = "patient"
            
        hashed_password = get_password_hash(data.get("password"))
        
        user_data = {
            "name": data.get("name"),
            "email": data.get("email"),
            "password": hashed_password,
            "role": role,
            "isActive": True
        }
        
        user_id = UserModel.create(user_data)
        
        return user_id, None

    @staticmethod
    def login_user(email: str, password: str):
        # Find user
        users = UserModel.find({"email": email})
        if not users:
            return None, "Invalid email or password"
            
        user = users[0]
        
        # Verify password
        if not verify_password(password, user.get("password")):
            return None, "Invalid email or password"
            
        # Create token
        token_data = {"sub": str(user["_id"]), "role": user.get("role")}
        access_token = create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user["_id"]),
                "name": user.get("name"),
                "email": user.get("email"),
                "role": user.get("role")
            }
        }, None
        
    @staticmethod
    def get_user_profile(user_id: str):
        user = UserModel.find_by_id(user_id)
        if not user:
            return None, "User not found"
            
        # Remove sensitive information
        user.pop("password", None)
        return user, None
