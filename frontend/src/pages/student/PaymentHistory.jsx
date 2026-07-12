import React, { useState, useEffect } from 'react';
import api from '../../api/axios';
import { CreditCard, AlertCircle, Calendar, ShieldAlert } from 'lucide-react';

const PaymentHistory = () => {
  const [payments, setPayments] = useState([]);
  const [courses, setCourses] = useState({}); // {courseId: title}
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPayments = async () => {
      setLoading(true);
      try {
        const res = await api.get('/api/payments/my-payments');
        setPayments(res.data);
        
        // Fetch course details for course titles mapping
        const distinctCourseIds = [...new Set(res.data.map(p => p.course_id))];
        const courseTitles = {};
        await Promise.all(
          distinctCourseIds.map(async (cId) => {
            try {
              const cRes = await api.get(`/api/courses/${cId}`);
              courseTitles[cId] = cRes.data.title;
            } catch (err) {
              courseTitles[cId] = 'Unknown Course';
            }
          })
        );
        setCourses(courseTitles);

      } catch (err) {
        console.error('Failed to load payments:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchPayments();
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10">
      
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-slate-905 text-slate-900 tracking-tight flex items-center gap-2">
          <CreditCard className="w-8 h-8 text-indigo-650 text-indigo-600" /> Billing History
        </h1>
        <p className="text-slate-500 mt-1">Review all your previous platform orders and payment receipts.</p>
      </div>

      {loading ? (
        <div className="space-y-4 animate-pulse">
          <div className="bg-white border border-slate-100 p-12 rounded-2xl"></div>
        </div>
      ) : payments.length === 0 ? (
        <div className="text-center py-16 bg-white border border-slate-100 rounded-3xl p-8 shadow-sm">
          <AlertCircle className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h3 className="font-bold text-slate-800">No transactions recorded</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            You haven't made any purchases on this platform yet.
          </p>
        </div>
      ) : (
        <div className="bg-white border border-slate-100 rounded-2xl shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs sm:text-sm">
              <thead className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider text-[10px] border-b border-slate-100">
                <tr>
                  <th className="px-6 py-4">Transaction ID / Provider</th>
                  <th className="px-6 py-4">Purchased Course</th>
                  <th className="px-6 py-4">Order Date</th>
                  <th className="px-6 py-4">Amount</th>
                  <th className="px-6 py-4 text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {payments.map((payment) => (
                  <tr key={payment.id} className="hover:bg-slate-50/50">
                    <td className="px-6 py-4 space-y-0.5">
                      <span className="font-bold text-slate-900 block truncate max-w-[150px]">{payment.transaction_id || payment.id}</span>
                      <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider block">{payment.provider}</span>
                    </td>
                    <td className="px-6 py-4 font-bold text-slate-800">
                      {courses[payment.course_id] || 'Loading...'}
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-500 text-xs">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3.5 h-3.5" />
                        {new Date(payment.created_at || Date.now()).toLocaleDateString()}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-black text-slate-900">
                      ${payment.amount?.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className={`inline-block px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                        payment.status === 'completed' 
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-100' 
                          : payment.status === 'pending'
                          ? 'bg-amber-50 text-amber-700 border border-amber-100 animate-pulse'
                          : 'bg-red-50 text-red-700 border border-red-100'
                      }`}>
                        {payment.status}
                      </span>
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

export default PaymentHistory;
