import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  X, Building2, Globe, Phone, Mail, MapPin, Users, DollarSign,
  Calendar, Edit2, Trash2, User, Target, TrendingUp
} from 'lucide-react'
import api from '../../api/client'
import toast from 'react-hot-toast'
import { formatCurrency } from '../../utils/helpers'

const CompanyDetailModal = ({ isOpen, onClose, company, onEdit, onDelete, onRefresh }) => {
  const [contacts, setContacts] = useState([])
  const [deals, setDeals] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (isOpen && company) {
      fetchCompanyDetails()
    }
  }, [isOpen, company])

  const fetchCompanyDetails = async () => {
    setLoading(true)
    try {
      // Fetch contacts for this company
      const contactsResponse = await api.get(`/contacts?company_id=${company.id}`)
      if (contactsResponse.data.success) {
        setContacts(contactsResponse.data.contacts || [])
      } else {
        setContacts(contactsResponse.data.contacts || contactsResponse.data || [])
      }

      // Fetch deals for this company
      const dealsResponse = await api.get(`/deals?company_id=${company.id}`)
      if (dealsResponse.data.success) {
        setDeals(dealsResponse.data.deals || [])
      } else {
        setDeals(dealsResponse.data.deals || dealsResponse.data || [])
      }
    } catch (error) {
      console.error('Error fetching company details:', error)
      setContacts([])
      setDeals([])
    } finally {
      setLoading(false)
    }
  }

  if (!company) return null

  const totalDealsValue = deals.reduce((sum, deal) => sum + (deal.value || 0), 0)
  const wonDeals = deals.filter(d => d.stage === 'Closed Won')
  const wonDealsValue = wonDeals.reduce((sum, deal) => sum + (deal.value || 0), 0)

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" onClick={onClose}>
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            onClick={(e) => e.stopPropagation()}
            className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col"
          >
            {/* Header */}
            <div className="p-6 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                    <Building2 className="w-8 h-8 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                      {company.name}
                    </h2>
                    <p className="text-gray-600 dark:text-gray-400 mt-1">
                      {company.industry || 'Industry not specified'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => {
                      onEdit(company)
                      onClose()
                    }}
                    className="p-2 hover:bg-blue-100 dark:hover:bg-blue-900 rounded-lg transition-colors"
                  >
                    <Edit2 className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  </button>
                  <button
                    onClick={() => {
                      onDelete(company.id, company.name)
                      onClose()
                    }}
                    className="p-2 hover:bg-red-100 dark:hover:bg-red-900 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-5 h-5 text-red-600 dark:text-red-400" />
                  </button>
                  <button
                    onClick={onClose}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="p-6 overflow-y-auto flex-1">
              {/* Company Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                {company.website && (
                  <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <Globe className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Website</p>
                      <a
                        href={company.website.startsWith('http') ? company.website : `https://${company.website}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 dark:text-blue-400 hover:underline"
                      >
                        {company.website}
                      </a>
                    </div>
                  </div>
                )}
                {company.phone && (
                  <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <Phone className="w-5 h-5 text-green-600 dark:text-green-400" />
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Phone</p>
                      <p className="text-gray-900 dark:text-gray-100">{company.phone}</p>
                    </div>
                  </div>
                )}
                {company.email && (
                  <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <Mail className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Email</p>
                      <p className="text-gray-900 dark:text-gray-100">{company.email}</p>
                    </div>
                  </div>
                )}
                {company.address && (
                  <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <MapPin className="w-5 h-5 text-red-600 dark:text-red-400" />
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Address</p>
                      <p className="text-gray-900 dark:text-gray-100">{company.address}</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-xl">
                  <div className="flex items-center justify-between mb-2">
                    <Users className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  </div>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{contacts.length}</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">Contacts</p>
                </div>
                <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-xl">
                  <div className="flex items-center justify-between mb-2">
                    <Target className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                  </div>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{deals.length}</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">Deals</p>
                </div>
                <div className="p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-xl">
                  <div className="flex items-center justify-between mb-2">
                    <DollarSign className="w-5 h-5 text-green-600 dark:text-green-400" />
                  </div>
                  <p className="text-lg font-bold text-gray-900 dark:text-white">{formatCurrency(totalDealsValue)}</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">Pipeline</p>
                </div>
                <div className="p-4 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 rounded-xl">
                  <div className="flex items-center justify-between mb-2">
                    <TrendingUp className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                  </div>
                  <p className="text-lg font-bold text-gray-900 dark:text-white">{formatCurrency(wonDealsValue)}</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">Won</p>
                </div>
              </div>

              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Contacts */}
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-3 flex items-center space-x-2">
                      <Users className="w-5 h-5" />
                      <span>Contacts ({contacts.length})</span>
                    </h3>
                    {contacts.length > 0 ? (
                      <div className="space-y-2">
                        {contacts.map(contact => (
                          <div key={contact.id} className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                              <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                                <User className="w-5 h-5 text-blue-600 dark:text-blue-300" />
                              </div>
                              <div>
                                <p className="font-semibold text-gray-900 dark:text-gray-100">
                                  {contact.first_name} {contact.last_name}
                                </p>
                                <p className="text-sm text-gray-600 dark:text-gray-400">{contact.email}</p>
                              </div>
                            </div>
                            {contact.job_title && (
                              <span className="text-sm text-gray-500 dark:text-gray-400">{contact.job_title}</span>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 dark:text-gray-400 text-sm">No contacts yet</p>
                    )}
                  </div>

                  {/* Deals */}
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-3 flex items-center space-x-2">
                      <Target className="w-5 h-5" />
                      <span>Deals ({deals.length})</span>
                    </h3>
                    {deals.length > 0 ? (
                      <div className="space-y-2">
                        {deals.map(deal => (
                          <div key={deal.id} className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg flex items-center justify-between">
                            <div>
                              <p className="font-semibold text-gray-900 dark:text-gray-100">{deal.title || deal.name}</p>
                              <p className="text-sm text-gray-600 dark:text-gray-400">{deal.stage}</p>
                            </div>
                            <div className="text-right">
                              <p className="font-bold text-green-600 dark:text-green-400">{formatCurrency(deal.value || 0)}</p>
                              {deal.expected_close_date && (
                                <p className="text-xs text-gray-500 dark:text-gray-400">
                                  {new Date(deal.expected_close_date).toLocaleDateString()}
                                </p>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 dark:text-gray-400 text-sm">No deals yet</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
}

export default CompanyDetailModal
