import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import api from '../api/axios';
import { getCourseThumbnail } from '../components/CourseCard';
import {
  BookOpen, Star, Clock, Globe, Award, Shield, ChevronDown, ChevronUp,
  Lock, CheckCircle2, MessageSquare, AlertCircle, ShoppingBag, CreditCard
} from 'lucide-react';

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

const CourseDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, user } = useSelector((state) => state.auth);

  // States
  const [course, setCourse] = useState(null);
  const [modules, setModules] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [ratingStats, setRatingStats] = useState(null);
  const [isEnrolled, setIsEnrolled] = useState(false);
  const [loading, setLoading] = useState(true);
  const [purchaseLoading, setPurchaseLoading] = useState(false);

  // Review form states
  const [newRating, setNewRating] = useState(5);
  const [newComment, setNewComment] = useState('');
  const [reviewError, setReviewError] = useState('');
  const [reviewSuccess, setReviewSuccess] = useState('');

  // Active Tab
  const [activeTab, setActiveTab] = useState('overview'); // 'overview', 'curriculum', 'reviews'

  // Accordion state
  const [expandedModules, setExpandedModules] = useState({});

  const fetchReviews = async () => {
    try {
      const res = await api.get(`/api/reviews/${id}`);
      const data = res.data.reviews || res.data || [];
      setReviews(data);
      if (res.data.rating_stats) {
        setRatingStats(res.data.rating_stats);
      }
    } catch (err) {
      console.error('Failed to fetch reviews:', err);
    }
  };

  useEffect(() => {
    const fetchCourseData = async () => {
      setLoading(true);
      try {
        // 1. Fetch Course details
        const courseRes = await api.get(`/api/courses/${id}`);
        setCourse(courseRes.data);

        // 2. Check enrollment if authenticated student
        if (isAuthenticated && user?.role === 'student') {
          const myCoursesRes = await api.get('/api/enrollments/my-courses');
          const enrolled = myCoursesRes.data.some((item) => item.course_id === id);
          setIsEnrolled(enrolled);

          if (enrolled) {
            // Fetch curriculum with lessons if enrolled
            const contentRes = await api.get(`/api/courses/${id}/content`);
            setModules(contentRes.data.modules || []);
          } else {
            // Fetch just modules for public overview
            const modulesRes = await api.get(`/api/modules/course/${id}`);
            setModules(modulesRes.data);
          }
        } else {
          // Unauthenticated or Mentor/Admin: fetch modules
          const modulesRes = await api.get(`/api/modules/course/${id}`);
          setModules(modulesRes.data);
        }

        // 3. Fetch reviews
        await fetchReviews();

      } catch (err) {
        console.error('Failed to load course details:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchCourseData();
  }, [id, isAuthenticated, user]);

  const toggleModule = (moduleId) => {
    setExpandedModules((prev) => ({
      ...prev,
      [moduleId]: !prev[moduleId],
    }));
  };

  const handleEnrollFree = async () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    setPurchaseLoading(true);
    try {
      await api.post(`/api/enrollments/${id}`);
      setIsEnrolled(true);
      navigate(`/learn/${id}`);
    } catch (err) {
      alert(err.response?.data?.message || 'Enrollment failed');
    } finally {
      setPurchaseLoading(false);
    }
  };

  const handleStripeCheckout = async () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    setPurchaseLoading(true);
    try {
      const res = await api.post(`/api/payments/stripe/create-checkout/${id}`);
      // Redirect to Stripe checkout
      if (res.data.checkout_url) {
        window.location.href = res.data.checkout_url;
      }
    } catch (err) {
      alert(err.response?.data?.message || 'Stripe Checkout failed');
    } finally {
      setPurchaseLoading(false);
    }
  };

  const handlePaypalCheckout = async () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    setPurchaseLoading(true);
    try {
      const res = await api.post(`/api/payments/paypal/create-order/${id}`);
      // Redirect to PayPal approve url
      if (res.data.approve_url) {
        window.location.href = res.data.approve_url;
      }
    } catch (err) {
      alert(err.response?.data?.message || 'PayPal Checkout failed');
    } finally {
      setPurchaseLoading(false);
    }
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    setReviewError('');
    setReviewSuccess('');

    try {
      await api.post(`/api/reviews/${id}`, {
        rating: newRating,
        comment: newComment.trim(),
      });
      toast.success('Review submitted!');
      setReviewSuccess('Your review has been submitted successfully!');
      setNewComment('');
      setNewRating(5);
      await fetchReviews();
    } catch (err) {
      const msg = err.response?.data?.message || 'Failed to submit review';
      setReviewError(msg);
      toast.error(msg);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-slate-800">Course Not Found</h2>
        <p className="text-slate-550 mt-1">The course you are looking for does not exist or has been removed.</p>
        <Link to="/courses" className="mt-6 inline-block bg-indigo-600 text-white font-semibold px-6 py-2.5 rounded-full">
          Back to Courses
        </Link>
      </div>
    );
  }

  const thumbnail = getCourseThumbnail(course.title);

  return (
    <div className="bg-[#F9FAFB] min-h-screen">

      {/* Hero Banner */}
      <div className="bg-slate-900 text-white py-12 sm:py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

            {/* Left Course details */}
            <div className="lg:col-span-8 space-y-4">
              <span className="inline-block bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-xs font-bold px-3 py-1 rounded uppercase tracking-wider">
                {course.level}
              </span>
              <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
                {course.title}
              </h1>
              <p className="text-slate-300 text-sm sm:text-base leading-relaxed line-clamp-3">
                {course.description}
              </p>

              <div className="flex flex-wrap gap-4 sm:gap-6 pt-2 text-xs sm:text-sm text-slate-305 text-slate-400">
                <span className="flex items-center gap-1.5">
                  <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
                  <strong className="text-white">4.7</strong> (184 ratings)
                </span>
                <span className="flex items-center gap-1.5">
                  <Clock className="w-4 h-4 text-slate-400" /> {course.duration_hours || '12'} Hours
                </span>
                <span className="flex items-center gap-1.5 capitalize">
                  <Globe className="w-4 h-4 text-slate-400" /> {course.language}
                </span>
              </div>
            </div>

          </div>
        </div>
      </div>

      {/* Main Grid content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start relative">

          {/* Left Area Tabs */}
          <div className="lg:col-span-8 space-y-8 bg-white border border-slate-100 p-6 sm:p-8 rounded-2xl shadow-sm">

            {/* Tabs Header */}
            <div className="flex border-b border-slate-100 gap-6 text-sm font-semibold">
              {['overview', 'curriculum', 'reviews'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`pb-4 capitalize border-b-2 transition-all ${activeTab === tab
                    ? 'border-indigo-600 text-indigo-600'
                    : 'border-transparent text-slate-550 text-slate-500 hover:text-indigo-600'
                    }`}
                >
                  {tab}
                </button>
              ))}
            </div>

            {/* Tab content */}
            <div>
              {/* Tab 1: Overview */}
              {activeTab === 'overview' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-lg font-bold text-slate-900 mb-3">Course Description</h2>
                    <p className="text-slate-650 text-sm leading-relaxed whitespace-pre-wrap text-slate-600">
                      {course.description}
                    </p>
                  </div>

                  <div className="bg-slate-50 rounded-2xl p-5 border border-slate-100">
                    <h3 className="font-bold text-slate-800 text-sm mb-3">What you'll learn in this course</h3>
                    <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs sm:text-sm text-slate-650 text-slate-600">
                      <li className="flex items-start gap-2">
                        <CheckCircle2 className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
                        <span>Master core and advanced industry methodologies.</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <CheckCircle2 className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
                        <span>Build responsive real-world portfolio projects.</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <CheckCircle2 className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
                        <span>Practice with interactive quiz questions and tests.</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <CheckCircle2 className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
                        <span>Earn a shareable, verifiable certificate of completion.</span>
                      </li>
                    </ul>
                  </div>
                </div>
              )}

              {/* Tab 2: Curriculum Accordion */}
              {activeTab === 'curriculum' && (
                <div className="space-y-4">
                  <h2 className="text-lg font-bold text-slate-900 mb-2">Curriculum Breakdown</h2>
                  {modules.length === 0 ? (
                    <div className="py-8 text-center text-slate-400 text-sm">
                      No modules have been created for this course yet.
                    </div>
                  ) : (
                    modules.map((mod) => {
                      const isOpen = !!expandedModules[mod.id];
                      return (
                        <div key={mod.id} className="border border-slate-100 rounded-xl overflow-hidden shadow-sm bg-white">

                          {/* Module Accordion Header */}
                          <div
                            onClick={() => toggleModule(mod.id)}
                            className="bg-slate-50/70 p-4 flex justify-between items-center cursor-pointer hover:bg-slate-50 transition-colors"
                          >
                            <div>
                              <h3 className="font-bold text-slate-800 text-sm sm:text-base">{mod.title}</h3>
                              <p className="text-xs text-slate-450 text-slate-400 mt-0.5">{mod.description || 'No description provided'}</p>
                            </div>
                            {isOpen ? <ChevronUp className="w-5 h-5 text-slate-500" /> : <ChevronDown className="w-5 h-5 text-slate-500" />}
                          </div>

                          {/* Module Accordion Lessons List */}
                          {isOpen && (
                            <div className="border-t border-slate-50 divide-y divide-slate-50">
                              {isEnrolled ? (
                                (mod.lessons || []).length === 0 ? (
                                  <div className="p-4 text-xs text-slate-400 italic">No lessons in this module.</div>
                                ) : (
                                  (mod.lessons || []).map((les) => (
                                    <div key={les.id} className="p-4 flex justify-between items-center text-slate-700 text-sm hover:bg-indigo-50/10 transition-colors">
                                      <span className="flex items-center gap-2">
                                        <BookOpen className="w-4 h-4 text-indigo-500" />
                                        {les.title}
                                      </span>
                                      <span className="text-xs text-slate-400 uppercase font-medium">{les.pdf_url ? 'PDF Document' : 'Video Lecture'}</span>
                                    </div>
                                  ))
                                )
                              ) : (
                                <div className="p-4 bg-slate-50/30 flex items-center gap-2.5 justify-center text-xs text-slate-450 text-slate-400">
                                  <Lock className="w-4 h-4 text-slate-400" />
                                  <span>Lessons are locked. Enroll in this course to inspect lectures.</span>
                                </div>
                              )}
                            </div>
                          )}

                        </div>
                      );
                    })
                  )}
                </div>
              )}

              {/* Tab 3: Reviews */}
              {activeTab === 'reviews' && (
                <div className="space-y-8">
                  <h2 className="text-lg font-bold text-slate-900 mb-2">Student Reviews</h2>

                  {/* Stats Summary */}
                  {ratingStats && (
                    <div className="bg-slate-50 rounded-2xl p-5 border border-slate-100 flex flex-col sm:flex-row items-center gap-6">
                      <div className="text-center sm:text-left space-y-1">
                        <span className="block text-4xl font-extrabold text-slate-800">4.7</span>
                        <div className="flex gap-0.5 justify-center sm:justify-start">
                          {Array(5).fill(0).map((_, i) => (
                            <Star key={i} className="w-4 h-4 fill-amber-400 text-amber-400" />
                          ))}
                        </div>
                        <span className="text-xs text-slate-400 font-medium block">Course Rating Stats</span>
                      </div>
                      <div className="flex-1 w-full text-slate-600 text-xs space-y-1.5">
                        <div className="flex items-center gap-2">
                          <span className="w-12">5 Star</span>
                          <div className="flex-1 bg-slate-200 h-2 rounded overflow-hidden"><div className="bg-amber-400 h-full rounded w-[80%]"></div></div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="w-12">4 Star</span>
                          <div className="flex-1 bg-slate-200 h-2 rounded overflow-hidden"><div className="bg-amber-400 h-full rounded w-[15%]"></div></div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="w-12">3 Star</span>
                          <div className="flex-1 bg-slate-200 h-2 rounded overflow-hidden"><div className="bg-amber-400 h-full rounded w-[5%]"></div></div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Reviews List */}
                  <div className="space-y-4">
                    {reviews.length === 0 ? (
                      <div className="py-8 text-center text-slate-400 text-sm">
                        No reviews have been published for this course yet.
                      </div>
                    ) : (
                      reviews.map((rev) => (
                        <div key={rev.id} className="p-4 border border-slate-100 rounded-xl bg-white space-y-2.5">
                          <div className="flex justify-between items-baseline flex-wrap gap-2">
                            <div className="flex items-center gap-2">
                              <span className="font-semibold text-slate-800 text-sm">
                                {rev.student_name || rev.user?.name || 'Student'}
                              </span>
                              <div className="flex gap-0.5">
                                {Array(5).fill(0).map((_, i) => (
                                  <Star
                                    key={i}
                                    className={`w-3.5 h-3.5 ${i < rev.rating ? 'fill-amber-400 text-amber-400' : 'text-slate-200'}`}
                                  />
                                ))}
                              </div>
                            </div>
                            <span className="text-[10px] text-slate-400">{new Date(rev.created_at || Date.now()).toLocaleDateString()}</span>
                          </div>
                          <p className="text-sm text-slate-700 leading-normal italic">
                            "{rev.comment || 'No comment provided'}"
                          </p>
                        </div>
                      ))
                    )}
                  </div>

                  {/* Add Review Form (Only for Enrolled Students) */}
                  {isEnrolled && user?.role === 'student' && (
                    <div className="pt-6 border-t border-slate-100 space-y-4">
                      <h3 className="font-bold text-slate-800 text-base">Write a Course Review</h3>

                      {reviewSuccess && (
                        <div className="bg-emerald-50 text-emerald-700 border border-emerald-100 rounded-xl p-3.5 text-xs">
                          {reviewSuccess}
                        </div>
                      )}

                      {reviewError && (
                        <div className="bg-red-550 bg-red-550/10 text-red-700 border border-red-100 rounded-xl p-3.5 text-xs">
                          {reviewError}
                        </div>
                      )}

                      <form onSubmit={handleReviewSubmit} className="space-y-4">
                        <div>
                          <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Rating</label>
                          <select
                            value={newRating}
                            onChange={(e) => setNewRating(Number(e.target.value))}
                            className="bg-slate-50 border border-slate-200 px-3 py-2 rounded-xl text-sm"
                          >
                            <option value={5}>5 Stars - Excellent</option>
                            <option value={4}>4 Stars - Good</option>
                            <option value={3}>3 Stars - Average</option>
                            <option value={2}>2 Stars - Poor</option>
                            <option value={1}>1 Star - Horrible</option>
                          </select>
                        </div>

                        <div>
                          <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Review Comment</label>
                          <textarea
                            rows={3}
                            required
                            placeholder="Share your learning experience..."
                            value={newComment}
                            onChange={(e) => setNewComment(e.target.value)}
                            className="w-full bg-slate-50 border border-slate-200 p-3 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                          ></textarea>
                        </div>

                        <button
                          type="submit"
                          className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs px-5 py-2.5 rounded-full transition-all hover:shadow-md"
                        >
                          Submit Review
                        </button>
                      </form>
                    </div>
                  )}

                </div>
              )}
            </div>

          </div>

          {/* Sticky Right Buy Drawer */}
          <div className="lg:col-span-4 bg-white border border-slate-100 rounded-2xl shadow-lg overflow-hidden lg:sticky lg:top-24 space-y-6 pb-6">
            <div className="aspect-video bg-slate-150 relative">
              <img
                src={thumbnail}
                alt={course.title}
                className="w-full h-full object-cover"
              />
            </div>

            <div className="px-6 space-y-6">

              {/* Pricing banner */}
              <div className="space-y-1">
                <span className="text-xs text-slate-400 font-bold uppercase tracking-widest block">Price</span>
                <span className="text-3xl font-black text-slate-800 block">
                  {course.price === 0 ? <span className="text-emerald-600">Free</span> : `$${course.price.toFixed(2)}`}
                </span>
              </div>

              {/* Action Button */}
              {isEnrolled ? (
                <Link
                  to={`/learn/${course.id}`}
                  className="w-full inline-block bg-indigo-650 bg-indigo-600 hover:bg-indigo-750 text-white text-center font-bold text-sm py-3 rounded-xl transition-all shadow-md shadow-indigo-100 hover:shadow-lg"
                >
                  Go to Learning Workspace
                </Link>
              ) : course.price === 0 ? (
                <button
                  onClick={handleEnrollFree}
                  disabled={purchaseLoading}
                  className="w-full bg-indigo-600 hover:bg-indigo-700 text-white text-center font-bold text-sm py-3 rounded-xl transition-all shadow-md"
                >
                  {purchaseLoading ? 'Enrolling...' : 'Enroll Now (Free)'}
                </button>
              ) : (
                <div className="space-y-3">
                  <button
                    onClick={handleStripeCheckout}
                    disabled={purchaseLoading}
                    className="w-full bg-indigo-600 hover:bg-indigo-700 text-white text-center font-bold text-sm py-3 rounded-xl transition-all shadow-md shadow-indigo-150 flex items-center justify-center gap-2 hover:shadow-lg"
                  >
                    <CreditCard className="w-4 h-4" />
                    {purchaseLoading ? 'Redirecting...' : 'Buy with Stripe'}
                  </button>

                  <button
                    onClick={handlePaypalCheckout}
                    disabled={purchaseLoading}
                    className="w-full bg-amber-500 hover:bg-amber-600 text-slate-900 text-center font-bold text-sm py-3 rounded-xl transition-all shadow-md flex items-center justify-center gap-2"
                  >
                    <ShoppingBag className="w-4 h-4" />
                    {purchaseLoading ? 'Redirecting...' : 'Buy with PayPal'}
                  </button>
                </div>
              )}

              {/* Specs checklist */}
              <div className="space-y-3.5 border-t border-slate-100 pt-6">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest">This course includes:</h4>
                <ul className="text-xs text-slate-650 text-slate-600 space-y-2.5 font-medium">
                  <li className="flex items-center gap-2"><Clock className="w-4.5 h-4.5 text-slate-400" /> {course.duration_hours || '12'} hours duration</li>
                  <li className="flex items-center gap-2"><Globe className="w-4.5 h-4.5 text-slate-400 font-bold" /> Full lifetime accessibility</li>
                  <li className="flex items-center gap-2"><Award className="w-4.5 h-4.5 text-slate-400" /> Verifiable completion certificate</li>
                </ul>
              </div>

            </div>
          </div>

        </div>
      </div>

    </div>
  );
};

export default CourseDetail;
