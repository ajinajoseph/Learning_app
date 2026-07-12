import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/axios';
import { ArrowLeft, BookOpen, Trash2, Check, X, AlertCircle } from 'lucide-react';

const Courses = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submittingId, setSubmittingId] = useState(null);

  const fetchCourses = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/admin/courses');
      setCourses(res.data);
    } catch (err) {
      console.error('Failed to load courses:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCourses();
  }, []);

  const handleApprove = async (id) => {
    setSubmittingId(id);
    try {
      await api.put(`/api/admin/courses/${id}/approve`);
      setCourses((prev) =>
        prev.map((c) => (c.id === id ? { ...c, is_approved: true } : c))
      );
    } catch (err) {
      alert('Failed to approve course');
    } finally {
      setSubmittingId(null);
    }
  };

  const handleReject = async (id) => {
    setSubmittingId(id);
    try {
      await api.put(`/api/admin/courses/${id}/reject`);
      setCourses((prev) =>
        prev.map((c) => (c.id === id ? { ...c, is_approved: false } : c))
      );
    } catch (err) {
      alert('Failed to reject course');
    } finally {
      setSubmittingId(null);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this course template? This is irreversible.')) {
      return;
    }
    setSubmittingId(id);
    try {
      await api.delete(`/api/admin/courses/${id}`);
      setCourses((prev) => prev.filter((c) => c.id !== id));
    } catch (err) {
      alert('Failed to delete course');
    } finally {
      setSubmittingId(null);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-10">

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
          <BookOpen className="w-8 h-8 text-indigo-600" /> Platform Catalog Moderation
        </h1>
        <p className="text-slate-500 mt-1">Review course submissions, inspect modules, and publish/reject courses.</p>
      </div>

      {loading ? (
        <div className="bg-white border border-slate-105 p-12 rounded-2xl animate-pulse"></div>
      ) : courses.length === 0 ? (
        <div className="text-center py-16 bg-white border border-slate-100 rounded-3xl p-8 shadow-sm">
          <AlertCircle className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h3 className="font-bold text-slate-800 text-sm">No courses exist yet</h3>
        </div>
      ) : (
        <div className="bg-white border border-slate-100 rounded-2xl shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs sm:text-sm">
              <thead className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider text-[10px] border-b border-slate-100">
                <tr>
                  <th className="px-6 py-4">Course Title</th>
                  <th className="px-6 py-4">Price / Level</th>
                  <th className="px-6 py-4">Publishing Status</th>
                  <th className="px-6 py-4 text-right">Moderation Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {courses.map((course) => (
                  <tr key={course.id} className="hover:bg-slate-50/50">
                    <td className="px-6 py-4">
                      <span className="font-bold text-slate-900 block">{course.title}</span>
                      <span className="text-[10px] text-slate-400 font-semibold block mt-0.5">ID: {course.id}</span>
                    </td>
                    <td className="px-6 py-4 space-y-0.5">
                      <span className="font-bold text-slate-800 block">{course.price === 0 ? 'Free' : `$${course.price}`}</span>
                      <span className="text-[10px] text-slate-400 capitalize block">{course.level}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-block px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${course.is_approved
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-100'
                          : 'bg-amber-50 text-amber-700 border border-amber-100'
                        }`}>
                        {course.is_approved ? 'Published' : 'Under Review'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right space-x-1.5 whitespace-nowrap">
                      <button
                        onClick={() => handleApprove(course.id)}
                        disabled={course.is_approved || submittingId === course.id}
                        className={`p-2 rounded-xl transition-all inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wide ${course.is_approved
                            ? 'bg-emerald-100 text-emerald-800 border border-emerald-200 cursor-not-allowed opacity-60'
                            : 'bg-emerald-50 hover:bg-emerald-600 text-emerald-700 hover:text-white border border-emerald-250 cursor-pointer disabled:opacity-50'
                          }`}
                      >
                        <Check className="w-3.5 h-3.5" /> Approve
                      </button>

                      <button
                        onClick={() => handleReject(course.id)}
                        disabled={submittingId === course.id}
                        className={`p-2 rounded-xl transition-all inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wide cursor-pointer disabled:opacity-50 ${!course.is_approved
                            ? 'bg-amber-50 hover:bg-amber-600 text-amber-700 hover:text-white border border-amber-200'
                            : 'bg-amber-50 hover:bg-amber-600 text-amber-700 hover:text-white border border-amber-200'
                          }`}
                      >
                        <X className="w-3.5 h-3.5" /> Reject
                      </button>

                      <button
                        onClick={() => handleDelete(course.id)}
                        disabled={submittingId === course.id}
                        className="bg-red-50 hover:bg-red-600 text-red-700 hover:text-white border border-red-200 p-2 rounded-xl transition-all inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wide cursor-pointer disabled:opacity-50"
                        title="Delete Permanently"
                      >
                        <Trash2 className="w-3.5 h-3.5" /> Delete
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

export default Courses;
