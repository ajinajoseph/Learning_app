import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../../api/axios';
import { 
  BookOpen, Star, Clock, Award, Shield, ChevronDown, ChevronUp, Lock,
  CheckCircle2, MessageSquare, AlertCircle, ShoppingBag, CreditCard,
  User, Check, X, ArrowLeft, Send, Sparkles, Megaphone, Pencil, Trash2, Plus
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

const getCourseThumbnail = (course) => {
  return course?.thumbnail_url || course?.image_url ||
    course?.thumbnail || '/default-course.png';
};

const TABS = ['Overview', 'Q&A Forum', 'Reviews', 'Students', 'Announcements'];

const QAReplyForm = ({ onSubmit, onCancel, placeholder = "Write a reply..." }) => {
  const [text, setText] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    setSubmitting(true);
    await onSubmit(text.trim());
    setText('');
    setSubmitting(false);
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 mt-2">
      <input
        autoFocus
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={placeholder}
        className="flex-1 bg-white border border-slate-200 px-3 py-2 
          rounded-xl text-xs focus:outline-none focus:ring-1 focus:ring-indigo-400"
      />
      <button
        type="submit"
        disabled={submitting || !text.trim()}
        className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 
          text-white text-xs font-bold px-3 py-1.5 rounded-xl"
      >
        {submitting ? '...' : 'Post'}
      </button>
      <button
        type="button"
        onClick={onCancel}
        className="text-slate-400 hover:text-slate-600 text-xs px-2 font-medium"
      >
        Cancel
      </button>
    </form>
  );
};

