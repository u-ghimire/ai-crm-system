import React from 'react'
import { formatDate } from '../../utils/helpers'
import { MessageSquare, Phone, Mail, Calendar } from 'lucide-react'

const RecentInteractions = ({ interactions }) => {
  const getIcon = (type) => {
    const icons = {
      email: Mail,
      phone: Phone,
      meeting: Calendar,
      chatbot: MessageSquare,
    }
    return icons[type] || MessageSquare
  }

  return (
    <div className="card">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Recent Interactions</h2>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Type</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Customer</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Notes</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Date</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">User</th>
            </tr>
          </thead>
          <tbody>
            {interactions?.map((interaction) => {
              const Icon = getIcon(interaction.type)
              return (
                <tr key={interaction.id} className="border-b hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <div className="flex items-center space-x-2">
                      <Icon className="w-4 h-4 text-gray-500" />
                      <span className="text-sm capitalize">{interaction.type}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-900">
                    {interaction.customer_name || 'N/A'}
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-600">
                    {interaction.notes?.substring(0, 50)}
                    {interaction.notes?.length > 50 && '...'}
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-600">
                    {formatDate(interaction.created_at)}
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-600">
                    {interaction.username || 'System'}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default RecentInteractions