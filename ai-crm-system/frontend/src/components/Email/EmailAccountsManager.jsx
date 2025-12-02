import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Mail, Plus, Trash2, RefreshCw, CheckCircle, XCircle, 
  Settings, Eye, EyeOff, AlertCircle 
} from 'lucide-react';
import api from '../../api/client';

const EmailAccountsManager = () => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [syncing, setSyncing] = useState({});
  const [newAccount, setNewAccount] = useState({
    email_address: '',
    provider: 'gmail',
    password: '',
    display_name: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      setLoading(true);
      const response = await api.get('/email/accounts');
      setAccounts(response.data.accounts || []);
    } catch (error) {
      console.error('Error fetching accounts:', error);
      setError('Failed to load email accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleAddAccount = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const response = await api.post('/email/accounts', newAccount);
      
      if (response.data.success) {
        setSuccess('Email account added successfully!');
        setShowAddModal(false);
        setNewAccount({
          email_address: '',
          provider: 'gmail',
          password: '',
          display_name: ''
        });
        fetchAccounts();
      } else {
        setError(response.data.error || 'Failed to add account');
      }
    } catch (error) {
      console.error('Error adding account:', error);
      setError(error.response?.data?.error || 'Failed to add email account. Please check your credentials.');
    }
  };

  const handleSyncAccount = async (accountId) => {
    setSyncing(prev => ({ ...prev, [accountId]: true }));
    setError('');
    setSuccess('');

    try {
      const response = await api.post(`/email/sync/${accountId}`, {
        days_back: 7,
        auto_log: true
      });

      if (response.data.success) {
        setSuccess(response.data.message);
        fetchAccounts(); // Refresh to update last_sync time
      } else {
        setError(response.data.error || 'Sync failed');
      }
    } catch (error) {
      console.error('Error syncing emails:', error);
      setError('Failed to sync emails. Please check account credentials.');
    } finally {
      setSyncing(prev => ({ ...prev, [accountId]: false }));
    }
  };

  const getProviderIcon = (provider) => {
    const icons = {
      gmail: '📧',
      outlook: '📨'
    };
    return icons[provider] || '✉️';
  };

  const formatLastSync = (lastSync) => {
    if (!lastSync) return 'Never';
    
    const syncDate = new Date(lastSync);
    const now = new Date();
    const diffMs = now - syncDate;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    return `${diffDays} days ago`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Email Accounts</h2>
          <p className="text-gray-600 mt-1">Manage your Gmail and Outlook accounts</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          <Plus className="w-4 h-4" />
          Add Account
        </button>
      </div>

      {/* Alerts */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800"
          >
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </motion.div>
        )}
        
        {success && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex items-center gap-2 p-4 bg-green-50 border border-green-200 rounded-lg text-green-800"
          >
            <CheckCircle className="w-5 h-5" />
            <span>{success}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Accounts List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : accounts.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <Mail className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No email accounts connected</h3>
          <p className="text-gray-600 mb-4">Connect your Gmail or Outlook to sync emails automatically</p>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Connect Account
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {accounts.map((account) => (
            <motion.div
              key={account.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4">
                  <div className="text-4xl">
                    {getProviderIcon(account.provider)}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {account.display_name || account.email_address}
                      </h3>
                      {account.is_primary && (
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded">
                          Primary
                        </span>
                      )}
                      {account.is_active ? (
                        <CheckCircle className="w-4 h-4 text-green-600" />
                      ) : (
                        <XCircle className="w-4 h-4 text-red-600" />
                      )}
                    </div>
                    <p className="text-gray-600 text-sm mt-1">{account.email_address}</p>
                    <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                      <span className="capitalize">{account.provider}</span>
                      <span>•</span>
                      <span>Last sync: {formatLastSync(account.last_sync)}</span>
                    </div>
                    <div className="flex items-center gap-3 mt-3">
                      {account.sync_enabled && (
                        <span className="flex items-center gap-1 text-xs text-green-600">
                          <CheckCircle className="w-3 h-3" />
                          Auto-sync enabled
                        </span>
                      )}
                      {account.auto_log_interactions && (
                        <span className="flex items-center gap-1 text-xs text-blue-600">
                          <CheckCircle className="w-3 h-3" />
                          Auto-log enabled
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleSyncAccount(account.id)}
                    disabled={syncing[account.id]}
                    className="flex items-center gap-2 px-3 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition disabled:opacity-50"
                  >
                    <RefreshCw className={`w-4 h-4 ${syncing[account.id] ? 'animate-spin' : ''}`} />
                    {syncing[account.id] ? 'Syncing...' : 'Sync Now'}
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Add Account Modal */}
      <AnimatePresence>
        {showAddModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-lg shadow-xl max-w-md w-full p-6"
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-gray-900">Add Email Account</h3>
                <button
                  onClick={() => setShowAddModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="w-6 h-6" />
                </button>
              </div>

              <form onSubmit={handleAddAccount} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Provider
                  </label>
                  <select
                    value={newAccount.provider}
                    onChange={(e) => setNewAccount({ ...newAccount, provider: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="gmail">Gmail</option>
                    <option value="outlook">Outlook</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address *
                  </label>
                  <input
                    type="email"
                    required
                    value={newAccount.email_address}
                    onChange={(e) => setNewAccount({ ...newAccount, email_address: e.target.value })}
                    placeholder="you@example.com"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    App Password *
                  </label>
                  <div className="relative">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={newAccount.password}
                      onChange={(e) => setNewAccount({ ...newAccount, password: e.target.value })}
                      placeholder="App-specific password"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {newAccount.provider === 'gmail' 
                      ? 'Generate app password at: myaccount.google.com/apppasswords'
                      : 'Use your Outlook account password or app password'}
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Display Name (optional)
                  </label>
                  <input
                    type="text"
                    value={newAccount.display_name}
                    onChange={(e) => setNewAccount({ ...newAccount, display_name: e.target.value })}
                    placeholder="Sales Team"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                  >
                    Add Account
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default EmailAccountsManager;
