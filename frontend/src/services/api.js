import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request Interceptor: Attach JWT Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('khams_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Structured Error Handling
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('khams_token');
      localStorage.removeItem('khams_user');
    }
    const errorData = error.response?.data?.error || {
      code: 'NETWORK_ERROR',
      message: 'تعذر الاتصال بالسيرفر. يرجى التحقق من اتصال الإنترنت.'
    };
    return Promise.reject(errorData);
  }
);

export default api;
