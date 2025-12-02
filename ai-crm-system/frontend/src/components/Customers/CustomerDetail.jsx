import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { X, Mail, Phone, Building2, MapPin, Globe, DollarSign, Sparkles } from 'lucide-react'
import { interactionsAPI, aiAPI, customersAPI } from '../../api/client'
import { formatDate, getLeadScoreColor, getStatusColor } from '../../utils/helpers'
import toast from 'react-hot-toast'
import ChurnRiskAlert from '../AI/ChurnRiskAlert'
import api from '../../api/client'

const CustomerDetail = ({ customer, onClose, onRefresh }) => {
  const [interactions, setInteractions] = useState([])
  const [aiInsights, setAiInsights] = useState(null)
  const [churnPrediction, setChurnPrediction] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [customer.id])

  const fetchData = async () => {
    try {
      const [interactionsRes, insightsRes, churnRes] = await Promise.all([
        interactionsAPI.getByCustomer(customer.id),
        aiAPI.analyzeLead(customer.id).catch(() => ({ data: null })),
        api.post('/ai/predict-churn', { contact_id: customer.id }).catch(() => ({ data: null }))
      ])
      setInteractions(interactionsRes.data)
      setAiInsights(insightsRes.data)
      setChurnPrediction(churnRes.data)
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this customer?')) {
      try {
        await customersAPI.delete(customer.id)
        toast.success('Customer deleted successfully')
        onRefresh()
        onClose()
      } catch (error) {
        toast.error('Failed to delete customer')
      }
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 dark:bg-black/70 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto"
      >
        <div className="sticky top-0 bg-white dark:bg-gray-800 border-b dark:border-gray-700 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{customer.name}</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
            <X className="w-5 h-5 text-gray-900 dark:text-gray-100" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Customer Info */}
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <Mail className="w-5 h-5 text-gray-400 dark:text-gray-500" />
                <span className="text-gray-700 dark:text-gray-300">{customer.email || 'N/A'}</span>
              </div>
              <div className="flex items-center space-x-3">
                <Phone className="w-5 h-5 text-gray-400 dark:text-gray-500" />
                <span className="text-gray-700 dark:text-gray-300">{customer.phone || 'N/A'}</span>
              </div>
              <div className="flex items-center space-x-3">
                <Building2 className="w-5 h-5 text-gray-400 dark:text-gray-500" />
                <span className="text-gray-700 dark:text-gray-300">{customer.company || 'N/A'}</span>
              </div>
            </div>
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <MapPin className="w-5 h-5 text-gray-400 dark:text-gray-500" />
                <span className="text-gray-700 dark:text-gray-300">{customer.location || 'N/A'}</span>
              </div>
              <div className="flex items-center space-x-3">
                <Globe className="w-5 h-5 text-gray-400 dark:text-gray-500" />
                <span className="text-gray-700 dark:text-gray-300">{customer.website || 'N/A'}</span>
              </div>
              <div className="flex items-center space-x-3">
                <DollarSign className="w-5 h-5 text-gray-400 dark:text-gray-500" />
                <span className="text-gray-700 dark:text-gray-300">{customer.budget ? `$${customer.budget}` : 'N/A'}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <span className={`px-4 py-2 rounded-full text-sm font-medium ${getStatusColor(customer.status)}`}>
              {customer.status || 'Lead'}
            </span>
            <span className={`px-4 py-2 rounded-full text-sm font-medium ${getLeadScoreColor(customer.lead_score)}`}>
              Lead Score: {Math.round(customer.lead_score || 0)}
            </span>
          </div>

          {/* Churn Risk Alert */}
          {churnPrediction && (
            <ChurnRiskAlert 
              riskScore={churnPrediction.churn_risk_score}
              riskLevel={churnPrediction.risk_level}
              insights={churnPrediction.insights}
              strategies={churnPrediction.retention_strategies}
              compact={false}
            />
          )}

          {/* AI Insights */}
          {aiInsights && (
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/30 dark:to-pink-900/30 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                <Sparkles className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                <h3 className="font-semibold text-gray-900 dark:text-gray-100">AI Insights</h3>
              </div>
              <p className="text-sm text-gray-700 dark:text-gray-300">{aiInsights.summary || 'No insights available'}</p>
            </div>
          )}

          {/* Interactions */}
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-3">Recent Interactions</h3>
            <div className="space-y-3">
              {interactions.length > 0 ? (
                interactions.map((interaction) => (
                  <div key={interaction.id} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-900 dark:text-gray-100 capitalize">
                        {interaction.type}
                      </span>
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        {formatDate(interaction.created_at)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{interaction.notes}</p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-500 dark:text-gray-400">No interactions yet</p>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-4 border-t dark:border-gray-700">
            <button
              onClick={handleDelete}
              className="px-6 py-2 border border-red-300 dark:border-red-700 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
            >
              Delete Customer
            </button>
            <button
              onClick={onClose}
              className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default CustomerDetail
