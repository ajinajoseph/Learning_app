import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api/axios';
import axios from 'axios';
import CourseCard from '../components/CourseCard';
import SkeletonCard from '../components/SkeletonCard';
import { 
  Search, BookOpen, Users, Award, ShieldCheck, ChevronRight, 
  Star, Quote, Play, ArrowRight, CheckCircle2 
} from 'lucide-react';
import { useSelector } from 'react-redux';
const Landing = () => {
  const navigate = useNavigate();
  const [searchVal, setSearchVal] = useState('');
  const [featuredCourses, setFeaturedCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const { user } = useSelector((state) => state.auth);

  useEffect(() => {
  const fetchCourses = async () => {
    try {
      // Use plain axios — no auth header needed for public route
      const res = await axios.get('http://localhost:5000/api/courses');
      setFeaturedCourses(res.data.slice(0, 3));
    } catch (err) {
      console.error('Failed to load courses:', err);
    } finally {
      setLoading(false);
    }
  };
  fetchCourses();
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchVal.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchVal)}`);
    }
  };

  const categories = [
    { name: 'Development', count: '120+ Courses', query: 'development', icon: '💻' },
    { name: 'Data Science', count: '80+ Courses', query: 'data science', icon: '📊' },
    { name: 'Design & UX', count: '65+ Courses', query: 'design', icon: '🎨' },
    { name: 'Business', count: '90+ Courses', query: 'business', icon: '💼' },
    { name: 'Marketing', count: '50+ Courses', query: 'marketing', icon: '📈' },
    { name: 'Languages', count: '30+ Courses', query: 'language', icon: '🗣️' },
  ];


  return (
    <div className="bg-[#F9FAFB] min-h-screen">
      
      {/* 1. Hero Section */}
      <header className="hero-gradient text-white py-20 lg:py-28 relative overflow-hidden">
        {/* Abstract background shapes */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 transform translate-x-20 -translate-y-20"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 transform -translate-x-20 translate-y-20"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center lg:text-left">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            
            {/* Left Content */}
            <div className="lg:col-span-7 space-y-6">
              <span className="inline-block bg-indigo-500/30 border border-indigo-400/40 text-indigo-200 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-widest">
                Start Learning Today
              </span>
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-tight">
                Unlock Your Potential With <span className="text-indigo-300">EduFlex</span>
              </h1>
              <p className="text-lg text-indigo-100 max-w-xl mx-auto lg:mx-0 leading-relaxed">
                Connect with industry-leading mentors and master real-world skills. Choose from hundreds of professional courses in Web Development, AI, Business, and Design.
              </p>

              {/* Search Bar */}
              <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto lg:mx-0 pt-2">
                <div className="relative flex-1">
                  <input
                    type="text"
                    placeholder="What do you want to learn?"
                    value={searchVal}
                    onChange={(e) => setSearchVal(e.target.value)}
                    className="w-full bg-white text-slate-800 placeholder-slate-400 pl-11 pr-4 py-3.5 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-400 text-sm font-medium"
                  />
                  <Search className="absolute left-4 top-4.5 w-4 h-4 text-slate-400" />
                </div>
                <button
                  type="submit"
                  className="bg-indigo-500 hover:bg-indigo-600 text-white font-bold text-sm px-6 py-3.5 rounded-xl transition-all shadow-md shadow-indigo-700/30"
                >
                  Search
                </button>
              </form>

              <div className="flex flex-wrap items-center justify-center lg:justify-start gap-6 pt-4 text-xs text-indigo-200">
                <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-indigo-400" /> Lifetime access</span>
                <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-indigo-400" /> Industry expert mentors</span>
                <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-indigo-400" /> Shareable certificates</span>
              </div>
            </div>

            {/* Right Media Mockup */}
            <div className="lg:col-span-5 hidden lg:block relative">
              <div className="relative mx-auto w-full max-w-[420px] aspect-square rounded-3xl overflow-hidden shadow-2xl border border-indigo-400/30">
                <img 
                   src="https://plus.unsplash.com/premium_vector-1720670407512-4fdfe6e67a18?q=80&w=1039&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
                  alt="Learning illustration"
                  className="w-full h-full object-contain p-6"
                />
                <div className="absolute inset-0 bg-indigo-900/10"></div>
              </div>
            </div>

          </div>
        </div>
      </header>

      {/* 2. Stats Banner */}
      <section className="bg-white border-y border-slate-100 py-8 relative -mt-6 rounded-2xl max-w-7xl mx-auto shadow-lg px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div className="space-y-1">
            <span className="block text-2xl sm:text-3xl font-extrabold text-indigo-600">1,200+</span>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Expert Courses</span>
          </div>
          <div className="space-y-1 border-l border-slate-150">
            <span className="block text-2xl sm:text-3xl font-extrabold text-indigo-600">45k+</span>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Learners</span>
          </div>
          <div className="space-y-1 border-l border-slate-150">
            <span className="block text-2xl sm:text-3xl font-extrabold text-indigo-600">350+</span>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Verified Mentors</span>
          </div>
          <div className="space-y-1 border-l border-slate-150">
            <span className="block text-2xl sm:text-3xl font-extrabold text-indigo-600">15k+</span>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Certificates Issued</span>
          </div>
        </div>
      </section>

      {/* 3. Category pills */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-20">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h2 className="text-3xl font-bold text-slate-900 tracking-tight">Explore Top Categories</h2>
          <p className="text-slate-500 mt-2">Discover popular fields of study and jumpstart your career pivot.</p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {categories.map((cat, idx) => (
            <div
              key={idx}
              onClick={() => navigate(`/courses?q=${encodeURIComponent(cat.query)}`)}
              className="bg-white p-5 rounded-2xl border border-slate-100 hover:border-indigo-200 shadow-sm text-center cursor-pointer card-hover"
            >
              <span className="text-3xl block mb-2">{cat.icon}</span>
              <h3 className="font-bold text-slate-800 text-sm">{cat.name}</h3>
              <span className="text-xs text-slate-450 text-slate-400 block mt-1">{cat.count}</span>
            </div>
          ))}
        </div>
      </section>

      {/* 4. Featured Courses */}
      <section className="bg-slate-50 py-16 lg:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row justify-between items-center mb-10 gap-4">
            <div className="text-center sm:text-left">
              <h2 className="text-3xl font-bold text-slate-900 tracking-tight">Featured Courses</h2>
              <p className="text-slate-500 mt-1">Begin your learning adventure with our handpicked student favorites.</p>
            </div>
            <Link 
              to="/courses"
              className="text-sm font-bold text-indigo-650 text-indigo-650 flex items-center gap-1 text-indigo-600 hover:text-indigo-850 hover:underline"
            >
              Explore all courses <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
            {loading ? (
              Array(3).fill(0).map((_, idx) => <SkeletonCard key={idx} />)
            ) : featuredCourses.length === 0 ? (
              <div className="col-span-full py-12 text-center text-slate-400 bg-white rounded-2xl border border-slate-100 p-8">
                <BookOpen className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                <p className="font-semibold text-slate-700">No courses published yet</p>
                <p className="text-xs mt-1">Check back later or register as a mentor to publish your own.</p>
              </div>
            ) : (
              featuredCourses.map((course) => (
  <CourseCard
  key={course.id}
  course={course}
  onView={(id) => {
    if (!user) {
      setShowAuthModal(true);
    } else {
      navigate(`/courses/${id}`);
    }
  }}
/>
))
            )}
          </div>
        </div>
      </section>

      {/* 5. Mentor Invitation Banner */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-20">
        <div className="bg-indigo-900 rounded-3xl p-8 sm:p-12 lg:p-16 text-white relative overflow-hidden shadow-xl">
          {/* Abstract circles */}
          <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-700/30 rounded-full translate-x-20 -translate-y-20"></div>

          <div className="max-w-xl relative z-10 space-y-6">
            <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight">Become a Mentor on EduFlex</h2>
            <p className="text-indigo-100 text-sm sm:text-base leading-relaxed">
              Share your knowledge, grow your audience, and earn passive income. Build a curriculum, upload video/PDF lectures, and answer students' Q&As inside our community.
            </p>
            <div>
              <Link
                to="/register"
                className="inline-flex items-center gap-2 bg-white text-indigo-900 font-bold px-6 py-3 rounded-xl hover:bg-indigo-50 transition-colors shadow-lg"
              >
                Apply as Instructor <ChevronRight className="w-4 h-4 text-indigo-900" />
              </Link>
            </div>
          </div>
        </div>
      </section>
      {showAuthModal && (
  <div
    className="fixed inset-0 z-50 flex items-center justify-center 
      bg-slate-900/60 backdrop-blur-sm px-4"
    onClick={() => setShowAuthModal(false)}
  >
    <div
      className="bg-white rounded-2xl shadow-2xl p-8 max-w-sm w-full 
        text-center space-y-4"
      onClick={(e) => e.stopPropagation()}
    >
      <div className="w-14 h-14 bg-indigo-100 rounded-full flex items-center 
        justify-center mx-auto text-2xl">
        🔐
      </div>
      <h3 className="text-lg font-bold text-slate-800">
        Sign in to view this course
      </h3>
      <p className="text-sm text-slate-500 leading-relaxed">
        Create a free account or sign in to access course details,
        enroll, and start learning.
      </p>
      <div className="flex gap-3 pt-2">
        <button
          onClick={() => navigate('/login')}
          className="flex-1 border border-indigo-600 text-indigo-600 
            font-bold text-sm px-4 py-2.5 rounded-xl hover:bg-indigo-50 
            transition-colors"
        >
          Sign In
        </button>
        <button
          onClick={() => navigate('/register')}
          className="flex-1 bg-indigo-600 text-white font-bold text-sm 
            px-4 py-2.5 rounded-xl hover:bg-indigo-700 transition-colors"
        >
          Register
        </button>
      </div>
      <button
        onClick={() => setShowAuthModal(false)}
        className="text-xs text-slate-400 hover:text-slate-600"
      >
        Maybe later
      </button>
    </div>
  </div>
)}

    </div>
  );
};

export default Landing;
