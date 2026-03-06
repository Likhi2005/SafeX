import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30000, // 30 seconds timeout
});

// Request interceptor for logging
api.interceptors.request.use(
    (config) => {
        console.log('Making API request:', config.method?.toUpperCase(), config.url);
        return config;
    },
    (error) => {
        console.error('Request error:', error);
        return Promise.reject(error);
    }
);

api.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        console.error('API response error:', error);

        if (error.code === 'ECONNABORTED') {
            throw new Error('Request timeout - please try again');
        }

        if (error.response) {
            throw new Error(error.response.data?.message || `API Error: ${error.response.status}`);
        }else if (error.request) {
            throw new Error('Network error - please check if the backend is running');
        } else {
            throw new Error('Request failed');
        }
    }
);

// API Functions
export const analyzePrompt = async (prompt, userId = 'frontend_user') => {
    try {
        const response = await api.post('/analyze', {
            prompt,
            user_id: userId,
        });

        return {
            success: true,
            data: response.data,
        };
    } catch (error) {
        return {
            success: false,
            error: error.message,
            data: null,
        };
    }
};

export const getHealthCheck = async () => {
    try {
        const response = await api.get('/health');
        return {
            success: true,
            data: response.data,
        };
    } catch (error) {
        return {
            success: false,
            error: error.message,
            data: null,
        };
    }
};

export default api;