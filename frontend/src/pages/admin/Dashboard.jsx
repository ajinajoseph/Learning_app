import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/axios';
import { Shield, Users, BookOpen, UserCheck, Star, Award, ChevronRight, BarChart3, AlertCircle } from 'lucide-react';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAdminStats = async () => {
      try {
        const res = await api.get('/api/admin/dashboard');
        setStats(res.data);
      } catch (err) {
        console.error('Failed to load admin stats:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAdminStats();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-slate-905 text-slate-900 tracking-tight flex items-center gap-2">
          <Shield className="w-8 h-8 text-indigo-650 text-indigo-600" /> Platform Administration
        </h1>
        <p className="text-slate-500 mt-1">Global monitoring panel, user directory access, and review queues.</p>
      </div>

      {/* Grid Stats cards */}
      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          
          <div className="bg-white p-5 border border-slate-100 rounded-2xl shadow-sm flex items-center gap-4">
            <div className="bg-blue-50 p-3.5 rounded-xl text-blue-600"><Users className="w-6 h-6" /></div>
            <div>
              <span className="block text-2xl font-black text-slate-800">{stats.total_users}</span>
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Users</span>
            </div>
          </div>

          <div className="bg-white p-5 border border-slate-100 rounded-2xl shadow-sm flex items-center gap-4">
            <div className="bg-purple-50 p-3.5 rounded-xl text-purple-600"><BookOpen className="w-6 h-6" /></div>
            <div>
              <span className="block text-2xl font-black text-slate-800">{stats.total_courses}</span>
              <span className="text-xs font-semibold text-slate-405 text-slate-400 uppercase tracking-wider">Total Courses</span>
            </div>
          </div>

          <div className="bg-white p-5 border border-slate-100 rounded-2xl shadow-sm flex items-center gap-4 animate-pulse-slow">
            <div className="bg-amber-50 p-3.5 rounded-xl text-amber-500"><UserCheck className="w-6 h-6" /></div>
            <div>
              <span className="block text-2xl font-black text-slate-800">{stats.pending_mentors}</span>
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Pending Mentors</span>
            </div>
          </div>

          <div className="bg-white p-5 border border-slate-100 rounded-2xl shadow-sm flex items-center gap-4">
            <div className="bg-emerald-50 p-3.5 rounded-xl text-emerald-600"><Award className="w-6 h-6" /></div>
            <div>
              <span className="block text-2xl font-black text-slate-800">{stats.total_enrollments}</span>
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Enrollments</span>
            </div>
          </div>

        </div>
      )}

      {/* Admin Shortcuts Panel */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        
        <Link 
          to="/admin/users" 
          className="bg-white border border-slate-100 hover:border-indigo-100 rounded-2xl p-6 shadow-sm flex items-center justify-between card-hover group"
        >
          <div className="space-y-1">
            <h3 className="font-bold text-slate-800 text-sm group-hover:text-indigo-600 transition-colors">Users Directory</h3>
            <p className="text-xs text-slate-400">Moderate roles and edit permissions.</p>
          </div>
          <ChevronRight className="w-5 h-5 text-slate-350 text-slate-400 group-hover:text-indigo-600 transition-colors" />
        </Link>

        <Link 
          to="/admin/courses" 
          className="bg-white border border-slate-100 hover:border-indigo-100 rounded-2xl p-6 shadow-sm flex items-center justify-between card-hover group"
        >
          <div className="space-y-1">
            <h3 className="font-bold text-slate-800 text-sm group-hover:text-indigo-600 transition-colors">Course Review</h3>
            <p className="text-xs text-slate-405 text-slate-400">Approve course submissions.</p>
          </div>
          <ChevronRight className="w-5 h-5 text-slate-400 group-hover:text-indigo-600 transition-colors" />
        </Link>

        <Link 
          to="/admin/mentors" 
          className="bg-white border border-slate-100 hover:border-indigo-100 rounded-2xl p-6 shadow-sm flex items-center justify-between card-hover group"
        >
          <div className="space-y-1">
            <h3 className="font-bold text-slate-800 text-sm group-hover:text-indigo-600 transition-colors">Pending Mentors</h3>
            <p className="text-xs text-slate-400">Approve mentor applications.</p>
          </div>
          <ChevronRight className="w-5 h-5 text-slate-400 group-hover:text-indigo-600 transition-colors" />
        </Link>

        <Link 
          to="/admin/reviews" 
          className="bg-white border border-slate-100 hover:border-indigo-100 rounded-2xl p-6 shadow-sm flex items-center justify-between card-hover group"
        >
          <div className="space-y-1">
            <h3 className="font-bold text-slate-800 text-sm group-hover:text-indigo-600 transition-colors">Reported Reviews</h3>
            <p className="text-xs text-slate-400">Moderate review reports.</p>
          </div>
          <ChevronRight className="w-5 h-5 text-slate-400 group-hover:text-indigo-600 transition-colors" />
        </Link>

      </div>

    </div>
  );
};

export default Dashboard;
