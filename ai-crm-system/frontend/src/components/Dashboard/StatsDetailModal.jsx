import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, User, Building2, TrendingUp, DollarSign, Calendar, Mail, Phone } from 'lucide-react'
import api from '../../api/client'
import { formatCurrency } from '../../utils/helpers'

const StatsDetailModal = ({ isOpen, onClose, statType, title }) => {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (isOpen) {
      fetchDetailData()
    }
  }, [isOpen, statType])

  const fetchDetailData = async () => {
    setLoading(true)
    try {
      let response
      switch (statType) {
        case 'customers':
          response = await api.get('/customers')
          setData(response.data || [])
          break
        case 'leads':
          response = await api.get('/customers')
          const allCustomers = response.data || []
          const leads = allCustomers.filter(c => c.lead_score > 0)
          setData(leads.sort((a, b) => b.lead_score - a.lead_score))
          break
        case 'conversion':
          response = await api.get('/deals/pipeline')
          const pipeline = response.data.pipeline || response.data || []
          setData(pipeline)
          break
        case 'revenue':
          response = await api.get('/deals')
          const allDeals = response.data.deals || response.data || []
          const wonDeals = allDeals
            .filter(d => d.stage === 'Closed Won')
            .sort((a, b) => new Date(b.actual_close_date || b.created_at) - new Date(a.actual_close_date || a.created_at))
          setData(wonDeals)
          break
        default:
          setData([])
      }
    } catch (error) {
      console.error('Error fetching detail data:', error)
      setData([])
    } finally {
      setLoading(false)
    }
  }

  const renderContent = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center py-12">
          <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
        </div>
      )
    }

    if (data.length === 0) {
      return (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400">No data available</p>
        </div>
      )
    }

    switch (statType) {
      case 'customers':
      case 'leads':
        return (
          <div className="space-y-3">
            {data.map((customer, index) => (
              <motion.div
                key={customer.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                      <User className="w-5 h-5 text-blue-600 dark:text-blue-300" />
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-gray-100">{customer.name}</p>
                      <div className="flex items-center space-x-3 text-sm text-gray-600 dark:text-gray-400">
                        {customer.email && (
                          <span className="flex items-center space-x-1">
                            <Mail className="w-3 h-3" />
                            <span>{customer.email}</span>
                          </span>
                        )}
                        {customer.phone && (
                          <span className="flex items-center space-x-1">
                            <Phone className="w-3 h-3" />
                            <span>{customer.phone}</span>
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  {statType === 'leads' && customer.lead_score > 0 && (
                    <span className="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-full text-sm font-semibold">
                      Score: {Math.round(customer.lead_score)}
                    </span>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        )

      case 'conversion':
        return (
          <div className="space-y-4">
            {data.map((stage, index) => (
              <motion.div
                key={stage.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-4 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-600 rounded-lg"
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold text-gray-900 dark:text-gray-100">{stage.name}</h4>
                  <div className="flex items-center space-x-4">
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {stage.deal_count} deals
                    </span>
                    <span className="font-bold text-green-600 dark:text-green-400">
                      {formatCurrency(stage.total_value)}
                    </span>
                  </div>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-800 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{ width: `${stage.default_probability}%` }}
                  />
                </div>
              </motion.div>
            ))}
          </div>
        )

      case 'revenue':
        return (
          <div className="space-y-3">
            {data.map((deal, index) => (
              <motion.div
                key={deal.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="font-semibold text-gray-900 dark:text-gray-100">{deal.title || deal.name}</p>
                    <div className="flex items-center space-x-3 mt-1 text-sm text-gray-600 dark:text-gray-400">
                      {deal.company_name && (
                        <span className="flex items-center space-x-1">
                          <Building2 className="w-3 h-3" />
                          <span>{deal.company_name}</span>
                        </span>
                      )}
                      {deal.actual_close_date && (
                        <span className="flex items-center space-x-1">
                          <Calendar className="w-3 h-3" />
                          <span>{new Date(deal.actual_close_date).toLocaleDateString()}</span>
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-green-600 dark:text-green-400">
                      {formatCurrency(deal.value)}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )

      default:
        return null
    }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-3xl w-full max-h-[80vh] overflow-hidden flex flex-col"
          >
            <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                {title}
              </h2>
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto flex-1">
              {renderContent()}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
}

export default StatsDetailModal
