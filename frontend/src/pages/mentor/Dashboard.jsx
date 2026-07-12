import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useSelector } from 'react-redux';
import api from '../../api/axios';
import { BookOpen, Users, DollarSign, Star, AlertTriangle, Plus, ListCollapse, BarChart3 } from 'lucide-react';

const Dashboard = () => {
  const { user } = useSelector((state) => state.auth);
  
  // States
  const [courses, setCourses] = useState([]);
  const [analytics, setAnalytics] = useState({}); // {courseId: analyticsData}
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMentorDashboard = async () => {
      setLoading(true);
      try {
        const res = await api.get('/api/courses/my-courses');
        const myCourses = res.data;
        setCourses(myCourses);

        // Fetch analytics for each course
        const analyticsData = {};
        await Promise.all(
          myCourses.map(async (c) => {
            try {
              const aRes = await api.get(`/api/analytics/course/${c.id}`);
              analyticsData[c.id] = aRes.data;
            } catch (err) {
              console.error(`Failed to load analytics for course ${c.id}`, err);
            }
          })
        );
        setAnalytics(analyticsData);

      } catch (err) {
        console.error('Failed to load mentor dashboard:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMentorDashboard();
  }, []);

  // Compute aggregate stats
  const totalCourses = courses.length;
  const totalStudents = Object.values(analytics).reduce((sum, item) => sum + (item.total_students || 0), 0);
  const totalRevenue = courses.reduce((sum, course) => {
    const courseStats = analytics[course.id];
    const students = courseStats?.total_students || 0;
    return sum + (students * course.price);
  }, 0);

  const avgRating = totalCourses > 0
    ? (Object.values(analytics).reduce((sum, item) => sum + (item.average_rating || 0), 0) / totalCourses).toFixed(1)
    : '0.0';

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      
      {/* Pending Approval warning banner */}
      {user && !user.is_approved && (
        <div className="bg-amber-50 border border-amber-100 p-5 rounded-2xl flex gap-3.5 items-start text-sm text-amber-800 mb-8 shadow-sm">
          <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h3 className="font-bold">Mentor Account Pending Approval</h3>
            <p className="text-xs text-amber-700 leading-relaxed">
              Your instructor application is undergoing administrative review. You can navigate the workspace, but you won't be able to submit course metadata or compile course content modules until your account is approved.
            </p>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Instructor Dashboard</h1>
          <p className="text-slate-500 mt-1">Manage your curricula and view platform performance metrics.</p>
        </div>

        {user?.is_approved && (
          <Link
            to="/mentor/courses/new"
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs px-5 py-2.5 rounded-xl transition-all shadow-md flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" /> Create Course
          </Link>
        )}
      </div>

      {/* Stats Cards grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        <div className="bg-white p-5 border border-slate-100 rounded-2xl shadow-sm flex items-center gap-4">
          <div className="bg-blue-50 p-3.5 rounded-xl text-blue-600">
            <BookOpen className="w-6 h-6" />
          </div>
          <div>
            <span className="block text-2xl font-black text-slate-800">{totalCourses}</span>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Courses Created</span>
          </div>
        </div>

        <div className="bg-white p-5 border border-slate-100 rounded-2xl shadow-sm flex items-center gap-4">
          <div className="bg-purple-50 p-3.5 rounded-xl text-purple-600">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <span className="block text-2xl font-black text-slate-800">{totalStudents}</span>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Students</span>
          </div>
        </div>

        <div className="bg-white p-5 border border-slate-100 rounded-2xl shadow-sm flex items-center gap-4">
          <div className="bg-emerald-50 p-3.5 rounded-xl text-emerald-600">
            <DollarSign className="w-6 h-6" />
          </div>
          <div>
            <span className="block text-2xl font-black text-slate-800">${totalRevenue.toFixed(2)}</span>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Est. Revenue</span>
          </div>
        </div>

        <div className="bg-white p-5 border border-slate-100 rounded-2xl shadow-sm flex items-center gap-4">
          <div className="bg-amber-50 p-3.5 rounded-xl text-amber-500">
            <Star className="w-6 h-6 fill-amber-400 text-amber-400" />
          </div>
          <div>
            <span className="block text-2xl font-black text-slate-800">{avgRating}</span>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Avg Rating</span>
          </div>
        </div>
      </div>

      {/* Created Courses Feed Table */}
      <div className="bg-white border border-slate-100 rounded-2xl shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-50 bg-slate-50/50">
          <h2 className="font-bold text-slate-800 text-sm">Course List & Basic Stats</h2>
        </div>

        {courses.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            <BookOpen className="w-12 h-12 mx-auto mb-3 text-slate-300" />
            <p className="font-bold text-slate-700">No courses created yet</p>
            <p className="text-xs mt-1">Get started by creating your first online curriculum class.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs sm:text-sm">
              <thead className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider text-[10px] border-b border-slate-100">
                <tr>
                  <th className="px-6 py-4">Title</th>
                  <th className="px-6 py-4">Enrolled Students</th>
                  <th className="px-6 py-4">Price / Level</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {courses.map((course) => {
                  const stats = analytics[course.id];
                  return (
                    <tr key={course.id} className="hover:bg-slate-50/30">
                      <td className="px-6 py-4 font-bold text-slate-900">{course.title}</td>
                      <td className="px-6 py-4 font-semibold text-slate-550">{stats?.total_students || 0}</td>
                      <td className="px-6 py-4 space-y-0.5">
                        <span className="font-bold text-slate-800 block">{course.price === 0 ? 'Free' : `$${course.price}`}</span>
                        <span className="text-[10px] text-slate-400 capitalize block">{course.level}</span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-block px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                          course.is_approved 
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-100' 
                            : 'bg-amber-50 text-amber-700 border border-amber-100 animate-pulse'
                        }`}>
                          {course.is_approved ? 'Approved' : 'Pending Approval'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right space-x-2 shrink-0">
                        <Link
                          to={`/mentor/courses/${course.id}/curriculum`}
                          className="bg-slate-50 border border-slate-205 text-slate-700 hover:text-indigo-650 hover:bg-indigo-50/50 font-bold text-[10px] px-3 py-2 rounded-xl transition-all"
                        >
                          Curriculum
                        </Link>
                        <Link
                          to={`/mentor/courses/${course.id}/analytics`}
                          className="bg-indigo-50 text-indigo-600 hover:bg-indigo-600 hover:text-white font-bold text-[10px] px-3 py-2 rounded-xl transition-all inline-flex items-center gap-1 shadow-sm"
                        >
                          <BarChart3 className="w-3 h-3" /> Analytics
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
};

export default Dashboard;
