import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/axios';
import CourseCard from '../../components/CourseCard';
import SkeletonCard from '../../components/SkeletonCard';
import { BookOpen, Search, AlertCircle } from 'lucide-react';

const MyCourses = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchVal, setSearchVal] = useState('');

  useEffect(() => {
    const fetchMyCourses = async () => {
      setLoading(true);
      try {
        const enrollmentsRes = await api.get('/api/enrollments/my-courses');
        const enrollments = enrollmentsRes.data;

        const coursesData = await Promise.all(
          enrollments.map(async (enrol) => {
            try {
              const [courseRes, progressRes] = await Promise.all([
                api.get(`/api/courses/${enrol.course_id}`),
                api.get(`/api/progress/course/${enrol.course_id}`)
              ]);
              return {
                ...courseRes.data,
                progress: progressRes.data.percentage
              };
            } catch (err) {
              console.error(`Failed to fetch course details: ${enrol.course_id}`, err);
              return null;
            }
          })
        );
        setCourses(coursesData.filter(Boolean));
      } catch (err) {
        console.error('Failed to load enrolled courses:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMyCourses();
  }, []);

  const filteredCourses = courses.filter((c) =>
    c.title?.toLowerCase().includes(searchVal.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      
      {/* Header and Search */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">My Courses</h1>
          <p className="text-slate-500 mt-1">Access all your enrolled classes and track your progress.</p>
        </div>

        <div className="relative w-full sm:w-64">
          <input
            type="text"
            placeholder="Search my courses..."
            value={searchVal}
            onChange={(e) => setSearchVal(e.target.value)}
            className="w-full bg-white border border-slate-200 text-slate-700 placeholder-slate-400 pl-9 pr-4 py-2 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <Search className="absolute left-3 top-3 w-4 h-4 text-slate-400" />
        </div>
      </div>

      {/* Courses Grid */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array(3).fill(0).map((_, idx) => <SkeletonCard key={idx} />)}
        </div>
      ) : filteredCourses.length === 0 ? (
        <div className="text-center py-20 bg-white border border-slate-100 p-8 rounded-3xl shadow-sm">
          <BookOpen className="w-12 h-12 text-slate-350 mx-auto mb-4" />
          <h3 className="font-bold text-slate-800 text-base">No courses found</h3>
          <p className="text-xs text-slate-550 mt-1 max-w-sm mx-auto">
            {searchVal 
              ? `No enrolled courses matched "${searchVal}"` 
              : "You haven't enrolled in any courses yet. Check out the explore page to find a class!"}
          </p>
          {!searchVal && (
            <Link 
              to="/courses"
              className="mt-6 inline-block bg-indigo-600 text-white font-bold text-xs px-5 py-2.5 rounded-full hover:bg-indigo-700 transition-all hover:shadow-md"
            >
              Explore Catalog
            </Link>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCourses.map((course) => (
            <CourseCard key={course.id} course={course} progress={course.progress} />
          ))}
        </div>
      )}

    </div>
  );
};

export default MyCourses;
