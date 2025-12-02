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
      <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-6">Recent Interactions</h2>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 dark:bg-gray-900">
            <tr className="border-b dark:border-gray-700">
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Type</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Customer</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Notes</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Date</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">User</th>
            </tr>
          </thead>
          <tbody>
            {interactions?.map((interaction) => {
              const Icon = getIcon(interaction.type)
              return (
                <tr key={interaction.id} className="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="py-3 px-4">
                    <div className="flex items-center space-x-2">
                      <Icon className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                      <span className="text-sm capitalize text-gray-900 dark:text-gray-100">{interaction.type}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-900 dark:text-gray-100">
                    {interaction.customer_name || 'N/A'}
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-300">
                    {interaction.notes?.substring(0, 50)}
                    {interaction.notes?.length > 50 && '...'}
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-300">
                    {formatDate(interaction.created_at)}
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-300">
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