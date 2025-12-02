import React from 'react'
import { AlertTriangle, Info } from 'lucide-react'

const ChurnRiskAlert = ({ riskScore, riskLevel, insights, strategies, compact = false }) => {
  if (!riskScore || riskScore < 30) return null // Only show for medium+ risk

  const getAlertColor = (level) => {
    const colors = {
      'Critical': 'bg-red-50 border-red-300 text-red-800',
      'High': 'bg-orange-50 border-orange-300 text-orange-800',
      'Medium': 'bg-yellow-50 border-yellow-300 text-yellow-800',
      'Low': 'bg-blue-50 border-blue-300 text-blue-800'
    }
    return colors[level] || colors.Medium
  }

  const getIconColor = (level) => {
    const colors = {
      'Critical': 'text-red-600',
      'High': 'text-orange-600',
      'Medium': 'text-yellow-600',
      'Low': 'text-blue-600'
    }
    return colors[level] || colors.Medium
  }

  if (compact) {
    return (
      <div className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg border ${getAlertColor(riskLevel)}`}>
        <AlertTriangle className={`w-4 h-4 ${getIconColor(riskLevel)}`} />
        <div>
          <span className="font-semibold">Churn Risk: {riskLevel}</span>
          <span className="ml-2 text-sm opacity-80">({Math.round(riskScore)}%)</span>
        </div>
      </div>
    )
  }

  return (
    <div className={`rounded-xl border-2 ${getAlertColor(riskLevel)} p-4`}>
      <div className="flex items-start gap-3">
        <AlertTriangle className={`w-6 h-6 flex-shrink-0 mt-0.5 ${getIconColor(riskLevel)}`} />
        <div className="flex-1">
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-bold text-lg">
              Churn Risk: {riskLevel}
            </h4>
            <span className="text-2xl font-bold">
              {Math.round(riskScore)}%
            </span>
          </div>

          {insights && (
            <p className="text-sm mb-3 opacity-90">
              {insights}
            </p>
          )}

          {strategies && strategies.length > 0 && (
            <div className="mt-3 pt-3 border-t border-current opacity-30">
              <div className="flex items-center gap-2 mb-2">
                <Info className="w-4 h-4" />
                <span className="font-semibold text-sm">Retention Strategies:</span>
              </div>
              <ul className="space-y-1">
                {strategies.slice(0, 3).map((strategy, idx) => (
                  <li key={idx} className="text-sm flex items-start gap-2">
                    <span className="opacity-50">•</span>
                    <span>{strategy}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ChurnRiskAlert
