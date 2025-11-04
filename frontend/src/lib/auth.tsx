import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { auth, Seller } from './api'

interface AuthContextType {
  user: Seller | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  refetch: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<Seller | null>(null)

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token')
      if (!token) return null
      const response = await auth.getMe()
      return response.data
    },
    retry: false,
  })

  useEffect(() => {
    if (data) {
      setUser(data)
    }
  }, [data])

  const loginMutation = useMutation({
    mutationFn: async ({ email, password }: { email: string; password: string }) => {
      const response = await auth.login(email, password)
      return response.data
    },
    onSuccess: (data) => {
      localStorage.setItem('access_token', data.access_token)
      setUser(data.seller)
      refetch()
    },
  })

  const login = async (email: string, password: string) => {
    await loginMutation.mutateAsync({ email, password })
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    setUser(null)
    window.location.href = '/login'
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout, refetch }}>
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
