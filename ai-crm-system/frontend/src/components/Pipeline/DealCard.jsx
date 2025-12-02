import React, { useState, useEffect } from 'react'
import { useDraggable } from '@dnd-kit/core'
import { DollarSign, Calendar, User, Building2, GripVertical, Users } from 'lucide-react'
import { motion } from 'framer-motion'
import DealWinProbability from '../AI/DealWinProbability'
import api from '../../api/client'

const DealCard = ({ deal, isDragging = false }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    isDragging: isDraggingActive,
  } = useDraggable({ id: deal.id })
  
  const [aiPrediction, setAiPrediction] = useState(null)
  const [loadingPrediction, setLoadingPrediction] = useState(false)

  // Fetch AI prediction for non-closed deals
  useEffect(() => {
    const fetchPrediction = async () => {
      // Only predict for active deals
      if (deal.stage === 'Closed Won' || deal.stage === 'Closed Lost') return
      
      setLoadingPrediction(true)
      try {
        const response = await api.post('/ai/predict-deal-success', { deal_id: deal.id })
        setAiPrediction(response.data)
      } catch (error) {
        console.error('Failed to fetch AI prediction:', error)
      } finally {
        setLoadingPrediction(false)
      }
    }

    fetchPrediction()
  }, [deal.id, deal.stage])

  const style = transform ? {
    transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
    opacity: isDraggingActive ? 0.5 : 1,
  } : {
    opacity: isDraggingActive ? 0.5 : 1,
  }

  const cardContent = (
    <div className={`bg-white dark:bg-gray-800 rounded-lg p-4 shadow-md hover:shadow-lg transition-shadow border border-gray-200 dark:border-gray-700 ${isDragging ? 'shadow-2xl scale-105' : ''}`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-start justify-between gap-2 mb-1">
            <h4 className="font-semibold text-gray-900 dark:text-white">
              {deal.name || deal.title}
            </h4>
            {/* AI Win Probability Badge */}
            {aiPrediction && aiPrediction.win_probability !== undefined && (
              <DealWinProbability 
                probability={aiPrediction.win_probability} 
                confidence={aiPrediction.confidence}
                size="sm"
              />
            )}
          </div>
          {/* Show company name prominently */}
          {deal.company_name && (
            <p className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-1 font-medium">
              <Building2 className="w-3 h-3" />
              {deal.company_name}
            </p>
          )}
        </div>
        <div
          {...attributes}
          {...listeners}
          className="cursor-grab active:cursor-grabbing text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
        >
          <GripVertical className="w-5 h-5" />
        </div>
      </div>

      <div className="space-y-2">
        {deal.value && (
          <div className="flex items-center gap-2 text-sm">
            <DollarSign className="w-4 h-4 text-green-600" />
            <span className="font-semibold text-green-600">
              ${Number(deal.value).toLocaleString()}
            </span>
          </div>
        )}

        {/* Show primary contact */}
        {deal.primary_contact_name && (
          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            <User className="w-4 h-4" />
            <span className="truncate">{deal.primary_contact_name}</span>
          </div>
        )}

        {/* Show additional contacts count */}
        {deal.contacts && deal.contacts.length > 0 && (
          <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
            <Users className="w-4 h-4" />
            <span>{deal.contacts.length} contact{deal.contacts.length !== 1 ? 's' : ''}</span>
          </div>
        )}

        {deal.expected_close_date && (
          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            <Calendar className="w-4 h-4" />
            <span>{new Date(deal.expected_close_date).toLocaleDateString()}</span>
          </div>
        )}

        {deal.probability !== undefined && deal.probability !== null && (
          <div className="mt-2">
            <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400 mb-1">
              <span>Probability</span>
              <span className="font-semibold">{deal.probability}%</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all"
                style={{ width: `${deal.probability}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )

  if (isDragging) {
    return cardContent
  }

  return (
    <div ref={setNodeRef} style={style}>
      {cardContent}
    </div>
  )
}

export default DealCard
