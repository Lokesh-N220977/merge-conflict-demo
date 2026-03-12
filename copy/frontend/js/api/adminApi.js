const BASE_URL = 'http://localhost:8000/api';

export const adminApi = {
    async addDoctor(data, token) {
        const response = await fetch(`${BASE_URL}/admin/add-doctor`, {
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

    async removeDoctor(id, token) {
        const response = await fetch(`${BASE_URL}/admin/remove-doctor/${id}`, {
            method: 'DELETE',
            headers: { 
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) throw new Error(await response.text());
        return response.json();
    },

    async getAllAppointments(token) {
        const response = await fetch(`${BASE_URL}/admin/all-appointments`, {
            method: 'GET',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json' 
            }
        });
        if (!response.ok) throw new Error(await response.text());
        return response.json();
    },

    async getDashboardStats(token) {
        const response = await fetch(`${BASE_URL}/admin/dashboard-stats`, {
            method: 'GET',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json' 
            }
        });
        if (!response.ok) throw new Error(await response.text());
        return response.json();
    }
};
