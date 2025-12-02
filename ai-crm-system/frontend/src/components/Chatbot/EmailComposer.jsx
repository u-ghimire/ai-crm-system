import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Send, Mail, User as UserIcon, FileText } from 'lucide-react'
import { chatbotAPI } from '../../api/client'
import toast from 'react-hot-toast'

const EmailComposer = ({ isOpen, onClose, emailData, onSent }) => {
  const [formData, setFormData] = useState({
    to: '',
    subject: '',
    body: '',
    contactId: null
  })
  const [contacts, setContacts] = useState([])
  const [filteredContacts, setFilteredContacts] = useState([])
  const [showContactDropdown, setShowContactDropdown] = useState(false)
  const [isSending, setIsSending] = useState(false)

  useEffect(() => {
    if (emailData) {
      setFormData(prev => ({
        ...prev,
        to: emailData.to || '',
        subject: emailData.subject || '',
        body: emailData.key_points ? emailData.key_points.join('\n\n') : ''
      }))
    }
  }, [emailData])

  useEffect(() => {
    // Fetch contacts for linking
    const fetchContacts = async () => {
      try {
        const response = await fetch('/api/customers')
        const data = await response.json()
        setContacts(data.customers || [])
      } catch (error) {
        console.error('Error fetching contacts:', error)
      }
    }
    if (isOpen) {
      fetchContacts()
    }
  }, [isOpen])

  useEffect(() => {
    // Filter contacts based on email input
    if (formData.to && contacts.length > 0) {
      const filtered = contacts.filter(contact => 
        contact.email?.toLowerCase().includes(formData.to.toLowerCase()) ||
        contact.name?.toLowerCase().includes(formData.to.toLowerCase())
      ).slice(0, 5)
      setFilteredContacts(filtered)
      setShowContactDropdown(filtered.length > 0)
    } else {
      setFilteredContacts([])
      setShowContactDropdown(false)
    }
  }, [formData.to, contacts])

  const handleSelectContact = (contact) => {
    setFormData(prev => ({
      ...prev,
      to: contact.email || contact.name,
      contactId: contact.id
    }))
    setShowContactDropdown(false)
  }

  const handleSend = async () => {
    if (!formData.to || !formData.subject || !formData.body) {
      toast.error('Please fill in all fields')
      return
    }

    setIsSending(true)
    try {
      // Send email via API
      const response = await fetch('/api/send-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          to: formData.to,
          subject: formData.subject,
          body: formData.body,
          contact_id: formData.contactId,
          user_id: 1 // TODO: Get from auth context
        })
      })

      const result = await response.json()

      if (response.ok && result.success) {
        toast.success('✅ Email sent successfully!')
        onSent?.()
        onClose()
      } else {
        toast.error(result.message || 'Failed to send email')
      }
    } catch (error) {
      console.error('Error sending email:', error)
      toast.error('Failed to send email')
    } finally {
      setIsSending(false)
    }
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, y: 20 }}
          animate={{ scale: 1, y: 0 }}
          exit={{ scale: 0.9, y: 20 }}
          onClick={(e) => e.stopPropagation()}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
                <Mail className="w-5 h-5 text-primary-600 dark:text-primary-400" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Compose Email</h2>
                <p className="text-sm text-gray-500 dark:text-gray-400">Send email to contact</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            </button>
          </div>

          {/* Form */}
          <div className="p-6 space-y-4">
            {/* To Field with Contact Dropdown */}
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <UserIcon className="w-4 h-4 inline mr-1" />
                To
              </label>
              <input
                type="text"
                value={formData.to}
                onChange={(e) => setFormData(prev => ({ ...prev, to: e.target.value }))}
                placeholder="Enter email or search contact..."
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
              
              {/* Contact Dropdown */}
              {showContactDropdown && filteredContacts.length > 0 && (
                <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                  {filteredContacts.map(contact => (
                    <button
                      key={contact.id}
                      onClick={() => handleSelectContact(contact)}
                      className="w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-600 flex items-center space-x-2"
                    >
                      <UserIcon className="w-4 h-4 text-gray-400" />
                      <div>
                        <div className="font-medium text-gray-900 dark:text-white">{contact.name}</div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">{contact.email}</div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Subject Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <FileText className="w-4 h-4 inline mr-1" />
                Subject
              </label>
              <input
                type="text"
                value={formData.subject}
                onChange={(e) => setFormData(prev => ({ ...prev, subject: e.target.value }))}
                placeholder="Enter email subject..."
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            {/* Body Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Message
              </label>
              <textarea
                value={formData.body}
                onChange={(e) => setFormData(prev => ({ ...prev, body: e.target.value }))}
                placeholder="Type your message here..."
                rows={10}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none"
              />
            </div>

            {/* Contact Link Info */}
            {formData.contactId && (
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
                <p className="text-sm text-blue-800 dark:text-blue-200">
                  ✓ This email will be linked to the contact and logged in interactions
                </p>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={onClose}
              disabled={isSending}
              className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSend}
              disabled={isSending || !formData.to || !formData.subject || !formData.body}
              className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {isSending ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Sending...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Send Email</span>
                </>
              )}
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

export default EmailComposer
