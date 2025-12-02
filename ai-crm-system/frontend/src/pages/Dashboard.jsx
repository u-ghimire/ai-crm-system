import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import DashboardStats from '../components/Dashboard/DashboardStats'
import SalesForecast from '../components/Dashboard/SalesForecast'
import TopLeads from '../components/Dashboard/TopLeads'
import RecentInteractions from '../components/Dashboard/RecentInteractions'
import AIReportModal from '../components/Dashboard/AIReportModal'
import AIInsightsWidget from '../components/AI/AIInsightsWidget'
import { dashboardAPI } from '../api/client'
import { Sparkles } from 'lucide-react'
import toast from 'react-hot-toast'

const Dashboard = () => {
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [showReport, setShowReport] = useState(false)
  const [aiReport, setAiReport] = useState(null)

  useEffect(() => {
    fetchAnalytics()
  }, [])

  const fetchAnalytics = async () => {
    try {
      const response = await dashboardAPI.getAnalytics()
      setAnalytics(response.data)
    } catch (error) {
      toast.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateAIReport = async () => {
    setGenerating(true)
    const loadingToast = toast.loading('Generating AI-powered business report...')
    
    try {
      const response = await dashboardAPI.generateAIReport()
      setAiReport(response.data)
      setShowReport(true)
      
      toast.dismiss(loadingToast)
      toast.success('AI Report generated successfully!', {
        duration: 3000,
      })
      
    } catch (error) {
      toast.dismiss(loadingToast)
      toast.error('Failed to generate AI report')
      console.error('Report generation error:', error)
    } finally {
      setGenerating(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-4xl font-extrabold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
            Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2 text-lg">Welcome back! Here's your business overview.</p>
        </div>
        <button 
          onClick={handleGenerateAIReport}
          disabled={generating}
          className="group relative overflow-hidden bg-gradient-to-r from-purple-600 via-pink-600 to-red-500 text-white px-8 py-3 rounded-2xl font-bold hover:shadow-2xl hover:shadow-purple-500/50 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105"
        >
          <span className="relative z-10 flex items-center space-x-2">
            <Sparkles className={`w-5 h-5 ${generating ? 'animate-spin' : ''}`} />
            <span>{generating ? 'Generating...' : 'Generate AI Report'}</span>
          </span>
          <div className="absolute inset-0 bg-gradient-to-r from-yellow-400 to-orange-500 opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
        </button>
      </motion.div>

      {analytics && (
        <>
          <DashboardStats analytics={analytics} />
          
          {/* AI Insights and Forecasting */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="lg:col-span-2 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-3xl shadow-xl p-1"
            >
              <div className="bg-white dark:bg-gray-800 rounded-3xl p-6 h-full">
                <SalesForecast forecast={analytics.sales_forecast} />
              </div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-gradient-to-br from-purple-50 to-pink-100 rounded-3xl shadow-xl p-1 max-h-[600px]"
            >
              <div className="bg-white dark:bg-gray-800 rounded-3xl p-6 h-full overflow-hidden flex flex-col">
                <AIInsightsWidget />
              </div>
            </motion.div>
          </div>
          
          {/* Top Leads */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-gradient-to-br from-green-50 to-emerald-100 rounded-3xl shadow-xl p-1"
          >
            <div className="bg-white dark:bg-gray-800 rounded-3xl p-6 h-full">
              <TopLeads leads={analytics.top_leads} />
            </div>
          </motion.div>
          
          {/* Recent Interactions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.45 }}
            className="bg-gradient-to-br from-blue-50 to-cyan-100 rounded-3xl shadow-xl p-1"
          >
            <div className="bg-white dark:bg-gray-800 rounded-3xl p-6">
              <RecentInteractions interactions={analytics.recent_interactions} />
            </div>
          </motion.div>
        </>
      )}

      <AIReportModal 
        isOpen={showReport}
        onClose={() => setShowReport(false)}
        report={aiReport}
      />
    </div>
  )
}

export default Dashboard