import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api/axios';
import CourseCard from '../components/CourseCard';
import SkeletonCard from '../components/SkeletonCard';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { Search, SlidersHorizontal, ArrowUpDown, ChevronLeft, ChevronRight, X, AlertCircle } from 'lucide-react';

const CourseList = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [courses, setCourses] = useState([]);
  const [filteredCourses, setFilteredCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchVal, setSearchVal] = useState(searchParams.get('q') || '');
  const [selectedLevel, setSelectedLevel] = useState(searchParams.get('level') || 'all');
  const [selectedPrice, setSelectedPrice] = useState('all'); // 'all', 'free', 'paid'
  const [selectedLanguage, setSelectedLanguage] = useState('all');
  const [sortBy, setSortBy] = useState('popular'); // 'popular', 'price-low', 'price-high'
  const [showMobileFilters, setShowMobileFilters] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const navigate = useNavigate();
const { user } = useSelector((state) => state.auth);
const [showAuthModal, setShowAuthModal] = useState(false);
  const perPage = 6;
  useEffect(() => {
    const q = searchParams.get('q');
    if (q) setSearchVal(q);
  }, [searchParams]);
  useEffect(() => {
  const fetchCourses = async () => {
    setLoading(true);
    try {
      const res =  await api.get('/api/courses');
      setCourses(res.data);
    } catch (err) {
      console.error('Failed to load courses:', err);
    } finally {
      setLoading(false);
    }
  };
  fetchCourses();
  }, []);

  // Filter and Sort Courses
  useEffect(() => {
    let result = [...courses];

    // Search query filter
    if (searchVal.trim()) {
      const q = searchVal.toLowerCase();
      result = result.filter(
        (c) =>
          c.title?.toLowerCase().includes(q) ||
          c.description?.toLowerCase().includes(q) ||
          (c.tags || []).some((t) => t.toLowerCase().includes(q))
      );
    }

    // Level filter
    if (selectedLevel !== 'all') {
      result = result.filter((c) => c.level?.toLowerCase() === selectedLevel.toLowerCase());
    }

    // Price filter
    if (selectedPrice === 'free') {
      result = result.filter((c) => c.price === 0);
    } else if (selectedPrice === 'paid') {
      result = result.filter((c) => c.price > 0);
    }

    // Language filter
    if (selectedLanguage !== 'all') {
      result = result.filter((c) => c.language?.toLowerCase() === selectedLanguage.toLowerCase());
    }

    // Sorting logic
    if (sortBy === 'price-low') {
      result.sort((a, b) => a.price - b.price);
    } else if (sortBy === 'price-high') {
      result.sort((a, b) => b.price - a.price);
    } else {
      // popular / default sorting
      result.sort((a, b) => b.id.localeCompare(a.id));
    }

    setFilteredCourses(result);
    setCurrentPage(1); // Reset to page 1 on filter change
  }, [courses, searchVal, selectedLevel, selectedPrice, selectedLanguage, sortBy]);

  // Pagination calculation
  const totalItems = filteredCourses.length;
  const totalPages = Math.ceil(totalItems / perPage);
  const indexOfLastItem = currentPage * perPage;
  const indexOfFirstItem = indexOfLastItem - perPage;
  const currentItems = filteredCourses.slice(indexOfFirstItem, indexOfLastItem);

  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const clearFilters = () => {
    setSearchVal('');
    setSelectedLevel('all');
    setSelectedPrice('all');
    setSelectedLanguage('all');
    setSortBy('popular');
    setSearchParams({});
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      
      {/* Header Panel */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Explore Courses</h1>
          <p className="text-slate-500 mt-1">Found {filteredCourses.length} results matching your interests</p>
        </div>
        
        {/* Sort & Search Top panel */}
        <div className="flex w-full md:w-auto gap-3 items-center">
          <div className="relative flex-1 md:w-64">
            <input
              type="text"
              placeholder="Search in explore..."
              value={searchVal}
              onChange={(e) => setSearchVal(e.target.value)}
              className="w-full bg-white border border-slate-200 text-slate-700 placeholder-slate-400 pl-9 pr-4 py-2 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <Search className="absolute left-3 top-3 w-4 h-4 text-slate-400" />
          </div>

          <div className="flex items-center gap-1 bg-white border border-slate-200 px-3 py-2 rounded-xl text-sm shrink-0">
            <ArrowUpDown className="w-4 h-4 text-slate-400 shrink-0" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-transparent border-none text-slate-700 focus:outline-none font-semibold text-xs pr-1"
            >
              <option value="popular">Popular</option>
              <option value="price-low">Price: Low to High</option>
              <option value="price-high">Price: High to Low</option>
            </select>
          </div>

          <button
            onClick={() => setShowMobileFilters(true)}
            className="md:hidden p-2 border border-slate-200 bg-white rounded-xl text-slate-700"
          >
            <SlidersHorizontal className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="flex gap-8">
        
        {/* Filter Sidebar (Desktop) */}
        <aside className="hidden md:block w-64 shrink-0 bg-white border border-slate-100 rounded-2xl p-6 shadow-sm h-fit space-y-6">
          <div className="flex justify-between items-center pb-4 border-b border-slate-100">
            <h3 className="font-bold text-slate-800 text-sm flex items-center gap-1.5">
              <SlidersHorizontal className="w-4 h-4 text-indigo-600" /> Filters
            </h3>
            <button onClick={clearFilters} className="text-xs font-semibold text-indigo-600 hover:text-indigo-800">
              Clear All
            </button>
          </div>

          {/* Price Category */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-450 uppercase tracking-wider text-slate-400">Price Tier</h4>
            <div className="flex flex-col gap-2">
              {['all', 'free', 'paid'].map((price) => (
                <label key={price} className="flex items-center gap-2 text-sm text-slate-650 cursor-pointer font-medium text-slate-650 text-slate-600 capitalize">
                  <input
                    type="radio"
                    checked={selectedPrice === price}
                    onChange={() => setSelectedPrice(price)}
                    className="accent-indigo-600"
                  />
                  {price}
                </label>
              ))}
            </div>
          </div>

          {/* Level Selection */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-450 uppercase tracking-wider text-slate-400">Level</h4>
            <div className="flex flex-col gap-2">
              {['all', 'beginner', 'intermediate', 'advanced'].map((lvl) => (
                <label key={lvl} className="flex items-center gap-2 text-sm text-slate-650 cursor-pointer font-medium text-slate-650 text-slate-600 capitalize">
                  <input
                    type="radio"
                    checked={selectedLevel === lvl}
                    onChange={() => setSelectedLevel(lvl)}
                    className="accent-indigo-600"
                  />
                  {lvl}
                </label>
              ))}
            </div>
          </div>

          {/* Language Selection */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-450 uppercase tracking-wider text-slate-400">Language</h4>
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 px-3 py-2 rounded-xl text-xs font-semibold text-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="all">All Languages</option>
              <option value="english">English</option>
              <option value="spanish">Spanish</option>
              <option value="french">French</option>
              <option value="german">German</option>
            </select>
          </div>
        </aside>

        {/* Content Area */}
        <div className="flex-1 space-y-8">
          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {Array(perPage).fill(0).map((_, idx) => <SkeletonCard key={idx} />)}
            </div>
          ) : currentItems.length === 0 ? (
            <div className="text-center py-20 bg-white rounded-3xl border border-slate-100 p-8 shadow-sm">
              <AlertCircle className="w-12 h-12 text-slate-300 mx-auto mb-4" />
              <h3 className="text-lg font-bold text-slate-800">No courses match filters</h3>
              <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                Try widening your search terms, modifying your filters, or clearing them to explore the catalog.
              </p>
              <button
                onClick={clearFilters}
                className="mt-5 bg-indigo-650 bg-indigo-600 text-white font-bold text-xs px-4 py-2.5 rounded-full hover:bg-indigo-750 transition-all hover:shadow-md"
              >
                Reset All Filters
              </button>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {currentItems.map((course) => (
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
))}
              </div>

              {/* Pagination Controls */}
              {totalPages > 1 && (
                <div className="flex justify-center items-center gap-2 pt-6">
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="p-2 border border-slate-200 rounded-xl bg-white text-slate-600 hover:text-indigo-600 disabled:opacity-40 transition-colors"
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </button>
                  
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                    <button
                      key={page}
                      onClick={() => handlePageChange(page)}
                      className={`w-10 h-10 font-bold rounded-xl border text-sm transition-all ${
                        currentPage === page
                          ? 'bg-indigo-600 text-white border-indigo-600 shadow-md shadow-indigo-100'
                          : 'bg-white text-slate-600 border-slate-200 hover:border-slate-350 hover:text-indigo-600'
                      }`}
                    >
                      {page}
                    </button>
                  ))}

                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    className="p-2 border border-slate-200 rounded-xl bg-white text-slate-600 hover:text-indigo-600 disabled:opacity-40 transition-colors"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
              )}
            </>
          )}
        </div>

      </div>

      {/* Mobile Filters Drawer */}
      {showMobileFilters && (
        <div className="fixed inset-0 z-50 overflow-hidden md:hidden flex justify-end">
          <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" onClick={() => setShowMobileFilters(false)}></div>
          <div className="relative w-80 bg-white h-full shadow-2xl p-6 flex flex-col justify-between animate-slide-left overflow-y-auto">
            <div className="space-y-6">
              <div className="flex justify-between items-center pb-4 border-b border-slate-100">
                <h3 className="font-bold text-slate-800 text-base">Filters</h3>
                <button onClick={() => setShowMobileFilters(false)}>
                  <X className="w-5 h-5 text-slate-500" />
                </button>
              </div>

              {/* Price Category */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Price Tier</h4>
                <div className="flex flex-col gap-2.5">
                  {['all', 'free', 'paid'].map((price) => (
                    <label key={price} className="flex items-center gap-2.5 text-sm text-slate-650 cursor-pointer font-medium text-slate-700 capitalize">
                      <input
                        type="radio"
                        checked={selectedPrice === price}
                        onChange={() => setSelectedPrice(price)}
                        className="accent-indigo-600"
                      />
                      {price}
                    </label>
                  ))}
                </div>
              </div>

              {/* Level Selection */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Level</h4>
                <div className="flex flex-col gap-2.5">
                  {['all', 'beginner', 'intermediate', 'advanced'].map((lvl) => (
                    <label key={lvl} className="flex items-center gap-2.5 text-sm text-slate-650 cursor-pointer font-medium text-slate-700 capitalize">
                      <input
                        type="radio"
                        checked={selectedLevel === lvl}
                        onChange={() => setSelectedLevel(lvl)}
                        className="accent-indigo-600"
                      />
                      {lvl}
                    </label>
                  ))}
                </div>
              </div>

              {/* Language Selection */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Language</h4>
                <select
                  value={selectedLanguage}
                  onChange={(e) => setSelectedLanguage(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 px-3 py-2.5 rounded-xl text-sm text-slate-700"
                >
                  <option value="all">All Languages</option>
                  <option value="english">English</option>
                  <option value="spanish">Spanish</option>
                  <option value="french">French</option>
                  <option value="german">German</option>
                </select>
              </div>
            </div>

            <div className="pt-6 border-t border-slate-100 flex gap-4 mt-6">
              <button
                onClick={() => {
                  clearFilters();
                  setShowMobileFilters(false);
                }}
                className="flex-1 py-3 border border-slate-200 font-bold text-xs rounded-xl text-slate-700 text-center"
              >
                Clear
              </button>
              <button
                onClick={() => setShowMobileFilters(false)}
                className="flex-1 py-3 bg-indigo-650 bg-indigo-600 font-bold text-xs rounded-xl text-white text-center hover:bg-indigo-700"
              >
                Apply Filters
              </button>
            </div>

          </div>
        </div>
      )}
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

export default CourseList;
