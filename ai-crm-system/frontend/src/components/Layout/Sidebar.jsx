import React from 'react'
import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Users, 
  MessageSquare, 
  BarChart3, 
  Settings,
  Sparkles
} from 'lucide-react'

const Sidebar = () => {
  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/customers', icon: Users, label: 'Customers' },
    { path: '/interactions', icon: MessageSquare, label: 'Interactions' },
    { path: '/reports', icon: BarChart3, label: 'Reports' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ]

  return (
    <aside className="w-64 bg-gradient-to-b from-primary-600 to-purple-700 text-white min-h-screen">
      <div className="p-6">
        <div className="flex items-center space-x-3 mb-8">
          <Sparkles className="w-8 h-8" />
          <div>
            <h1 className="text-xl font-bold">AI CRM</h1>
            <p className="text-xs text-white/70">Smart Solutions</p>
          </div>
        </div>

        <nav className="space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-white/20 text-white'
                      : 'text-white/70 hover:bg-white/10 hover:text-white'
                  }`
                }
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </NavLink>
            )
          })}
        </nav>
      </div>
    </aside>
  )
}

export default Sidebar
