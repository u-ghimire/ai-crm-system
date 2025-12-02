import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { BarChart, Bar, PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, FunnelChart, Funnel, LabelList } from 'recharts'
import { Download, TrendingUp, TrendingDown, Users, DollarSign, Target, Activity, Calendar } from 'lucide-react'
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

  const funnelData = reportData?.conversion_funnel
    ? [
        { name: 'Leads', value: reportData.conversion_funnel.leads, fill: '#8b5cf6' },
        { name: 'Qualified', value: reportData.conversion_funnel.qualified, fill: '#3b82f6' },
        { name: 'Proposal', value: reportData.conversion_funnel.proposal, fill: '#10b981' },
        { name: 'Negotiation', value: reportData.conversion_funnel.negotiation, fill: '#f59e0b' },
        { name: 'Closed', value: reportData.conversion_funnel.closed, fill: '#22c55e' }
      ]
    : []

  const interactionsData = reportData?.interactions_by_type
    ? Object.entries(reportData.interactions_by_type).map(([name, value]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        value
      }))
    : []

  const COLORS = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#6366f1']

  const handleExport = () => {
    toast.success('Export functionality coming soon!')
  }

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
        <button onClick={handleExport} className="btn-primary flex items-center space-x-2">
          <Download className="w-4 h-4" />
          <span>Export Report</span>
        </button>
      </motion.div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card"
        >
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-600 mb-1">Total Revenue</h3>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(reportData?.total_revenue || 0)}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {reportData?.converted_customers || 0} customers
              </p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <DollarSign className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card"
        >
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-600 mb-1">Pipeline Value</h3>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(reportData?.pipeline_value || 0)}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Active opportunities
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Target className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-600 mb-1">Conversion Rate</h3>
              <p className="text-2xl font-bold text-gray-900">
                {reportData?.conversion_rate || 0}%
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Win rate: {reportData?.win_rate || 0}%
              </p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-600 mb-1">Avg Deal Size</h3>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(reportData?.avg_deal_size || 0)}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {reportData?.total_interactions || 0} interactions
              </p>
            </div>
            <div className="p-3 bg-orange-100 rounded-lg">
              <Activity className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </motion.div>
      </div>

      {/* Secondary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card bg-gradient-to-br from-blue-50 to-purple-50"
        >
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-700">Total Customers</h3>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {reportData?.total_customers || 0}
              </p>
            </div>
            <Users className="w-10 h-10 text-blue-500 opacity-50" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="card bg-gradient-to-br from-green-50 to-emerald-50"
        >
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-700">Active Leads</h3>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {reportData?.active_leads || 0}
              </p>
            </div>
            <Target className="w-10 h-10 text-green-500 opacity-50" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="card bg-gradient-to-br from-orange-50 to-amber-50"
        >
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-700">Avg Interactions</h3>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {reportData?.avg_interactions_per_customer || 0}
              </p>
            </div>
            <Activity className="w-10 h-10 text-orange-500 opacity-50" />
          </div>
        </motion.div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="card"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Conversion Funnel</h2>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={funnelData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" />
              <Tooltip />
              <Bar dataKey="value" radius={[0, 8, 8, 0]}>
                {funnelData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="card"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Customers by Status</h2>
          <ResponsiveContainer width="100%" height={350}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={120}
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
          transition={{ delay: 0.9 }}
          className="card"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Revenue by Industry</h2>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={industryData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis tickFormatter={(value) => `$${(value/1000).toFixed(0)}k`} />
              <Tooltip formatter={(value) => formatCurrency(value)} />
              <Bar dataKey="value" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.0 }}
          className="card"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Interactions by Type</h2>
          <ResponsiveContainer width="100%" height={350}>
            <PieChart>
              <Pie
                data={interactionsData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={120}
                fill="#8884d8"
                paddingAngle={5}
                dataKey="value"
                label
              >
                {interactionsData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>
      </div>
    </div>
  )
}

export default Reports
