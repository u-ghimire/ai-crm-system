import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import DashboardStats from '../components/Dashboard/DashboardStats'
import SalesForecast from '../components/Dashboard/SalesForecast'
import TopLeads from '../components/Dashboard/TopLeads'
import RecentInteractions from '../components/Dashboard/RecentInteractions'
import { dashboardAPI } from '../api/client'
import { Sparkles } from 'lucide-react'
import toast from 'react-hot-toast'

const Dashboard = () => {
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)

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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Welcome back! Here's your business overview.</p>
        </div>
        <button className="btn-primary flex items-center space-x-2">
          <Sparkles className="w-4 h-4" />
          <span>Generate AI Report</span>
        </button>
      </motion.div>

      {analytics && (
        <>
          <DashboardStats analytics={analytics} />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <SalesForecast forecast={analytics.sales_forecast} />
            <TopLeads leads={analytics.top_leads} />
          </div>
          <RecentInteractions interactions={analytics.recent_interactions} />
        </>
      )}
    </div>
  )
}

export default Dashboard