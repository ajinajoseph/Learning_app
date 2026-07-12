import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useSelector } from 'react-redux';
import api from '../../api/axios';
import CourseCard from '../../components/CourseCard';
import { BookOpen, Award, FileText, ArrowRight, Activity, Smile, GraduationCap, CheckCircle } from 'lucide-react';

const Dashboard = () => {
  const { user } = useSelector((state) => state.auth);
  
  // State
  const [enrolledCourses, setEnrolledCourses] = useState([]);
  const [certificates, setCertificates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        // 1. Fetch student enrollments
        const enrollmentsRes = await api.get('/api/enrollments/my-courses');
        const enrollments = enrollmentsRes.data;

        // 2. Fetch full details & progress for each course
        const coursesData = await Promise.all(
          enrollments.map(async (enrol) => {
            try {
              const [courseRes, progressRes] = await Promise.all([
                api.get(`/api/courses/${enrol.course_id}`),
                api.get(`/api/progress/course/${enrol.course_id}`)
              ]);
              return {
                ...courseRes.data,
                progress: progressRes.data.percentage,
                completed: progressRes.data.percentage === 100
              };
            } catch (err) {
              console.error(`Failed to fetch details for course ${enrol.course_id}`, err);
              return null;
            }
          })
        );

        setEnrolledCourses(coursesData.filter(Boolean));

        // 3. Fetch certificates
        const certRes = await api.get('/api/certificates/my');
        setCertificates(certRes.data);

      } catch (err) {
        console.error('Failed to load student dashboard:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const inProgressCourses = enrolledCourses.filter((c) => c.progress < 100);
  const completedCoursesCount = enrolledCourses.filter((c) => c.progress === 100).length;

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      
      {/* Welcome Header */}
      <div className="bg-indigo-900 rounded-3xl p-6 sm:p-8 text-white flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8 shadow-md">
        <div className="space-y-1">
          <h1 className="text-2xl sm:text-3xl font-extrabold flex items-center gap-2">
            Hi, {user?.name}! <Smile className="w-7 h-7 text-indigo-200" />
          </h1>
          <p className="text-indigo-200 text-xs sm:text-sm">
            Ready to learn something new today? Keep pushing towards your learning goals.
          </p>
        </div>
        <Link 
          to="/courses"
          className="bg-white text-indigo-900 font-bold text-xs px-5 py-2.5 rounded-xl hover:bg-indigo-50 transition-colors shadow-lg"
        >
          Explore Catalog
        </Link>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-10">
        <div className="bg-white p-5 border border-slate-100 rounded-2xl shadow-sm flex items-center gap-4">
          <div className="bg-blue-50 p-3.5 rounded-xl text-blue-600">
            <BookOpen className="w-6 h-6" />
          </div>
          <div>
            <span className="block text-2xl font-black text-slate-800">{enrolledCourses.length}</span>
            <span className="text-xs font-semibold text-slate-405 text-slate-400 uppercase tracking-wider">Enrolled Courses</span>
          </div>
        </div>

        <div className="bg-white p-5 border border-slate-100 rounded-2xl shadow-sm flex items-center gap-4">
          <div className="bg-emerald-50 p-3.5 rounded-xl text-emerald-600">
            <CheckCircle className="w-6 h-6" />
          </div>
          <div>
            <span className="block text-2xl font-black text-slate-800">{completedCoursesCount}</span>
            <span className="text-xs font-semibold text-slate-405 text-slate-400 uppercase tracking-wider">Completed Courses</span>
          </div>
        </div>

        <div className="bg-white p-5 border border-slate-100 rounded-2xl shadow-sm flex items-center gap-4">
          <div className="bg-purple-50 p-3.5 rounded-xl text-purple-600">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <span className="block text-2xl font-black text-slate-800">{certificates.length}</span>
            <span className="text-xs font-semibold text-slate-405 text-slate-400 uppercase tracking-wider">Certificates Earned</span>
          </div>
        </div>
      </div>

      {/* Main Grid content */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left ongoing learning */}
        <div className="lg:col-span-8 space-y-8">
          
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
              <GraduationCap className="w-5 h-5 text-indigo-600" /> Ongoing Courses
            </h2>
            <Link to="/my-courses" className="text-xs font-bold text-indigo-650 text-indigo-600 hover:text-indigo-800 flex items-center gap-0.5">
              View all my courses <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {inProgressCourses.length === 0 ? (
            <div className="text-center py-16 bg-white border border-slate-100 p-8 rounded-2xl shadow-sm">
              <BookOpen className="w-12 h-12 text-slate-200 mx-auto mb-3" />
              <h3 className="font-bold text-slate-800 text-sm">No ongoing courses</h3>
              <p className="text-xs text-slate-500 mt-1">You are fully caught up or haven't enrolled in any paid/free courses yet.</p>
              <Link to="/courses" className="mt-4 inline-block bg-indigo-600 text-white font-bold text-xs px-4 py-2.5 rounded-full">
                Find a Course
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {inProgressCourses.map((course) => (
                <CourseCard key={course.id} course={course} progress={course.progress} />
              ))}
            </div>
          )}

        </div>

        {/* Right side widgets: Activity / certificates */}
        <div className="lg:col-span-4 space-y-8">
          
          {/* Recent Activity */}
          <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm">
            <h3 className="font-bold text-slate-800 text-sm flex items-center gap-2 mb-4">
              <Activity className="w-4 h-4 text-indigo-600" /> Recent Activity
            </h3>
            <div className="space-y-4">
              <div className="flex gap-3 text-xs leading-relaxed">
                <div className="w-2.5 h-2.5 bg-indigo-600 rounded-full mt-1 shrink-0"></div>
                <div>
                  <p className="font-semibold text-slate-700">Enrolled in the platform</p>
                  <span className="text-slate-400 text-[10px]">Just now</span>
                </div>
              </div>
              {enrolledCourses.slice(0, 2).map((course, idx) => (
                <div key={idx} className="flex gap-3 text-xs leading-relaxed">
                  <div className="w-2.5 h-2.5 bg-indigo-400 rounded-full mt-1 shrink-0"></div>
                  <div>
                    <p className="font-semibold text-slate-700">Enrolled in course: <strong className="text-indigo-600">{course.title}</strong></p>
                    <span className="text-slate-400 text-[10px]">Recent</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Earned certificates widget */}
          <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm">
            <h3 className="font-bold text-slate-800 text-sm flex items-center gap-2 mb-4">
              <Award className="w-4 h-4 text-indigo-600" /> Certificates ({certificates.length})
            </h3>
            {certificates.length === 0 ? (
              <p className="text-xs text-slate-400 italic">No certificates earned yet. Hit 100% progress on enrolled courses to receive your award.</p>
            ) : (
              <div className="space-y-3">
                {certificates.slice(0, 2).map((cert) => (
                  <div key={cert.id} className="p-3 border border-slate-50 bg-slate-50/50 rounded-xl flex items-center justify-between gap-3 text-xs">
                    <div className="min-w-0">
                      <p className="font-semibold text-slate-800 truncate">{cert.course_name || 'Course Certificate'}</p>
                      <span className="text-[10px] text-slate-400">Awarded on {new Date(cert.issued_at).toLocaleDateString()}</span>
                    </div>
                    <a 
                      href={cert.certificate_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs font-bold text-indigo-600 shrink-0 hover:underline"
                    >
                      View
                    </a>
                  </div>
                ))}
                {certificates.length > 2 && (
                  <Link to="/certificates" className="text-[11px] font-bold text-indigo-600 hover:underline block text-center mt-2">
                    View all certificates
                  </Link>
                )}
              </div>
            )}
          </div>

        </div>

      </div>

    </div>
  );
};

export default Dashboard;
