import React, { useState, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertTriangle, Clock, TrendingUp, X, ExternalLink } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import api from '../../api/client'

const SmartRemindersPanel = ({ isOpen, onClose }) => {
  const [reminders, setReminders] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all') // all, high, medium, low
  const [dismissedReminders, setDismissedReminders] = useState(() => {
    const saved = localStorage.getItem('dismissedReminders')
    return saved ? JSON.parse(saved) : []
  })
  const navigate = useNavigate()

  useEffect(() => {
    if (isOpen) {
      fetchReminders()
      // Add ESC key listener
      const handleEscape = (e) => {
        if (e.key === 'Escape') {
          onClose()
        }
      }
      document.addEventListener('keydown', handleEscape)
      return () => document.removeEventListener('keydown', handleEscape)
    }
  }, [isOpen, onClose])
  
  // Don't render if not open
  if (!isOpen) return null

  const fetchReminders = async () => {
    try {
      setLoading(true)
      const response = await api.get('/ai/smart-reminders')
      if (response.data.success) {
        // Filter out dismissed reminders and add unique IDs
        const remindersWithIds = response.data.reminders.map((r, idx) => ({
          ...r,
          id: `${r.type}-${r.contact_id || r.deal_id}-${idx}`
        }))
        const activeReminders = remindersWithIds.filter(
          r => !dismissedReminders.includes(r.id)
        )
        setReminders(activeReminders)
      }
    } catch (error) {
      console.error('Error fetching reminders:', error)
    } finally {
      setLoading(false)
    }
  }

  const getPriorityColor = (priority) => {
    const colors = {
      high: 'bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 border-red-200 dark:border-red-800',
      medium: 'bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 border-orange-200 dark:border-orange-800',
      low: 'bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-800'
    }
    return colors[priority] || colors.medium
  }

  const getPriorityTextColor = (priority) => {
    const colors = {
      high: 'text-red-700 dark:text-red-300',
      medium: 'text-orange-700 dark:text-orange-300',
      low: 'text-blue-700 dark:text-blue-300'
    }
    return colors[priority] || colors.medium
  }

  const getPriorityBadge = (priority) => {
    const colors = {
      high: 'bg-red-500 text-white',
      medium: 'bg-orange-500 text-white',
      low: 'bg-blue-500 text-white'
    }
    return colors[priority] || colors.medium
  }

  const getPriorityIcon = (priority) => {
    if (priority === 'high') return <AlertTriangle className="w-4 h-4" />
    if (priority === 'medium') return <Clock className="w-4 h-4" />
    return <TrendingUp className="w-4 h-4" />
  }

  const getTypeLabel = (type) => {
    const labels = {
      quiet_lead: '😴 Quiet Lead',
      stalled_deal: '⏸️ Stalled Deal',
      closing_soon: '🎯 Closing Soon'
    }
    return labels[type] || type
  }

  const handleNavigate = (reminder) => {
    if (reminder.type === 'quiet_lead') {
      navigate(`/contacts`)
    } else if (reminder.type === 'stalled_deal' || reminder.type === 'closing_soon') {
      navigate(`/pipeline`)
    }
    if (onClose) onClose()
  }

  const dismissReminder = (reminderId) => {
    const newDismissed = [...dismissedReminders, reminderId]
    setDismissedReminders(newDismissed)
    localStorage.setItem('dismissedReminders', JSON.stringify(newDismissed))
    setReminders(reminders.filter(r => r.id !== reminderId))
  }

  const clearAllDismissed = () => {
    setDismissedReminders([])
    localStorage.removeItem('dismissedReminders')
    fetchReminders()
  }

  const filteredReminders = filter === 'all' 
    ? reminders 
    : reminders.filter(r => r.priority === filter)

  const modalContent = (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 z-[9999] flex items-center justify-center p-4 overflow-y-auto"
        onClick={onClose}
      >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-4xl max-h-[85vh] my-auto overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4 text-white flex-shrink-0">
          <div className="flex items-center justify-between gap-4">
            <div className="flex-1 min-w-0">
              <h2 className="text-xl sm:text-2xl font-bold flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 sm:w-6 sm:h-6 flex-shrink-0" />
                <span className="truncate">Smart Reminders</span>
              </h2>
              <p className="text-blue-100 text-sm mt-1 line-clamp-1">
                AI-powered alerts for leads and deals requiring attention
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2.5 sm:p-3 bg-white hover:bg-red-500 text-blue-600 hover:text-white rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl flex-shrink-0 hover:scale-105 group"
              title="Close (ESC)"
            >
              <X className="w-5 h-5 sm:w-6 sm:h-6" />
            </button>
          </div>

          {/* Filter Tabs */}
          <div className="flex gap-2 mt-4 flex-wrap">
            {[
              { value: 'all', label: 'All', icon: '📋' },
              { value: 'high', label: 'High', icon: '🔴' },
              { value: 'medium', label: 'Medium', icon: '🟠' },
              { value: 'low', label: 'Low', icon: '🔵' }
            ].map((filterOption) => (
              <button
                key={filterOption.value}
                onClick={() => setFilter(filterOption.value)}
                className={`px-4 py-2 rounded-xl font-bold transition-all duration-300 transform hover:scale-105 shadow-md ${
                  filter === filterOption.value
                    ? 'bg-white text-blue-600 shadow-lg scale-105'
                    : 'bg-white/20 text-white hover:bg-white/30'
                }`}
              >
                <span className="mr-1">{filterOption.icon}</span>
                {filterOption.label}
                {filterOption.value === 'all' && (
                  <span className="ml-2 bg-blue-600 text-white px-2.5 py-0.5 rounded-full text-xs font-bold">
                    {reminders.length}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto flex-1 min-h-0">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : filteredReminders.length === 0 ? (
            <div className="text-center py-12">
              <TrendingUp className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400 text-lg">
                {filter === 'all' 
                  ? "No reminders - you're all caught up! 🎉"
                  : `No ${filter} priority reminders`
                }
              </p>
              {dismissedReminders.length > 0 && (
                <button
                  onClick={clearAllDismissed}
                  className="mt-4 text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  Show {dismissedReminders.length} dismissed reminder{dismissedReminders.length !== 1 ? 's' : ''}
                </button>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              <AnimatePresence>
                {filteredReminders.map((reminder, index) => (
                  <motion.div
                    key={reminder.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ delay: index * 0.05 }}
                    className={`border rounded-2xl p-5 ${getPriorityColor(reminder.priority)} relative group shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02]`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-3 flex-wrap">
                          <div className={`p-2 rounded-lg ${getPriorityBadge(reminder.priority)} shadow-md`}>
                            {getPriorityIcon(reminder.priority)}
                          </div>
                          <span className={`font-bold text-sm uppercase tracking-wide ${getPriorityTextColor(reminder.priority)}`}>
                            {getTypeLabel(reminder.type)}
                          </span>
                          <span className={`px-3 py-1 rounded-full text-xs font-bold ${getPriorityBadge(reminder.priority)} shadow-sm`}>
                            {reminder.priority.toUpperCase()}
                          </span>
                          <button
                            onClick={() => dismissReminder(reminder.id)}
                            className="ml-auto p-1.5 hover:bg-white/70 dark:hover:bg-black/30 rounded-lg transition-all duration-200 hover:scale-110"
                            title="Dismiss this reminder"
                          >
                            <X className="w-4 h-4 text-gray-600 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400" />
                          </button>
                        </div>

                        <p className={`font-semibold text-base mb-3 ${getPriorityTextColor(reminder.priority)}`}>
                          {reminder.message}
                        </p>

                        {/* Suggested Actions */}
                        {reminder.suggested_actions && reminder.suggested_actions.length > 0 && (
                          <div className="mt-4 p-3 bg-white/50 dark:bg-gray-900/30 rounded-xl space-y-2">
                            <p className="text-xs font-bold uppercase tracking-wide text-gray-600 dark:text-gray-400 mb-2">
                              💡 Suggested Actions:
                            </p>
                            {reminder.suggested_actions.map((action, idx) => (
                              <div key={idx} className="text-sm text-gray-700 dark:text-gray-300 flex items-start gap-2 pl-2">
                                <span className={`mt-1 ${getPriorityTextColor(reminder.priority)} font-bold`}>→</span>
                                <span className="flex-1">{action}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>

                      <button
                        onClick={() => handleNavigate(reminder)}
                        className={`ml-4 p-3 rounded-xl transition-all duration-200 flex-shrink-0 hover:scale-110 shadow-md ${getPriorityBadge(reminder.priority)}`}
                        title="Go to item"
                      >
                        <ExternalLink className="w-5 h-5" />
                      </button>
                    </div>

                    {/* Action Button */}
                    <div className="mt-4 pt-4 border-t-2 border-white/50 dark:border-gray-700">
                      <button
                        onClick={() => handleNavigate(reminder)}
                        className={`w-full px-6 py-3 rounded-xl font-bold text-white transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl ${
                          reminder.priority === 'high' 
                            ? 'bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700' 
                            : reminder.priority === 'medium'
                            ? 'bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700'
                            : 'bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700'
                        }`}
                      >
                        {reminder.action || 'Take Action'} →
                      </button>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-gray-50 dark:bg-gray-900 px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex-shrink-0">
          <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
            <span>Last updated: {new Date().toLocaleTimeString()}</span>
            <div className="flex gap-3">
              <button
                onClick={fetchReminders}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                Refresh
              </button>
              <button
                onClick={onClose}
                className="px-4 py-1 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )

  // Use portal to render outside the DOM hierarchy
  return createPortal(modalContent, document.body)
}

export default SmartRemindersPanel