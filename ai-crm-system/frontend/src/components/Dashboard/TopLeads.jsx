import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Star, ArrowRight } from 'lucide-react'
import { getLeadScoreColor } from '../../utils/helpers'
import StatsDetailModal from './StatsDetailModal'

const TopLeads = ({ leads }) => {
  const [showModal, setShowModal] = useState(false)

  return (
    <>
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Top Leads</h2>
          <button 
            onClick={() => setShowModal(true)}
            className="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 text-sm font-medium"
          >
            View All
          </button>
        </div>

      <div className="space-y-4">
        {leads?.map((lead, index) => (
          <motion.div
            key={lead.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer"
          >
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
                <span className="text-primary-600 dark:text-primary-300 font-semibold">
                  {lead.name?.charAt(0) || 'L'}
                </span>
              </div>
              <div>
                <p className="font-medium text-gray-900 dark:text-gray-100">{lead.name}</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">{lead.company}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getLeadScoreColor(lead.lead_score)}`}>
                Score: {Math.round(lead.lead_score)}
              </span>
              <ArrowRight className="w-4 h-4 text-gray-400 dark:text-gray-500" />
            </div>
          </motion.div>
        ))}
      </div>
    </div>

    <StatsDetailModal
      isOpen={showModal}
      onClose={() => setShowModal(false)}
      statType="leads"
      title="All Active Leads"
    />
  </>
  )
}

export default TopLeads
