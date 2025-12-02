import React, { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Users, 
  Building2,
  TrendingUp,
  CheckSquare,
  MessageSquare, 
  BarChart3, 
  Settings,
  Sparkles,
  ChevronRight
} from 'lucide-react'
import { motion } from 'framer-motion'

const Sidebar = () => {
  const [hoveredItem, setHoveredItem] = useState(null)

  const navItems = [
    { 
      path: '/dashboard', 
      icon: LayoutDashboard, 
      label: 'Dashboard',
      gradient: 'from-blue-500 to-blue-600',
      badge: null
    },
    { 
      path: '/companies', 
      icon: Building2, 
      label: 'Companies',
      gradient: 'from-indigo-500 to-indigo-600',
      badge: null
    },
    { 
      path: '/contacts', 
      icon: Users, 
      label: 'Contacts',
      gradient: 'from-purple-500 to-purple-600',
      badge: null
    },
    { 
      path: '/pipeline', 
      icon: TrendingUp, 
      label: 'Pipeline',
      gradient: 'from-pink-500 to-pink-600',
      badge: null
    },
    { 
      path: '/tasks', 
      icon: CheckSquare, 
      label: 'Tasks',
      gradient: 'from-yellow-500 to-yellow-600',
      badge: null
    },
    { 
      path: '/interactions', 
      icon: MessageSquare, 
      label: 'Interactions',
      gradient: 'from-green-500 to-green-600',
      badge: null
    },
    { 
      path: '/reports', 
      icon: BarChart3, 
      label: 'Reports',
      gradient: 'from-orange-500 to-orange-600',
      badge: null
    },
    { 
      path: '/settings', 
      icon: Settings, 
      label: 'Settings',
      gradient: 'from-gray-500 to-gray-600',
      badge: null
    },
  ]

  return (
    <aside className="w-72 bg-gradient-to-br from-gray-50 via-white to-gray-50 dark:from-gray-800 dark:via-gray-900 dark:to-gray-800 border-r border-gray-200 dark:border-gray-700 min-h-screen flex flex-col shadow-lg">
      {/* Logo Section */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl shadow-lg">
            <Sparkles className="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent tracking-tight">
              Lead Mind
            </h1>
            <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">Intelligent CRM Platform</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navItems.map((item, index) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.path}
              to={item.path}
              onMouseEnter={() => setHoveredItem(index)}
              onMouseLeave={() => setHoveredItem(null)}
              className={({ isActive }) => {
                const baseClasses = "group relative flex items-center justify-between px-4 py-3.5 rounded-xl transition-all duration-300 font-medium"
                if (isActive) {
                  return `${baseClasses} bg-gradient-to-r ${item.gradient} text-white shadow-lg shadow-${item.gradient.split('-')[1]}-500/30 scale-[1.02]`
                }
                return `${baseClasses} text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100`
              }}
            >
              {({ isActive }) => (
                <>
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg transition-all duration-300 ${
                      isActive 
                        ? 'bg-white/20' 
                        : 'bg-gray-100 dark:bg-gray-700 group-hover:bg-gray-200 dark:group-hover:bg-gray-600'
                    }`}>
                      <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-gray-600 dark:text-gray-300'}`} />
                    </div>
                    <span>{item.label}</span>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {item.badge && (
                      <span className={`px-2 py-0.5 text-xs font-bold rounded-full ${
                        isActive 
                          ? 'bg-white/20 text-white' 
                          : 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                      }`}>
                        {item.badge}
                      </span>
                    )}
                    <ChevronRight className={`w-4 h-4 transition-transform duration-300 ${
                      isActive ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-2'
                    } group-hover:opacity-100 group-hover:translate-x-0`} />
                  </div>

                  {/* Active indicator */}
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute left-0 top-0 bottom-0 w-1 bg-white rounded-r-full"
                      transition={{ type: "spring", stiffness: 380, damping: 30 }}
                    />
                  )}
                </>
              )}
            </NavLink>
          )
        })}
      </nav>

      {/* Bottom Section */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/30 dark:to-purple-900/30 rounded-xl p-4 border border-blue-100 dark:border-blue-800">
          <div className="flex items-start space-x-3">
            <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
              <TrendingUp className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100 mb-1">Performance Up!</h3>
              <p className="text-xs text-gray-600 dark:text-gray-400 mb-3">Your sales increased by 23% this month</p>
              <button className="w-full px-3 py-1.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-xs font-semibold rounded-lg hover:shadow-lg transition-all duration-300">
                View Details
              </button>
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
