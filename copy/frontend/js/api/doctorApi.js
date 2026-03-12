const BASE_URL = 'http://localhost:8000/api';

export const doctorApi = {
    async getDoctors() {
        const response = await fetch(`${BASE_URL}/doctors`);
        if (!response.ok) throw new Error(await response.text());
        return response.json();
    },

    async getDoctorById(id) {
        const response = await fetch(`${BASE_URL}/doctors/${id}`);
        if (!response.ok) throw new Error(await response.text());
        return response.json();
    },

    async getDoctorSchedule(id) {
        const response = await fetch(`${BASE_URL}/doctors/${id}/schedule`);
        if (!response.ok) throw new Error(await response.text());
        return response.json();
    },

    async setSchedule(data, token) {
        const response = await fetch(`${BASE_URL}/doctors/set-schedule`, {
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

    async setLeave(data, token) {
        const response = await fetch(`${BASE_URL}/doctors/set-leave`, {
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

    async getTodayAppointments(token) {
        const response = await fetch(`${BASE_URL}/doctors/today-appointments`, {
            method: 'GET',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json' 
            }
        });
        if (!response.ok) throw new Error(await response.text());
        return response.json();
    },

    async getUpcomingAppointments(token) {
        const response = await fetch(`${BASE_URL}/doctor/upcoming-appointments`, {
            method: 'GET',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json' 
            }
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

    async cancelAppointment(id, token) {
        const response = await fetch(`${BASE_URL}/appointments/reject`, {
            method: 'POST',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json' 
            },
            body: JSON.stringify({ appointment_id: id })
        });
        if (!response.ok) throw new Error(await response.text());
        return response.json();
    }
};
