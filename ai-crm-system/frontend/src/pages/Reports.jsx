import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Download, TrendingUp } from 'lucide-react'
import { reportsAPI } from '../api/client'
import { formatCurrency } from '../utils/helpers'
import toast from 'react-hot-toast'

const Reports = () => {
  const [reportData, setReportData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchReports()
  }, [])

  const fetchReports = async () => {
    try {
      const response = await reportsAPI.getSalesReport()
      setReportData(response.data)
    } catch (error) {
      toast.error('Failed to load reports')
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

  const statusData = reportData?.customers_by_status 
    ? Object.entries(reportData.customers_by_status).map(([name, value]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        value
      }))
    : []

  const industryData = reportData?.revenue_by_industry
    ? Object.entries(reportData.revenue_by_industry).map(([name, value]) => ({
        name,
        value
      }))
    : []

  const COLORS = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#6366f1']

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Reports & Analytics</h1>
          <p className="text-gray-600 mt-1">Insights into your business performance</p>
        </div>
        <button className="btn-primary flex items-center space-x-2">
          <Download className="w-4 h-4" />
          <span>Export Report</span>
        </button>
      </motion.div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card"
        >
          <h3 className="text-sm font-medium text-gray-600 mb-2">Total Revenue</h3>
          <p className="text-3xl font-bold text-gray-900">
            {formatCurrency(reportData?.total_revenue || 0)}
          </p>
          <div className="flex items-center space-x-2 mt-2 text-green-600">
            <TrendingUp className="w-4 h-4" />
            <span className="text-sm">+12% from last month</span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card"
        >
          <h3 className="text-sm font-medium text-gray-600 mb-2">Pipeline Value</h3>
          <p className="text-3xl font-bold text-gray-900">
            {formatCurrency(reportData?.pipeline_value || 0)}
          </p>
          <div className="flex items-center space-x-2 mt-2 text-blue-600">
            <TrendingUp className="w-4 h-4" />
            <span className="text-sm">+8% from last month</span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <h3 className="text-sm font-medium text-gray-600 mb-2">Total Customers</h3>
          <p className="text-3xl font-bold text-gray-900">
            {Object.values(reportData?.customers_by_status || {}).reduce((a, b) => a + b, 0)}
          </p>
          <div className="flex items-center space-x-2 mt-2 text-purple-600">
            <TrendingUp className="w-4 h-4" />
            <span className="text-sm">+15% from last month</span>
          </div>
        </motion.div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Customers by Status</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Revenue by Industry</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={industryData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis tickFormatter={(value) => `$${value/1000}k`} />
              <Tooltip formatter={(value) => formatCurrency(value)} />
              <Bar dataKey="value" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>
    </div>
  )
}

export default Reports
