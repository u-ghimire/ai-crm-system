import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, DollarSign, TrendingUp, Target, Building2, Calendar, User } from 'lucide-react'
import api from '../../api/client'
import { formatCurrency } from '../../utils/helpers'

const ReportDetailModal = ({ isOpen, onClose, metricType, title }) => {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (isOpen) {
      fetchDetailData()
    }
  }, [isOpen, metricType])

  const fetchDetailData = async () => {
    setLoading(true)
    try {
      let response
      switch (metricType) {
        case 'revenue':
        case 'pipeline':
        case 'avg_deal':
          response = await api.get('/deals')
          let deals = response.data.deals || response.data || []
          
          if (metricType === 'revenue') {
            deals = deals.filter(d => d.stage === 'Closed Won')
          } else if (metricType === 'pipeline') {
            deals = deals.filter(d => d.stage !== 'Closed Won' && d.stage !== 'Closed Lost')
          }
          
          setData(deals.sort((a, b) => (b.value || 0) - (a.value || 0)))
          break
          
        case 'conversion':
        case 'win_rate':
          response = await api.get('/deals/pipeline')
          setData(response.data.pipeline || response.data || [])
          break
          
        case 'customers':
          response = await api.get('/customers')
          setData(response.data || [])
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

    if (metricType === 'conversion' || metricType === 'win_rate') {
      return (
        <div className="space-y-4">
          {data.map((stage, index) => (
            <motion.div
              key={stage.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="p-5 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border border-blue-100 dark:border-blue-800"
            >
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h4 className="font-bold text-gray-900 dark:text-gray-100 text-lg">{stage.name}</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {stage.deal_count} deals • {stage.default_probability}% probability
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {formatCurrency(stage.total_value)}
                  </p>
                </div>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                <div
                  className="bg-gradient-to-r from-blue-600 to-indigo-600 h-3 rounded-full transition-all flex items-center justify-end px-2"
                  style={{ width: `${Math.min(stage.default_probability, 100)}%` }}
                >
                  {stage.default_probability > 20 && (
                    <span className="text-xs font-bold text-white">{stage.default_probability}%</span>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )
    }

    if (metricType === 'customers') {
      return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.map((customer, index) => (
            <motion.div
              key={customer.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.05 }}
              className="p-4 bg-gray-50 dark:bg-gray-700 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                  {customer.name?.charAt(0) || 'C'}
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-gray-900 dark:text-gray-100">{customer.name}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{customer.email}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )
    }

    // Deals (revenue, pipeline, avg_deal)
    return (
      <div className="space-y-3">
        {data.slice(0, 20).map((deal, index) => (
          <motion.div
            key={deal.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.03 }}
            className="p-4 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-600 rounded-xl hover:shadow-md transition-all"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="font-bold text-gray-900 dark:text-gray-100 mb-1">
                  {deal.title || deal.name}
                </p>
                <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
                  {deal.company_name && (
                    <span className="flex items-center space-x-1">
                      <Building2 className="w-3 h-3" />
                      <span>{deal.company_name}</span>
                    </span>
                  )}
                  {deal.primary_contact_name && (
                    <span className="flex items-center space-x-1">
                      <User className="w-3 h-3" />
                      <span>{deal.primary_contact_name}</span>
                    </span>
                  )}
                  {deal.expected_close_date && (
                    <span className="flex items-center space-x-1">
                      <Calendar className="w-3 h-3" />
                      <span>{new Date(deal.expected_close_date).toLocaleDateString()}</span>
                    </span>
                  )}
                </div>
              </div>
              <div className="text-right ml-4">
                <p className="text-xl font-bold text-green-600 dark:text-green-400">
                  {formatCurrency(deal.value || 0)}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {deal.stage || 'Unknown'}
                </p>
              </div>
            </div>
          </motion.div>
        ))}
        {data.length > 20 && (
          <p className="text-center text-sm text-gray-500 dark:text-gray-400 py-4">
            Showing top 20 of {data.length} deals
          </p>
        )}
      </div>
    )
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" onClick={onClose}>
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            onClick={(e) => e.stopPropagation()}
            className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[85vh] overflow-hidden flex flex-col"
          >
            <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                {title}
              </h2>
              <button
                onClick={onClose}
                className="p-2 hover:bg-white/50 dark:hover:bg-gray-700 rounded-lg transition-colors"
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

export default ReportDetailModal
