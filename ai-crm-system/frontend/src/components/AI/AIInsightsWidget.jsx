import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Brain, TrendingUp, AlertTriangle, Sparkles, RefreshCw, X } from 'lucide-react'
import api from '../../api/client'

const AIInsightsWidget = () => {
  const [insights, setInsights] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [isHidden, setIsHidden] = useState(() => {
    // Load hidden state from localStorage
    const saved = localStorage.getItem('aiInsightsWidgetHidden')
    return saved === 'true'
  })
  const [dismissedInsights, setDismissedInsights] = useState(() => {
    // Load dismissed insights from localStorage
    const saved = localStorage.getItem('dismissedInsights')
    return saved ? JSON.parse(saved) : []
  })

  useEffect(() => {
    fetchInsights()
  }, [])

  const fetchInsights = async () => {
    try {
      setLoading(true)
      // Fetch multiple AI insights
      const [remindersRes, dealsRes, churnRes] = await Promise.all([
        api.get('/ai/smart-reminders').catch(() => ({ data: { reminders: [] } })),
        api.get('/ai/batch-predict-deals').catch(() => ({ data: { predictions: [] } })),
        api.get('/ai/batch-predict-churn').catch(() => ({ data: { predictions: [] } }))
      ])

      const allInsights = []

      // High-priority reminders
      if (remindersRes.data.reminders) {
        const highPriority = remindersRes.data.reminders.filter(r => r.priority === 'high').slice(0, 3)
        allInsights.push(...highPriority.map(r => ({
          type: 'reminder',
          priority: 'high',
          icon: <AlertTriangle className="w-5 h-5" />,
          message: r.message,
          action: r.action,
          color: 'text-red-600 bg-red-50'
        })))
      }

      // High-risk deals
      if (dealsRes.data.predictions) {
        const highRisk = dealsRes.data.predictions.filter(p => p.risk_level === 'High Risk').slice(0, 2)
        allInsights.push(...highRisk.map(p => ({
          type: 'deal_risk',
          priority: 'medium',
          icon: <TrendingUp className="w-5 h-5" />,
          message: `Deal "${p.deal_title}" has ${p.win_probability}% win probability`,
          action: 'Review deal',
          color: 'text-orange-600 bg-orange-50'
        })))
      }

      // High-confidence wins
      if (dealsRes.data.predictions) {
        const highWin = dealsRes.data.predictions.filter(p => p.win_probability > 80).slice(0, 2)
        allInsights.push(...highWin.map(p => ({
          type: 'win_opportunity',
          priority: 'low',
          icon: <Sparkles className="w-5 h-5" />,
          message: `Deal "${p.deal_title}" shows ${p.win_probability}% win chance - prioritize!`,
          action: 'Close deal',
          color: 'text-green-600 bg-green-50'
        })))
      }

      // Churn risks
      if (churnRes.data.predictions) {
        const criticalChurn = churnRes.data.predictions.filter(p => p.risk_level === 'Critical').slice(0, 2)
        allInsights.push(...criticalChurn.map(p => ({
          type: 'churn_risk',
          priority: 'high',
          icon: <AlertTriangle className="w-5 h-5" />,
          message: `${p.contact_name} at risk of churning (${Math.round(p.churn_risk_score)}% risk)`,
          action: 'Re-engage',
          color: 'text-red-600 bg-red-50'
        })))
      }

      // Add unique IDs to insights for dismissal tracking
      const insightsWithIds = allInsights.map((insight, idx) => ({
        ...insight,
        id: `${insight.type}-${insight.message.substring(0, 30)}-${idx}`
      }))

      // Sort by priority
      const priorityOrder = { high: 0, medium: 1, low: 2 }
      insightsWithIds.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority])

      // Filter out dismissed insights
      const activeInsights = insightsWithIds.filter(
        insight => !dismissedInsights.includes(insight.id)
      )

      setInsights(activeInsights.slice(0, 10)) // Top 10 insights
    } catch (error) {
      console.error('Error fetching AI insights:', error)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const handleRefresh = () => {
    setRefreshing(true)
    fetchInsights()
  }

  const dismissInsight = (insightId) => {
    const newDismissed = [...dismissedInsights, insightId]
    setDismissedInsights(newDismissed)
    localStorage.setItem('dismissedInsights', JSON.stringify(newDismissed))
    setInsights(insights.filter(insight => insight.id !== insightId))
  }

  const clearAllDismissed = () => {
    setDismissedInsights([])
    localStorage.removeItem('dismissedInsights')
    fetchInsights()
  }

  const hideWidget = () => {
    setIsHidden(true)
    localStorage.setItem('aiInsightsWidgetHidden', 'true')
  }

  const showWidget = () => {
    setIsHidden(false)
    localStorage.setItem('aiInsightsWidgetHidden', 'false')
    fetchInsights()
  }

  if (isHidden) {
    return (
      <div className="flex flex-col h-full items-center justify-center">
        <button
          onClick={showWidget}
          className="w-full p-6 text-center text-sm text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-all hover:bg-gray-50 dark:hover:bg-gray-700 rounded-xl"
        >
          <Brain className="w-8 h-8 mx-auto mb-2 text-purple-600" />
          <span className="font-medium">Show AI Insights</span>
        </button>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex flex-col h-full">
        <div className="flex items-center justify-between mb-4 flex-shrink-0">
          <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Brain className="w-5 h-5 text-purple-600" />
            AI Insights
          </h3>
          <button
            onClick={hideWidget}
            className="p-2 hover:bg-red-100 dark:hover:bg-red-900 rounded-lg transition-colors group"
            title="Close AI Insights"
          >
            <X className="w-5 h-5 text-gray-600 dark:text-gray-400 group-hover:text-red-600 dark:group-hover:text-red-400" />
          </button>
        </div>
        <div className="flex items-center justify-center py-8 flex-1">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-4 flex-shrink-0">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <Brain className="w-5 h-5 text-purple-600" />
          AI Insights
        </h3>
        <div className="flex items-center gap-1">
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className={`p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors ${refreshing ? 'animate-spin' : ''}`}
            title="Refresh insights"
          >
            <RefreshCw className="w-4 h-4 text-gray-600 dark:text-gray-400" />
          </button>
          <button
            onClick={hideWidget}
            className="p-2 hover:bg-red-100 dark:hover:bg-red-900 rounded-lg transition-colors group"
            title="Close AI Insights"
          >
            <X className="w-5 h-5 text-gray-600 dark:text-gray-400 group-hover:text-red-600 dark:group-hover:text-red-400" />
          </button>
        </div>
      </div>

      {insights.length === 0 ? (
        <div className="text-center py-8 flex-1 flex flex-col items-center justify-center">
          <Sparkles className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-600 dark:text-gray-400">
            No critical insights at the moment. You're doing great! 🎉
          </p>
          {dismissedInsights.length > 0 && (
            <button
              onClick={clearAllDismissed}
              className="mt-4 text-xs text-blue-600 hover:text-blue-700 font-medium"
            >
              Show dismissed insights
            </button>
          )}
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto space-y-3 pr-2 min-h-0" style={{ scrollbarWidth: 'thin' }}>
          <AnimatePresence>
            {insights.map((insight, index) => (
              <motion.div
                key={insight.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.1 }}
                className={`p-3 rounded-lg border-l-4 ${insight.color.split(' ')[1]} border-current relative group`}
              >
                <div className="flex items-start gap-2">
                  <div className={`${insight.color.split(' ')[0]} flex-shrink-0`}>
                    {insight.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900 dark:text-white font-medium mb-1 break-words">
                      {insight.message}
                    </p>
                    {insight.action && (
                      <button className="text-xs text-blue-600 hover:text-blue-700 font-medium">
                        {insight.action} →
                      </button>
                    )}
                  </div>
                  <button
                    onClick={() => dismissInsight(insight.id)}
                    className="flex-shrink-0 p-1.5 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-full transition-colors"
                    title="Dismiss this insight"
                  >
                    <X className="w-4 h-4 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300" />
                  </button>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 flex-shrink-0">
        <div className="flex items-center justify-between">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Powered by AI • {new Date().toLocaleTimeString()}
          </p>
          {insights.length > 0 && (
            <button
              onClick={handleRefresh}
              className="text-xs text-blue-600 hover:text-blue-700 font-medium"
            >
              Refresh
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default AIInsightsWidget
