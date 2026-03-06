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
            throw new Error(error.response.data?.error || `API Error: ${error.response.status}`);
        } else if (error.request) {
            throw new Error('Network error - please check if the backend is running');
        } else {
            throw new Error('Request failed');
        }
    }
);

// API Functions

// Enhanced analysis with detailed filter results (NEW)
export const analyzePromptEnhanced = async (prompt, userId = 'frontend_user', includeDetails = true) => {
    try {
        const response = await api.post('/api/v1/analyze', {
            prompt,
            user_id: userId,
            include_details: includeDetails
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

// Original analyze function (for backward compatibility)
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

// Get detailed filter breakdown (NEW)
export const getFilterDetails = async (prompt, userId = 'frontend_user') => {
    try {
        const response = await api.post('/api/v1/analyze/filters', {
            prompt,
            user_id: userId
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

// Quick analysis for high-throughput scenarios (NEW)
export const quickAnalyze = async (prompt, userId = 'frontend_user') => {
    try {
        const response = await api.post('/analyze/quick', {
            prompt,
            user_id: userId
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

// Batch analysis for multiple prompts (NEW)
export const analyzeBatch = async (prompts, userId = 'frontend_user') => {
    try {
        const response = await api.post('/analyze/batch', {
            prompts,
            user_id: userId
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

// Health check
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

// Get system statistics (NEW)
export const getStats = async () => {
    try {
        const response = await api.get('/stats');
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

// Advanced API functions for specific use cases

// Test connectivity to backend
export const testConnection = async () => {
    try {
        const response = await api.get('/health', { timeout: 5000 });
        return {
            success: true,
            data: {
                connected: true,
                latency: response.headers['x-response-time'] || 'Unknown',
                status: response.data.status
            }
        };
    } catch (error) {
        return {
            success: false,
            error: error.message,
            data: { connected: false }
        };
    }
};

// Get detailed system information
export const getSystemInfo = async () => {
    try {
        const [healthResponse, statsResponse] = await Promise.all([
            api.get('/health'),
            api.get('/stats')
        ]);

        return {
            success: true,
            data: {
                health: healthResponse.data,
                stats: statsResponse.data,
                timestamp: new Date().toISOString()
            }
        };
    } catch (error) {
        return {
            success: false,
            error: error.message,
            data: null
        };
    }
};

// Enhanced analyze function that tries multiple endpoints for reliability
export const analyzePromptReliable = async (prompt, userId = 'frontend_user') => {
    // First try enhanced endpoint
    try {
        const enhancedResult = await analyzePromptEnhanced(prompt, userId);
        if (enhancedResult.success) {
            return {
                ...enhancedResult,
                method: 'enhanced'
            };
        }
    } catch (error) {
        console.warn('Enhanced analysis failed, falling back to legacy:', error.message);
    }

    // Fallback to legacy endpoint
    try {
        const legacyResult = await analyzePrompt(prompt, userId);
        return {
            ...legacyResult,
            method: 'legacy'
        };
    } catch (error) {
        return {
            success: false,
            error: `All analysis methods failed: ${error.message}`,
            data: null,
            method: 'failed'
        };
    }
};

// Utility function to check if enhanced features are available
export const checkEnhancedFeaturesAvailable = async () => {
    try {
        const response = await api.get('/api/v1/analyze', {
            timeout: 2000,
            validateStatus: (status) => status === 405 // Method not allowed is expected for GET
        });

        return {
            available: true,
            version: 'v1'
        };
    } catch (error) {
        if (error.response?.status === 405) {
            return {
                available: true,
                version: 'v1'
            };
        }

        return {
            available: false,
            version: 'legacy'
        };
    }
};

export default api;











// import axios from 'axios';

// const API_BASE_URL = 'http://localhost:5000';

// const api = axios.create({
//     baseURL: API_BASE_URL,
//     headers: {
//         'Content-Type': 'application/json',
//     },
//     timeout: 30000, // 30 seconds timeout
// });

// // Request interceptor for logging
// api.interceptors.request.use(
//     (config) => {
//         console.log('Making API request:', config.method?.toUpperCase(), config.url);
//         return config;
//     },
//     (error) => {
//         console.error('Request error:', error);
//         return Promise.reject(error);
//     }
// );

// api.interceptors.response.use(
//     (response) => {
//         return response;
//     },
//     (error) => {
//         console.error('API response error:', error);

//         if (error.code === 'ECONNABORTED') {
//             throw new Error('Request timeout - please try again');
//         }

//         if (error.response) {
//             throw new Error(error.response.data?.message || `API Error: ${error.response.status}`);
//         }else if (error.request) {
//             throw new Error('Network error - please check if the backend is running');
//         } else {
//             throw new Error('Request failed');
//         }
//     }
// );

// // API Functions
// export const analyzePrompt = async (prompt, userId = 'frontend_user') => {
//     try {
//         const response = await api.post('/analyze', {
//             prompt,
//             user_id: userId,
//         });

//         return {
//             success: true,
//             data: response.data,
//         };
//     } catch (error) {
//         return {
//             success: false,
//             error: error.message,
//             data: null,
//         };
//     }
// };

// export const getHealthCheck = async () => {
//     try {
//         const response = await api.get('/health');
//         return {
//             success: true,
//             data: response.data,
//         };
//     } catch (error) {
//         return {
//             success: false,
//             error: error.message,
//             data: null,
//         };
//     }
// };

// export default api;