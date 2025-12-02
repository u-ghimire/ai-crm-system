import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Plus, CheckCircle, Clock, AlertCircle, Filter,
  Search, Calendar, User, Building2
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../api/client'
import { formatDateTime } from '../utils/helpers'
import AddTaskModal from '../components/Tasks/AddTaskModal'

const PRIORITIES = {
  high: { label: 'High', color: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400', icon: AlertCircle },
  medium: { label: 'Medium', color: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400', icon: Clock },
  low: { label: 'Low', color: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400', icon: CheckCircle }
}

const Tasks = () => {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('pending')
  const [searchTerm, setSearchTerm] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)

  useEffect(() => {
    fetchTasks()
  }, [filter])

  const fetchTasks = async () => {
    try {
      const response = await api.get(`/tasks?status=${filter}`)
      if (response.data.success && response.data.tasks) {
        setTasks(response.data.tasks)
      } else if (Array.isArray(response.data)) {
        setTasks(response.data)
      } else {
        console.error('Failed to fetch tasks:', response.data.message)
        setTasks([])
      }
    } catch (error) {
      console.error('Error loading tasks:', error)
      toast.error('Failed to load tasks')
      setTasks([])
    } finally {
      setLoading(false)
    }
  }

  const handleCompleteTask = async (taskId) => {
    try {
      await api.put(`/tasks/${taskId}/status`, { 
        status: 'completed'
      })
      toast.success('Task completed!')
      fetchTasks()
    } catch (error) {
      console.error('Error completing task:', error)
      toast.error(error.response?.data?.message || 'Failed to complete task')
    }
  }

  const filteredTasks = tasks.filter(task =>
    task.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    task.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    task.customer_name?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const groupTasksByDate = (tasks) => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)
    
    const groups = {
      overdue: [],
      today: [],
      tomorrow: [],
      upcoming: [],
      no_date: []
    }

    tasks.forEach(task => {
      if (!task.due_date) {
        groups.no_date.push(task)
        return
      }

      const dueDate = new Date(task.due_date)
      dueDate.setHours(0, 0, 0, 0)

      if (dueDate < today) {
        groups.overdue.push(task)
      } else if (dueDate.getTime() === today.getTime()) {
        groups.today.push(task)
      } else if (dueDate.getTime() === tomorrow.getTime()) {
        groups.tomorrow.push(task)
      } else {
        groups.upcoming.push(task)
      }
    })

    return groups
  }

  const groupedTasks = groupTasksByDate(filteredTasks)

  const renderTaskGroup = (title, tasks, color) => {
    if (tasks.length === 0) return null

    return (
      <div className="mb-8">
        <h3 className={`text-lg font-bold ${color} mb-4 flex items-center space-x-2`}>
          <span>{title}</span>
          <span className="text-sm font-normal">({tasks.length})</span>
        </h3>
        <div className="space-y-3">
          {tasks.map((task, index) => {
            const PriorityIcon = PRIORITIES[task.priority]?.icon || Clock
            const priorityColor = PRIORITIES[task.priority]?.color || PRIORITIES.medium.color
            
            // Check if task is overdue
            const isOverdue = task.status === 'pending' && task.due_date && 
                            new Date(task.due_date) < new Date(new Date().setHours(0, 0, 0, 0))

            return (
              <motion.div
                key={task.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`bg-white dark:bg-gray-800 rounded-xl shadow-md hover:shadow-lg transition-all duration-200 p-5 border ${
                  isOverdue 
                    ? 'border-red-500 bg-red-50 dark:bg-red-900/20 dark:border-red-600' 
                    : 'border-gray-100 dark:border-gray-700'
                }`}
              >
                <div className="flex items-start space-x-4">
                  {/* Checkbox */}
                  {task.status === 'pending' && (
                    <button
                      onClick={() => handleCompleteTask(task.id)}
                      className="mt-1 w-6 h-6 rounded-full border-2 border-gray-300 dark:border-gray-600 hover:border-green-500 dark:hover:border-green-400 transition-colors flex items-center justify-center"
                      title="Mark as completed"
                    >
                      <div className="w-3 h-3 rounded-full bg-transparent hover:bg-green-500 dark:hover:bg-green-400 transition-colors"></div>
                    </button>
                  )}
                  {task.status === 'completed' && (
                    <div className="mt-1 w-6 h-6 rounded-full flex items-center justify-center">
                      <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-500" />
                    </div>
                  )}

                  {/* Task Content */}
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <h4 className={`text-lg font-bold ${
                          task.status === 'completed' 
                            ? 'text-gray-500 dark:text-gray-500 line-through' 
                            : 'text-gray-900 dark:text-gray-100'
                        }`}>
                          {task.title}
                        </h4>
                        {isOverdue && (
                          <span className="px-2 py-0.5 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-xs font-semibold rounded-full">
                            OVERDUE
                          </span>
                        )}
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold flex items-center space-x-1 ${priorityColor}`}>
                        <PriorityIcon className="w-3 h-3" />
                        <span>{PRIORITIES[task.priority]?.label || 'Medium'}</span>
                      </span>
                    </div>

                    {task.description && (
                      <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">
                        {task.description}
                      </p>
                    )}

                    <div className="flex flex-wrap items-center gap-4 text-sm">
                      {task.due_date && (
                        <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
                          <Calendar className="w-4 h-4" />
                          <span>{formatDateTime(task.due_date)}</span>
                        </div>
                      )}
                      
                      {task.customer_name && (
                        <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
                          <User className="w-4 h-4" />
                          <span>{task.customer_name}</span>
                        </div>
                      )}

                      {task.deal_title && (
                        <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
                          <Building2 className="w-4 h-4" />
                          <span>{task.deal_title}</span>
                        </div>
                      )}

                      {task.assigned_to_name && (
                        <div className="flex items-center space-x-2">
                          <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                            <span className="text-white text-xs font-bold">
                              {task.assigned_to_name.charAt(0).toUpperCase()}
                            </span>
                          </div>
                          <span className="text-gray-600 dark:text-gray-400 text-sm">
                            {task.assigned_to_name}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-4xl font-extrabold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
            Tasks & Activities
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Manage your tasks and follow-ups</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-xl transition-all duration-200 flex items-center space-x-2"
        >
          <Plus className="w-5 h-5" />
          <span>New Task</span>
        </button>
      </motion.div>

      {/* Filters and Search */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6"
      >
        <div className="flex flex-col md:flex-row items-center gap-4">
          {/* Search */}
          <div className="flex-1 relative w-full">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search tasks..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>

          {/* Status Filter */}
          <div className="flex items-center space-x-2">
            {['pending', 'completed', 'all'].map(status => (
              <button
                key={status}
                onClick={() => setFilter(status === 'all' ? '' : status)}
                className={`px-4 py-2 rounded-xl font-semibold transition-all duration-200 ${
                  filter === status || (filter === '' && status === 'all')
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Tasks List */}
      {loading ? (
        <div className="flex items-center justify-center py-16">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div>
          {renderTaskGroup('Overdue', groupedTasks.overdue, 'text-red-600 dark:text-red-400')}
          {renderTaskGroup('Today', groupedTasks.today, 'text-blue-600 dark:text-blue-400')}
          {renderTaskGroup('Tomorrow', groupedTasks.tomorrow, 'text-purple-600 dark:text-purple-400')}
          {renderTaskGroup('Upcoming', groupedTasks.upcoming, 'text-gray-700 dark:text-gray-300')}
          {renderTaskGroup('No Due Date', groupedTasks.no_date, 'text-gray-500 dark:text-gray-500')}

          {filteredTasks.length === 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-16"
            >
              <Clock className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
                No tasks found
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                {searchTerm ? 'Try adjusting your search' : 'Get started by creating your first task'}
              </p>
              <button
                onClick={() => setShowAddModal(true)}
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-xl transition-all duration-200"
              >
                Create Task
              </button>
            </motion.div>
          )}
        </div>
      )}

      {/* Add Task Modal */}
      {showAddModal && (
        <AddTaskModal
          onClose={() => setShowAddModal(false)}
          onSuccess={() => {
            setShowAddModal(false)
            fetchTasks()
          }}
        />
      )}
    </div>
  )
}

export default Tasks
