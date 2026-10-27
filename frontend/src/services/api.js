
import axios from 'axios';

/**
 * Returns the backend base origin (without trailing /api or slash).
 */
export const getBackendOrigin = () => {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl && typeof envUrl === 'string') {
    return envUrl.replace(/\/api\/?$/, '').replace(/\/+$/, '');
  }
  return '';
};

/**
 * Safely resolves an attachment or media URL against the backend origin.
 * Handles absolute HTTP(S) URLs, relative URLs, data URLs, and filters unsupported schemes.
 */
export const resolveMediaUrl = (url) => {
  if (!url || typeof url !== 'string') return '';
  const trimmed = url.trim();
  if (
    trimmed.startsWith('http://') ||
    trimmed.startsWith('https://') ||
    trimmed.startsWith('data:') ||
    trimmed.startsWith('blob:')
  ) {
    return trimmed;
  }
  // If unsupported non-HTTP protocol like whatsapp://, return empty string so fallback is used
  if (trimmed.includes('://')) {
    return '';
  }

  const origin = getBackendOrigin();
  const cleanPath = trimmed.startsWith('/') ? trimmed : `/${trimmed}`;
  return `${origin}${cleanPath}`;
};

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL
    ? `${import.meta.env.VITE_API_URL}/api`
    : '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});


// Request Interceptor: Attach JWT Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('nexora_token') || localStorage.getItem('khams_token') || localStorage.getItem('token');
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
      localStorage.removeItem('nexora_token');
      localStorage.removeItem('nexora_user');
      localStorage.removeItem('khams_token');
      localStorage.removeItem('khams_user');
      localStorage.removeItem('token');
    }

    const errorData = error.response?.data?.error || {
      code: 'NETWORK_ERROR',
      message: 'تعذر الاتصال بالسيرفر. يرجى التحقق من اتصال الإنترنت.'
    };

    return Promise.reject(errorData);
  }
);

export default api;
