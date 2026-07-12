import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../../api/axios';
import { BookOpen, Plus, Trash2, Edit, ListCollapse, BarChart3, AlertCircle } from 'lucide-react';

const toast = {
  success: (message) => {
    const el = document.createElement('div');
    el.className = 'fixed bottom-4 right-4 bg-emerald-600 text-white px-4 py-3 rounded-xl shadow-2xl z-50 flex items-center gap-2 text-sm font-semibold transition-all duration-300 transform translate-y-10 opacity-0';
    el.innerHTML = `<span>✓</span><span>${message}</span>`;
    document.body.appendChild(el);
    setTimeout(() => el.classList.remove('translate-y-10', 'opacity-0'), 10);
    setTimeout(() => {
      el.classList.add('translate-y-10', 'opacity-0');
      setTimeout(() => el.remove(), 300);
    }, 3000);
  },
  error: (message) => {
    const el = document.createElement('div');
    el.className = 'fixed bottom-4 right-4 bg-rose-600 text-white px-4 py-3 rounded-xl shadow-2xl z-50 flex items-center gap-2 text-sm font-semibold transition-all duration-300 transform translate-y-10 opacity-0';
    el.innerHTML = `<span>⚠</span><span>${message}</span>`;
    document.body.appendChild(el);
    setTimeout(() => el.classList.remove('translate-y-10', 'opacity-0'), 10);
    setTimeout(() => {
      el.classList.add('translate-y-10', 'opacity-0');
      setTimeout(() => el.remove(), 300);
    }, 3000);
  }
};

const MyCourses = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchMyCourses = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/courses/my-courses');
      setCourses(res.data);
    } catch (err) {
      console.error('Failed to fetch mentor courses:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMyCourses();
  }, []);

  const handleDelete = async (courseId) => {
    if (!window.confirm(
      'Are you sure? This will permanently delete the course, ' +
      'all modules, lessons, and student data.'
    )) return;
    try {
      await api.delete(`/api/courses/${courseId}`);
      toast.success('Course deleted');
      fetchMyCourses(); // refresh list
    } catch (err) {
      console.error('Delete error:', err.response?.data);
      toast.error(
        err.response?.data?.message || 'Failed to delete course'
      );
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      
      {/* Header Panel */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-905 text-slate-900 tracking-tight">My Courses</h1>
          <p className="text-slate-500 mt-1">Add course templates, structure curriculum modules, and review student rosters.</p>
        </div>

        <Link
          to="/mentor/courses/new"
          className="bg-indigo-650 bg-indigo-600 hover:bg-indigo-755 hover:bg-indigo-700 text-white font-bold text-xs px-5 py-2.5 rounded-xl transition-all shadow-md flex items-center gap-1.5 shrink-0"
        >
          <Plus className="w-4 h-4" /> Create New Course
        </Link>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 animate-pulse">
          {Array(3).fill(0).map((_, idx) => (
            <div key={idx} className="bg-white border border-slate-100 p-16 rounded-2xl h-44"></div>
          ))}
        </div>
      ) : courses.length === 0 ? (
        <div className="text-center py-20 bg-white border border-slate-100 p-8 rounded-3xl shadow-sm">
          <BookOpen className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h3 className="font-bold text-slate-808 text-slate-850 text-slate-800">No courses created yet</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            You haven't structured any courses. Click the button above to define your first course!
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.map((course) => (
            <div 
              key={course.id} 
              className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden flex flex-col p-5 hover:shadow-md transition-shadow relative cursor-pointer"
              onClick={(e) => {
                // Ignore click if it originated on a button or link
                if (e.target.closest('button') || e.target.closest('a')) {
                  return;
                }
                navigate(`/mentor/courses/${course.id}/detail`);
              }}
            >
              <div className="flex-1 space-y-3">
                <div className="flex justify-between items-start gap-3">
                  <h3 className="font-bold text-slate-800 text-base leading-snug line-clamp-2">{course.title}</h3>
                  <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider ${
                    course.is_approved 
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-100' 
                      : 'bg-amber-50 text-amber-700 border border-amber-100'
                  }`}>
                    {course.is_approved ? 'Approved' : 'Pending'}
                  </span>
                </div>
                
                <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed">{course.description}</p>
                
                <div className="text-xs font-semibold text-slate-600 flex gap-4 pt-1">
                  <span>Price: <strong className="text-slate-800">{course.price === 0 ? 'Free' : `$${course.price}`}</strong></span>
                  <span className="capitalize">Level: <strong className="text-slate-800">{course.level}</strong></span>
                </div>
              </div>

              {/* Actions panel */}
              <div className="border-t border-slate-50 mt-5 pt-4 flex justify-between items-center gap-2">
                <div className="flex gap-2">
                  <Link
                    to={`/mentor/courses/${course.id}/edit`}
                    className="p-2 border border-slate-150 rounded-lg text-slate-500 hover:text-indigo-600 hover:bg-slate-50 transition-colors"
                    title="Edit Metadata"
                  >
                    <Edit className="w-4 h-4" />
                  </Link>
                  <button
                    onClick={() => handleDelete(course.id)}
                    className="p-2 border border-slate-150 rounded-lg text-slate-500 hover:text-red-600 hover:bg-slate-50 transition-colors"
                    title="Delete Course"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="flex gap-2">
                  <Link
                    to={`/mentor/courses/${course.id}/curriculum`}
                    className="bg-slate-100 hover:bg-indigo-50 border border-slate-150 text-slate-700 hover:text-indigo-650 font-bold text-xs px-3.5 py-2 rounded-xl transition-all flex items-center gap-1"
                  >
                    <ListCollapse className="w-3.5 h-3.5" /> Modules
                  </Link>
                  <Link
                    to={`/mentor/courses/${course.id}/analytics`}
                    className="bg-indigo-50 text-indigo-600 hover:bg-indigo-600 hover:text-white font-bold text-xs px-3.5 py-2 rounded-xl transition-all flex items-center gap-1"
                  >
                    <BarChart3 className="w-3.5 h-3.5" /> Analytics
                  </Link>
                </div>
              </div>

            </div>
          ))}
        </div>
      )}

    </div>
  );
};

export default MyCourses;

