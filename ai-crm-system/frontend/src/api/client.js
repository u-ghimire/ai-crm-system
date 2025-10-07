import axios from 'axios'

// Create axios instance with default config
const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Auth API
export const authAPI = {
  login: (username, password) => 
    axios.post('/login', { username, password }, { withCredentials: true }),
  logout: () => 
    axios.post('/logout', {}, { withCredentials: true })
}

// Customers API
export const customersAPI = {
  getAll: () => api.get('/customers'),
  getById: (id) => api.get(`/customers/${id}`),
  create: (data) => api.post('/customers', data),
  update: (id, data) => api.put(`/customers/${id}`, data),
  delete: (id) => api.delete(`/customers/${id}`)
}

// Interactions API
export const interactionsAPI = {
  getAll: () => api.get('/interactions'),
  getByCustomer: (customerId) => api.get(`/interactions?customer_id=${customerId}`),
  create: (data) => api.post('/interactions', data)
}

// Dashboard API
export const dashboardAPI = {
  getAnalytics: () => api.get('/dashboard/analytics'),
  generateAIReport: () => api.post('/generate-ai-report')
}

// Notifications API
export const notificationsAPI = {
  getAll: (limit = 10) => api.get(`/notifications?limit=${limit}`)
}

// Chatbot API
export const chatbotAPI = {
  sendMessage: (message, customerId) => 
    api.post('/chatbot/message', { message, customer_id: customerId })
}

// AI Services API
export const aiAPI = {
  analyzeLead: (customerId) => 
    api.post('/ai/analyze-lead', { customer_id: customerId })
}

// Opportunities API
export const opportunitiesAPI = {
  getAll: () => api.get('/opportunities'),
  getByCustomer: (customerId) => api.get(`/opportunities?customer_id=${customerId}`),
  create: (data) => api.post('/opportunities', data)
}

// Reports API
export const reportsAPI = {
  getSalesReport: () => api.get('/reports/sales')
}

export default api
