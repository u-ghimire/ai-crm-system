import React from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Sparkles, 
  TrendingUp, 
  Users, 
  BarChart3, 
  MessageSquare, 
  Shield, 
  Zap, 
  Globe,
  CheckCircle,
  ArrowRight,
  Star
} from 'lucide-react'

const LandingPage = () => {
  const navigate = useNavigate()

  const features = [
    {
      icon: Sparkles,
      title: 'AI-Powered Insights',
      description: 'Get intelligent recommendations and predictive analytics powered by advanced AI',
      gradient: 'from-purple-500 to-pink-500'
    },
    {
      icon: Users,
      title: 'Customer Management',
      description: 'Manage all your customer relationships in one centralized platform',
      gradient: 'from-blue-500 to-cyan-500'
    },
    {
      icon: BarChart3,
      title: 'Sales Analytics',
      description: 'Real-time dashboards and reports to track your sales performance',
      gradient: 'from-orange-500 to-red-500'
    },
    {
      icon: MessageSquare,
      title: 'Smart Chatbot',
      description: 'AI chatbot to handle customer inquiries and automate responses',
      gradient: 'from-green-500 to-emerald-500'
    },
    {
      icon: TrendingUp,
      title: 'Lead Scoring',
      description: 'Automatically score and prioritize leads based on engagement',
      gradient: 'from-indigo-500 to-purple-500'
    },
    {
      icon: Zap,
      title: 'Workflow Automation',
      description: 'Automate repetitive tasks and streamline your sales process',
      gradient: 'from-yellow-500 to-orange-500'
    }
  ]

  const benefits = [
    'Increase sales productivity by 40%',
    'Reduce response time by 60%',
    'Improve customer satisfaction',
    'Make data-driven decisions',
    'Scale your business efficiently',
    '24/7 AI-powered support'
  ]

  const stats = [
    { value: '3x', label: 'Faster Deal Closure' },
    { value: '50%', label: 'More Productive' },
    { value: '80%', label: 'Tasks Automated' },
    { value: '24/7', label: 'AI Assistance' }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100" style={{ color: '#111827' }}>
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 bg-white backdrop-blur-lg border-b border-gray-200 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold text-gray-900" style={{ color: '#111827' }}>
                Lead Mind
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/login')}
                className="px-6 py-2 text-gray-800 hover:text-gray-900 font-bold transition-colors"
                style={{ color: '#1f2937' }}
              >
                Sign In
              </button>
              <button
                onClick={() => navigate('/register')}
                className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-200"
              >
                Get Started
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="inline-flex items-center space-x-2 bg-purple-100 text-purple-700 px-4 py-2 rounded-full mb-6">
                <Sparkles className="w-4 h-4" />
                <span className="text-sm font-semibold" style={{ color: '#7c3aed' }}>Next-Generation CRM Platform</span>
              </div>
              <h1 className="text-5xl lg:text-6xl font-extrabold text-gray-900 mb-6 leading-tight" style={{ color: '#111827' }}>
                Transform Your Sales with{' '}
                <span style={{ color: '#111827'}}>AI-Powered CRM </span>
              </h1>
              <p className="text-xl text-gray-700 mb-8 leading-relaxed font-medium" style={{ color: '#374151' }}>
                Streamline your customer relationships, boost productivity, and close more deals with 
                intelligent automation and real-time insights.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <button
                  onClick={() => navigate('/register')}
                  className="group px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-bold text-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300 flex items-center justify-center space-x-2"
                >
                  <span>Start Free Trial</span>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>
                <button
                  onClick={() => navigate('/login')}
                  className="px-8 py-4 bg-white border-2 border-gray-300 text-gray-700 rounded-xl font-bold text-lg hover:border-purple-600 hover:text-purple-600 transition-all duration-300"
                >
                  Watch Demo
                </button>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="relative"
            >
              <div className="relative rounded-2xl overflow-hidden shadow-2xl">
                <div className="bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 p-8">
                  <div className="bg-white rounded-xl p-6 space-y-4">
                    {/* Mock Dashboard Preview */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full" />
                        <div>
                          <div className="h-3 w-24 bg-gray-200 rounded" />
                          <div className="h-2 w-16 bg-gray-100 rounded mt-1" />
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <div className="w-8 h-8 bg-green-100 rounded-lg" />
                        <div className="w-8 h-8 bg-blue-100 rounded-lg" />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg">
                        <div className="h-2 w-16 bg-blue-300 rounded mb-2" />
                        <div className="h-6 w-20 bg-blue-500 rounded" />
                      </div>
                      <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg">
                        <div className="h-2 w-16 bg-purple-300 rounded mb-2" />
                        <div className="h-6 w-20 bg-purple-500 rounded" />
                      </div>
                    </div>
                    <div className="space-y-2">
                      {[1, 2, 3].map((i) => (
                        <div key={i} className="flex items-center space-x-3 bg-gray-50 p-3 rounded-lg">
                          <div className="w-8 h-8 bg-gradient-to-br from-orange-400 to-red-400 rounded-full" />
                          <div className="flex-1">
                            <div className="h-2 bg-gray-200 rounded mb-1" />
                            <div className="h-2 w-2/3 bg-gray-100 rounded" />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
              {/* Floating elements */}
              <motion.div
                animate={{ y: [0, -10, 0] }}
                transition={{ duration: 3, repeat: Infinity }}
                className="absolute -top-6 -right-6 bg-white rounded-xl shadow-lg p-4"
              >
                <TrendingUp className="w-8 h-8 text-green-500" />
              </motion.div>
              <motion.div
                animate={{ y: [0, 10, 0] }}
                transition={{ duration: 3, repeat: Infinity, delay: 0.5 }}
                className="absolute -bottom-6 -left-6 bg-white rounded-xl shadow-lg p-4"
              >
                <Users className="w-8 h-8 text-blue-500" />
              </motion.div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                viewport={{ once: true }}
                className="text-center"
              >
                <div className="text-4xl lg:text-5xl font-bold text-white mb-2">{stat.value}</div>
                <div className="text-blue-100 font-medium">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4" style={{ color: '#111827' }}>
                Powerful Features for Modern Sales Teams
              </h2>
              <p className="text-xl text-gray-700 max-w-3xl mx-auto font-medium" style={{ color: '#374151' }}>
                Everything you need to manage customers, automate workflows, and grow your business
              </p>
            </motion.div>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="group bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 hover:border-transparent hover:-translate-y-2"
                >
                  <div className={`inline-flex p-4 bg-gradient-to-br ${feature.gradient} rounded-xl mb-4 group-hover:scale-110 transition-transform duration-300`}>
                    <Icon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-3" style={{ color: '#111827' }}>{feature.title}</h3>
                  <p className="text-gray-700 font-medium" style={{ color: '#374151' }}>{feature.description}</p>
                </motion.div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-gray-100 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <h2 className="text-4xl font-bold text-gray-900 mb-6" style={{ color: '#111827' }}>
                Why Choose Our CRM?
              </h2>
              <p className="text-xl text-gray-700 mb-8 font-medium" style={{ color: '#374151' }}>
                Join thousands of businesses that have transformed their sales process with our AI-powered platform.
              </p>
              <div className="space-y-4">
                {benefits.map((benefit, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    viewport={{ once: true }}
                    className="flex items-center space-x-3"
                  >
                    <div className="flex-shrink-0 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                      <CheckCircle className="w-4 h-4 text-white" />
                    </div>
                    <span className="text-lg text-gray-800 font-semibold" style={{ color: '#1f2937' }}>{benefit}</span>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="grid grid-cols-2 gap-6"
            >
              <div className="space-y-6">
                <div className="bg-white rounded-2xl p-6 shadow-lg">
                  <Shield className="w-12 h-12 text-blue-500 mb-4" />
                  <h4 className="font-bold text-gray-900 mb-2 text-lg" style={{ color: '#111827' }}>Secure & Reliable</h4>
                  <p className="text-sm text-gray-700 font-medium" style={{ color: '#111827' }}>Enterprise-grade security for your data</p>
                </div>
                <div className="bg-white rounded-2xl p-6 shadow-lg">
                  <Globe className="w-12 h-12 text-purple-500 mb-4" />
                  <h4 className="font-bold text-gray-900 mb-2 text-lg" style={{ color: '#111827' }}>Global Support</h4>
                  <p className="text-sm text-gray-700 font-medium" style={{ color: '#111827' }}>24/7 customer support worldwide</p>
                </div>
              </div>
              <div className="space-y-6 pt-12">
                <div className="bg-white rounded-2xl p-6 shadow-lg">
                  <Zap className="w-12 h-12 text-orange-500 mb-4" />
                  <h4 className="font-bold text-gray-900 mb-2 text-lg" style={{ color: '#111827' }}>Lightning Fast</h4>
                  <p className="text-sm text-gray-700 font-medium" style={{ color: '#111827' }}>Optimized for speed and performance</p>
                </div>
                <div className="bg-white rounded-2xl p-6 shadow-lg">
                  <BarChart3 className="w-12 h-12 text-green-500 mb-4" />
                  <h4 className="font-bold text-gray-900 mb-2 text-lg" style={{ color: '#111827' }}>Advanced Analytics</h4>
                  <p className="text-sm text-gray-700 font-medium" style={{ color: '#111827' }}>Deep insights into your business</p>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-3xl p-12 text-center relative overflow-hidden"
          >
            <div className="absolute inset-0 bg-black/10" />
            <div className="relative z-10">
              <h2 className="text-4xl lg:text-5xl font-bold text-white mb-6">
                Ready to Transform Your Sales?
              </h2>
              <p className="text-xl text-white mb-8 max-w-2xl mx-auto font-medium">
                Start your free trial today. No credit card required. Cancel anytime.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={() => navigate('/register')}
                  className="px-8 py-4 bg-white text-purple-600 rounded-xl font-bold text-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300"
                >
                  Get Started Free
                </button>
                <button
                  onClick={() => navigate('/login')}
                  className="px-8 py-4 bg-transparent border-2 border-white text-white rounded-xl font-bold text-lg hover:bg-white hover:text-purple-600 transition-all duration-300"
                >
                  Sign In
                </button>
              </div>
              <p className="text-sm text-white mt-6 font-semibold">
                Demo credentials: <strong>admin / admin123</strong>
              </p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold">Lead Mind</span>
          </div>
          <p className="text-gray-300 mb-6 font-medium">
            Empowering businesses with intelligent customer relationship management
          </p>
          <div className="flex justify-center space-x-6 text-sm text-gray-300 font-medium">
            <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
            <a href="#" className="hover:text-white transition-colors">Contact</a>
          </div>
          <p className="text-sm text-gray-400 mt-6 font-medium">
            © 2025 Lead Mind. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage
