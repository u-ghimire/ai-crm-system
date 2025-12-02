import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, TrendingUp, TrendingDown, DollarSign, Target, Lightbulb, BarChart3 } from 'lucide-react'
import { formatCurrency } from '../../utils/helpers'

const AIReportModal = ({ isOpen, onClose, report }) => {
  if (!isOpen || !report) return null

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0 bg-black bg-opacity-50 dark:bg-opacity-70"
        />

        {/* Modal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="relative bg-white dark:bg-gray-800 rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        >
          {/* Header */}
          <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between z-10">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center space-x-2">
                <BarChart3 className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                <span>AI-Generated Business Report</span>
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Generated on {new Date(report.generated_at).toLocaleString()}
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <X className="w-6 h-6 text-gray-500 dark:text-gray-400" />
            </button>
          </div>

          {/* Content */}
          <div className="px-6 py-6 space-y-6">
            {/* Summary Section */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center space-x-2">
                <Target className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                <span>Business Summary</span>
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border dark:border-blue-800">
                  <p className="text-sm text-blue-600 dark:text-blue-400 font-medium">Total Customers</p>
                  <p className="text-2xl font-bold text-blue-900 dark:text-blue-300 mt-1">
                    {report.summary.total_customers}
                  </p>
                </div>
                <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 border dark:border-purple-800">
                  <p className="text-sm text-purple-600 dark:text-purple-400 font-medium">Active Leads</p>
                  <p className="text-2xl font-bold text-purple-900 dark:text-purple-300 mt-1">
                    {report.summary.active_leads}
                  </p>
                </div>
                <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border dark:border-green-800">
                  <p className="text-sm text-green-600 dark:text-green-400 font-medium">Conversion Rate</p>
                  <p className="text-2xl font-bold text-green-900 dark:text-green-300 mt-1">
                    {report.summary.conversion_rate}%
                  </p>
                </div>
                <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 border dark:border-yellow-800">
                  <p className="text-sm text-yellow-600 dark:text-yellow-400 font-medium">Monthly Revenue</p>
                  <p className="text-2xl font-bold text-yellow-900 dark:text-yellow-300 mt-1">
                    {formatCurrency(report.summary.monthly_revenue)}
                  </p>
                </div>
                <div className="bg-indigo-50 dark:bg-indigo-900/20 rounded-lg p-4 border dark:border-indigo-800">
                  <p className="text-sm text-indigo-600 dark:text-indigo-400 font-medium">Avg Lead Score</p>
                  <p className="text-2xl font-bold text-indigo-900 dark:text-indigo-300 mt-1">
                    {report.summary.average_lead_score}
                  </p>
                </div>
                <div className="bg-pink-50 dark:bg-pink-900/20 rounded-lg p-4 border dark:border-pink-800">
                  <p className="text-sm text-pink-600 dark:text-pink-400 font-medium">Top Industry</p>
                  <p className="text-lg font-bold text-pink-900 dark:text-pink-300 mt-1">
                    {report.summary.top_performing_industry}
                  </p>
                </div>
              </div>
            </div>

            {/* AI Insights Section */}
            {report.insights && (
              <div className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-lg p-6 border dark:border-purple-800/50">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center space-x-2">
                  <Lightbulb className="w-5 h-5 text-yellow-500 dark:text-yellow-400" />
                  <span>AI-Powered Insights</span>
                </h3>
                <div className="prose prose-sm max-w-none text-gray-700 dark:text-gray-300 space-y-3">
                  {(report.insights.summary || 'Analyzing your business data...').split('\n').map((line, idx) => {
                    // Convert markdown bold (**text**) to HTML
                    const formatted = line
                      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                      .replace(/\*(.+?)\*/g, '<em>$1</em>')
                    
                    return (
                      <p 
                        key={idx} 
                        dangerouslySetInnerHTML={{ __html: formatted }}
                        className="leading-relaxed"
                      />
                    )
                  })}
                </div>
              </div>
            )}

            {/* Trends Section */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center space-x-2">
                <TrendingUp className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                <span>Key Trends</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(report.trends).map(([key, value]) => (
                  <div key={key} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600">
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400 capitalize">
                      {key.replace(/_/g, ' ')}
                    </p>
                    <p className="text-base text-gray-900 dark:text-gray-100 mt-1">{value}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Forecast Section */}
            {report.forecast && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center space-x-2">
                  <DollarSign className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                  <span>Sales Forecast</span>
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {report.forecast.predictions && report.forecast.predictions.map((pred, idx) => (
                    <div key={idx} className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
                      <p className="text-sm text-green-700 dark:text-green-400 font-medium">{pred.period}</p>
                      <p className="text-xl font-bold text-green-900 dark:text-green-300 mt-1">
                        {formatCurrency(pred.value)}
                      </p>
                    </div>
                  ))}
                </div>
                {report.forecast.confidence && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-3">
                    Confidence Level: <span className="font-semibold">{(report.forecast.confidence * 100).toFixed(0)}%</span>
                  </p>
                )}
              </div>
            )}

            {/* Recommendations Section */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center space-x-2">
                <Target className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                <span>AI Recommendations</span>
              </h3>
              <div className="space-y-3">
                {report.recommendations.map((rec, idx) => (
                  <div key={idx} className="flex items-start space-x-3 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="w-6 h-6 bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 rounded-full flex items-center justify-center flex-shrink-0 text-sm font-semibold">
                      {idx + 1}
                    </div>
                    <p className="text-gray-700 dark:text-gray-300 flex-1">{rec}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="sticky bottom-0 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              This report was generated using AI-powered analytics
            </p>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => window.print()}
                className="btn-secondary"
              >
                Export Report
              </button>
              <button
                onClick={onClose}
                className="btn-primary"
              >
                Close
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}

export default AIReportModal
