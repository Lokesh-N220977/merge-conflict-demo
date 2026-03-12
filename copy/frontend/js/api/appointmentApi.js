const BASE_URL = 'http://localhost:8000/api';

export const appointmentApi = {
    async bookAppointment(data, token) {
        const response = await fetch(`${BASE_URL}/appointments/book`, {
            method: 'POST',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json' 
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error(await response.text());
        return response.json();
    },

    async getPatientAppointments(patientId, token) {
        const response = await fetch(`${BASE_URL}/appointments/patient/${patientId}`, {
            method: 'GET',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json' 
            }
        });
        if (!response.ok) throw new Error(await response.text());
        return response.json();
    },

    async getDoctorAppointments(doctorId, token) {
        const response = await fetch(`${BASE_URL}/appointments/doctor/${doctorId}`, {
            method: 'GET',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json' 
            }
        });
        if (!response.ok) throw new Error(await response.text());
        return response.json();
    },

    async cancelAppointment(id, token) {
        const response = await fetch(`${BASE_URL}/appointments/cancel`, {
            method: 'POST',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json' 
            },
            body: JSON.stringify({ appointment_id: id })
        });
        if (!response.ok) throw new Error(await response.text());
        return response.json();
    },

    async confirmAppointment(id, token) {
        const response = await fetch(`${BASE_URL}/appointments/confirm`, {
            method: 'POST',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json' 
            },
            body: JSON.stringify({ appointment_id: id })
        });
        if (!response.ok) throw new Error(await response.text());
        return response.json();
    },

    async rescheduleAppointment(data, token) {
        const response = await fetch(`${BASE_URL}/appointments/reschedule`, {
            method: 'POST',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json' 
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error(await response.text());
        return response.json();
    }
};
