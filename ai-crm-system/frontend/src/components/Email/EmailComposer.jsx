import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, X, FileText, Users, Building2, Sparkles, 
  ChevronDown, Check, Loader
} from 'lucide-react';
import api from '../../api/client';

const EmailComposer = ({ isOpen, onClose, prefilledData = {} }) => {
  const [emailData, setEmailData] = useState({
    to_email: prefilledData.to_email || '',
    subject: prefilledData.subject || '',
    body: prefilledData.body || '',
    customer_id: prefilledData.customer_id || null,
    cc: '',
    template_id: null
  });

  const [templates, setTemplates] = useState([]);
  const [showTemplates, setShowTemplates] = useState(false);
  const [customers, setCustomers] = useState([]);
  const [showCustomers, setShowCustomers] = useState(false);
  const [sending, setSending] = useState(false);
  const [drafting, setDrafting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (isOpen) {
      fetchTemplates();
      fetchCustomers();
    }
  }, [isOpen]);

  useEffect(() => {
    if (prefilledData) {
      setEmailData(prev => ({
        ...prev,
        ...prefilledData
      }));
    }
  }, [prefilledData]);

  const fetchTemplates = async () => {
    try {
      const response = await api.get('/email/templates');
      setTemplates(response.data.templates || []);
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const fetchCustomers = async () => {
    try {
      const response = await api.get('/customers');
      setCustomers(response.data || []);
    } catch (error) {
      console.error('Error fetching customers:', error);
    }
  };

  const handleTemplateSelect = async (template) => {
    setDrafting(true);
    try {
      // Find customer data for variable substitution
      const customer = customers.find(c => c.id === emailData.customer_id);
      const variables = {
        name: customer?.name || 'there',
        company: customer?.company || '',
        email: emailData.to_email || customer?.email || ''
      };

      const response = await api.post(`/email/templates/${template.id}/apply`, { variables });
      
      if (response.data.success) {
        setEmailData(prev => ({
          ...prev,
          subject: response.data.subject,
          body: response.data.body,
          template_id: template.id
        }));
        setShowTemplates(false);
      }
    } catch (error) {
      console.error('Error applying template:', error);
      setError('Failed to apply template');
    } finally {
      setDrafting(false);
    }
  };

  const handleCustomerSelect = (customer) => {
    setEmailData(prev => ({
      ...prev,
      to_email: customer.email,
      customer_id: customer.id
    }));
    setShowCustomers(false);
  };

  const handleAIDraft = async () => {
    if (!emailData.to_email) {
      setError('Please select a recipient first');
      return;
    }

    setDrafting(true);
    setError('');

    try {
      const customer = customers.find(c => c.id === emailData.customer_id);
      const context = `Following up with ${customer?.name || 'customer'} at ${customer?.company || 'their company'}`;
      
      const response = await api.post('/ai/draft-email', {
        context,
        tone: 'professional',
        purpose: 'follow_up',
        recipient_info: {
          name: customer?.name || '',
          company: customer?.company || '',
          email: emailData.to_email
        }
      });

      if (response.data.success && response.data.email) {
        setEmailData(prev => ({
          ...prev,
          subject: response.data.email.subject || prev.subject,
          body: response.data.email.body || prev.body
        }));
      }
    } catch (error) {
      console.error('Error drafting email:', error);
      setError('Failed to generate AI draft');
    } finally {
      setDrafting(false);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSending(true);

    try {
      const response = await api.post('/email/send', emailData);

      if (response.data.success) {
        setSuccess('Email sent successfully!');
        setTimeout(() => {
          onClose();
          // Reset form
          setEmailData({
            to_email: '',
            subject: '',
            body: '',
            customer_id: null,
            cc: '',
            template_id: null
          });
          setSuccess('');
        }, 2000);
      } else {
        setError(response.data.error || 'Failed to send email');
      }
    } catch (error) {
      console.error('Error sending email:', error);
      setError(error.response?.data?.error || 'Failed to send email. Please check your email account configuration.');
    } finally {
      setSending(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-white rounded-lg shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">Compose Email</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Alerts */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="px-6 pt-4"
            >
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-800 text-sm">
                {error}
              </div>
            </motion.div>
          )}
          
          {success && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="px-6 pt-4"
            >
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-green-800 text-sm flex items-center gap-2">
                <Check className="w-4 h-4" />
                {success}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Form */}
        <form onSubmit={handleSend} className="flex-1 overflow-y-auto p-6 space-y-4">
          {/* Quick Actions */}
          <div className="flex items-center gap-2 pb-4 border-b border-gray-200">
            <div className="relative">
              <button
                type="button"
                onClick={() => setShowTemplates(!showTemplates)}
                className="flex items-center gap-2 px-3 py-2 text-sm bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition"
              >
                <FileText className="w-4 h-4" />
                Templates
                <ChevronDown className="w-4 h-4" />
              </button>
              
              {showTemplates && (
                <div className="absolute top-full left-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 max-h-60 overflow-y-auto z-10">
                  {templates.length === 0 ? (
                    <div className="p-4 text-sm text-gray-500 text-center">
                      No templates available
                    </div>
                  ) : (
                    templates.map((template) => (
                      <button
                        key={template.id}
                        type="button"
                        onClick={() => handleTemplateSelect(template)}
                        className="w-full text-left px-4 py-3 hover:bg-gray-50 transition border-b border-gray-100 last:border-0"
                      >
                        <div className="font-medium text-gray-900">{template.name}</div>
                        <div className="text-xs text-gray-500 mt-1">{template.subject}</div>
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>

            <button
              type="button"
              onClick={handleAIDraft}
              disabled={drafting}
              className="flex items-center gap-2 px-3 py-2 text-sm bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition disabled:opacity-50"
            >
              {drafting ? (
                <Loader className="w-4 h-4 animate-spin" />
              ) : (
                <Sparkles className="w-4 h-4" />
              )}
              AI Draft
            </button>
          </div>

          {/* To Field */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              To *
            </label>
            <div className="relative">
              <input
                type="email"
                required
                value={emailData.to_email}
                onChange={(e) => setEmailData({ ...emailData, to_email: e.target.value })}
                onFocus={() => setShowCustomers(true)}
                placeholder="recipient@example.com"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              
              {showCustomers && customers.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-lg shadow-lg border border-gray-200 max-h-48 overflow-y-auto z-10">
                  {customers.filter(c => c.email).slice(0, 10).map((customer) => (
                    <button
                      key={customer.id}
                      type="button"
                      onClick={() => handleCustomerSelect(customer)}
                      className="w-full text-left px-4 py-3 hover:bg-gray-50 transition border-b border-gray-100 last:border-0"
                    >
                      <div className="flex items-center gap-2">
                        <Users className="w-4 h-4 text-gray-400" />
                        <div>
                          <div className="font-medium text-gray-900">{customer.name}</div>
                          <div className="text-xs text-gray-500">{customer.email}</div>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* CC Field */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              CC
            </label>
            <input
              type="text"
              value={emailData.cc}
              onChange={(e) => setEmailData({ ...emailData, cc: e.target.value })}
              placeholder="cc@example.com"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Subject Field */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Subject *
            </label>
            <input
              type="text"
              required
              value={emailData.subject}
              onChange={(e) => setEmailData({ ...emailData, subject: e.target.value })}
              placeholder="Email subject"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Body Field */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Message *
            </label>
            <textarea
              required
              value={emailData.body}
              onChange={(e) => setEmailData({ ...emailData, body: e.target.value })}
              placeholder="Type your message here..."
              rows={12}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none font-mono text-sm"
            />
          </div>
        </form>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
          <div className="text-sm text-gray-600">
            {emailData.template_id && (
              <span className="flex items-center gap-1">
                <FileText className="w-4 h-4" />
                Using template
              </span>
            )}
          </div>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-white transition"
            >
              Cancel
            </button>
            <button
              onClick={handleSend}
              disabled={sending}
              className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
            >
              {sending ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  Sending...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Send Email
                </>
              )}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default EmailComposer;