const MentorQANode = ({ msg, depth = 0, courseId, onRefresh }) => {
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [showReplies, setShowReplies] = useState(true);
  const [isDeleting, setIsDeleting] = useState(false);
  const userName = msg.user?.name || msg.user_name || 'Student';
  const replyCount = msg.replies?.length || 0;

  const handleAnswer = async (text) => {
    try {
      await api.post(`/api/qa/forum/course/${courseId}/post`, {
        message: text,
        parent_id: msg.id
      });
      setShowReplyForm(false);
      onRefresh();
    } catch (err) {
      console.error('Answer failed:', err);
    }
  };
  const handleDelete = async () => {
    if (!window.confirm('Delete this message? All replies will also be deleted.')) return;
    setIsDeleting(true);
    try {
      await api.delete(`/api/qa/forum/message/${msg.id}`);
      onRefresh();
    } catch (err) {
      console.error('Delete failed:', err);
      alert(err.response?.data?.message || 'Failed to delete');
    } finally {
      setIsDeleting(false);
    }
    };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    const now = new Date();
    const diff = Math.floor((now - d) / 1000);
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });
  };

  const avatarColor = depth === 0
    ? 'bg-indigo-100 text-indigo-700'
    : 'bg-emerald-100 text-emerald-700';

  return (
    <div className={`flex gap-3 ${depth > 0 ? 'mt-3 border-l-2 border-slate-100 pl-3' : ''}`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center 
        font-bold text-xs shrink-0 ${avatarColor}`}>
        {userName.charAt(0).toUpperCase()}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap mb-1">
          <span className="text-xs font-bold text-slate-800">{userName}</span>
          {depth > 0 && (
            <span className="text-[9px] bg-emerald-100 text-emerald-700 
              px-1.5 py-0.5 rounded font-semibold uppercase tracking-wide">
              Reply
            </span>
          )}
          <span className="text-[10px] text-slate-400">
            {formatDate(msg.created_at)}
          </span>
        </div>

        <p className="text-sm text-slate-700 leading-relaxed">{msg.message}</p>

        <div className="flex items-center gap-3 mt-1.5">
    {depth < 3 && (
      <button
        onClick={() => setShowReplyForm(!showReplyForm)}
        className="text-[11px] font-bold text-indigo-600 hover:text-indigo-700"
      >
        {depth === 0 ? '✏️ Answer' : '↩ Reply'}
      </button>
    )}
    {replyCount > 0 && (
      <button
        onClick={() => setShowReplies(!showReplies)}
        className="text-[11px] font-semibold text-slate-400 hover:text-slate-600"
      >
        {showReplies
          ? `▲ Hide ${replyCount}`
          : `▼ Show ${replyCount} replies`}
      </button>
    )}
    <button
      onClick={handleDelete}
      disabled={isDeleting}
      className="text-[11px] font-bold text-red-400 hover:text-red-600 
        transition-colors disabled:opacity-50"
    >
      {isDeleting ? '...' : '🗑 Delete'}
    </button>
    </div>
         

        {showReplyForm && (
          <QAReplyForm
            onSubmit={handleAnswer}
            onCancel={() => setShowReplyForm(false)}
            placeholder={depth === 0 ? "Write your answer..." : `Reply to ${userName}...`}
          />
        )}

        {showReplies && msg.replies && msg.replies.length > 0 && (
          <div className="mt-3 space-y-3">
            {msg.replies.map((reply) => (
              <MentorQANode
                key={reply.id}
                msg={reply}
                depth={depth + 1}
                courseId={courseId}
                onRefresh={onRefresh}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
const MentorCourseDetail = () => {
  const { courseId } = useParams();
  const navigate = useNavigate();

  // Common states
  const [course, setCourse] = useState(null);
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('Overview');

  // Tab 2: Q&A States
  const [questions, setQuestions] = useState([]);
  const [answerTexts, setAnswerTexts] = useState({}); // { questionId: text }

  // Tab 3: Reviews States
  const [reviews, setReviews] = useState([]);
  const [pendingReviews, setPendingReviews] = useState([]);
  const [ratingStats, setRatingStats] = useState(null);

  // Tab 4: Students States
  const [students, setStudents] = useState([]);

  // Announcements States
  const [announcements, setAnnouncements] = useState([]);
  const [announcementForm, setAnnouncementForm] = useState({ title: '', message: '' });
  const [editingAnnouncementId, setEditingAnnouncementId] = useState(null);
  const [isSubmittingAnnouncement, setIsSubmittingAnnouncement] = useState(false);

  // Fetch course & curriculum overview
  const fetchCourseData = async () => {
    try {
      const contentRes = await api.get(`/api/courses/${courseId}/content`);
      setCourse(contentRes.data.course);
      setModules(contentRes.data.modules || []);
    } catch (err) {
      console.error('Failed to fetch course detail overview:', err);
    }
  };

  const fetchQA = async () => {
  try {
    const res = await api.get(`/api/qa/forum/course/${courseId}/thread`);
    setQuestions(res.data.threads || []);
  } catch (err) {
    console.error('Failed to fetch Q&A:', err);
  }
  };


  const fetchReviews = async () => {
    try {
      const reviewsRes = await api.get(`/api/reviews/${courseId}`);
      const data = reviewsRes.data.reviews || reviewsRes.data || [];
      setReviews(data);
      if (reviewsRes.data.rating_stats) {
        setRatingStats(reviewsRes.data.rating_stats);
      }
    } catch (err) {
      console.error('Failed to fetch published reviews:', err);
    }
  };

  // Fetch Pending Reviews
  const fetchPendingReviews = async () => {
    try {
      const pendingRes = await api.get(`/api/reviews/pending/${courseId}`);
      setPendingReviews(pendingRes.data || []);
    } catch (err) {
      console.error('Failed to fetch pending reviews:', err);
    }
  };

  // Fetch Students progress roster
  const fetchStudents = async () => {
    try {
      const res = await api.get(`/api/courses/${courseId}/students`);
      setStudents(res.data || []);
    } catch (err) {
      console.error('Failed to fetch enrolled students progress roster:', err);
    }
  };

  // Fetch announcements
  const fetchAnnouncements = async () => {
    try {
      const res = await api.get(`/api/announcements/${courseId}`);
      setAnnouncements(res.data || []);
    } catch (err) {
      console.error('Failed to fetch announcements:', err);
    }
  };

  // Initial load
  useEffect(() => {
    setLoading(true);
    fetchCourseData().finally(() => setLoading(false));
  }, [courseId]);

  // Load active tab data
  useEffect(() => {
    if (activeTab === 'Q&A Forum') {
      fetchQA();
    } else if (activeTab === 'Reviews') {
      fetchReviews();
      fetchPendingReviews();
    } else if (activeTab === 'Students') {
      fetchStudents();
    } else if (activeTab === 'Announcements') {
      fetchAnnouncements();
    }
  }, [activeTab, courseId]);

  const handleAnswerQuestion = async (parentId, answerText) => {
  if (!answerText || !answerText.trim()) return;
  try {
    await api.post(`/api/qa/forum/course/${courseId}/post`, {
      message: answerText.trim(),
      parent_id: parentId
    });
    toast.success('Answer posted!');
    setAnswerTexts(prev => ({ ...prev, [parentId]: '' }));
    fetchQA();
  } catch (err) {
    console.error('Answer submission error:', err);
    toast.error('Failed to submit answer.');
  }
  };

  // Moderate review (Approve / Reject)
  const handleModerateReview = async (reviewId, action) => {
    try {
      await api.put(`/api/reviews/${reviewId}/moderate`, { action });
      toast.success(`Review successfully ${action}d`);
      fetchReviews();
      fetchPendingReviews();
    } catch (err) {
      console.error('Review moderation error:', err);
      toast.error('Failed to moderate review.');
    }
  };

  const handleAnnouncementSubmit = async (e) => {
    e.preventDefault();
    if (!announcementForm.title.trim() || !announcementForm.message.trim()) return;

    setIsSubmittingAnnouncement(true);
    try {
      const payload = {
        course_id: courseId,
        title: announcementForm.title.trim(),
        message: announcementForm.message.trim(),
      };

      if (editingAnnouncementId) {
        await api.put(`/api/announcements/${editingAnnouncementId}`, payload);
        toast.success('Announcement updated');
      } else {
        await api.post('/api/announcements', payload);
        toast.success('Announcement published');
      }

      setAnnouncementForm({ title: '', message: '' });
      setEditingAnnouncementId(null);
      fetchAnnouncements();
    } catch (err) {
      console.error('Announcement submission error:', err);
      toast.error(err.response?.data?.message || 'Failed to save announcement.');
    } finally {
      setIsSubmittingAnnouncement(false);
    }
  };

  const handleEditAnnouncement = (announcement) => {
    setEditingAnnouncementId(announcement.id);
    setAnnouncementForm({
      title: announcement.title,
      message: announcement.message,
    });
  };

  const handleDeleteAnnouncement = async (announcementId) => {
    if (!window.confirm('Delete this announcement?')) return;

    try {
      await api.delete(`/api/announcements/${announcementId}`);
      toast.success('Announcement deleted');
      if (editingAnnouncementId === announcementId) {
        setEditingAnnouncementId(null);
        setAnnouncementForm({ title: '', message: '' });
      }
      fetchAnnouncements();
    } catch (err) {
      console.error('Announcement deletion error:', err);
      toast.error('Failed to delete announcement.');
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
        <p className="text-slate-550 mt-1">The course details could not be loaded.</p>
        <Link to="/mentor/courses" className="mt-6 inline-block bg-indigo-600 text-white font-semibold px-6 py-2.5 rounded-full">
          Back to Courses
        </Link>
      </div>
    );
  }

  return (
    <div className="bg-[#F9FAFB] min-h-screen pb-12">
      
      {/* Course Detail Hero Banner */}
      <div className="bg-slate-900 text-white py-12 sm:py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3 mb-4">
            <Link to="/mentor/courses" className="p-2 bg-slate-800 rounded-xl hover:bg-slate-700 text-slate-300">
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <span className="text-xs text-indigo-400 font-bold tracking-widest uppercase">Mentor Workspace</span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
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
            </div>
          </div>
        </div>
      </div>

      {/* Main Tabs Panel */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-10">
        <div className="bg-white border border-slate-100 rounded-3xl shadow-sm overflow-hidden p-6 sm:p-8 space-y-8">
          
          {/* Tabs Navigation Header */}
          <div className="flex border-b border-slate-100 gap-6 text-sm font-semibold overflow-x-auto">
            {TABS.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`pb-4 capitalize border-b-2 transition-all whitespace-nowrap ${
                  activeTab === tab
                    ? 'border-indigo-600 text-indigo-600 font-bold'
                    : 'border-transparent text-slate-550 text-slate-500 hover:text-indigo-650'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Tab Body Contents */}
          <div>
            
            {/* Tab 1: Overview Tab */}
            {activeTab === 'Overview' && (
              <div className="space-y-6">
                <div className="flex justify-between items-center">
                  <h2 className="text-lg font-bold text-slate-900">Curriculum Breakdown</h2>
                  <Link 
                    to={`/mentor/courses/${courseId}/curriculum`}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs px-4 py-2 rounded-xl transition-all shadow-md"
                  >
                    Edit Curriculum
                  </Link>
                </div>

                {modules.length === 0 ? (
                  <div className="py-12 text-center text-slate-400 text-sm">
                    No curriculum modules established for this course.
                  </div>
                ) : (
                  <div className="space-y-4">
                    {modules.map((mod) => (
                      <div key={mod.id} className="border border-slate-100 rounded-xl overflow-hidden bg-slate-50/20">
                        <div className="bg-slate-50/60 p-4 border-b border-slate-100">
                          <h3 className="font-bold text-slate-800 text-sm sm:text-base">{mod.title}</h3>
                          <p className="text-xs text-slate-400 mt-0.5">{mod.description || 'No description provided'}</p>
                        </div>

                        <div className="divide-y divide-slate-100 bg-white">
                          {(mod.lessons || []).length === 0 ? (
                            <div className="p-4 text-xs text-slate-400 italic">No lessons created inside this module.</div>
                          ) : (
                            (mod.lessons || []).map((les) => (
                              <div key={les.id} className="p-4 flex justify-between items-center text-slate-700 text-sm">
                                <span className="flex items-center gap-2">
                                  <BookOpen className="w-4 h-4 text-indigo-500" />
                                  {les.title}
                                </span>
                                <span className="text-[10px] text-slate-400 font-bold uppercase shrink-0">
                                  {les.pdf_url ? 'PDF' : les.video_url ? 'Video' : 'Text'}
                                </span>
                              </div>
                            ))
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'Q&A Forum' && (
              <div className="space-y-6">
                <h2 className="text-lg font-bold text-slate-900">Student Q&A Threads</h2>

                {questions.length === 0 ? (
                  <div className="py-12 text-center text-slate-400 text-sm italic">
                    No Q&A threads have been started yet.
                  </div>
                ) : (
                  <div className="space-y-4">
                    {questions.map((msg) => (
                      <div key={msg.id}
                        className="bg-white border border-slate-100 rounded-2xl p-4 shadow-sm">
                        <MentorQANode
                          msg={msg}
                          depth={0}
                          courseId={courseId}
                          onRefresh={fetchQA}
                        />
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
            {/* Tab 3: Reviews Tab */}
            {activeTab === 'Reviews' && (
              <div className="space-y-8">
                
                {/* Moderation Pending Reviews Section */}
                {pendingReviews.length > 0 && (
                  <div className="space-y-4">
                    <h3 className="font-extrabold text-sm text-slate-400 uppercase tracking-widest flex items-center gap-1.5">
                      <Sparkles className="w-4 h-4 text-amber-500" /> Pending Moderation ({pendingReviews.length})
                    </h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {pendingReviews.map((rev) => (
                        <div key={rev.id} className="border border-amber-200 rounded-2xl bg-amber-50/10 p-5 space-y-3 flex flex-col justify-between">
                          <div className="space-y-2">
                            <div className="flex justify-between items-baseline flex-wrap gap-2 text-xs">
                              <span className="font-bold text-slate-700">{rev.student_name || 'Anonymous Student'}</span>
                              <div className="flex text-yellow-400 gap-0.5">
                                {Array(5).fill(0).map((_, i) => (
                                  <Star key={i} className={`w-3.5 h-3.5 ${i < rev.rating ? 'fill-amber-400 text-amber-400' : 'text-slate-200'}`} />
                                ))}
                              </div>
                            </div>
                            <p className="text-xs text-slate-650 italic">"{rev.comment || 'No comment provided'}"</p>
                          </div>
                          
                          <div className="flex justify-end gap-2 border-t border-slate-100/50 pt-3">
                            <button
                              onClick={() => handleModerateReview(rev.id, 'reject')}
                              className="bg-white border border-rose-200 text-rose-600 hover:bg-rose-50 px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1"
                            >
                              <X className="w-3.5 h-3.5" /> Reject
                            </button>
                            <button
                              onClick={() => handleModerateReview(rev.id, 'approve')}
                              className="bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1 shadow-sm"
                            >
                              <Check className="w-3.5 h-3.5" /> Approve
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Published Reviews Roster */}
                <div className="space-y-4">
                  <h3 className="font-extrabold text-sm text-slate-400 uppercase tracking-widest">Published Reviews ({reviews.length})</h3>

                  {reviews.length === 0 ? (
                    <div className="py-8 text-center text-slate-400 text-sm">
                      No published reviews exist for this course yet.
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {reviews.map((rev) => (
                        <div key={rev.id} className="border border-slate-100 rounded-2xl bg-white p-5 space-y-2">
                          <div className="flex justify-between items-baseline flex-wrap gap-2 text-xs">
                            <div className="flex items-center gap-2">
                              <span className="font-semibold text-slate-800 text-sm">{rev.student_name || 'Student'}</span>
                              <div className="flex gap-0.5">
                                {Array(5).fill(0).map((_, i) => (
                                  <Star key={i} className={`w-3.5 h-3.5 ${i < rev.rating ? 'fill-amber-400 text-amber-400' : 'text-slate-200'}`} />
                                ))}
                              </div>
                            </div>
                            <span className="text-[10px] text-slate-400">
                              {new Date(rev.created_at || Date.now()).toLocaleDateString()}
                            </span>
                          </div>
                          <p className="text-xs text-slate-655 italic leading-relaxed">"{rev.comment || 'No comment provided'}"</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

              </div>
            )}

            {/* Tab 4: Enrolled Students Tab */}
            {activeTab === 'Announcements' && (
              <div className="space-y-6">
                <div className="bg-white border border-slate-100 rounded-2xl p-5 shadow-sm space-y-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h2 className="text-lg font-bold text-slate-900">Announcements</h2>
                      <p className="text-sm text-slate-500 mt-1">Share course updates, reminders, and important news with your students.</p>
                    </div>
                  </div>

                  <form onSubmit={handleAnnouncementSubmit} className="space-y-3">
                    <input
                      type="text"
                      placeholder="Announcement title"
                      value={announcementForm.title}
                      onChange={(e) => setAnnouncementForm(prev => ({ ...prev, title: e.target.value }))}
                      className="w-full border border-slate-200 rounded-xl p-3 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none bg-slate-50"
                      required
                    />
                    <textarea
                      rows={4}
                      placeholder="Write your announcement here..."
                      value={announcementForm.message}
                      onChange={(e) => setAnnouncementForm(prev => ({ ...prev, message: e.target.value }))}
                      className="w-full border border-slate-200 rounded-xl p-3 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none bg-slate-50"
                      required
                    />
                    <div className="flex justify-end gap-2">
                      {editingAnnouncementId && (
                        <button
                          type="button"
                          onClick={() => {
                            setEditingAnnouncementId(null);
                            setAnnouncementForm({ title: '', message: '' });
                          }}
                          className="px-4 py-2 rounded-xl text-sm font-semibold text-slate-600 border border-slate-200 hover:bg-slate-50"
                        >
                          Cancel
                        </button>
                      )}
                      <button
                        type="submit"
                        disabled={isSubmittingAnnouncement}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs px-4 py-2 rounded-xl transition-all shadow-md inline-flex items-center gap-2"
                      >
                        {isSubmittingAnnouncement ? 'Saving...' : editingAnnouncementId ? 'Update Announcement' : 'Publish Announcement'}
                      </button>
                    </div>
                  </form>
                </div>

                <div className="space-y-4">
                  {announcements.length === 0 ? (
                    <div className="py-10 text-center text-slate-400 text-sm italic border border-dashed border-slate-200 rounded-2xl bg-white">
                      No announcements posted yet.
                    </div>
                  ) : (
                    announcements.map((announcement) => (
                      <div key={announcement.id} className="bg-white border border-slate-100 rounded-2xl p-5 shadow-sm">
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <h3 className="font-bold text-slate-900 text-sm">{announcement.title}</h3>
                            <p className="text-[11px] text-slate-400 mt-1">{new Date(announcement.created_at).toLocaleString()}</p>
                          </div>
                          <div className="flex gap-2">
                            <button
                              type="button"
                              onClick={() => handleEditAnnouncement(announcement)}
                              className="p-2 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50"
                            >
                              <Pencil className="w-4 h-4" />
                            </button>
                            <button
                              type="button"
                              onClick={() => handleDeleteAnnouncement(announcement.id)}
                              className="p-2 rounded-lg border border-rose-200 text-rose-600 hover:bg-rose-50"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                        <p className="mt-3 text-sm text-slate-600 leading-relaxed whitespace-pre-wrap">{announcement.message}</p>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}

            {activeTab === 'Students' && (
              <div className="space-y-6">
                <h2 className="text-lg font-bold text-slate-900">Enrolled Student Progress Roster</h2>

                {students.length === 0 ? (
                  <div className="py-12 text-center text-slate-400 text-sm italic">
                    No students have enrolled in this course yet.
                  </div>
                ) : (
                  <div className="overflow-x-auto border border-slate-100 rounded-2xl">
                    <table className="w-full text-left border-collapse text-xs sm:text-sm">
                      <thead>
                        <tr className="bg-slate-50 border-b border-slate-100 text-slate-500 font-bold uppercase tracking-wider text-[10px]">
                          <th className="py-4 px-5">Student Name</th>
                          <th className="py-4 px-5">Email Address</th>
                          <th className="py-4 px-5">Enrollment Date</th>
                          <th className="py-4 px-5 w-48 sm:w-64">Course Progress</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 text-slate-700">
                        {students.map((student) => (
                          <tr key={student.id} className="hover:bg-slate-50/50 transition-colors">
                            <td className="py-4 px-5 font-semibold text-slate-800 flex items-center gap-2">
                              <div className="w-7 h-7 bg-indigo-50 text-indigo-650 rounded-full flex items-center justify-center font-bold text-xs uppercase">
                                {student.name ? student.name[0] : 'S'}
                              </div>
                              {student.name}
                            </td>
                            <td className="py-4 px-5 text-slate-500">{student.email}</td>
                            <td className="py-4 px-5 text-slate-400">
                              {student.enrolled_at ? new Date(student.enrolled_at).toLocaleDateString() : 'N/A'}
                            </td>
                            <td className="py-4 px-5">
                              <div className="space-y-1.5">
                                <div className="flex justify-between items-center text-[10px] font-bold text-indigo-600">
                                  <span>{Math.round(student.progress_percentage)}% Completed</span>
                                </div>
                                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                                  <div 
                                    className="bg-indigo-600 h-full rounded-full transition-all duration-300"
                                    style={{ width: `${student.progress_percentage}%` }}
                                  />
                                </div>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

          </div>

        </div>
      </div>
      
    </div>
  );
};

export default MentorCourseDetail;
