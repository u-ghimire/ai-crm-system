import React from 'react'
import { motion } from 'framer-motion'
import { Star, ArrowRight } from 'lucide-react'
import { getLeadScoreColor } from '../../utils/helpers'

const TopLeads = ({ leads }) => {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Top Leads</h2>
        <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
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
            className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
          >
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                <span className="text-primary-600 font-semibold">
                  {lead.name?.charAt(0) || 'L'}
                </span>
              </div>
              <div>
                <p className="font-medium text-gray-900">{lead.name}</p>
                <p className="text-sm text-gray-600">{lead.company}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getLeadScoreColor(lead.lead_score)}`}>
                Score: {Math.round(lead.lead_score)}
              </span>
              <ArrowRight className="w-4 h-4 text-gray-400" />
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

export default TopLeads
