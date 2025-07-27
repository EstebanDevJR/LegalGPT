"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { apiService, type User as ApiUser } from "@/lib/api"

interface User {
  id: string
  name: string
  email: string
  plan: "basic" | "professional" | "enterprise"
  full_name?: string
  company_name?: string
  company_type?: string
}

interface AuthContextType {
  user: User | null
  login: (user: User) => void
  logout: () => void
  loginWithCredentials: (email: string, password: string) => Promise<void>
  register: (userData: {
    email: string
    password: string
    full_name: string
    company_name: string
    company_type: 'micro' | 'pequeña' | 'mediana'
  }) => Promise<void>
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Verificar si hay un token guardado al cargar la aplicación
    const checkAuthStatus = async () => {
      try {
        if (apiService.isAuthenticated()) {
          const currentUser = await apiService.getCurrentUser()
          setUser({
            id: currentUser.id,
            name: currentUser.full_name || currentUser.email,
            email: currentUser.email,
            plan: getPlanFromCompanyType(currentUser.company_type),
            full_name: currentUser.full_name,
            company_name: currentUser.company_name,
            company_type: currentUser.company_type,
          })
        }
      } catch (error) {
        console.error('Error checking auth status:', error)
        // Si hay error, limpiar el token
        apiService.removeToken()
      } finally {
        setLoading(false)
      }
    }

    checkAuthStatus()
  }, [])

  const getPlanFromCompanyType = (companyType: string): "basic" | "professional" | "enterprise" => {
    switch (companyType) {
      case 'micro':
        return 'basic'
      case 'pequeña':
        return 'professional'
      case 'mediana':
        return 'enterprise'
      default:
        return 'basic'
    }
  }

  const login = (userData: User) => {
    setUser(userData)
  }

  const loginWithCredentials = async (email: string, password: string) => {
    try {
      const response = await apiService.login({ email, password })
      apiService.setToken(response.access_token)
      
      setUser({
        id: response.user.id,
        name: response.user.full_name || response.user.email,
        email: response.user.email,
        plan: getPlanFromCompanyType(response.user.company_type),
        full_name: response.user.full_name,
        company_name: response.user.company_name,
        company_type: response.user.company_type,
      })
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }

  const register = async (userData: {
    email: string
    password: string
    full_name: string
    company_name: string
    company_type: 'micro' | 'pequeña' | 'mediana'
  }) => {
    try {
      const response = await apiService.register(userData)
      apiService.setToken(response.access_token)
      
      setUser({
        id: response.user.id,
        name: response.user.full_name || response.user.email,
        email: response.user.email,
        plan: getPlanFromCompanyType(response.user.company_type),
        full_name: response.user.full_name,
        company_name: response.user.company_name,
        company_type: response.user.company_type,
      })
    } catch (error) {
      console.error('Register error:', error)
      throw error
    }
  }

  const logout = async () => {
    try {
      await apiService.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      apiService.removeToken()
      setUser(null)
    }
  }

  return (
    <AuthContext.Provider 
      value={{ 
        user, 
        login, 
        logout, 
        loginWithCredentials,
        register,
        loading 
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
