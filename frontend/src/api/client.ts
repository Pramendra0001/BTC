import axios from 'axios'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
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
    // Only handle 401 when not already on the login endpoint or login page
    const isLoginRequest = error.config?.url?.includes('/auth/login')
    const isOnLoginPage = window.location.pathname.endsWith('/login') || window.location.pathname.endsWith('/login/')

    if (error.response?.status === 401 && !isLoginRequest && !isOnLoginPage) {
      localStorage.removeItem('token')
      const baseUrl = import.meta.env.BASE_URL || '/'
      const loginPath = baseUrl.endsWith('/') ? `${baseUrl}login` : `${baseUrl}/login`
      window.location.href = loginPath
    }
    return Promise.reject(error)
  }
)
