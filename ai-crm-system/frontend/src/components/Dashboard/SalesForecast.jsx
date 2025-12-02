import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendingUp } from 'lucide-react'
import { formatCurrency } from '../../utils/helpers'

// Custom Tooltip Component for Dark Mode
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3 shadow-lg">
        <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">{label}</p>
        <p className="text-sm font-semibold text-purple-600 dark:text-purple-400">
          {formatCurrency(payload[0].value)}
        </p>
      </div>
    )
  }
  return null
}

const SalesForecast = ({ forecast }) => {
  const data = [
    { name: 'Current', value: 50000 },
    { name: 'Next Month', value: forecast?.next_month || 55000 },
    { name: 'Quarter', value: forecast?.quarter || 65000 },
    { name: 'Year', value: forecast?.year || 80000 },
  ]

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Sales Forecast</h2>
        <div className="flex items-center space-x-2 text-green-600 dark:text-green-400">
          <TrendingUp className="w-5 h-5" />
          <span className="text-sm font-medium">{forecast?.trend || 'Growing'}</span>
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#4b5563" />
          <XAxis 
            dataKey="name" 
            stroke="#9ca3af"
            tick={{ fill: '#9ca3af' }}
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#9ca3af"
            tick={{ fill: '#9ca3af' }}
            style={{ fontSize: '12px' }}
            tickFormatter={(value) => `$${value/1000}k`} 
          />
          <Tooltip content={<CustomTooltip />} />
          <Line 
            type="monotone" 
            dataKey="value" 
            stroke="#8b5cf6" 
            strokeWidth={3}
            dot={{ fill: '#8b5cf6', r: 6 }}
            activeDot={{ r: 8 }}
          />
        </LineChart>
      </ResponsiveContainer>
      
      <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
        <p className="text-sm text-gray-600 dark:text-gray-300">
          <strong>Confidence Level:</strong> {forecast?.confidence || '95%'}
        </p>
      </div>
    </div>
  )
}

export default SalesForecast