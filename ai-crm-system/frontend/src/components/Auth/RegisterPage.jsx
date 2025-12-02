import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { UserPlus, Sparkles, AlertCircle, CheckCircle, ArrowLeft } from 'lucide-react'
import axios from 'axios'

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'sales_rep'
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      setLoading(false)
      return
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters')
      setLoading(false)
      return
    }

    try {
      const response = await axios.post('/api/register', {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        role: formData.role
      }, {
        withCredentials: true
      })

      if (response.data.success) {
        setSuccess(true)
        setTimeout(() => {
          navigate('/login')
        }, 2000)
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white rounded-3xl shadow-2xl p-10 w-full max-w-md text-center"
        >
          <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-6">
            <CheckCircle className="w-10 h-10 text-green-600" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-3">Registration Successful!</h2>
          <p className="text-gray-600 text-lg mb-4">Your account has been created.</p>
          <p className="text-sm text-gray-500">Redirecting to login page...</p>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="auth-page min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 flex items-center justify-center p-4 relative overflow-hidden" style={{ color: '#111827' }}>
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-yellow-400 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-pink-400 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
        <div className="absolute top-40 left-40 w-80 h-80 bg-purple-400 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
      </div>

      {/* Back to Home Button */}
      <Link
        to="/"
        className="absolute top-8 left-8 flex items-center space-x-2 text-white hover:text-blue-100 transition-colors z-10"
      >
        <ArrowLeft className="w-5 h-5" />
        <span className="font-semibold">Back to Home</span>
      </Link>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative rounded-3xl shadow-2xl p-10 w-full max-w-md border border-gray-200"
        style={{ 
          color: '#111827', 
          backgroundColor: '#ffffff',
          opacity: 1
        }}
      >
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 rounded-2xl mb-4 shadow-2xl">
            <UserPlus className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-extrabold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
            Create Account
          </h1>
          <p style={{ color: '#374151', fontWeight: '600', fontSize: '18px' }}>Join Lead Mind - The Future of CRM</p>
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-red-50 border-2 border-red-300 rounded-xl flex items-center gap-2"
          >
            <AlertCircle className="w-5 h-5 text-red-700 flex-shrink-0" />
            <p className="text-sm text-red-800 font-semibold">{error}</p>
          </motion.div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label htmlFor="username" style={{ display: 'block', fontSize: '14px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>
              Username
            </label>
            <input
              id="username"
              name="username"
              type="text"
              required
              value={formData.username}
              onChange={handleChange}
              className="w-full px-5 py-3.5 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent font-medium transition-all duration-200"
              style={{ 
                color: '#111827 !important', 
                backgroundColor: '#ffffff !important',
                WebkitTextFillColor: '#111827',
                opacity: 1
              }}
              placeholder="johndoe"
            />
          </div>

          <div>
            <label htmlFor="email" style={{ display: 'block', fontSize: '14px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              required
              value={formData.email}
              onChange={handleChange}
              className="w-full px-5 py-3.5 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent font-medium transition-all duration-200"
              style={{ 
                color: '#111827 !important', 
                backgroundColor: '#ffffff !important',
                WebkitTextFillColor: '#111827',
                opacity: 1
              }}
              placeholder="john@company.com"
            />
          </div>

          <div>
            <label htmlFor="password" style={{ display: 'block', fontSize: '14px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              required
              value={formData.password}
              onChange={handleChange}
              className="w-full px-5 py-3.5 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent font-medium transition-all duration-200"
              style={{ 
                color: '#111827 !important', 
                backgroundColor: '#ffffff !important',
                WebkitTextFillColor: '#111827',
                opacity: 1
              }}
              placeholder="••••••••"
            />
            <p style={{ marginTop: '8px', fontSize: '12px', color: '#4b5563', fontWeight: '600' }}>At least 6 characters</p>
          </div>

          <div>
            <label htmlFor="confirmPassword" style={{ display: 'block', fontSize: '14px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              required
              value={formData.confirmPassword}
              onChange={handleChange}
              className="w-full px-5 py-3.5 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent font-medium transition-all duration-200"
              style={{ 
                color: '#111827 !important', 
                backgroundColor: '#ffffff !important',
                WebkitTextFillColor: '#111827',
                opacity: 1
              }}
              placeholder="••••••••"
            />
          </div>

          <div>
            <label htmlFor="role" style={{ display: 'block', fontSize: '14px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>
              Role
            </label>
            <select
              id="role"
              name="role"
              value={formData.role}
              onChange={handleChange}
              className="w-full px-5 py-3.5 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent font-medium transition-all duration-200"
              style={{ 
                color: '#111827 !important', 
                backgroundColor: '#ffffff !important',
                WebkitTextFillColor: '#111827',
                opacity: 1
              }}
            >
              <option value="sales_rep" style={{ color: '#111827', backgroundColor: '#ffffff' }}>Sales Representative</option>
              <option value="manager" style={{ color: '#111827', backgroundColor: '#ffffff' }}>Manager</option>
              <option value="admin" style={{ color: '#111827', backgroundColor: '#ffffff' }}>Administrator</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white py-4 rounded-xl font-bold text-lg hover:shadow-2xl hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:scale-100 flex items-center justify-center space-x-2 shadow-lg"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                <span>Creating Account...</span>
              </>
            ) : (
              <>
                <UserPlus className="w-6 h-6" />
                <span>Create Account</span>
              </>
            )}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p style={{ fontSize: '14px', color: '#374151', fontWeight: '600' }}>
            Already have an account?{' '}
            <Link to="/login" className="text-purple-600 hover:text-purple-700 font-bold">
              Sign in
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}

export default RegisterPage
