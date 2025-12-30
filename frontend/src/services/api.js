import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Upload CSV file
export const uploadCSV = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });

    return response.data;
};

// Get all reports
export const getAllReports = async () => {
    const response = await api.get('/reports');
    return response.data;
};

// Get specific report
export const getReport = async (reportId) => {
    const response = await api.get(`/reports/${reportId}`);
    return response.data;
};

// Delete report
export const deleteReport = async (reportId) => {
    const response = await api.delete(`/reports/${reportId}`);
    return response.data;
};

export default api;