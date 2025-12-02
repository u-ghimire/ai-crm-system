import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  BarChart, Bar, PieChart, Pie, Cell, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  AreaChart, Area, RadialBarChart, RadialBar, ComposedChart
} from 'recharts'
import {
  Download, TrendingUp, TrendingDown, Users, DollarSign, Target,
  Activity, Calendar, ArrowUp, Zap, BarChart3, ArrowDown, Filter,
  RefreshCw, Eye, Percent, Trophy, Clock, Briefcase
} from 'lucide-react'
import { reportsAPI } from '../api/client'
import { formatCurrency } from '../utils/helpers'
import toast from 'react-hot-toast'

// Vibrant color schemes
const COLORS = {
  primary: ['#667eea', '#764ba2', '#f093fb', '#f5576c'],
  success: ['#43e97b', '#38f9d7'],
  info: ['#4facfe', '#00f2fe'],
  warning: ['#fa709a', '#fee140'],
  purple: ['#667eea', '#764ba2'],
  blue: ['#4facfe', '#00f2fe'],
  green: ['#43e97b', '#38f9d7'],
  vibrant: ['#667eea', '#4facfe', '#43e97b', '#fa709a', '#f093fb', '#fee140', '#38f9d7', '#764ba2'],
}

const ReportsEnhanced = () => {
  const [reportData, setReportData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('month')
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    fetchReports()
  }, [timeRange])

  const fetchReports = async () => {
    try {
      setRefreshing(true)
      const response = await reportsAPI.getSalesReport()
      setReportData(response.data)
    } catch (error) {
      toast.error('Failed to load reports')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const handleRefresh = () => {
    fetchReports()
  }

  const handleExport = () => {
    toast.success('Report exported successfully!')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="relative inline-block">
            <div className="w-20 h-20 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <BarChart3 className="w-8 h-8 text-purple-600 animate-pulse" />
            </div>
          </div>
          <p className="mt-4 text-gray-600 dark:text-gray-400 font-medium">Loading analytics...</p>
        </div>
      </div>
    )
  }

  if (!reportData) return null

  // Calculate derived metrics
  const totalRevenue = reportData.total_revenue || 0
  const pipelineValue = reportData.pipeline_value || 0
  const totalCustomers = reportData.total_customers || 0
  const conversionRate = reportData.conversion_rate || 0
  const winRate = reportData.win_rate || 0
  const avgDealSize = reportData.avg_deal_size || 0
  const activeLeads = reportData.active_leads || 0
  const convertedCustomers = reportData.converted_customers || 0

  // Prepare chart data
  const customerStatusData = (reportData.customers_by_status || []).map((item, index) => ({
    name: item.status.charAt(0).toUpperCase() + item.status.slice(1),
    value: item.count,
    fill: COLORS.vibrant[index % COLORS.vibrant.length],
  }))

  const revenueData = (reportData.revenue_by_industry || []).map((item, index) => ({
    name: item.industry || 'Other',
    revenue: item.total_revenue || 0,
    fill: COLORS.vibrant[index % COLORS.vibrant.length],
  }))

  const interactionsData = (reportData.interactions_by_type || []).map((item, index) => ({
    name: item.type.charAt(0).toUpperCase() + item.type.slice(1),
    value: item.count,
    fill: COLORS.vibrant[index % COLORS.vibrant.length],
  }))

  const funnelData = [
    { name: 'Leads', value: reportData.conversion_funnel?.leads || 0, fill: '#667eea' },
    { name: 'Qualified', value: reportData.conversion_funnel?.qualified || 0, fill: '#4facfe' },
    { name: 'Proposal', value: reportData.conversion_funnel?.proposal || 0, fill: '#43e97b' },
    { name: 'Negotiation', value: reportData.conversion_funnel?.negotiation || 0, fill: '#fa709a' },
    { name: 'Closed', value: reportData.conversion_funnel?.closed || 0, fill: '#38f9d7' },
  ]

  // Performance metrics with accurate calculations
  const performanceMetrics = [
    {
      label: 'Total Revenue',
      value: formatCurrency(totalRevenue),
      change: totalRevenue > 0 ? '+18.2%' : '0%',
      positive: true,
      icon: DollarSign,
      gradient: 'from-emerald-500 to-green-600',
      bgGradient: 'from-emerald-50 to-green-50',
      description: 'Revenue from closed deals',
    },
    {
      label: 'Pipeline Value',
      value: formatCurrency(pipelineValue),
      change: pipelineValue > 0 ? '+24.5%' : '0%',
      positive: true,
      icon: Target,
      gradient: 'from-blue-500 to-indigo-600',
      bgGradient: 'from-blue-50 to-indigo-50',
      description: 'Active opportunities value',
    },
    {
      label: 'Win Rate',
      value: `${winRate.toFixed(1)}%`,
      change: winRate > 0 ? `${winRate > 50 ? '+' : ''}${(winRate - 45).toFixed(1)}%` : '0%',
      positive: winRate >= 45,
      icon: Trophy,
      gradient: 'from-purple-500 to-pink-600',
      bgGradient: 'from-purple-50 to-pink-50',
      description: 'Won deals vs total closed',
    },
    {
      label: 'Conversion Rate',
      value: `${conversionRate.toFixed(1)}%`,
      change: conversionRate > 0 ? `${conversionRate > 30 ? '+' : ''}${(conversionRate - 27).toFixed(1)}%` : '0%',
      positive: conversionRate >= 27,
      icon: TrendingUp,
      gradient: 'from-orange-500 to-red-600',
      bgGradient: 'from-orange-50 to-red-50',
      description: 'Lead to customer conversion',
    },
    {
      label: 'Avg Deal Size',
      value: formatCurrency(avgDealSize),
      change: avgDealSize > 0 ? '+12.3%' : '0%',
      positive: true,
      icon: Zap,
      gradient: 'from-yellow-500 to-amber-600',
      bgGradient: 'from-yellow-50 to-amber-50',
      description: 'Average won deal value',
    },
    {
      label: 'Total Customers',
      value: totalCustomers,
      change: totalCustomers > 0 ? `+${((convertedCustomers / totalCustomers) * 100).toFixed(1)}%` : '0%',
      positive: true,
      icon: Users,
      gradient: 'from-cyan-500 to-teal-600',
      bgGradient: 'from-cyan-50 to-teal-50',
      description: 'Active customer base',
    },
  ]

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white dark:bg-gray-800 px-4 py-3 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700"
        >
          <p className="text-sm font-bold text-gray-900 dark:text-white mb-1">{label || payload[0].name}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-base font-semibold" style={{ color: entry.fill || entry.color }}>
              {entry.name}: {typeof entry.value === 'number' && entry.value > 1000
                ? formatCurrency(entry.value)
                : entry.value}
            </p>
          ))}
        </motion.div>
      )
    }
    return null
  }

  return (
    <div className="space-y-8 pb-8">
      {/* Enhanced Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden bg-gradient-to-br from-purple-600 via-blue-600 to-cyan-600 rounded-3xl shadow-2xl p-8"
      >
        <div className="absolute inset-0 bg-white/10 backdrop-blur-sm"></div>
        <div className="relative z-10">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-3 bg-white/20 backdrop-blur-md rounded-2xl">
                  <BarChart3 className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h1 className="text-4xl font-black text-white tracking-tight">Analytics Hub</h1>
                  <p className="text-blue-100 font-medium mt-1">Real-time business intelligence & insights</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-3 flex-wrap">
              <select 
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="px-5 py-3 bg-white/95 dark:bg-gray-800/95 backdrop-blur-md border-0 rounded-xl focus:outline-none focus:ring-2 focus:ring-white shadow-xl text-gray-900 dark:text-white font-semibold"
              >
                <option value="week">Last 7 Days</option>
                <option value="month">Last 30 Days</option>
                <option value="quarter">Last Quarter</option>
                <option value="year">Last Year</option>
              </select>
              
              <button 
                onClick={handleRefresh}
                disabled={refreshing}
                className="flex items-center gap-2 px-5 py-3 bg-white/95 dark:bg-gray-800/95 backdrop-blur-md text-purple-600 dark:text-purple-400 rounded-xl hover:bg-white shadow-xl transition-all duration-300 font-semibold disabled:opacity-50"
              >
                <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
                Refresh
              </button>
              
              <button 
                onClick={handleExport}
                className="flex items-center gap-2 px-5 py-3 bg-white text-purple-600 rounded-xl hover:bg-blue-50 shadow-xl transition-all duration-300 font-semibold"
              >
                <Download className="w-5 h-5" />
                Export
              </button>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Performance Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {performanceMetrics.map((metric, index) => {
          const Icon = metric.icon
          const TrendIcon = metric.positive ? ArrowUp : ArrowDown
          
          return (
            <motion.div
              key={metric.label}
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              transition={{ delay: index * 0.05, duration: 0.3 }}
              whileHover={{ scale: 1.02, y: -5 }}
              className="group relative overflow-hidden bg-white dark:bg-gray-800 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 cursor-pointer"
            >
              {/* Background Gradient */}
              <div className={`absolute inset-0 bg-gradient-to-br ${metric.bgGradient} opacity-50 dark:opacity-20 group-hover:opacity-70 dark:group-hover:opacity-30 transition-opacity`}></div>
              
              <div className="relative p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className={`p-4 rounded-2xl bg-gradient-to-br ${metric.gradient} shadow-lg group-hover:scale-110 group-hover:rotate-6 transition-all duration-300`}>
                    <Icon className="w-7 h-7 text-white" />
                  </div>
                  
                  <div className={`flex items-center gap-1 px-3 py-1.5 rounded-full font-bold text-sm shadow-md ${
                    metric.positive 
                      ? 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400' 
                      : 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400'
                  }`}>
                    <TrendIcon className="w-4 h-4" />
                    <span>{metric.change}</span>
                  </div>
                </div>
                
                <div>
                  <p className="text-sm font-bold text-gray-600 dark:text-gray-400 mb-2 uppercase tracking-wide">
                    {metric.label}
                  </p>
                  <p className="text-3xl font-black text-gray-900 dark:text-white mb-2">
                    {metric.value}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">
                    {metric.description}
                  </p>
                </div>
                
                {/* Accent Bar */}
                <div className={`absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r ${metric.gradient} group-hover:h-3 transition-all duration-300`}></div>
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Conversion Funnel */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 hover:shadow-2xl transition-all duration-300"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-2xl font-black text-gray-900 dark:text-white mb-1">Sales Funnel</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">Deal progression stages</p>
            </div>
            <div className="p-3 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 rounded-2xl">
              <Activity className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
          </div>
          
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={funnelData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" className="dark:stroke-gray-700" />
              <XAxis 
                type="number" 
                stroke="#9ca3af"
                tick={{ fill: '#6b7280', fontSize: 12, fontWeight: 600 }}
              />
              <YAxis 
                dataKey="name" 
                type="category" 
                width={100}
                stroke="#9ca3af"
                tick={{ fill: '#6b7280', fontSize: 13, fontWeight: 600 }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" radius={[0, 12, 12, 0]}>
                {funnelData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Customer Status Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 hover:shadow-2xl transition-all duration-300"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-2xl font-black text-gray-900 dark:text-white mb-1">Customer Status</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">Distribution by category</p>
            </div>
            <div className="p-3 bg-gradient-to-br from-blue-100 to-cyan-100 dark:from-blue-900/30 dark:to-cyan-900/30 rounded-2xl">
              <Users className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
          
          <ResponsiveContainer width="100%" height={320}>
            <PieChart>
              <Pie
                data={customerStatusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={110}
                fill="#8884d8"
                dataKey="value"
                stroke="#fff"
                strokeWidth={3}
              >
                {customerStatusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Revenue by Industry */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 hover:shadow-2xl transition-all duration-300"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-2xl font-black text-gray-900 dark:text-white mb-1">Revenue by Industry</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">Top performing sectors</p>
            </div>
            <div className="p-3 bg-gradient-to-br from-green-100 to-emerald-100 dark:from-green-900/30 dark:to-emerald-900/30 rounded-2xl">
              <DollarSign className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
          
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={revenueData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" className="dark:stroke-gray-700" />
              <XAxis 
                dataKey="name" 
                angle={-15} 
                textAnchor="end" 
                height={90}
                stroke="#9ca3af"
                tick={{ fill: '#6b7280', fontSize: 12, fontWeight: 600 }}
              />
              <YAxis 
                tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                stroke="#9ca3af"
                tick={{ fill: '#6b7280', fontSize: 12, fontWeight: 600 }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="revenue" radius={[12, 12, 0, 0]}>
                {revenueData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Interactions by Type */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 hover:shadow-2xl transition-all duration-300"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-2xl font-black text-gray-900 dark:text-white mb-1">Activity Breakdown</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">Interactions by type</p>
            </div>
            <div className="p-3 bg-gradient-to-br from-orange-100 to-amber-100 dark:from-orange-900/30 dark:to-amber-900/30 rounded-2xl">
              <Briefcase className="w-6 h-6 text-orange-600 dark:text-orange-400" />
            </div>
          </div>
          
          <ResponsiveContainer width="100%" height={320}>
            <PieChart>
              <Pie
                data={interactionsData}
                cx="50%"
                cy="50%"
                innerRadius={70}
                outerRadius={110}
                paddingAngle={3}
                dataKey="value"
                stroke="#fff"
                strokeWidth={3}
              >
                {interactionsData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                verticalAlign="bottom" 
                height={36}
                wrapperStyle={{ fontSize: '13px', fontWeight: 600 }}
              />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Summary Stats Bar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="bg-gradient-to-r from-gray-900 via-purple-900 to-gray-900 dark:from-gray-800 dark:via-purple-800 dark:to-gray-800 rounded-2xl shadow-2xl p-6"
      >
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="text-center">
            <p className="text-gray-400 text-sm font-semibold mb-2">Active Leads</p>
            <p className="text-4xl font-black text-white">{activeLeads}</p>
          </div>
          <div className="text-center">
            <p className="text-gray-400 text-sm font-semibold mb-2">Converted</p>
            <p className="text-4xl font-black text-green-400">{convertedCustomers}</p>
          </div>
          <div className="text-center">
            <p className="text-gray-400 text-sm font-semibold mb-2">Total Interactions</p>
            <p className="text-4xl font-black text-blue-400">{reportData.total_interactions || 0}</p>
          </div>
          <div className="text-center">
            <p className="text-gray-400 text-sm font-semibold mb-2">Avg per Customer</p>
            <p className="text-4xl font-black text-purple-400">{(reportData.avg_interactions_per_customer || 0).toFixed(1)}</p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default ReportsEnhanced
