import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Mail, RefreshCw, CheckCircle, Clock, ExternalLink } from 'lucide-react';
import api from '../../api/client';

const EmailSyncWidget = () => {
  const [syncedEmails, setSyncedEmails] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [syncing, setSyncing] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [emailsRes, accountsRes] = await Promise.all([
        api.get('/email/synced?limit=5'),
        api.get('/email/accounts')
      ]);
      
      setSyncedEmails(emailsRes.data.emails || []);
      setAccounts(accountsRes.data.accounts || []);
    } catch (error) {
      console.error('Error fetching email data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSyncAll = async () => {
    setSyncing(true);
    try {
      // Sync all active accounts
      const activeAccounts = accounts.filter(acc => acc.is_active && acc.sync_enabled);
      
      for (const account of activeAccounts) {
        await api.post(`/email/sync/${account.id}`, {
          days_back: 7,
          auto_log: true
        });
      }
      
      // Refresh data
      await fetchData();
    } catch (error) {
      console.error('Error syncing emails:', error);
    } finally {
      setSyncing(false);
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Mail className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Email Sync</h3>
              <p className="text-sm text-gray-600">
                {accounts.filter(a => a.is_active).length} account(s) connected
              </p>
            </div>
          </div>
          <button
            onClick={handleSyncAll}
            disabled={syncing || accounts.length === 0}
            className="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'Syncing...' : 'Sync Now'}
          </button>
        </div>
      </div>

      {/* Recent Emails */}
      <div className="p-6">
        {syncedEmails.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Mail className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p>No emails synced yet</p>
            {accounts.length > 0 && (
              <p className="text-sm mt-2">Click "Sync Now" to fetch emails</p>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">Recent Emails</h4>
            {syncedEmails.map((email, index) => (
              <motion.div
                key={email.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 transition cursor-pointer"
              >
                <div className={`p-2 rounded-full ${email.is_sent ? 'bg-green-100' : 'bg-blue-100'}`}>
                  <Mail className={`w-4 h-4 ${email.is_sent ? 'text-green-600' : 'text-blue-600'}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <h5 className="text-sm font-medium text-gray-900 truncate">
                      {email.subject || '(No subject)'}
                    </h5>
                    <span className="text-xs text-gray-500 whitespace-nowrap">
                      {formatDate(email.sent_date)}
                    </span>
                  </div>
                  <p className="text-xs text-gray-600 mt-1">
                    {email.is_sent ? 'To: ' : 'From: '}
                    {email.is_sent ? email.to_email : email.from_email}
                  </p>
                  {email.customer_name && (
                    <div className="flex items-center gap-1 mt-1">
                      <CheckCircle className="w-3 h-3 text-green-600" />
                      <span className="text-xs text-green-600">
                        Logged for {email.customer_name}
                      </span>
                    </div>
                  )}
                  <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                    {email.body_preview}
                  </p>
                </div>
              </motion.div>
            ))}
            
            {syncedEmails.length >= 5 && (
              <button className="w-full py-2 text-sm text-blue-600 hover:text-blue-700 font-medium">
                View All Emails →
              </button>
            )}
          </div>
        )}
      </div>

      {/* Sync Status */}
      {accounts.length > 0 && (
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2 text-gray-600">
              <Clock className="w-4 h-4" />
              <span>
                Last sync: {accounts[0]?.last_sync 
                  ? formatDate(accounts[0].last_sync)
                  : 'Never'}
              </span>
            </div>
            <a
              href="/settings"
              className="flex items-center gap-1 text-blue-600 hover:text-blue-700"
            >
              Manage Accounts
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmailSyncWidget;
