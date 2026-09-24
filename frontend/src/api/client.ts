import axios from 'axios'

const getBaseUrl = (): string => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  if (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) {
    return 'http://localhost:8000';
  }
  return import.meta.env.PROD ? 'https://btc-3jme.onrender.com' : 'http://localhost:8000';
};

export const apiClient = axios.create({
  baseURL: getBaseUrl(),
  timeout: 25000, // 25s bounded timeout to prevent infinite hanging
  headers: {
    'Content-Type': 'application/json',
  },
})


apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Only handle true 401 unauthorized when not on login endpoint or login page
    const isLoginRequest = error.config?.url?.includes('/auth/login')
    const isOnLoginPage = window.location.pathname.endsWith('/login') || window.location.pathname.endsWith('/login/')

    if (error.response?.status === 401 && !isLoginRequest && !isOnLoginPage) {
      localStorage.removeItem('token')
      const baseUrl = import.meta.env.BASE_URL || '/'
      const loginPath = baseUrl.endsWith('/') ? `${baseUrl}login` : `${baseUrl}/login`
      window.location.href = loginPath
      return Promise.reject(new Error('Session expired. Please log in again.'))
    }

    // Friendly messages for timeouts and network failures
    if (error.code === 'ECONNABORTED' || error.message?.toLowerCase().includes('timeout')) {
      error.message = 'Request timed out (server took >25s). Please retry.'
    } else if (!error.response && error.request) {
      error.message = 'Unable to connect to the BTC-SHIELD backend. Check network or server status.'
    } else if (error.response?.status >= 500) {
      error.message = error.response?.data?.detail || 'Server encountered an error. Please retry shortly.'
    }

    return Promise.reject(error)
  }
)

