import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendingUp } from 'lucide-react'
import { formatCurrency } from '../../utils/helpers'

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
        <h2 className="text-xl font-semibold text-gray-900">Sales Forecast</h2>
        <div className="flex items-center space-x-2 text-green-600">
          <TrendingUp className="w-5 h-5" />
          <span className="text-sm font-medium">{forecast?.trend || 'Growing'}</span>
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="name" stroke="#6b7280" />
          <YAxis stroke="#6b7280" tickFormatter={(value) => `$${value/1000}k`} />
          <Tooltip 
            formatter={(value) => formatCurrency(value)}
            contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
          />
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
      
      <div className="mt-4 p-4 bg-gray-50 rounded-lg">
        <p className="text-sm text-gray-600">
          <strong>Confidence Level:</strong> {forecast?.confidence || '95%'}
        </p>
      </div>
    </div>
  )
}

export default SalesForecast