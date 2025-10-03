import { format, formatDistance, parseISO } from 'date-fns'

// Format currency
export const formatCurrency = (amount) => {
  if (amount === null || amount === undefined) return '$0'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount)
}

// Format date
export const formatDate = (date) => {
  if (!date) return 'N/A'
  try {
    const parsedDate = typeof date === 'string' ? parseISO(date) : new Date(date)
    return format(parsedDate, 'MMM d, yyyy')
  } catch (error) {
    return 'Invalid date'
  }
}

// Format date with time
export const formatDateTime = (date) => {
  if (!date) return 'N/A'
  try {
    const parsedDate = typeof date === 'string' ? parseISO(date) : new Date(date)
    return format(parsedDate, 'MMM d, yyyy h:mm a')
  } catch (error) {
    return 'Invalid date'
  }
}

// Format relative time
export const formatRelativeTime = (date) => {
  if (!date) return 'N/A'
  try {
    const parsedDate = typeof date === 'string' ? parseISO(date) : new Date(date)
    return formatDistance(parsedDate, new Date(), { addSuffix: true })
  } catch (error) {
    return 'Invalid date'
  }
}

// Get lead score color
export const getLeadScoreColor = (score) => {
  if (score >= 80) return 'bg-green-100 text-green-800'
  if (score >= 60) return 'bg-blue-100 text-blue-800'
  if (score >= 40) return 'bg-yellow-100 text-yellow-800'
  return 'bg-red-100 text-red-800'
}

// Get status color
export const getStatusColor = (status) => {
  const colors = {
    lead: 'bg-gray-100 text-gray-800',
    interested: 'bg-blue-100 text-blue-800',
    qualified: 'bg-purple-100 text-purple-800',
    hot: 'bg-red-100 text-red-800',
    customer: 'bg-green-100 text-green-800',
    cold: 'bg-gray-100 text-gray-600'
  }
  return colors[status?.toLowerCase()] || 'bg-gray-100 text-gray-800'
}

// Truncate text
export const truncate = (text, length = 50) => {
  if (!text) return ''
  if (text.length <= length) return text
  return text.substring(0, length) + '...'
}

// Validate email
export const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

// Validate phone
export const validatePhone = (phone) => {
  const re = /^[\d\s\-\+\(\)]+$/
  return re.test(phone)
}

// Generate initials
export const getInitials = (name) => {
  if (!name) return '?'
  const parts = name.split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.substring(0, 2).toUpperCase()
}

// Calculate percentage
export const calculatePercentage = (value, total) => {
  if (!total || total === 0) return 0
  return Math.round((value / total) * 100)
}

// Format percentage
export const formatPercentage = (value) => {
  return `${Math.round(value)}%`
}
