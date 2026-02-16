import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Map HTTP status codes to user-friendly messages
 */
const statusMessages = {
  400: 'Please check your input.',
  401: 'Login required.',
  403: "You don't have permission.",
  404: 'Not found.',
  500: 'Server problem. Try later.',
  0: 'Server not reachable. Check your connection.',
}

/**
 * Get user-friendly error message from response
 */
export const getErrorMessage = (error) => {
  if (!error.response) {
    // Network error
    console.error('Network error:', error.message)
    return statusMessages[0]
  }
  
  const { status, data } = error.response
  
  // Log error for debugging (in development)
  if (import.meta.env.DEV) {
    console.error(`API Error [${status}]:`, data)
  }
  
  // Use backend message if available, otherwise use status mapping
  if (data?.message) {
    return data.message
  }
  
  return statusMessages[status] || 'Something went wrong.'
}

/**
 * Get field-specific errors from response
 */
export const getFieldErrors = (error) => {
  return error.response?.data?.errors || {}
}

// Add token to request headers
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post('http://localhost:8000/api/token/refresh/', {
            refresh: refreshToken,
          })
          
          localStorage.setItem('access_token', response.data.access)
          api.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`
          
          return api(originalRequest)
        }
      } catch (refreshError) {
        console.error('Token refresh failed')
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export default api
