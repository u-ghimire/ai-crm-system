import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Plus, MessageSquare, Phone, Mail, Calendar } from 'lucide-react'
import { interactionsAPI, customersAPI } from '../api/client'
import { formatDateTime } from '../utils/helpers'
import toast from 'react-hot-toast'

const Interactions = () => {
  const [interactions, setInteractions] = useState([])
  const [customers, setCustomers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [interactionsRes, customersRes] = await Promise.all([
        interactionsAPI.getAll(),
        customersAPI.getAll()
      ])
      setInteractions(interactionsRes.data)
      setCustomers(customersRes.data)
    } catch (error) {
      toast.error('Failed to load interactions')
    } finally {
      setLoading(false)
    }
  }

  const getIcon = (type) => {
    const icons = {
      email: Mail,
      phone: Phone,
      meeting: Calendar,
      chatbot: MessageSquare,
    }
    return icons[type] || MessageSquare
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Interactions</h1>
          <p className="text-gray-600 mt-1">Track all customer communications</p>
        </div>
        <button 
          onClick={() => setShowAddModal(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Log Interaction</span>
        </button>
      </motion.div>

      <div className="card">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Type</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Customer</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Subject</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Notes</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Date</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">User</th>
              </tr>
            </thead>
            <tbody>
              {interactions.map((interaction, index) => {
                const Icon = getIcon(interaction.type)
                const customer = customers.find(c => c.id === interaction.customer_id)
                return (
                  <motion.tr
                    key={interaction.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: index * 0.05 }}
                    className="border-b hover:bg-gray-50"
                  >
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-2">
                        <Icon className="w-4 h-4 text-gray-500" />
                        <span className="text-sm capitalize">{interaction.type}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-900">
                      {customer?.name || 'Unknown'}
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-900">
                      {interaction.subject || 'N/A'}
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      {interaction.notes?.substring(0, 50)}
                      {interaction.notes?.length > 50 && '...'}
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      {formatDateTime(interaction.created_at)}
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      {interaction.username || 'System'}
                    </td>
                  </motion.tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Interactions
