import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { DndContext, DragOverlay, closestCorners, PointerSensor, useSensor, useSensors } from '@dnd-kit/core'
import { TrendingUp, Plus, DollarSign, Calendar } from 'lucide-react'
import api from '../api/client'
import DealCard from '../components/Pipeline/DealCard'
import PipelineColumn from '../components/Pipeline/PipelineColumn'
import AddDealModal from '../components/Pipeline/AddDealModal'

const Pipeline = () => {
  const [pipeline, setPipeline] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [activeId, setActiveId] = useState(null)
  const [customers, setCustomers] = useState([])
  const [companies, setCompanies] = useState([])

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  )

  useEffect(() => {
    fetchPipeline()
    fetchCustomers()
    fetchCompanies()
  }, [])

  const fetchPipeline = async () => {
    try {
      setLoading(true)
      const response = await api.get('/deals/pipeline')
      if (response.data.success) {
        setPipeline(response.data.pipeline)
      }
    } catch (error) {
      console.error('Error fetching pipeline:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchCustomers = async () => {
    try {
      const response = await api.get('/customers')
      // Handle both array response and object response
      if (Array.isArray(response.data)) {
        setCustomers(response.data)
      } else if (response.data.success && response.data.customers) {
        setCustomers(response.data.customers)
      } else if (response.data && !response.data.success) {
        console.error('Failed to fetch customers:', response.data.message)
      }
    } catch (error) {
      console.error('Error fetching customers:', error)
    }
  }

  const fetchCompanies = async () => {
    try {
      const response = await api.get('/companies')
      if (response.data.success && response.data.companies) {
        setCompanies(response.data.companies)
      } else if (Array.isArray(response.data)) {
        setCompanies(response.data)
      } else {
        console.error('Failed to fetch companies:', response.data.message)
      }
    } catch (error) {
      console.error('Error fetching companies:', error)
    }
  }

  const handleDragStart = (event) => {
    setActiveId(event.active.id)
  }

  const handleDragEnd = async (event) => {
    const { active, over } = event
    
    if (!over) {
      setActiveId(null)
      return
    }

    const dealId = active.id
    const newStage = over.id
    
    console.log(`🎯 Drag ended: Deal ${dealId} → ${newStage}`)

    // Optimistically update UI
    setPipeline(prevPipeline => {
      const newPipeline = prevPipeline.map(column => ({
        ...column,
        deals: column.deals.filter(deal => deal.id !== dealId)
      }))

      const deal = prevPipeline.flatMap(col => col.deals).find(d => d.id === dealId)

      if (deal) {
        const targetColumn = newPipeline.find(col => col.name === newStage)
        if (targetColumn) {
          // Update deal stage for proper calculation
          deal.stage = newStage
          targetColumn.deals.push(deal)
          
          // Recalculate column metrics
          targetColumn.deal_count = targetColumn.deals.length
          targetColumn.total_value = targetColumn.deals.reduce((sum, d) => sum + (d.value || 0), 0)
        }
      }

      // Recalculate source column metrics
      newPipeline.forEach(column => {
        if (!column.deals.some(d => d.id === dealId)) {
          column.deal_count = column.deals.length
          column.total_value = column.deals.reduce((sum, d) => sum + (d.value || 0), 0)
        }
      })

      return newPipeline
    })

    try {
      console.log(`📡 Sending API request: PUT /deals/${dealId}/stage`, { stage: newStage })
      const response = await api.put(`/deals/${dealId}/stage`, { stage: newStage })
      console.log(`✅ API response:`, response.data)
      // Fetch fresh data from server to ensure accuracy
      fetchPipeline()
    } catch (error) {
      console.error('❌ Error updating deal stage:', error)
      console.error('Error details:', error.response?.data || error.message)
      // Revert by fetching fresh data
      fetchPipeline()
    }

    setActiveId(null)
  }

  const getTotalValue = () => {
    return pipeline.reduce((sum, column) => sum + column.total_value, 0)
  }

  const getTotalDeals = () => {
    return pipeline.reduce((sum, column) => sum + column.deal_count, 0)
  }

  const getActiveDeals = () => {
    return pipeline.filter(col => !['Closed Won', 'Closed Lost'].includes(col.name)).reduce((sum, column) => sum + column.deal_count, 0)
  }

  const activeDeal = pipeline.flatMap(col => col.deals).find(deal => deal.id === activeId)

  return (
    <div className="p-6">
      <div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <TrendingUp className="w-8 h-8 text-blue-600" />
            Sales Pipeline
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Track and manage your deals through stages</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          Add Deal
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Pipeline Value</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">${getTotalValue().toLocaleString()}</p>
            </div>
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl flex items-center justify-center">
              <DollarSign className="w-6 h-6 text-white" />
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Deals</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">{getTotalDeals()}</p>
            </div>
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Active Deals</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">{getActiveDeals()}</p>
            </div>
            <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-pink-500 rounded-xl flex items-center justify-center">
              <Calendar className="w-6 h-6 text-white" />
            </div>
          </div>
        </motion.div>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 dark:text-gray-400 mt-4">Loading pipeline...</p>
        </div>
      ) : (
        <DndContext sensors={sensors} collisionDetection={closestCorners} onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
          <div className="flex gap-6 overflow-x-auto pb-6">
            {pipeline.map((column) => (
              <PipelineColumn key={column.name} column={column} deals={column.deals} />
            ))}
          </div>
          <DragOverlay>{activeId && activeDeal ? <DealCard deal={activeDeal} isDragging /> : null}</DragOverlay>
        </DndContext>
      )}

      {showModal && (
        <AddDealModal onClose={() => setShowModal(false)} onSuccess={() => { setShowModal(false); fetchPipeline(); }} customers={customers} companies={companies} />
      )}
    </div>
  )
}

export default Pipeline
