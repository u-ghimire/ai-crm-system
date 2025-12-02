import React from 'react'
import { useDroppable } from '@dnd-kit/core'
import DealCard from './DealCard'
import { DollarSign } from 'lucide-react'

const PipelineColumn = ({ column, deals }) => {
  const { setNodeRef, isOver } = useDroppable({
    id: column.name,
  })

  const getStageColor = (stageName) => {
    const colors = {
      'Lead': 'bg-gray-100 dark:bg-gray-800 border-gray-300 dark:border-gray-600',
      'Qualified': 'bg-blue-50 dark:bg-blue-900/20 border-blue-300 dark:border-blue-700',
      'Proposal': 'bg-purple-50 dark:bg-purple-900/20 border-purple-300 dark:border-purple-700',
      'Negotiation': 'bg-orange-50 dark:bg-orange-900/20 border-orange-300 dark:border-orange-700',
      'Closed Won': 'bg-green-50 dark:bg-green-900/20 border-green-300 dark:border-green-700',
      'Closed Lost': 'bg-red-50 dark:bg-red-900/20 border-red-300 dark:border-red-700',
    }
    return colors[stageName] || 'bg-gray-100 dark:bg-gray-800 border-gray-300 dark:border-gray-600'
  }

  const getStageTextColor = (stageName) => {
    const colors = {
      'Lead': 'text-gray-700 dark:text-gray-300',
      'Qualified': 'text-blue-700 dark:text-blue-300',
      'Proposal': 'text-purple-700 dark:text-purple-300',
      'Negotiation': 'text-orange-700 dark:text-orange-300',
      'Closed Won': 'text-green-700 dark:text-green-300',
      'Closed Lost': 'text-red-700 dark:text-red-300',
    }
    return colors[stageName] || 'text-gray-700 dark:text-gray-300'
  }

  return (
    <div className="flex-shrink-0 w-80">
      <div className={`rounded-xl border-2 ${getStageColor(column.name)} p-4 transition-all ${isOver ? 'ring-2 ring-blue-500 ring-opacity-50' : ''}`}>
        {/* Column Header */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className={`font-bold text-lg ${getStageTextColor(column.name)}`}>
              {column.name}
            </h3>
            <span className="bg-white dark:bg-gray-700 px-2 py-1 rounded-full text-sm font-semibold text-gray-600 dark:text-gray-300">
              {column.deal_count}
            </span>
          </div>
          <div className="flex items-center gap-1 text-sm font-semibold text-gray-700 dark:text-gray-300">
            <DollarSign className="w-4 h-4" />
            <span>${(column.total_value || 0).toLocaleString()}</span>
          </div>
        </div>

        {/* Deals List */}
        <div
          ref={setNodeRef}
          className="space-y-3 min-h-[200px]"
        >
          {deals.length === 0 ? (
            <div className="text-center py-8 text-gray-400 dark:text-gray-500 text-sm">
              No deals in this stage
            </div>
          ) : (
            deals.map((deal) => (
              <DealCard key={deal.id} deal={deal} />
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default PipelineColumn
