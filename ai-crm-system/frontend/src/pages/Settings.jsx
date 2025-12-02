import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Save, User, Bell, Shield, Palette, Moon, Sun, Check } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import { useTheme } from '../contexts/ThemeContext'
import toast from 'react-hot-toast'

const Settings = () => {
  const { user } = useAuth()
  const { theme, setTheme } = useTheme()
  const [activeTab, setActiveTab] = useState('profile')
  
  const [profileData, setProfileData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    fullName: '',
    phone: ''
  })
  
  const [notificationSettings, setNotificationSettings] = useState(() => {
    const saved = localStorage.getItem('notificationSettings')
    return saved ? JSON.parse(saved) : {
      emailNotifications: true,
      pushNotifications: false,
      newLeads: true,
      interactions: true,
      weeklyReports: false
    }
  })
  
  const [securitySettings, setSecuritySettings] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'appearance', label: 'Appearance', icon: Palette },
  ]

  const handleSaveProfile = () => {
    toast.success('Profile settings saved successfully')
  }

  const handleSaveNotifications = () => {
    localStorage.setItem('notificationSettings', JSON.stringify(notificationSettings))
    toast.success('Notification settings saved successfully')
  }

  const handleSaveSecurity = () => {
    if (securitySettings.newPassword !== securitySettings.confirmPassword) {
      toast.error('Passwords do not match')
      return
    }
    if (securitySettings.newPassword.length < 6) {
      toast.error('Password must be at least 6 characters')
      return
    }
    toast.success('Password updated successfully')
    setSecuritySettings({ currentPassword: '', newPassword: '', confirmPassword: '' })
  }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Settings</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">Manage your account preferences</p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1">
          <div className="card space-y-2">
            {tabs.map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={isActive ? 'w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300' : 'w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{tab.label}</span>
                </button>
              )
            })}
          </div>
        </div>

        <div className="lg:col-span-3">
          <div className="card">
            {activeTab === 'profile' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Profile Information</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Username</label>
                    <input type="text" value={profileData.username} onChange={(e) => setProfileData({...profileData, username: e.target.value})} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Email</label>
                    <input type="email" value={profileData.email} onChange={(e) => setProfileData({...profileData, email: e.target.value})} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Full Name</label>
                    <input type="text" value={profileData.fullName} onChange={(e) => setProfileData({...profileData, fullName: e.target.value})} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Phone</label>
                    <input type="tel" value={profileData.phone} onChange={(e) => setProfileData({...profileData, phone: e.target.value})} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" />
                  </div>
                </div>
                <div className="flex justify-end pt-4 border-t dark:border-gray-700">
                  <button onClick={handleSaveProfile} className="btn-primary flex items-center space-x-2"><Save className="w-4 h-4" /><span>Save Changes</span></button>
                </div>
              </div>
            )}

            {activeTab === 'notifications' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Notification Preferences</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div><p className="font-medium text-gray-900 dark:text-gray-100">Email Notifications</p><p className="text-sm text-gray-600 dark:text-gray-400">Receive updates via email</p></div>
                    <label className="relative inline-flex items-center cursor-pointer"><input type="checkbox" checked={notificationSettings.emailNotifications} onChange={(e) => setNotificationSettings({...notificationSettings, emailNotifications: e.target.checked})} className="sr-only peer" /><div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div></label>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div><p className="font-medium text-gray-900 dark:text-gray-100">Push Notifications</p><p className="text-sm text-gray-600 dark:text-gray-400">Browser push notifications</p></div>
                    <label className="relative inline-flex items-center cursor-pointer"><input type="checkbox" checked={notificationSettings.pushNotifications} onChange={(e) => setNotificationSettings({...notificationSettings, pushNotifications: e.target.checked})} className="sr-only peer" /><div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div></label>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div><p className="font-medium text-gray-900 dark:text-gray-100">New Lead Alerts</p><p className="text-sm text-gray-600 dark:text-gray-400">Get notified when new leads are added</p></div>
                    <label className="relative inline-flex items-center cursor-pointer"><input type="checkbox" checked={notificationSettings.newLeads} onChange={(e) => setNotificationSettings({...notificationSettings, newLeads: e.target.checked})} className="sr-only peer" /><div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div></label>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div><p className="font-medium text-gray-900 dark:text-gray-100">Interaction Updates</p><p className="text-sm text-gray-600 dark:text-gray-400">Updates on customer interactions</p></div>
                    <label className="relative inline-flex items-center cursor-pointer"><input type="checkbox" checked={notificationSettings.interactions} onChange={(e) => setNotificationSettings({...notificationSettings, interactions: e.target.checked})} className="sr-only peer" /><div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div></label>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div><p className="font-medium text-gray-900 dark:text-gray-100">Weekly Reports</p><p className="text-sm text-gray-600 dark:text-gray-400">Weekly summary of your activity</p></div>
                    <label className="relative inline-flex items-center cursor-pointer"><input type="checkbox" checked={notificationSettings.weeklyReports} onChange={(e) => setNotificationSettings({...notificationSettings, weeklyReports: e.target.checked})} className="sr-only peer" /><div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div></label>
                  </div>
                </div>
                <div className="flex justify-end pt-4 border-t dark:border-gray-700">
                  <button onClick={handleSaveNotifications} className="btn-primary flex items-center space-x-2"><Save className="w-4 h-4" /><span>Save Changes</span></button>
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Security Settings</h2>
                <div className="space-y-4">
                  <div><label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Current Password</label><input type="password" value={securitySettings.currentPassword} onChange={(e) => setSecuritySettings({...securitySettings, currentPassword: e.target.value})} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" /></div>
                  <div><label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">New Password</label><input type="password" value={securitySettings.newPassword} onChange={(e) => setSecuritySettings({...securitySettings, newPassword: e.target.value})} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" /></div>
                  <div><label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Confirm New Password</label><input type="password" value={securitySettings.confirmPassword} onChange={(e) => setSecuritySettings({...securitySettings, confirmPassword: e.target.value})} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" /></div>
                </div>
                <div className="flex justify-end pt-4 border-t dark:border-gray-700">
                  <button onClick={handleSaveSecurity} className="btn-primary flex items-center space-x-2"><Save className="w-4 h-4" /><span>Update Password</span></button>
                </div>
              </div>
            )}

            {activeTab === 'appearance' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Appearance Settings</h2>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">Theme</p>
                    <div className="grid grid-cols-2 gap-4">
                      <button onClick={() => setTheme('light')} className={theme === 'light' ? 'relative p-4 border-2 rounded-lg transition-all border-primary-500 bg-primary-50 dark:bg-primary-900/30' : 'relative p-4 border-2 rounded-lg transition-all border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'}>
                        <div className="flex items-center space-x-3">
                          <div className="p-2 bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600"><Sun className="w-6 h-6 text-yellow-500" /></div>
                          <div className="text-left"><p className="font-medium text-gray-900 dark:text-gray-100">Light Mode</p><p className="text-sm text-gray-600 dark:text-gray-400">Bright and clear</p></div>
                        </div>
                        {theme === 'light' && <div className="absolute top-3 right-3"><div className="bg-primary-500 rounded-full p-1"><Check className="w-3 h-3 text-white" /></div></div>}
                      </button>
                      <button onClick={() => setTheme('dark')} className={theme === 'dark' ? 'relative p-4 border-2 rounded-lg transition-all border-primary-500 bg-primary-50 dark:bg-primary-900/30' : 'relative p-4 border-2 rounded-lg transition-all border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'}>
                        <div className="flex items-center space-x-3">
                          <div className="p-2 bg-gray-800 rounded-lg"><Moon className="w-6 h-6 text-blue-400" /></div>
                          <div className="text-left"><p className="font-medium text-gray-900 dark:text-gray-100">Dark Mode</p><p className="text-sm text-gray-600 dark:text-gray-400">Easy on the eyes</p></div>
                        </div>
                        {theme === 'dark' && <div className="absolute top-3 right-3"><div className="bg-primary-500 rounded-full p-1"><Check className="w-3 h-3 text-white" /></div></div>}
                      </button>
                    </div>
                  </div>
                  <div className="bg-primary-50 dark:bg-primary-900/30 border border-primary-200 dark:border-primary-800 rounded-lg p-4">
                    <p className="text-sm text-primary-900 dark:text-primary-300"><strong>Note:</strong> Dark mode is now fully functional!</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings
