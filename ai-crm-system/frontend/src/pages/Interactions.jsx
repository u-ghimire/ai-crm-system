import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Plus, MessageSquare, Phone, Mail, Calendar, Filter, Search } from 'lucide-react'
import { interactionsAPI, customersAPI } from '../api/client'
import { formatDateTime } from '../utils/helpers'
import toast from 'react-hot-toast'
import AddInteractionModal from '../components/Interactions/AddInteractionModal'

const Interactions = () => {
  const [interactions, setInteractions] = useState([])
  const [customers, setCustomers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('all')

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

  const handleInteractionAdded = () => {
    fetchData()
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

  // Filter interactions
  const filteredInteractions = interactions.filter(interaction => {
    const customer = customers.find(c => c.id === interaction.customer_id)
    const customerName = customer?.name?.toLowerCase() || ''
    const subject = interaction.subject?.toLowerCase() || ''
    const notes = interaction.notes?.toLowerCase() || ''
    const search = searchTerm.toLowerCase()
    
    const matchesSearch = customerName.includes(search) || subject.includes(search) || notes.includes(search)
    const matchesType = filterType === 'all' || interaction.type === filterType
    
    return matchesSearch && matchesType
  })

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
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Interactions</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Track all customer communications</p>
        </div>
        <button 
          onClick={() => setShowAddModal(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Log Interaction</span>
        </button>
      </motion.div>

      {/* Filters and Search */}
      <div className="card">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500 w-5 h-5" />
            <input
              type="text"
              placeholder="Search interactions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder:text-gray-500 dark:placeholder:text-gray-400"
            />
          </div>
          <div className="flex items-center space-x-2">
            <Filter className="w-5 h-5 text-gray-400 dark:text-gray-500" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            >
              <option value="all">All Types</option>
              <option value="email">Email</option>
              <option value="phone">Phone</option>
              <option value="meeting">Meeting</option>
              <option value="chatbot">Chatbot</option>
            </select>
          </div>
        </div>
      </div>

      {/* Interactions Table */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr className="border-b dark:border-gray-700">
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Type</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Customer</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Subject</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Notes</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Date</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">User</th>
              </tr>
            </thead>
            <tbody>
              {filteredInteractions.length === 0 ? (
                <tr>
                  <td colSpan="6" className="py-8 text-center text-gray-500 dark:text-gray-400">
                    {searchTerm || filterType !== 'all' 
                      ? 'No interactions found matching your filters'
                      : 'No interactions yet. Click "Log Interaction" to add one.'
                    }
                  </td>
                </tr>
              ) : (
                filteredInteractions.map((interaction, index) => {
                  const Icon = getIcon(interaction.type)
                  const customer = customers.find(c => c.id === interaction.customer_id)
                  return (
                    <motion.tr
                      key={interaction.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: index * 0.05 }}
                      className="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700"
                    >
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-2">
                          <Icon className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                          <span className="text-sm capitalize text-gray-900 dark:text-gray-100">{interaction.type}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-900 dark:text-gray-100">
                        {customer?.name || 'Unknown'}
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-900 dark:text-gray-100">
                        {interaction.subject || 'N/A'}
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                        {interaction.notes?.substring(0, 50)}
                        {interaction.notes?.length > 50 && '...'}
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                        {formatDateTime(interaction.created_at)}
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                        {interaction.username || 'System'}
                      </td>
                    </motion.tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Interaction Modal */}
      <AddInteractionModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        customers={customers}
        onInteractionAdded={handleInteractionAdded}
      />
    </div>
  )
}

export default Interactions
