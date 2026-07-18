import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { io } from 'socket.io-client';
import api from '../../api/axios';
import {
  BookOpen, ChevronLeft, ChevronRight, CheckCircle, Circle, Video, FileText,
  HelpCircle, MessageSquare, Megaphone, Send, Award, Download, X, AlertCircle
} from 'lucide-react';

const getCourseThumbnail = (course) => {
  return course?.thumbnail_url || course?.image_url ||
    course?.thumbnail || '/default-course.png';
};

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
// ── Put this ABOVE the LearnPage component ──────────────────────

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
          rounded-xl text-xs focus:outline-none focus:ring-1 
          focus:ring-indigo-400"
      />
      <button
        type="submit"
        disabled={submitting || !text.trim()}
        className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 
          text-white text-xs font-bold px-3 py-1.5 rounded-xl transition-colors"
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

const QAMessageNode = ({ msg, depth = 0, courseId, currentUser, onRefresh }) => {
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [showReplies, setShowReplies] = useState(true);
   const [isDeleting, setIsDeleting] = useState(false); 
  const isCurrentUser = msg.user_id === currentUser?.id;
  const userName = msg.user?.name || 'Student';
  const initial = userName.charAt(0).toUpperCase();
  const replyCount = msg.replies?.length || 0;

  const avatarColor = depth === 0
    ? 'bg-indigo-100 text-indigo-700'
    : depth === 1
    ? 'bg-emerald-100 text-emerald-700'
    : 'bg-amber-100 text-amber-700';

  const handleReplySubmit = async (text) => {
    try {
      await api.post(`/api/qa/forum/course/${courseId}/post`, {
        message: text,
        parent_id: msg.id
      });
      setShowReplyForm(false);
      onRefresh();
    } catch (err) {
      console.error('Reply failed:', err);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Delete this message?')) return;
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

  return (
    <div className={`flex gap-3 ${depth > 0 ? 'mt-3' : ''}`}>
      {/* Thread line for nested replies */}
      {depth > 0 && (
        <div className="flex flex-col items-center shrink-0">
          <div className="w-px flex-1 bg-slate-200 ml-3.5 min-h-[20px]"></div>
        </div>
      )}

      <div className="flex-1 min-w-0">
        <div className="flex gap-2.5">
          {/* Avatar */}
          <div className={`w-8 h-8 rounded-full flex items-center justify-center 
            font-bold text-xs shrink-0 ${avatarColor}`}>
            {initial}
          </div>

          <div className="flex-1 min-w-0">
            {/* Name + time */}
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-bold text-slate-800">{userName}</span>
              {isCurrentUser && (
                <span className="text-[9px] bg-indigo-100 text-indigo-600 
                  px-1.5 py-0.5 rounded font-semibold uppercase tracking-wide">
                  You
                </span>
              )}
              <span className="text-[10px] text-slate-400">
                {formatDate(msg.created_at)}
              </span>
            </div>

            {/* Message */}
            <p className="text-sm text-slate-700 mt-0.5 leading-relaxed">
              {msg.message}
            </p>

            {/* Actions */}
            <div className="flex items-center gap-3 mt-1.5">
              {depth < 3 && (
                <button
                  onClick={() => setShowReplyForm(!showReplyForm)}
                  className="text-[11px] font-bold text-slate-400 
                    hover:text-indigo-600 transition-colors flex items-center gap-1"
                >
                  ↩ Reply
                </button>
              )}
              {replyCount > 0 && (
                <button
                  onClick={() => setShowReplies(!showReplies)}
                  className="text-[11px] font-semibold text-indigo-500 
                    hover:text-indigo-700 transition-colors"
                >
                  {showReplies
                    ? `▲ Hide ${replyCount} ${replyCount === 1 ? 'reply' : 'replies'}`
                    : `▼ Show ${replyCount} ${replyCount === 1 ? 'reply' : 'replies'}`
                  }
                </button>
              )}
              {isCurrentUser && (
                <button
                  onClick={handleDelete}
                  disabled={isDeleting}
                  className="text-[11px] font-bold text-red-400 hover:text-red-600 
                    transition-colors disabled:opacity-50"
                >
                  {isDeleting ? '...' : '🗑 Delete'}
                </button>
              )}
            </div>
            {/* Inline reply form */}
            {showReplyForm && (
              <QAReplyForm
                onSubmit={handleReplySubmit}
                onCancel={() => setShowReplyForm(false)}
                placeholder={`Reply to ${userName}...`}
              />
            )}

            {/* Nested replies */}
            {showReplies && msg.replies && msg.replies.length > 0 && (
              <div className="mt-3 space-y-0 border-l-2 border-slate-100 pl-3">
                {msg.replies.map((reply) => (
                  <QAMessageNode
                    key={reply.id}
                    msg={reply}
                    depth={depth + 1}
                    courseId={courseId}
                    currentUser={currentUser}
                    onRefresh={onRefresh}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
const LearnPage = () => {
  const { courseId } = useParams();
  const { user } = useSelector((state) => state.auth);
  const [course, setCourse] = useState(null);
  const [modules, setModules] = useState([]);
  const [completedLessons, setCompletedLessons] = useState([]);
  const [currentLesson, setCurrentLesson] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [progressPercent, setProgressPercent] = useState(0);
  const [activeTab, setActiveTab] = useState('overview'); // 'overview', 'qa', 'chat', 'announcements'
  const [questions, setQuestions] = useState([]);
  const [newQuestionText, setNewQuestionText] = useState('');
  const [chatMessages, setChatMessages] = useState([]);
  const [newChatMessage, setNewChatMessage] = useState('');
  const [socketConnected, setSocketConnected] = useState(false);
  const [announcements, setAnnouncements] = useState([]);
  const [quizModalOpen, setQuizModalOpen] = useState(false);
  const [quizDetails, setQuizDetails] = useState(null);
  const [selectedOptions, setSelectedOptions] = useState({}); // {questionId: optionId}
  const [quizResult, setQuizResult] = useState(null);
  const [quizError, setQuizError] = useState('');
  const [certificateUrl, setCertificateUrl] = useState('');
  const [isGeneratingCert, setIsGeneratingCert] = useState(false);
  const socketRef = useRef(null);
  const chatBottomRef = useRef(null);
  const fetchCurriculum = async () => {
    try {
      const contentRes = await api.get(`/api/courses/${courseId}/content`);
      setCourse(contentRes.data.course);

      const mods = contentRes.data.modules || [];
      setModules(mods);

      if (mods.length > 0 && !currentLesson) {
        const firstModule = mods[0];
        if (firstModule.lessons && firstModule.lessons.length > 0) {
          setCurrentLesson(firstModule.lessons[0]);
        }
      }
      const progressRes = await api.get(`/api/progress/course/${courseId}`);
      const completed = progressRes.data.completed_lessons || [];
      const completedIds = completed.map(l => l.lesson_id || l.id || l);
      setCompletedLessons(completedIds);

      const allLessons = mods.flatMap(m => m.lessons || []);
      const totalLessons = allLessons.length;
      const percent = totalLessons > 0 
        ? Math.round((completedIds.length / totalLessons) * 100) 
        : 0;
      setProgressPercent(percent);
      if (percent === 100) {
        const certRes = await api.get('/api/certificates/my');
        const existingCert = certRes.data.find((c) => c.course_id === courseId);
        if (existingCert) {
          setCertificateUrl(existingCert.certificate_url);
        }
      }

    } catch (err) {
      console.error('Failed to fetch course content:', err);
    }
  };

  const fetchProgress = async () => {
    try {
      const res = await api.get(`/api/progress/course/${courseId}`);
      const completed = res.data.completed_lessons || [];
      const completedIds = completed.map(l => l.lesson_id || l.id || l);
      setCompletedLessons(completedIds);

      const allLessons = modules.flatMap(m => m.lessons || []);
      const totalLessons = allLessons.length;
      const percent = totalLessons > 0 
        ? Math.round((completedIds.length / totalLessons) * 100) 
        : 0;
      setProgressPercent(percent);

      if (percent === 100) {
        const certRes = await api.get('/api/certificates/my');
        const existingCert = certRes.data.find((c) => c.course_id === courseId);
        if (existingCert) {
          setCertificateUrl(existingCert.certificate_url);
        }
      }
    } catch (err) {
      console.error('Failed to fetch progress:', err);
    }
  };

  useEffect(() => {
    setLoading(true);
    fetchCurriculum().finally(() => setLoading(false));
  }, [courseId]);
  useEffect(() => {
    if (activeTab === 'qa') {
      fetchQAThreads();
    } else if (activeTab === 'chat') {
      fetchChatHistory();
    } else if (activeTab === 'announcements') {
      fetchAnnouncements();
    }
  }, [activeTab, courseId]);

  useEffect(() => {
    if (activeTab !== 'announcements' || !courseId) return;

    const interval = window.setInterval(() => {
      fetchAnnouncements();
    }, 8000);

    return () => window.clearInterval(interval);
  }, [activeTab, courseId]);
  useEffect(() => {
    if (user && courseId) {
      try {
        const token = localStorage.getItem('access_token');
        const socket = io('http://localhost:5000', {
          transports: ['websocket', 'polling'],
          reconnection: true,
          reconnectionAttempts: 10,
          reconnectionDelay: 1000,
          reconnectionDelayMax: 5000,
          auth: {
            token: token,
          },
        });

        socketRef.current = socket;

        const handleConnect = () => {
          console.log("Socket connected:", socket.id);
          setSocketConnected(true);
          socket.emit("join_course", {
              course_id: courseId
          });
      };

        const handleDisconnect = (reason) => {
          console.log("Socket disconnected:", reason);
          setSocketConnected(false);
      };

        const handleConnectError = (err) => {
          console.log("Connection Error");
          console.log(err);
          setSocketConnected(false);
      };

        const handleNewMessage = (msg) => {
          if (msg.course_id === courseId) {
            setChatMessages((prev) => {
              if (prev.some(m => m.id === msg.id)) return prev;
              return [...prev, msg];
            });
            setTimeout(() => {
              chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
            }, 100);
          }
        };

        socket.on('connect', handleConnect);
        socket.on('disconnect', handleDisconnect);
        socket.on('connect_error', handleConnectError);
        socket.on('new_message', handleNewMessage);
      } catch (err) {
        console.error('Socket connection error in LearnPage:', err);
      }

      return () => {
        if (socketRef.current) {
          socketRef.current.emit('leave_course', { course_id: courseId });
          socketRef.current.off('connect');
          socketRef.current.off('disconnect');
          socketRef.current.off('connect_error');
          socketRef.current.off('new_message');
          socketRef.current.disconnect();
          socketRef.current = null;
        }
      };
    }
  }, [courseId, user]);
  const handleMarkComplete = async (lessonId) => {
    try {
      await api.post(`/api/progress/complete/${lessonId}`);
      // Update local state immediately for instant UI feedback
      setCompletedLessons(prev => {
        if (prev.includes(lessonId)) return prev;
        return [...prev, lessonId];
      });
      // Recalculate progress
      await fetchProgress();
    } catch (err) {
      console.error('Failed to mark complete:', err);
    }
  };

  const handleGenerateCertificate = async () => {
    setIsGeneratingCert(true);
    try {
      const res = await api.post(`/api/certificates/generate/${courseId}`);
      setCertificateUrl(res.data.certificate_url);
    } catch (err) {
      alert('Failed to generate certificate. Please make sure progress is 100% complete.');
    } finally {
      setIsGeneratingCert(false);
    }
  };
  const fetchQAThreads = async () => {
  try {
    const res = await api.get(`/api/qa/forum/course/${courseId}/thread`);
    setQuestions(res.data.threads || []);
  } catch (err) {
    console.error('QA load failed:', err);
  }
  };

  const handleQAAsk = async (e) => {
  e.preventDefault();
  if (!newQuestionText.trim()) return;
  try {
    await api.post(`/api/qa/forum/course/${courseId}/post`, {
      message: newQuestionText.trim(),
      parent_id: null
    });
    setNewQuestionText('');
    fetchQAThreads();
  } catch (err) {
    console.error('Post failed:', err);
  }
  };
  

  const fetchChatHistory = async () => {
    try {
      const res = await api.get(`/api/qa/chat/${courseId}`);
      setChatMessages(res.data.messages || []);
      setTimeout(() => {
        chatBottomRef.current?.scrollIntoView({ behavior: 'auto' });
      }, 100);
    } catch (err) {
      console.error('Chat history failed:', err);
    }
  };

  const sendMessage = () => {
    if (!newChatMessage.trim()) return;
    if (!socketRef.current || !socketRef.current.connected) {
      toast.error('Chat not connected. Please refresh.');
      return;
    }
    socketRef.current.emit('send_message', {
      course_id: courseId,
      message: newChatMessage.trim(),
      user_name: user?.name || 'Student'
    });
    setNewChatMessage('');
  };

  const handleSendChatMessage = (e) => {
    e.preventDefault();
    sendMessage();
  };

  const fetchAnnouncements = async () => {
    try {
      const res = await api.get(`/api/announcements/${courseId}`);
      setAnnouncements(res.data || []);
    } catch (err) {
      console.error('Announcements failed:', err);
    }
  };
  const handleOpenQuiz = async (quizId) => {
    setQuizError('');
    setQuizResult(null);
    setSelectedOptions({});
    try {
      const res = await api.get(`/api/quizzes/${quizId}`);
      setQuizDetails(res.data);
      setQuizModalOpen(true);
    } catch (err) {
      alert('Failed to load quiz details');
    }
  };

  const handleSelectOption = (questionId, optionId) => {
    setSelectedOptions((prev) => ({
      ...prev,
      [questionId]: optionId,
    }));
  };

  const handleQuizSubmit = async (e) => {
    e.preventDefault();
    setQuizError('');
    const unanswered = quizDetails.questions.some((q) => !selectedOptions[q.id]);
    if (unanswered) {
      setQuizError('Please answer all questions before submitting.');
      return;
    }

    const payload = {
      answers: Object.entries(selectedOptions).map(([qId, optId]) => ({
        question_id: qId,
        option_id: optId,
      })),
    };

    try {
      const res = await api.post(`/api/quizzes/submit/${quizDetails.quiz.id}`, payload);
      setQuizResult(res.data);
      if (res.data.passed) {
        fetchCurriculum();
      }
    } catch (err) {
      setQuizError(err.response?.data?.message || 'Quiz submission failed.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F9FAFB]">
        <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 text-slate-500 font-semibold">
        Loading...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">

      <div className="bg-slate-900 text-white h-14 px-4 flex items-center justify-between z-10 select-none">
        <div className="flex items-center gap-3 min-w-0">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-white"
          >
            {sidebarOpen ? <ChevronLeft className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
          </button>
          <h1 className="font-bold text-sm sm:text-base truncate">{course?.title}</h1>
        </div>
        <div className="flex items-center gap-4 shrink-0">
          <div className="hidden sm:block text-right">
            <span className="block text-xs font-semibold text-slate-400">Course Progress</span>
            <span className="text-sm font-bold text-indigo-400">{Math.round(progressPercent)}% Complete</span>
          </div>
          <div className="w-20 sm:w-28 bg-slate-800 h-2.5 rounded-full overflow-hidden shrink-0">
            <div className="bg-indigo-500 h-full transition-all duration-300" style={{ width: `${progressPercent}%` }}></div>
          </div>

          {progressPercent === 100 && (
            certificateUrl ? (
              <a
                href={certificateUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs px-3.5 py-1.5 rounded flex items-center gap-1 shrink-0"
              >
                <Award className="w-4 h-4" /> Certificate
              </a>
            ) : (
              <button
                onClick={handleGenerateCertificate}
                disabled={isGeneratingCert}
                className="bg-indigo-600 hover:bg-indigo-750 text-white font-bold text-xs px-3.5 py-1.5 rounded flex items-center gap-1 shrink-0"
              >
                <Award className="w-4 h-4" /> {isGeneratingCert ? 'Generating...' : 'Get Certificate'}
              </button>
            )
          )}
        </div>
      </div>

      <div className="flex flex-1 relative overflow-hidden">
        <aside className={`${sidebarOpen ? 'w-80 border-r border-slate-200' : 'w-0'} bg-white flex flex-col transition-all duration-300 z-10 shrink-0`}>
          <div className="p-4 border-b border-slate-100 bg-slate-50/50">
            <h2 className="font-bold text-slate-800 text-sm">Course Curriculum</h2>
          </div>

          <div className="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-4">
            {modules.map((mod) => (
              <div key={mod.id} className="space-y-1.5">
                <h3 className="font-bold text-xs text-slate-400 uppercase tracking-widest px-2">{mod.title}</h3>

                <div className="space-y-1">
                  {(mod.lessons || []).map((les) => {
                    const isCompleted = completedLessons.includes(les.id);
                    const isCurrent = currentLesson?.id === les.id;
                    return (
                      <button
                        key={les.id}
                        onClick={() => setCurrentLesson(les)}
                        className={`w-full text-left px-2.5 py-2.5 rounded-lg flex items-center gap-3 transition-colors text-xs font-semibold ${isCurrent
                            ? 'bg-indigo-50 text-indigo-700 border-l-4 border-indigo-600'
                            : 'text-slate-650 hover:bg-slate-50'
                          }`}
                      >
                        <div
                          onClick={(e) => {
                            e.stopPropagation();
                            handleMarkComplete(les.id);
                          }}
                          className={`w-5 h-5 rounded-full border-2 cursor-pointer flex 
                            items-center justify-center transition-all shrink-0
                            ${completedLessons.includes(les.id) 
                              ? 'bg-green-500 border-green-500' 
                              : 'border-gray-400 hover:border-indigo-500'}`}
                        >
                          {completedLessons.includes(les.id) && (
                            <svg className="w-3 h-3 text-white" fill="currentColor" 
                                 viewBox="0 0 20 20">
                              <path fillRule="evenodd" 
                                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 
                                   01-1.414 0l-4-4a1 1 0 011.414-1.414L8 
                                   12.586l7.293-7.293a1 1 0 011.414 0z" 
                                clipRule="evenodd" />
                            </svg>
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="truncate">{les.title}</p>
                          <span className="text-[10px] text-slate-400 flex items-center gap-1 mt-0.5 font-medium">
                            {les.pdf_url ? <FileText className="w-3 h-3" /> : <Video className="w-3 h-3" />}
                            {les.quiz ? 'Lesson Quiz' : les.pdf_url ? 'PDF' : 'Video'}
                          </span>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </aside>

        <main className="flex-1 flex flex-col overflow-y-auto custom-scrollbar">
          {currentLesson ? (
            <div className="bg-slate-900 flex flex-col items-center justify-center relative aspect-video max-h-[500px]">
              {currentLesson?.video_url ? (
                <video
                  key={currentLesson?.id}
                  src={currentLesson?.video_url?.startsWith('/') ? `http://localhost:5000${currentLesson?.video_url}` : currentLesson?.video_url}
                  controls
                  onEnded={() => handleMarkComplete(currentLesson.id)}
                  className="w-full h-full object-contain"
                  poster={getCourseThumbnail(course)}
                />
              ) : currentLesson?.pdf_url ? (
                <iframe
                  key={currentLesson?.id}
                  src={currentLesson?.pdf_url?.startsWith('/') ? `http://localhost:5000${currentLesson?.pdf_url}#toolbar=0` : `${currentLesson?.pdf_url}#toolbar=0`}
                  title={currentLesson?.title}
                  className="w-full h-full border-none bg-white"
                />
              ) : (
                <div className="p-8 text-center text-slate-300 space-y-4">
                  <FileText className="w-16 h-16 text-indigo-400 mx-auto" />
                  <div>
                    <h3 className="text-lg font-bold text-white">{currentLesson?.title}</h3>
                    <p className="text-xs text-slate-400 mt-1">This lesson is a text study session. Read the overview details below.</p>
                  </div>
                </div>
              )}
              <div className="absolute bottom-4 right-4 z-20">
                {currentLesson?.quiz ? (
                  <button
                    onClick={() => handleOpenQuiz(currentLesson?.quiz?.id)}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs px-4 py-2 rounded shadow-lg flex items-center gap-1.5"
                  >
                    <HelpCircle className="w-4 h-4" /> Take Quiz
                  </button>
                ) : completedLessons.includes(currentLesson?.id) ? (
                  <span className="bg-emerald-600 text-white font-bold text-xs px-4 py-2 rounded flex items-center gap-1.5 shadow-lg select-none">
                    <CheckCircle className="w-4 h-4" /> Lesson Complete
                  </span>
                ) : (
                  <button
                    onClick={() => handleMarkComplete(currentLesson?.id)}
                    className="bg-indigo-600 hover:bg-indigo-755 hover:bg-indigo-700 text-white font-bold text-xs px-4 py-2 rounded shadow-lg flex items-center gap-1.5"
                  >
                    Mark as Complete
                  </button>
                )}
              </div>

            </div>
          ) : (
            <div className="aspect-video max-h-[500px] bg-slate-950 flex flex-col items-center justify-center text-slate-500">
              <BookOpen className="w-16 h-16 mb-2" />
              <p className="text-sm">Select a lesson from the curriculum sidebar to start learning.</p>
            </div>
          )}
          <div className="p-6 max-w-4xl w-full mx-auto space-y-6">
            <div className="flex border-b border-slate-200 gap-6 text-sm font-semibold mb-6">
              {['overview', 'qa', 'chat', 'announcements'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`pb-3 capitalize border-b-2 transition-all ${activeTab === tab
                      ? 'border-indigo-600 text-indigo-600'
                      : 'border-transparent text-slate-500 hover:text-indigo-600'
                    }`}
                >
                  {tab === 'qa' ? 'Q&A Forum' : tab === 'chat' ? 'Live Chat' : tab}
                </button>
              ))}
            </div>

            <div>
              {activeTab === 'overview' && currentLesson && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-lg font-bold text-slate-800 mb-2">{currentLesson?.title}</h2>
                    <p className="text-sm text-slate-600 leading-relaxed whitespace-pre-wrap">
                      {currentLesson?.content || 'No text content available for this lesson.'}
                    </p>
                  </div>

                  {currentLesson?.pdf_url && (
                    <div className="border-t border-slate-100 pt-6">
                      <h3 className="font-bold text-slate-800 text-sm mb-3">
                        Lesson Resources
                      </h3>

                      <a
                        href={currentLesson.pdf_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="bg-white border border-slate-200 p-3 rounded-xl flex items-center justify-between text-slate-700 hover:border-indigo-200 transition-colors"
                      >
                        <span>Lesson Notes (PDF)</span>
                        <Download className="w-4 h-4 text-indigo-600" />
                      </a>
                    </div>
                  )}

                  
                  {currentLesson?.attachments && currentLesson?.attachments.length > 0 && (
                    <div className="border-t border-slate-100 pt-6">
                      <h3 className="font-bold text-slate-800 text-sm mb-3">Download Attachments</h3>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-semibold">
                        {currentLesson?.attachments.map((file) => {
                          const fileUrl = file.file_url?.startsWith('/')
                            ? `http://localhost:5000${file.file_url}`
                            : (file.file_url || file.file_key);
                          return (
                            <a
                              key={file.id}
                              href={fileUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="bg-white border border-slate-200 p-3 rounded-xl flex items-center justify-between text-slate-700 hover:border-indigo-200 transition-colors"
                            >
                              <span className="truncate">{file.title}</span>
                              <Download className="w-4 h-4 text-indigo-600 shrink-0" />
                            </a>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              )}

              
             
              {activeTab === 'qa' && (
                <div className="space-y-6">
                  {/* New question form */}
                  <form onSubmit={handleQAAsk} 
                    className="bg-white border border-slate-200 rounded-2xl p-4 space-y-3">
                    <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                      Ask a Question
                    </h4>
                    <div className="flex gap-3">
                      <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center 
                        justify-center text-indigo-700 font-bold text-xs shrink-0">
                        {(user?.name || 'S').charAt(0).toUpperCase()}
                      </div>
                      <div className="flex-1 flex gap-2">
                        <input
                          type="text"
                          placeholder="Ask something about this course..."
                          value={newQuestionText}
                          onChange={(e) => setNewQuestionText(e.target.value)}
                          className="flex-1 bg-slate-50 border border-slate-200 px-4 
                            py-2.5 rounded-xl text-sm focus:outline-none focus:ring-1 
                            focus:ring-indigo-400 focus:bg-white"
                        />
                        <button
                          type="submit"
                          disabled={!newQuestionText.trim()}
                          className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 
                            text-white font-bold text-xs px-5 py-2.5 rounded-xl transition-colors"
                        >
                          Post
                        </button>
                      </div>
                    </div>
                  </form>

                  {/* Thread list */}
                  <div className="space-y-4">
                    {questions.length === 0 ? (
                      <div className="text-center py-12 text-slate-400">
                        <MessageSquare className="w-10 h-10 mx-auto mb-2 opacity-30" />
                        <p className="text-sm">No questions yet. Be the first to ask!</p>
                      </div>
                    ) : (
                      questions.map((msg) => (
                        <div key={msg.id} 
                          className="bg-white border border-slate-100 rounded-2xl p-4 shadow-sm">
                          <QAMessageNode
                            msg={msg}
                            depth={0}
                            courseId={courseId}
                            currentUser={user}
                            onRefresh={fetchQAThreads}
                          />
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
              {activeTab === 'chat' && (
                <div className="bg-white border border-slate-200/60 rounded-2xl shadow-sm flex flex-col h-[400px] overflow-hidden">
                  <div className={`text-xs px-4 pt-2.5 ${socketConnected ? 'text-green-500 font-semibold' : 'text-red-500 font-semibold'}`}>
                    {socketConnected ? '● Connected' : '● Disconnected'}
                  </div>
                  <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-3.5 bg-slate-50/50">
                    {chatMessages.length === 0 ? (
                      <p className="text-xs text-slate-400 italic text-center py-10">Classroom chat room is empty. Send a message to start.</p>
                    ) : (
                      chatMessages.map((msg) => (
                        <div
                          key={msg.id}
                          className={`flex flex-col max-w-[80%] ${msg.user_id === user.id ? 'ml-auto items-end' : 'mr-auto'}`}
                        >
                          <span className="text-[9px] font-bold text-slate-400 mb-0.5 px-1">{msg.user_name || msg.user?.name || 'Student'}</span>
                          <div className={`p-3 rounded-2xl text-sm ${msg.user_id === user.id
                              ? 'bg-indigo-600 text-white rounded-tr-none'
                              : 'bg-white border border-slate-100 text-slate-800 rounded-tl-none'
                            }`}>
                            <p>{msg.message}</p>
                          </div>
                        </div>
                      ))
                    )}
                    <div ref={chatBottomRef} />
                  </div>
                  <form onSubmit={handleSendChatMessage} className="p-3 border-t border-slate-100 bg-white flex gap-2">
                    <input
                      type="text"
                      placeholder="Say something to the class..."
                      value={newChatMessage}
                      onChange={(e) => setNewChatMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                      className="flex-1 bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:bg-white"
                    />
                    <button
                      type="submit"
                      className="bg-indigo-600 text-white p-2.5 rounded-xl hover:bg-indigo-700 transition-colors"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                  </form>
                </div>
              )}
              {activeTab === 'announcements' && (
                <div className="space-y-4">
                  {announcements.length === 0 ? (
                    <p className="text-xs text-slate-400 italic text-center py-8">No announcements posted for this course.</p>
                  ) : (
                    announcements.map((ann) => (
                      <div key={ann.id} className="bg-white border border-slate-100 p-5 rounded-2xl shadow-sm flex gap-3.5 items-start">
                        <div className="bg-indigo-50 p-2.5 rounded-xl text-indigo-655 text-indigo-605 text-indigo-600 shrink-0">
                          <Megaphone className="w-5 h-5" />
                        </div>
                        <div className="space-y-1">
                          <div className="flex justify-between items-baseline mb-0.5">
                            <h4 className="font-bold text-slate-805 text-slate-800 text-sm">{ann.title}</h4>
                            <span className="text-[10px] text-slate-400">{new Date(ann.created_at).toLocaleDateString()}</span>
                          </div>
                          <p className="text-xs sm:text-sm text-slate-500 leading-relaxed">{ann.message}</p>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}

            </div>

          </div>

        </main>

      </div>
      {quizModalOpen && quizDetails && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm px-4">
          <div className="bg-white max-w-lg w-full rounded-2xl shadow-2xl border border-slate-150 p-6 flex flex-col justify-between max-h-[85vh] overflow-hidden">

            {/* Header */}
            <div className="flex justify-between items-center pb-4 border-b border-slate-100 shrink-0">
              <div>
                <h3 className="font-bold text-slate-900 text-base">{quizDetails.quiz.title}</h3>
                <span className="text-[10px] text-indigo-600 font-semibold tracking-wide uppercase mt-0.5 block">
                  Required passing score: {quizDetails.quiz.pass_percentage}%
                </span>
              </div>
              <button onClick={() => setQuizModalOpen(false)}>
                <X className="w-5 h-5 text-slate-400 hover:text-slate-655" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto custom-scrollbar py-4 space-y-6">

              {quizError && (
                <div className="bg-red-50 text-red-750 border border-red-100 rounded-xl p-3 flex gap-2 text-xs">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{quizError}</span>
                </div>
              )}

              {quizResult ? (
                <div className="text-center py-6 space-y-4">
                  <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto text-white shadow-md ${quizResult.passed ? 'bg-emerald-600' : 'bg-red-650 bg-red-600'
                    }`}>
                    {quizResult.passed ? <CheckCircle className="w-8 h-8" /> : <AlertCircle className="w-8 h-8" />}
                  </div>

                  <div>
                    <h4 className="text-lg font-bold text-slate-800">
                      {quizResult.passed ? 'Congratulations! You Passed!' : 'Quiz Attempt Failed'}
                    </h4>
                    <p className="text-xs text-slate-500 mt-1">
                      You scored <strong className="text-slate-700">{quizResult.score}</strong>. Passing threshold requires answering at least {quizResult.required_score} questions correctly.
                    </p>
                  </div>
                </div>
              ) : (
                quizDetails.questions.map((q, qIdx) => (
                  <div key={q.id} className="space-y-2.5">
                    <p className="text-sm font-semibold text-slate-855 text-slate-800">
                      {qIdx + 1}. {q.question}
                    </p>
                    <div className="grid grid-cols-1 gap-2">
                      {q.options.map((opt) => (
                        <button
                          key={opt.id}
                          type="button"
                          onClick={() => handleSelectOption(q.id, opt.id)}
                          className={`w-full text-left p-3.5 rounded-xl border text-xs font-semibold transition-all ${selectedOptions[q.id] === opt.id
                              ? 'border-indigo-650 bg-indigo-50/50 text-indigo-700 font-bold border-indigo-600'
                              : 'border-slate-200 hover:border-slate-350 hover:bg-slate-50 text-slate-650'
                            }`}
                        >
                          {opt.option_text}
                        </button>
                      ))}
                    </div>
                  </div>
                ))
              )}

            </div>
            <div className="pt-4 border-t border-slate-100 shrink-0">
              {quizResult ? (
                <button
                  onClick={() => setQuizModalOpen(false)}
                  className="w-full bg-slate-900 text-white font-bold text-xs py-2.5 rounded-xl"
                >
                  Close Modal
                </button>
              ) : (
                <button
                  onClick={handleQuizSubmit}
                  className="w-full bg-indigo-600 hover:bg-indigo-755 hover:bg-indigo-700 text-white font-bold text-xs py-2.5 rounded-xl shadow-md"
                >
                  Submit Answers
                </button>
              )}
            </div>

          </div>
        </div>
      )}

    </div>
  );
};

export default LearnPage;
