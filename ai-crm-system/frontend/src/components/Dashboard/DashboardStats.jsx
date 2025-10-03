import React from 'react'
import { motion } from 'framer-motion'
import { Users, TrendingUp, DollarSign, Target } from 'lucide-react'
import { formatCurrency } from '../../utils/helpers'

const DashboardStats = ({ analytics }) => {
  const stats = [
    {
      title: 'Total Customers',
      value: analytics.total_customers,
      icon: Users,
      color: 'bg-blue-500',
      change: '+12%',
    },
    {
      title: 'Active Leads',
      value: analytics.active_leads,
      icon: Target,
      color: 'bg-purple-500',
      change: '+5%',
    },
    {
      title: 'Conversion Rate',
      value: `${analytics.conversion_rate}%`,
      icon: TrendingUp,
      color: 'bg-green-500',
      change: '+3.2%',
    },
    {
      title: 'Monthly Revenue',
      value: formatCurrency(analytics.monthly_revenue),
      icon: DollarSign,
      color: 'bg-yellow-500',
      change: '+18%',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => {
        const Icon = stat.icon
        return (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="card hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                <p className="text-sm text-green-600 mt-2">{stat.change}</p>
              </div>
              <div className={`${stat.color} p-3 rounded-lg`}>
                <Icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </motion.div>
        )
      })}
    </div>
  )
}

export default DashboardStats