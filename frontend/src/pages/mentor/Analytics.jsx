import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../../api/axios';
import { BarChart3, ArrowLeft, Users, DollarSign, Star, Percent, RefreshCw, MessageSquare } from 'lucide-react';

const Analytics = () => {
  const { id } = useParams(); // courseId
  
  // State
  const [course, setCourse] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchAnalytics = async () => {
    setLoading(true);
    setError('');
    try {
      const [courseRes, analyticsRes] = await Promise.all([
        api.get(`/api/courses/${id}`),
        api.get(`/api/analytics/course/${id}`)
      ]);
      setCourse(courseRes.data);
      setAnalytics(analyticsRes.data);
    } catch (err) {
      setError('Failed to fetch course analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (error || !course || !analytics) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center space-y-4">
        <div className="bg-red-50 text-red-700 p-4 border border-red-100 rounded-xl text-sm max-w-sm mx-auto">
          {error || 'Course or analytics data could not be retrieved.'}
        </div>
        <Link to="/mentor/dashboard" className="inline-flex items-center gap-1.5 bg-indigo-650 bg-indigo-600 text-white font-semibold text-xs px-5 py-2.5 rounded-xl shadow-md">
          <ArrowLeft className="w-4 h-4" /> Back to Dashboard
        </Link>
      </div>
    );
  }

  const estimatedRevenue = analytics.total_students * course.price;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10">
      
      {/* Back Button */}
      <Link 
        to="/mentor/dashboard" 
        className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-indigo-600 mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </Link>

      {/* Header */}
      <div className="flex justify-between items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-905 text-slate-900 tracking-tight flex items-center gap-2">
            <BarChart3 className="w-8 h-8 text-indigo-600" /> Course Performance Analytics
          </h1>
          <p className="text-slate-500 mt-1">Course: <strong className="text-slate-700">{course.title}</strong></p>
        </div>

        <button 
          onClick={fetchAnalytics}
          className="p-2.5 bg-white border border-slate-200 text-slate-550 hover:text-indigo-600 rounded-xl transition-colors shadow-sm"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Analytics Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        
        {/* Total Enrollments */}
        <div className="bg-white border border-slate-100 rounded-2xl p-5 shadow-sm space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-xs font-bold text-slate-405 uppercase tracking-wider">Students Enrolled</span>
            <div className="bg-blue-50 p-2 rounded-lg text-blue-600"><Users className="w-4.5 h-4.5" /></div>
          </div>
          <div>
            <span className="block text-2xl font-black text-slate-800">{analytics.total_students}</span>
            <span className="text-[10px] text-slate-400 font-semibold uppercase">Lifetime active enrollments</span>
          </div>
        </div>

        {/* Total Estimated Revenue */}
        <div className="bg-white border border-slate-100 rounded-2xl p-5 shadow-sm space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-xs font-bold text-slate-405 uppercase tracking-wider">Est. Revenue</span>
            <div className="bg-emerald-50 p-2 rounded-lg text-emerald-600"><DollarSign className="w-4.5 h-4.5" /></div>
          </div>
          <div>
            <span className="block text-2xl font-black text-slate-800">${estimatedRevenue.toFixed(2)}</span>
            <span className="text-[10px] text-slate-450 text-slate-400 font-semibold uppercase">Price: ${course.price.toFixed(2)}</span>
          </div>
        </div>

        {/* Average Rating */}
        <div className="bg-white border border-slate-100 rounded-2xl p-5 shadow-sm space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-xs font-bold text-slate-405 uppercase tracking-wider">Average Rating</span>
            <div className="bg-amber-50 p-2 rounded-lg text-amber-500">
              <Star className="w-4.5 h-4.5 fill-amber-400 text-amber-400" />
            </div>
          </div>
          <div>
            <span className="block text-2xl font-black text-slate-800">{analytics.average_rating || '0.0'}</span>
            <span className="text-[10px] text-slate-450 text-slate-400 font-semibold uppercase">Reviews count: {analytics.total_reviews}</span>
          </div>
        </div>

        {/* Completion Rate */}
        <div className="bg-white border border-slate-100 rounded-2xl p-5 shadow-sm space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-xs font-bold text-slate-405 uppercase tracking-wider">Completion Rate</span>
            <div className="bg-purple-50 p-2 rounded-lg text-purple-600"><Percent className="w-4.5 h-4.5" /></div>
          </div>
          <div>
            <span className="block text-2xl font-black text-slate-800">{analytics.completion_rate}%</span>
            <span className="text-[10px] text-slate-450 text-slate-400 font-semibold uppercase">Completed vs Total lessons</span>
          </div>
        </div>

      </div>

      {/* Explanatory Analytics widget */}
      <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm space-y-4">
        <h3 className="font-bold text-slate-808 text-slate-850 text-slate-800 text-sm">Course Optimization Recommendations</h3>
        <ul className="text-xs sm:text-sm text-slate-600 divide-y divide-slate-50 leading-relaxed font-semibold">
          <li className="py-3 flex justify-between gap-4 items-baseline">
            <span>Student Retention Indicator</span>
            <span className={analytics.completion_rate > 50 ? 'text-emerald-600' : 'text-amber-600'}>
              {analytics.completion_rate > 50 ? 'Healthy' : 'Needs attention'}
            </span>
          </li>
          <li className="py-3 flex justify-between gap-4 items-baseline">
            <span>Feedback Loop Index</span>
            <span className="text-indigo-600">{analytics.total_reviews > 0 ? 'Excellent engagement' : 'Awaiting reviews'}</span>
          </li>
        </ul>
      </div>

    </div>
  );
};

export default Analytics;
