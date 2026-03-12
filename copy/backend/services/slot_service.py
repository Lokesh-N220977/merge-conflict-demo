from datetime import datetime
from typing import List
from models.schedule_model import ScheduleModel
from models.leave_model import LeaveModel
from models.appointment_model import AppointmentModel

class SlotService:
    
    @staticmethod
    def generate_slots(doctor_id: str, date_str: str) -> dict:
        """
        Generates available appointment slots for a given doctor on a specific date.
        
        Args:
            doctor_id (str): The ID of the doctor
            date_str (str): Date in 'YYYY-MM-DD' format
            
        Returns:
             dict: A dictionary containing available slots or an error message.
        """
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return {"error": "Invalid date format. Please use YYYY-MM-DD."}

        # 1. Get Doctor Leave
        # Check if the doctor is on leave on this date
        leaves = LeaveModel.find({
            "doctor_id": doctor_id,
            "start_date": {"$lte": date_str},
            "end_date": {"$gte": date_str}
        })
        
        if leaves:
            return {"error": "Doctor is on leave on this date", "slots": []}

        # 2. Get Doctor Schedule
        # Find if the doctor has defined working hours for this date or day of the week
        # Assuming schedule stores 'date' or a generic day
        schedules = ScheduleModel.find({
            "doctor_id": doctor_id,
            "date": date_str
        })
        
        if not schedules:
            return {"error": "Doctor is not available on this date", "slots": []}
            
        # For simplicity, assuming the first schedule record for this date is the one
        schedule = schedules[0]
        
        # Example schedule document structure:
        # { "available_times": ["09:00", "09:30", "10:00", "10:30", "14:00", "14:30"] }
        potential_slots = schedule.get("available_times", [])
        
        if not potential_slots:
            return {"error": "No time slots defined for this schedule", "slots": []}

        # 3. Get Existing Appointments
        # Fetch all appointments for that doctor on that date to filter out booked slots
        appointments = AppointmentModel.find({
            "doctor_id": doctor_id,
            "date": date_str,
            "status": {"$ne": "cancelled"} # Ignore cancelled appointments
        })
        
        booked_times = [apt.get("time") for apt in appointments if "time" in apt]
        
        # 4. Generate Available Slots
        # Remove already booked appointments from potential slots
        available_slots = [slot for slot in potential_slots if slot not in booked_times]
        
        return {"slots": available_slots}
