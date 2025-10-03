import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './hooks/useAuth'
import LoginPage from './components/Auth/LoginPage'
import Navbar from './components/Layout/Navbar'
import Sidebar from './components/Layout/Sidebar'
import Dashboard from './pages/Dashboard'
import Customers from './pages/Customers'
import Interactions from './pages/Interactions'
import Reports from './pages/Reports'
import Settings from './pages/Settings'
import ChatWidget from './components/Chatbot/ChatWidget'

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return children
}

// Main Layout Component
const MainLayout = ({ children }) => {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Navbar />
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
      <ChatWidget />
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Toaster position="top-right" />
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <Dashboard />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/customers"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <Customers />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/interactions"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <Interactions />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/reports"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <Reports />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <Settings />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
