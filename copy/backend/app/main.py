from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers from routes
from app.routes import users, doctors, appointments, admin, visit_history

# Create the FastAPI app
app = FastAPI(title="MedicPulse Backend API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(users.router, prefix="/api/auth", tags=["auth"])
app.include_router(doctors.router, prefix="/api/doctors", tags=["doctors"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["appointments"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(visit_history.router, prefix="/api/visit-history", tags=["visit-history"])

@app.get("/")
def root():
    return {"message": "API is running"}
