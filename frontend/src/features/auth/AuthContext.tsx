import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import apiClient from '@/api/client'

interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  full_name: string
  role: string
  role_display: string
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      fetchUser()
    } else {
      setIsLoading(false)
    }
  }, [])

  const fetchUser = async () => {
    try {
      const response = await apiClient.get('/auth/me/')
      setUser(response.data)
    } catch {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    // OAuth2 password grant - token endpoint is at /o/token/ (not under /api/)
    const baseUrl = import.meta.env.VITE_API_URL?.replace('/api', '') || ''
    const response = await fetch(`${baseUrl}/o/token/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        grant_type: 'password',
        username: email,
        password: password,
        client_id: import.meta.env.VITE_OAUTH_CLIENT_ID || 'shelter-frontend',
        client_secret: import.meta.env.VITE_CLIENT_SECRET
      }),
    })

    if (!response.ok) {
      throw new Error('Login failed')
    }

    const data = await response.json()

    const { access_token, refresh_token } = data
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', refresh_token)

    await fetchUser()
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
