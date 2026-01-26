import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          // OAuth2 refresh token endpoint is at /o/token/ (not under /api/)
          const baseUrl = API_BASE_URL.replace('/api', '')
          const response = await axios.post(`${baseUrl}/o/token/`,
            new URLSearchParams({
              grant_type: 'refresh_token',
              refresh_token: refreshToken,
              client_id: import.meta.env.VITE_OAUTH_CLIENT_ID || 'shelter-frontend',
            }),
            {
              headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
              },
            }
          )
          const { access_token } = response.data
          localStorage.setItem('access_token', access_token)
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return apiClient(originalRequest)
        } catch {
          // Refresh failed, clear tokens
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient
