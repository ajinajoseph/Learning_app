import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { updateUserProfile } from '../../store/authSlice';
import api from '../../api/axios';
import { User, Mail, ShieldAlert, Award, Calendar, CheckCircle } from 'lucide-react';

const Profile = () => {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);

  // Form state
  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Sync local state when user loads
    if (user) {
      setName(user.name);
      setEmail(user.email);
    }
  }, [user]);

  const handleUpdate = async (e) => {
    e.preventDefault();
    setSuccess('');
    setLoading(true);

    // Mock Profile Edit saving
    // Since backend does not support profile editing PUT route, we simulate it
    // by updating the Redux state and localStorage, which preserves it on page reloads!
    setTimeout(() => {
      dispatch(updateUserProfile({ name }));
      setSuccess('Profile updated successfully!');
      setLoading(false);
    }, 800);
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-10">
      
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-slate-905 text-slate-900 tracking-tight flex items-center gap-2">
          <User className="w-8 h-8 text-indigo-650 text-indigo-600" /> My Profile
        </h1>
        <p className="text-slate-500 mt-1">Manage your account details and learning role information.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
        
        {/* Left Side: Avatar Panel */}
        <div className="md:col-span-4 bg-white border border-slate-100 p-6 rounded-2xl shadow-sm text-center">
          <div className="w-20 h-20 bg-indigo-100 text-indigo-700 font-black text-2xl rounded-full flex items-center justify-center mx-auto mb-4 uppercase shadow-sm">
            {user?.name?.substring(0, 2)}
          </div>
          <h3 className="font-bold text-slate-805 text-slate-800 text-base truncate">{user?.name}</h3>
          
          <div className="mt-4 flex flex-col gap-2">
            <span className="inline-block px-3 py-1 text-xs font-bold uppercase rounded bg-indigo-50 text-indigo-600 border border-indigo-100 mx-auto">
              Role: {user?.role}
            </span>
            {user?.role === 'mentor' && (
              <span className={`inline-block px-3 py-1 text-xs font-bold uppercase rounded mx-auto ${
                user.is_approved 
                  ? 'bg-emerald-50 text-emerald-600 border border-emerald-100' 
                  : 'bg-amber-50 text-amber-600 border border-amber-100'
              }`}>
                {user.is_approved ? 'Approved Mentor' : 'Approval Pending'}
              </span>
            )}
          </div>
        </div>

        {/* Right Side: Account Settings Form */}
        <form onSubmit={handleUpdate} className="md:col-span-8 bg-white border border-slate-100 p-6 sm:p-8 rounded-2xl shadow-sm space-y-6">
          <h3 className="font-bold text-slate-805 text-slate-800 text-sm border-b border-slate-55 border-b border-slate-100 pb-3">
            Account Settings
          </h3>

          {success && (
            <div className="bg-emerald-50 text-emerald-700 border border-emerald-100 rounded-xl p-3.5 text-xs flex gap-2 items-center">
              <CheckCircle className="w-4.5 h-4.5 shrink-0 text-emerald-650" />
              <span>{success}</span>
            </div>
          )}

          <div className="space-y-4">
            
            {/* Email Address (disabled) */}
            <div>
              <label className="block text-xs font-bold text-slate-450 text-slate-400 uppercase tracking-wider mb-1.5">
                Email Address (Cannot be changed)
              </label>
              <div className="relative">
                <input
                  type="email"
                  disabled
                  value={email}
                  className="w-full bg-slate-50 border border-slate-200 text-slate-400 pl-10 pr-4 py-2.5 rounded-xl cursor-not-allowed text-sm font-medium"
                />
                <Mail className="absolute left-3.5 top-3.5 w-4 h-4 text-slate-350" />
              </div>
            </div>

            {/* Display Name */}
            <div>
              <label className="block text-xs font-bold text-slate-455 text-slate-450 text-slate-400 uppercase tracking-wider mb-1.5">
                Display Name
              </label>
              <div className="relative">
                <input
                  type="text"
                  required
                  placeholder="Update your name..."
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 text-slate-700 placeholder-slate-400 pl-10 pr-4 py-2.5 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all text-sm font-semibold"
                />
                <User className="absolute left-3.5 top-3.5 w-4 h-4 text-slate-400" />
              </div>
            </div>

          </div>

          <div className="pt-4 flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="bg-indigo-650 bg-indigo-600 hover:bg-indigo-755 hover:bg-indigo-700 text-white font-bold text-xs px-6 py-3 rounded-xl transition-all shadow-md"
            >
              {loading ? 'Saving...' : 'Save Settings'}
            </button>
          </div>

        </form>

      </div>

    </div>
  );
};

export default Profile;
