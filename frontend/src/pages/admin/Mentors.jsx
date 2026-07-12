import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/axios';
import { ArrowLeft, UserCheck, Check, X, AlertCircle } from 'lucide-react';

const Mentors = () => {
  const [pendingList, setPendingList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submittingId, setSubmittingId] = useState(null);

  const fetchPendingMentors = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/admin/mentors/pending');
      setPendingList(res.data);
    } catch (err) {
      console.error('Failed to load pending mentors:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPendingMentors();
  }, []);

  const handleApprove = async (id) => {
    setSubmittingId(id);
    try {
      await api.put(`/api/admin/mentors/${id}/approve`);
      setPendingList((prev) => prev.filter((m) => m.id !== id));
    } catch (err) {
      alert('Failed to approve mentor account');
    } finally {
      setSubmittingId(null);
    }
  };

  const handleReject = async (id) => {
    setSubmittingId(id);
    try {
      await api.put(`/api/admin/mentors/${id}/reject`);
      setPendingList((prev) => prev.filter((m) => m.id !== id));
    } catch (err) {
      alert('Failed to reject mentor application');
    } finally {
      setSubmittingId(null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-10">
      
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
          <UserCheck className="w-8 h-8 text-indigo-655 text-indigo-600" /> Pending Mentor Approvals
        </h1>
        <p className="text-slate-500 mt-1">Review applicant profiles, check background metrics, and approve applications.</p>
      </div>

      {loading ? (
        <div className="bg-white border border-slate-100 p-12 rounded-2xl animate-pulse"></div>
      ) : pendingList.length === 0 ? (
        <div className="text-center py-16 bg-white border border-slate-100 rounded-3xl p-8 shadow-sm">
          <Check className="w-12 h-12 text-emerald-600 bg-emerald-50 rounded-full p-2 mx-auto mb-4" />
          <h3 className="font-bold text-slate-808 text-slate-850 text-slate-800">All applications processed!</h3>
          <p className="text-xs text-slate-500 mt-1">No pending instructor approval files currently await moderation.</p>
        </div>
      ) : (
        <div className="bg-white border border-slate-100 rounded-2xl shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs sm:text-sm">
              <thead className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider text-[10px] border-b border-slate-100">
                <tr>
                  <th className="px-6 py-4">Applicant Name</th>
                  <th className="px-6 py-4">Email</th>
                  <th className="px-6 py-4 text-right">Approve / Reject Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {pendingList.map((mentor) => (
                  <tr key={mentor.id} className="hover:bg-slate-50/50">
                    <td className="px-6 py-4 font-bold text-slate-900 flex items-center gap-2">
                      <div className="w-8 h-8 bg-slate-100 rounded-full flex items-center justify-center font-bold uppercase text-slate-500 shrink-0 text-xs">
                        {mentor.name?.substring(0, 2)}
                      </div>
                      <span>{mentor.name}</span>
                    </td>
                    <td className="px-6 py-4 text-slate-500 font-semibold">{mentor.email}</td>
                    <td className="px-6 py-4 text-right space-x-1.5 shrink-0">
                      <button
                        onClick={() => handleApprove(mentor.id)}
                        disabled={submittingId === mentor.id}
                        className="bg-emerald-50 hover:bg-emerald-600 text-emerald-700 hover:text-white border border-emerald-150 p-2 px-3 rounded-xl transition-all inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wide cursor-pointer disabled:opacity-50"
                      >
                        <Check className="w-3.5 h-3.5" /> Approve
                      </button>
                      <button
                        onClick={() => handleReject(mentor.id)}
                        disabled={submittingId === mentor.id}
                        className="bg-red-50 hover:bg-red-600 text-red-700 hover:text-white border border-red-200 p-2 px-3 rounded-xl transition-all inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wide cursor-pointer disabled:opacity-50"
                      >
                        <X className="w-3.5 h-3.5" /> Reject
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

    </div>
  );
};

export default Mentors;
