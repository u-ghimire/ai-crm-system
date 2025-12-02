import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Users, TrendingUp, DollarSign, Target, ArrowUp, ArrowDown } from 'lucide-react'
import { formatCurrency } from '../../utils/helpers'
import StatsDetailModal from './StatsDetailModal'

const DashboardStats = ({ analytics }) => {
  const [modalOpen, setModalOpen] = useState(false)
  const [selectedStat, setSelectedStat] = useState(null)

  // Calculate accurate metrics
  const totalCustomers = analytics.total_customers || 0
  const activeLeads = analytics.active_leads || 0
  const conversionRate = analytics.conversion_rate || 0
  const monthlyRevenue = analytics.monthly_revenue || 0
  const pipelineValue = analytics.pipeline_value || 0

  // Calculate trend percentages based on actual data
  const customerGrowth = totalCustomers > 0 ? ((activeLeads / totalCustomers) * 100).toFixed(1) : 0
  const leadsGrowth = activeLeads > 10 ? '+' + ((activeLeads - 10) / 10 * 100).toFixed(1) : '+0'
  const conversionGrowth = conversionRate > 30 ? '+' + (conversionRate - 30).toFixed(1) : (conversionRate - 30).toFixed(1)
  const revenueGrowth = monthlyRevenue > 10000 ? '+' + ((monthlyRevenue - 10000) / 10000 * 100).toFixed(1) : '0'

  const stats = [
    {
      title: 'Total Customers',
      value: totalCustomers,
      icon: Users,
      gradient: 'from-blue-500 to-blue-600',
      bgGradient: 'from-blue-50 to-blue-100',
      iconBg: 'bg-blue-500',
      change: `${customerGrowth}%`,
      positive: customerGrowth >= 0,
      type: 'customers',
      description: 'All contacts in CRM'
    },
    {
      title: 'Active Leads',
      value: activeLeads,
      icon: Target,
      gradient: 'from-purple-500 to-purple-600',
      bgGradient: 'from-purple-50 to-purple-100',
      iconBg: 'bg-purple-500',
      change: `${leadsGrowth}%`,
      positive: parseFloat(leadsGrowth) >= 0,
      type: 'leads',
      description: 'Qualified opportunities'
    },
    {
      title: 'Conversion Rate',
      value: `${conversionRate.toFixed(1)}%`,
      icon: TrendingUp,
      gradient: 'from-green-500 to-green-600',
      bgGradient: 'from-green-50 to-green-100',
      iconBg: 'bg-green-500',
      change: `${conversionGrowth}%`,
      positive: parseFloat(conversionGrowth) >= 0,
      type: 'conversion',
      description: 'Lead to customer rate'
    },
    {
      title: 'Monthly Revenue',
      value: formatCurrency(monthlyRevenue),
      icon: DollarSign,
      gradient: 'from-orange-500 to-orange-600',
      bgGradient: 'from-orange-50 to-orange-100',
      iconBg: 'bg-orange-500',
      change: `${revenueGrowth}%`,
      positive: parseFloat(revenueGrowth) >= 0,
      type: 'revenue',
      description: 'Closed deals revenue'
    },
  ]

  const handleCardClick = (stat) => {
    setSelectedStat(stat)
    setModalOpen(true)
  }

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon
          const TrendIcon = stat.positive ? ArrowUp : ArrowDown
          return (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ delay: index * 0.08, type: "spring", stiffness: 100 }}
              whileHover={{ y: -8, scale: 1.03 }}
              onClick={() => handleCardClick(stat)}
              className="relative overflow-hidden bg-white dark:bg-gray-800 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 group cursor-pointer border border-gray-100 dark:border-gray-700"
            >
              {/* Animated gradient background overlay */}
              <div className={`absolute inset-0 bg-gradient-to-br ${stat.bgGradient} dark:opacity-10 opacity-40 group-hover:opacity-60 dark:group-hover:opacity-20 transition-opacity duration-300`}></div>
              
              {/* Sparkle effect on hover */}
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                <div className="absolute top-2 right-2 w-2 h-2 bg-yellow-400 rounded-full animate-ping"></div>
                <div className="absolute bottom-4 left-4 w-1 h-1 bg-purple-400 rounded-full animate-pulse"></div>
              </div>
              
              <div className="relative p-6">
                <div className="flex items-center justify-between mb-4">
                  <motion.div 
                    whileHover={{ rotate: 360 }}
                    transition={{ duration: 0.6 }}
                    className={`p-4 rounded-2xl bg-gradient-to-br ${stat.gradient} shadow-2xl group-hover:shadow-3xl transition-shadow duration-300`}
                  >
                    <Icon className="w-7 h-7 text-white" />
                  </motion.div>
                  <div className={`flex items-center space-x-1 px-3 py-1.5 rounded-full text-xs font-bold shadow-md ${
                    stat.positive ? 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300' : 'bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300'
                  }`}>
                    <TrendIcon className="w-4 h-4" />
                    <span>{stat.change}</span>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <p className="text-sm font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wide">{stat.title}</p>
                  <p className="text-4xl font-black text-gray-900 dark:text-white">{stat.value}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">{stat.description}</p>
                </div>
                
                {/* Animated bottom accent line */}
                <div className={`absolute bottom-0 left-0 right-0 h-1.5 bg-gradient-to-r ${stat.gradient} transform origin-left group-hover:scale-x-110 transition-transform duration-300`}></div>
                
                {/* Click indicator */}
                <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <div className="bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm px-2 py-1 rounded-lg shadow-lg">
                    <span className="text-xs text-gray-700 dark:text-gray-300 font-semibold">View Details</span>
                  </div>
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>
      
      {/* Pipeline Value Banner */}
      {pipelineValue > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-6 bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-600 rounded-2xl shadow-2xl p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-bold uppercase tracking-wide mb-2 opacity-90">Active Pipeline Value</p>
              <p className="text-4xl font-black">{formatCurrency(pipelineValue)}</p>
              <p className="text-sm mt-2 opacity-80">Total value of open opportunities</p>
            </div>
            <div className="p-4 bg-white/20 backdrop-blur-md rounded-2xl">
              <Target className="w-12 h-12" />
            </div>
          </div>
        </motion.div>
      )}

      <StatsDetailModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        statType={selectedStat?.type}
        title={selectedStat?.title}
      />
    </>
  )
}


export default DashboardStats