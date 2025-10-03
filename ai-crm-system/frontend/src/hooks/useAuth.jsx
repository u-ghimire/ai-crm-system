import { useState, useEffect, createContext, useContext } from 'react'
import { authAPI } from '../api/client'
import toast from 'react-hot-toast'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is logged in on mount
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser))
      } catch (error) {
        localStorage.removeItem('user')
      }
    }
    setLoading(false)
  }, [])

  const login = async (username, password) => {
    try {
      const response = await authAPI.login(username, password)
      if (response.data.success) {
        const userData = response.data.user
        setUser(userData)
        localStorage.setItem('user', JSON.stringify(userData))
        toast.success('Login successful!')
        return true
      } else {
        toast.error(response.data.message || 'Login failed')
        return false
      }
    } catch (error) {
      toast.error('Login failed. Please check your credentials.')
      return false
    }
  }

  const logout = async () => {
    try {
      await authAPI.logout()
      setUser(null)
      localStorage.removeItem('user')
      toast.success('Logged out successfully')
    } catch (error) {
      console.error('Logout error:', error)
      // Still clear local state even if API call fails
      setUser(null)
      localStorage.removeItem('user')
    }
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
