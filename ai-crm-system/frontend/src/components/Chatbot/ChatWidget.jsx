import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MessageCircle, X, Send, Bot, User, ExternalLink, Mail } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { chatbotAPI } from '../../api/client'
import toast from 'react-hot-toast'
import EmailComposer from './EmailComposer'

const ChatWidget = () => {
  const navigate = useNavigate()
  const [isOpen, setIsOpen] = useState(false)
  const [showEmailComposer, setShowEmailComposer] = useState(false)
  const [emailData, setEmailData] = useState(null)
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your AI assistant. I can help you with:\n• Viewing CRM data (deals, contacts, leads)\n• Navigating to different sections\n• Creating records\n• Analytics and insights\n\nWhat would you like to do?",
      sender: 'bot',
      timestamp: new Date()
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsTyping(true)

    try {
      // Use the enhanced chatbot endpoint for better responses
      const response = await chatbotAPI.sendMessage(inputMessage, null)
      
      const botMessage = {
        id: Date.now() + 1,
        text: response.data.message || response.data.response,
        sender: 'bot',
        timestamp: new Date(),
        intent: response.data.intent || response.data.action,
        data: response.data.extracted_data || response.data.data,
        emailData: response.data.data, // Store email data for composer
        navigationTarget: response.data.navigation_target,
        actions: response.data.actions // Store available actions
      }
      
      setMessages(prev => [...prev, botMessage])
      
      // Handle email draft ready
      if (response.data.intent === 'send_email' && response.data.action === 'draft_ready') {
        setEmailData(response.data.data)
      }
      
      // Auto-navigate if navigation target is provided
      if (response.data.navigation_target) {
        toast.success(`Navigating to ${response.data.navigation_target}`)
        setTimeout(() => {
          navigate(response.data.navigation_target)
          setIsOpen(false)
        }, 1500)
      }
      
      // Show success toast for completed actions
      if (response.data.action_executed) {
        toast.success('Action completed successfully!')
      }
    } catch (error) {
      console.error('Chatbot error:', error)
      toast.error('Failed to send message')
      
      // Fallback friendly error message
      const errorMessage = {
        id: Date.now() + 1,
        text: "I'm having trouble processing that right now. Could you try rephrasing your question?",
        sender: 'bot',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <>
      {/* Chat Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0 }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setIsOpen(true)}
            className="fixed bottom-6 right-6 w-14 h-14 bg-primary-600 rounded-full shadow-lg flex items-center justify-center text-white hover:bg-primary-700 transition-colors z-40"
          >
            <MessageCircle className="w-6 h-6" />
          </motion.button>
        )}
      </AnimatePresence>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-6 right-6 w-96 h-[600px] bg-white dark:bg-gray-800 rounded-xl shadow-2xl flex flex-col z-50 border border-gray-200 dark:border-gray-700"
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-primary-600 to-purple-600 p-4 rounded-t-xl flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                  <Bot className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-white font-semibold">AI Assistant</h3>
                  <p className="text-white/80 text-sm">Always here to help</p>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-white" />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900">
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex items-start space-x-2 max-w-[80%] ${message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      message.sender === 'user' ? 'bg-primary-600' : 'bg-gray-300 dark:bg-gray-600'
                    }`}>
                      {message.sender === 'user' ? (
                        <User className="w-5 h-5 text-white" />
                      ) : (
                        <Bot className="w-5 h-5 text-gray-600 dark:text-gray-200" />
                      )}
                    </div>
                    <div className={`px-4 py-2 rounded-lg ${
                      message.sender === 'user' 
                        ? 'bg-primary-600 text-white' 
                        : 'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-700'
                    }`}>
                      <p className="text-sm whitespace-pre-line">{message.text}</p>
                      
                      {/* Email Action Buttons */}
                      {message.intent === 'send_email' && message.actions?.includes('send') && (
                        <div className="mt-3 flex gap-2">
                          <button
                            onClick={() => {
                              setEmailData(message.emailData)
                              setShowEmailComposer(true)
                            }}
                            className="px-3 py-1.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-1 text-xs"
                          >
                            <Mail className="w-3 h-3" />
                            Send
                          </button>
                          <button
                            onClick={() => {
                              setEmailData(message.emailData)
                              setShowEmailComposer(true)
                            }}
                            className="px-3 py-1.5 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors text-xs"
                          >
                            Edit
                          </button>
                        </div>
                      )}
                      
                      {message.navigationTarget && (
                        <button
                          onClick={() => {
                            navigate(message.navigationTarget)
                            setIsOpen(false)
                          }}
                          className="mt-2 flex items-center gap-1 text-xs text-primary-600 dark:text-primary-400 hover:underline"
                        >
                          <ExternalLink className="w-3 h-3" />
                          Go now
                        </button>
                      )}
                      <p className={`text-xs mt-1 ${
                        message.sender === 'user' ? 'text-white/70' : 'text-gray-500 dark:text-gray-400'
                      }`}>
                        {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
              
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex items-center space-x-2 text-gray-500 dark:text-gray-400"
                >
                  <div className="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center">
                    <Bot className="w-5 h-5 text-gray-600 dark:text-gray-200" />
                  </div>
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </motion.div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message..."
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder:text-gray-500 dark:placeholder:text-gray-400"
                />
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || isTyping}
                  className="p-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="w-5 h-5" />
                </motion.button>
              </div>
              
              <div className="mt-3 flex flex-wrap gap-2">
                {[
                  'Show top leads',
                  'Deals closing this week',
                  'Show won deals',
                  'Recent contacts',
                  'Show companies',
                  'Show tasks',
                  'Show reports',
                  'Summarize CRM',
                  'Create customer',
                  'Create task',
                  'Send email',
                  'Go to pipeline'
                ].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => setInputMessage(suggestion)}
                    className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full text-xs hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Email Composer Modal */}
      <EmailComposer
        isOpen={showEmailComposer}
        onClose={() => {
          setShowEmailComposer(false)
          setEmailData(null)
        }}
        emailData={emailData}
        onSent={() => {
          toast.success('Email sent and logged in interactions!')
          setMessages(prev => [...prev, {
            id: Date.now(),
            text: '✅ Email sent successfully and logged to contact interactions!',
            sender: 'bot',
            timestamp: new Date()
          }])
        }}
      />
    </>
  )
}

export default ChatWidget