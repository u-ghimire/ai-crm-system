import React, { useState } from 'react'
import { useAuth } from '../../hooks/useAuth'
import { useNavigate } from 'react-router-dom'
import { LogOut, User, Bell } from 'lucide-react'
import NotificationsDropdown from './NotificationsDropdown'

const Navbar = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [showNotifications, setShowNotifications] = useState(false)

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const handleNotificationClick = () => {
    setShowNotifications(!showNotifications)
  }

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h2 className="text-xl font-semibold text-gray-800">AI CRM System</h2>
        </div>

        <div className="flex items-center space-x-4">
          <div className="relative">
            <button 
              onClick={handleNotificationClick}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors relative"
              title="Notifications"
            >
              <Bell className="w-5 h-5 text-gray-600" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>

            <NotificationsDropdown 
              isOpen={showNotifications}
              onClose={() => setShowNotifications(false)}
            />
          </div>

          <div className="flex items-center space-x-3 pl-4 border-l border-gray-200">
            <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-white" />
            </div>
            <div className="text-sm">
              <p className="font-medium text-gray-900">{user?.username || 'User'}</p>
              <p className="text-gray-500 text-xs capitalize">{user?.role || 'User'}</p>
            </div>
          </div>

          <button
            onClick={handleLogout}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Logout"
          >
            <LogOut className="w-5 h-5 text-gray-600" />
          </button>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
