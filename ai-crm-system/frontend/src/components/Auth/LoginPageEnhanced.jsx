import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { motion, AnimatePresence } from 'framer-motion'
import { LogIn, Brain, Lock, User, Eye, EyeOff, Zap, TrendingUp, Users, Shield } from 'lucide-react'

const LoginPageEnhanced = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    const success = await login(username, password)
    if (success) {
      navigate('/dashboard')
    }
    
    setLoading(false)
  }

  const features = [
    { icon: Zap, text: 'AI-Powered Insights', color: 'from-yellow-400 to-orange-500' },
    { icon: TrendingUp, text: 'Real-Time Analytics', color: 'from-green-400 to-emerald-500' },
    { icon: Users, text: 'Smart Lead Scoring', color: 'from-blue-400 to-cyan-500' },
    { icon: Shield, text: 'Enterprise Security', color: 'from-purple-400 to-pink-500' },
  ]

  return (
    <div className="min-h-screen flex bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Left Side - Branding & Features */}
      <motion.div
        initial={{ opacity: 0, x: -50 }}
        animate={{ opacity: 1, x: 0 }}
        className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 p-12 flex-col justify-between relative overflow-hidden"
      >
        {/* Mesh gradient overlay */}
        <div className="absolute inset-0 opacity-30">
          <div className="absolute inset-0 bg-gradient-to-tr from-cyan-500/20 via-transparent to-yellow-500/20"></div>
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-pink-500/20 via-transparent to-transparent"></div>
        </div>
        
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden">
          <motion.div 
            animate={{ 
              scale: [1, 1.2, 1],
              rotate: [0, 90, 0],
            }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            className="absolute -top-40 -left-40 w-96 h-96 bg-gradient-to-br from-white/10 to-transparent rounded-full blur-3xl"
          />
          <motion.div 
            animate={{ 
              scale: [1, 1.3, 1],
              rotate: [0, -90, 0],
            }}
            transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
            className="absolute -bottom-40 -right-40 w-[500px] h-[500px] bg-gradient-to-tl from-white/10 to-transparent rounded-full blur-3xl"
          />
        </div>

        <div className="relative z-10">
          {/* Logo */}
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.6, type: "spring" }}
            className="inline-flex items-center space-x-4 mb-16 bg-white/10 backdrop-blur-xl rounded-3xl p-4 border border-white/20 shadow-2xl"
          >
            <div className="p-3 bg-gradient-to-br from-white/30 to-white/10 rounded-2xl">
              <Brain className="w-10 h-10 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-black text-white tracking-tight">Lead Mind</h1>
              <p className="text-white/80 font-medium text-sm">Intelligent CRM Platform</p>
            </div>
          </motion.div>

          {/* Main heading */}
          <motion.div
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.8 }}
            className="mb-16"
          >
            <h2 className="text-6xl font-black text-white mb-6 leading-[1.1] tracking-tight">
              Transform Your
              <span className="block bg-gradient-to-r from-cyan-200 via-white to-pink-200 bg-clip-text text-transparent">
                Customer
              </span>
              Relationships
            </h2>
            <p className="text-lg text-white/90 font-medium max-w-lg leading-relaxed">
              Powered by cutting-edge AI to help you close deals faster and build lasting customer relationships.
            </p>
          </motion.div>

          {/* Features Grid */}
          <div className="grid grid-cols-2 gap-5">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ y: 30, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.4 + index * 0.1, duration: 0.6 }}
                whileHover={{ y: -4, scale: 1.02 }}
                className="group bg-white/10 backdrop-blur-xl rounded-2xl p-5 border border-white/20 hover:bg-white/15 hover:border-white/30 transition-all duration-300 cursor-pointer shadow-lg hover:shadow-2xl"
              >
                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 shadow-xl group-hover:scale-110 transition-transform duration-300`}>
                  <feature.icon className="w-7 h-7 text-white" />
                </div>
                <p className="text-white font-bold text-base leading-snug">{feature.text}</p>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Success Metrics */}
        <motion.div
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.8, duration: 0.8 }}
          className="relative z-10"
        >
          <div className="bg-gradient-to-br from-white/15 to-white/5 backdrop-blur-xl rounded-3xl p-6 border border-white/20 shadow-2xl">
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center space-x-2">
                <motion.div 
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="w-2.5 h-2.5 bg-emerald-400 rounded-full shadow-lg"
                />
                <span className="text-white font-bold">Why Lead Mind?</span>
              </div>
              <span className="text-xs text-white/90 font-semibold bg-gradient-to-r from-white/20 to-white/10 px-3 py-1.5 rounded-full backdrop-blur-sm border border-white/20">Proven Results</span>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <motion.div 
                whileHover={{ scale: 1.05 }}
                className="text-center bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/20 hover:bg-white/15 transition-all"
              >
                <div className="text-3xl font-black text-white mb-1">3x</div>
                <div className="text-xs text-white/80 font-medium">Deal Closure</div>
              </motion.div>
              <motion.div 
                whileHover={{ scale: 1.05 }}
                className="text-center bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/20 hover:bg-white/15 transition-all"
              >
                <div className="text-3xl font-black text-white mb-1">50%</div>
                <div className="text-xs text-white/80 font-medium">Productivity</div>
              </motion.div>
              <motion.div 
                whileHover={{ scale: 1.05 }}
                className="text-center bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/20 hover:bg-white/15 transition-all"
              >
                <div className="text-3xl font-black text-white mb-1">80%</div>
                <div className="text-xs text-white/80 font-medium">Automation</div>
              </motion.div>
            </div>
          </div>
        </motion.div>
      </motion.div>

      {/* Right Side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 lg:p-12 bg-white dark:bg-gray-900 relative">
        {/* Mobile Logo */}
        <div className="lg:hidden absolute top-8 left-8">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl shadow-lg">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-black bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              Lead Mind
            </span>
          </div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.8 }}
          className="w-full max-w-md"
        >
          {/* Welcome back section */}
          <div className="mb-12">
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="inline-block mb-4"
            >
              <span className="text-sm font-bold text-purple-600 bg-purple-50 dark:bg-purple-900/20 px-4 py-2 rounded-full">
                👋 Welcome Back!
              </span>
            </motion.div>
            <motion.h2
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="text-4xl lg:text-5xl font-black text-gray-900 dark:text-white mb-3 tracking-tight"
            >
              Sign in to
              <span className="block bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                Lead Mind
              </span>
            </motion.h2>
            <motion.p
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.6 }}
              className="text-gray-600 dark:text-gray-400 text-base"
            >
              Access your intelligent CRM dashboard
            </motion.p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Username Field */}
            <motion.div
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.7 }}
            >
              <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-2.5">
                Username
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <User className="w-5 h-5 text-gray-400 group-focus-within:text-purple-500 transition-colors" />
                </div>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-12 pr-4 py-3.5 bg-gray-50 dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 focus:bg-white dark:focus:bg-gray-900 text-gray-900 dark:text-white font-medium transition-all duration-200 hover:border-gray-300 dark:hover:border-gray-600"
                  placeholder="Enter your username"
                  required
                />
              </div>
            </motion.div>

            {/* Password Field */}
            <motion.div
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.8 }}
            >
              <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-2.5">
                Password
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Lock className="w-5 h-5 text-gray-400 group-focus-within:text-purple-500 transition-colors" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-12 pr-12 py-3.5 bg-gray-50 dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 focus:bg-white dark:focus:bg-gray-900 text-gray-900 dark:text-white font-medium transition-all duration-200 hover:border-gray-300 dark:hover:border-gray-600"
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-purple-600 dark:hover:text-purple-400 transition-colors"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </motion.div>

            {/* Remember & Forgot */}
            <motion.div
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.9 }}
              className="flex items-center justify-between pt-1"
            >
              <label className="flex items-center cursor-pointer group">
                <input type="checkbox" className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-2 focus:ring-purple-500 transition-all" />
                <span className="ml-2.5 text-sm text-gray-600 dark:text-gray-400 font-medium group-hover:text-gray-900 dark:group-hover:text-gray-200 transition-colors">Remember me</span>
              </label>
              <a href="#" className="text-sm font-bold text-purple-600 hover:text-purple-700 dark:hover:text-purple-400 transition-colors">
                Forgot password?
              </a>
            </motion.div>

            {/* Submit Button */}
            <motion.button
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 1.0 }}
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              type="submit"
              disabled={loading}
              className="w-full mt-8 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white py-4 rounded-xl font-bold text-lg shadow-lg shadow-purple-500/30 hover:shadow-xl hover:shadow-purple-500/40 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-3 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Signing in...</span>
                </>
              ) : (
                <>
                  <span>Sign In</span>
                  <LogIn className="w-5 h-5" />
                </>
              )}
            </motion.button>
          </form>

          {/* Demo credentials */}
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 1.1 }}
            className="mt-6 p-4 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800/50 rounded-2xl"
          >
            <div className="flex items-center space-x-2 mb-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              <p className="text-sm text-blue-800 dark:text-blue-200 font-bold">Demo Credentials</p>
            </div>
            <p className="text-xs text-blue-700 dark:text-blue-300 font-medium">
              <span className="font-mono bg-white/60 dark:bg-gray-800/60 px-2.5 py-1 rounded-lg">admin</span>
              {' / '}
              <span className="font-mono bg-white/60 dark:bg-gray-800/60 px-2.5 py-1 rounded-lg">admin123</span>
            </p>
          </motion.div>

          {/* Sign up link */}
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 1.2 }}
            className="mt-8 text-center"
          >
            <p className="text-gray-600 dark:text-gray-400">
              Don't have an account?{' '}
              <Link to="/register" className="font-bold text-purple-600 hover:text-purple-700 dark:hover:text-purple-400 transition-colors">
                Sign up for free →
              </Link>
            </p>
          </motion.div>
        </motion.div>
      </div>
    </div>
  )
}

export default LoginPageEnhanced
