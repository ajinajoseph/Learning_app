import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/axios';
import { ArrowLeft, Star, ShieldAlert, Check, Trash2, AlertCircle } from 'lucide-react';

const Reviews = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/admin/review-reports');
      setReports(res.data);
    } catch (err) {
      console.error('Failed to load review reports:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleResolve = async (reportId) => {
    try {
      await api.put(`/api/admin/review-reports/${reportId}`, { action: 'resolve' });
      setReports((prev) => prev.filter((r) => r.id !== reportId));
    } catch (err) {
      alert('Failed to resolve report');
    }
  };

  const handleDismiss = async (reportId) => {
    try {
      await api.put(`/api/admin/review-reports/${reportId}`, { action: 'dismiss' });
      setReports((prev) => prev.filter((r) => r.id !== reportId));
    } catch (err) {
      alert('Failed to dismiss report');
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10">
      
      {/* Back Button */}
      <Link 
        to="/admin/dashboard" 
        className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-indigo-650 mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Administration
      </Link>

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-slate-905 text-slate-900 tracking-tight flex items-center gap-2">
          <ShieldAlert className="w-8 h-8 text-indigo-650 text-indigo-600" /> Reported Reviews Moderation
        </h1>
        <p className="text-slate-500 mt-1">Review student flags, read flagged comments, and remove/dismiss reviews.</p>
      </div>

      {loading ? (
        <div className="bg-white border border-slate-105 p-12 rounded-2xl animate-pulse"></div>
      ) : reports.length === 0 ? (
        <div className="text-center py-16 bg-white border border-slate-100 rounded-3xl p-8 shadow-sm">
          <Check className="w-12 h-12 text-emerald-600 bg-emerald-50 rounded-full p-2 mx-auto mb-4" />
          <h3 className="font-bold text-slate-808 text-slate-850 text-slate-800">All reports resolved!</h3>
          <p className="text-xs text-slate-500 mt-1">No reported course review items are currently flagged for review.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {reports.map((report) => (
            <div 
              key={report.id} 
              className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm flex flex-col md:flex-row justify-between gap-6"
            >
              
              <div className="space-y-3 flex-1 min-w-0">
                <div className="flex flex-wrap gap-2 text-[10px] font-bold uppercase tracking-wider">
                  <span className="bg-red-50 text-red-700 border border-red-100 px-2 py-0.5 rounded">
                    Reason: {report.reason}
                  </span>
                  <span className="bg-slate-100 text-slate-500 px-2 py-0.5 rounded">
                    Reporter ID: {report.reporter_id}
                  </span>
                </div>

                <div className="p-4 bg-slate-50 border border-slate-100 rounded-xl space-y-2">
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest">Flagged Comment</p>
                  <p className="text-sm text-slate-700 italic">
                    "{report.review?.comment || 'No comment text'}"
                  </p>
                  <div className="flex gap-0.5">
                    {Array(report.review?.rating || 5).fill(0).map((_, i) => (
                      <Star key={i} className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                    ))}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex md:flex-col justify-end items-end gap-2.5 shrink-0">
                <button
                  onClick={() => handleResolve(report.id)}
                  className="w-full md:w-36 bg-red-600 hover:bg-red-700 text-white font-bold text-xs py-2.5 rounded-xl shadow-sm inline-flex items-center justify-center gap-1 uppercase tracking-wider"
                >
                  <Trash2 className="w-3.5 h-3.5" /> Remove Review
                </button>
                <button
                  onClick={() => handleDismiss(report.id)}
                  className="w-full md:w-36 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs py-2.5 rounded-xl border border-slate-200 inline-flex items-center justify-center gap-1 uppercase tracking-wider"
                >
                  <Check className="w-3.5 h-3.5" /> Dismiss Report
                </button>
              </div>

            </div>
          ))}
        </div>
      )}

    </div>
  );
};

export default Reviews;
