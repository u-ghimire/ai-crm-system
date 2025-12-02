import React, { useState } from 'react'
import { useAuth } from '../../hooks/useAuth'
import { useNavigate } from 'react-router-dom'
import { LogOut, User, Bell, Search, Settings, HelpCircle, Menu, Sparkles } from 'lucide-react'
import NotificationsDropdown from './NotificationsDropdown'
import SmartRemindersPanel from '../AI/SmartRemindersPanel'
import { motion, AnimatePresence } from 'framer-motion'

const Navbar = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [showNotifications, setShowNotifications] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [showSmartReminders, setShowSmartReminders] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const handleNotificationClick = () => {
    setShowNotifications(!showNotifications)
    setShowUserMenu(false)
  }

  const handleUserMenuClick = () => {
    setShowUserMenu(!showUserMenu)
    setShowNotifications(false)
  }

  // Get user initials for avatar
  const getUserInitials = () => {
    const username = user?.username || 'User'
    return username.substring(0, 2).toUpperCase()
  }

  return (
    <nav className="sticky top-0 z-40 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm backdrop-blur-lg bg-white/80 dark:bg-gray-800/80">
      <div className="px-6 py-3">
        <div className="flex items-center justify-between">
          {/* Search Bar */}
          <div className="flex-1 max-w-2xl">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search customers, interactions, reports..."
                className="w-full pl-11 pr-4 py-2.5 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300 text-sm text-gray-900 dark:text-gray-100 placeholder:text-gray-400 dark:placeholder:text-gray-500"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-400"
                >
                  ×
                </button>
              )}
            </div>
          </div>

          {/* Right Section */}
          <div className="flex items-center space-x-3 ml-6">
            {/* Smart Reminders Button */}
            <button 
              onClick={() => setShowSmartReminders(true)}
              className="relative p-2.5 hover:bg-purple-50 dark:hover:bg-purple-900/20 rounded-xl transition-all duration-300 group"
              title="AI Smart Reminders"
            >
              <Sparkles className="w-5 h-5 text-purple-600 dark:text-purple-400 group-hover:scale-110 transition-transform" />
              <span className="absolute -top-1 -right-1 px-1.5 py-0.5 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-xs font-bold rounded-full animate-pulse">
                AI
              </span>
            </button>

            {/* Help Button */}
            <button className="p-2.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl transition-all duration-300 group">
              <HelpCircle className="w-5 h-5 text-gray-600 dark:text-gray-400 group-hover:text-blue-600 transition-colors" />
            </button>

            {/* Notifications */}
            <div className="relative">
              <button 
                onClick={handleNotificationClick}
                className="relative p-2.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl transition-all duration-300 group"
                title="Notifications"
              >
                <Bell className="w-5 h-5 text-gray-600 dark:text-gray-400 group-hover:text-blue-600 transition-colors" />
                <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                <span className="absolute top-1.5 right-1.5 w-3 h-3 bg-red-500/30 rounded-full animate-ping"></span>
              </button>

              <NotificationsDropdown 
                isOpen={showNotifications}
                onClose={() => setShowNotifications(false)}
              />
            </div>

            {/* Divider */}
            <div className="h-8 w-px bg-gray-200 dark:bg-gray-700"></div>

            {/* User Profile */}
            <div className="relative">
              <button
                onClick={handleUserMenuClick}
                className="flex items-center space-x-3 px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl transition-all duration-300 group"
              >
                <div className="relative">
                  <div className="w-9 h-9 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow">
                    <span className="text-white text-sm font-bold">{getUserInitials()}</span>
                  </div>
                  <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 border-2 border-white dark:border-gray-800 rounded-full"></div>
                </div>
                <div className="text-left hidden md:block">
                  <p className="font-semibold text-gray-900 dark:text-gray-100 text-sm">{user?.username || 'User'}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">{user?.role || 'User'}</p>
                </div>
                <svg className="w-4 h-4 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* User Dropdown Menu */}
              <AnimatePresence>
                {showUserMenu && (
                  <motion.div
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 10, scale: 0.95 }}
                    transition={{ duration: 0.2 }}
                    className="absolute right-0 mt-2 w-64 bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-100 dark:border-gray-700 overflow-hidden z-50"
                  >
                    {/* User Info */}
                    <div className="px-4 py-3 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/30 dark:to-purple-900/30 border-b border-gray-100 dark:border-gray-700">
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                          <span className="text-white font-bold">{getUserInitials()}</span>
                        </div>
                        <div className="flex-1">
                          <p className="font-bold text-gray-900 dark:text-gray-100">{user?.username || 'User'}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">{user?.email || 'user@example.com'}</p>
                        </div>
                      </div>
                    </div>

                    {/* Menu Items */}
                    <div className="py-2">
                      <button
                        onClick={() => {
                          navigate('/settings')
                          setShowUserMenu(false)
                        }}
                        className="w-full flex items-center space-x-3 px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors group"
                      >
                        <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg group-hover:bg-blue-100 dark:group-hover:bg-blue-900/40 transition-colors">
                          <Settings className="w-4 h-4 text-gray-600 dark:text-gray-400 group-hover:text-blue-600 transition-colors" />
                        </div>
                        <div className="text-left">
                          <p className="text-sm font-medium text-gray-900 dark:text-gray-100">Settings</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">Manage your account</p>
                        </div>
                      </button>

                      <button
                        onClick={() => {
                          navigate('/settings')
                          setShowUserMenu(false)
                        }}
                        className="w-full flex items-center space-x-3 px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors group"
                      >
                        <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg group-hover:bg-purple-100 dark:group-hover:bg-purple-900/40 transition-colors">
                          <User className="w-4 h-4 text-gray-600 dark:text-gray-400 group-hover:text-purple-600 transition-colors" />
                        </div>
                        <div className="text-left">
                          <p className="text-sm font-medium text-gray-900 dark:text-gray-100">Profile</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">View your profile</p>
                        </div>
                      </button>
                    </div>

                    {/* Logout */}
                    <div className="border-t border-gray-100 dark:border-gray-700 py-2">
                      <button
                        onClick={() => {
                          handleLogout()
                          setShowUserMenu(false)
                        }}
                        className="w-full flex items-center space-x-3 px-4 py-2.5 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors group"
                      >
                        <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg group-hover:bg-red-100 dark:group-hover:bg-red-900/40 transition-colors">
                          <LogOut className="w-4 h-4 text-gray-600 dark:text-gray-400 group-hover:text-red-600 transition-colors" />
                        </div>
                        <span className="text-sm font-medium text-gray-900 dark:text-gray-100 group-hover:text-red-600 transition-colors">
                          Sign Out
                        </span>
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Overlay */}
              {showUserMenu && (
                <div
                  className="fixed inset-0 z-40"
                  onClick={() => setShowUserMenu(false)}
                ></div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Smart Reminders Modal */}
      <SmartRemindersPanel 
        isOpen={showSmartReminders}
        onClose={() => setShowSmartReminders(false)}
      />
    </nav>
  )
}

export default Navbar
