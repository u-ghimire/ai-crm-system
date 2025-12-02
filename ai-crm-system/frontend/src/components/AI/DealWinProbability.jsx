import React from 'react'
import { TrendingUp, AlertCircle, CheckCircle } from 'lucide-react'

const DealWinProbability = ({ probability, confidence, size = 'md' }) => {
  if (!probability && probability !== 0) return null

  const getColor = (prob) => {
    if (prob >= 70) return 'green'
    if (prob >= 40) return 'yellow'
    return 'red'
  }

  const getIcon = (prob) => {
    if (prob >= 70) return <CheckCircle className="w-4 h-4" />
    if (prob >= 40) return <TrendingUp className="w-4 h-4" />
    return <AlertCircle className="w-4 h-4" />
  }

  const color = getColor(probability)
  const icon = getIcon(probability)

  const colorClasses = {
    green: 'bg-green-100 text-green-800 border-green-300',
    yellow: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    red: 'bg-red-100 text-red-800 border-red-300'
  }

  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1.5',
    lg: 'text-base px-4 py-2'
  }

  return (
    <div className={`inline-flex items-center gap-1.5 rounded-full border ${colorClasses[color]} ${sizeClasses[size]} font-semibold`}>
      {icon}
      <span>{Math.round(probability)}% Win</span>
      {confidence && (
        <span className="opacity-70 text-xs">
          ({Math.round(confidence)}% confidence)
        </span>
      )}
    </div>
  )
}

export default DealWinProbability
