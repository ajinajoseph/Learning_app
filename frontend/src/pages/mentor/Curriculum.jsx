import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../../api/axios';
import { 
  BookOpen, ArrowLeft, Plus, Edit, Trash2, Video, FileText, 
  HelpCircle, ChevronDown, ChevronUp, Upload, Check, X, AlertCircle, CheckSquare 
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

const getFileUrl = (path) => {
  if (!path) return null;
  if (path.startsWith('http')) return path;
  return `${import.meta.env.VITE_API_BASE_URL}${path}`;
};

const Curriculum = () => {
  const { id } = useParams(); // courseId

  // Data State
  const [course, setCourse] = useState(null);
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);

  // Active Modals & Forms State
  const [activeModuleId, setActiveModuleId] = useState(null); // module we're adding lesson to
  const [showModuleModal, setShowModuleModal] = useState(false);
  const [moduleTitle, setModuleTitle] = useState('');
  const [moduleDesc, setModuleDesc] = useState('');
  const [editingModule, setEditingModule] = useState(null);

  const [showLessonModal, setShowLessonModal] = useState(false);
  const [lessonTitle, setLessonTitle] = useState('');
  const [lessonContent, setLessonContent] = useState('');
  const [editingLesson, setEditingLesson] = useState(null);

  // Media / Attachment Upload State
  const [uploadingMediaId, setUploadingMediaId] = useState(null); // lessonId
  const [uploadType, setUploadType] = useState(''); // 'video', 'pdf', 'attachment'
  const [uploadTitle, setUploadTitle] = useState(''); // for attachments
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);

  // Quiz Builder Modal State
  const [showQuizModal, setShowQuizModal] = useState(false);
  const [quizLessonId, setQuizLessonId] = useState(null);
  const [quizTitle, setQuizTitle] = useState('');
  const [quizPassPercent, setQuizPassPercent] = useState(70);
  const [currentQuiz, setCurrentQuiz] = useState(null); // active quiz we are editing questions for
  const [editingQuestionId, setEditingQuestionId] = useState(null);
  const [editQuestionText, setEditQuestionText] = useState('');
  const [editOptions, setEditOptions] = useState([]);

  // Quiz Questions builder state
  const [questionText, setQuestionText] = useState('');
  const [options, setOptions] = useState([
    { text: '', isCorrect: false },
    { text: '', isCorrect: false },
    { text: '', isCorrect: false },
    { text: '', isCorrect: false },
  ]);

  // Load Course Content
  const fetchCurriculum = async () => {
    try {
      const res = await api.get(`/api/courses/${id}/content`);
      setCourse(res.data.course);
      setModules(res.data.modules || []);
    } catch (err) {
      console.error('Failed to load curriculum:', err);
    }
  };

  useEffect(() => {
    setLoading(true);
    fetchCurriculum().finally(() => setLoading(false));
  }, [id]);

  // ----------------------------------------
  // MODULE CRUD
  // ----------------------------------------
  const handleSaveModule = async (e) => {
    e.preventDefault();
    try {
      if (editingModule) {
        await api.put(`/api/modules/${editingModule.id}`, {
          title: moduleTitle,
          description: moduleDesc,
        });
      } else {
        await api.post('/api/modules', {
          title: moduleTitle,
          description: moduleDesc,
          course_id: id,
        });
      }
      setModuleTitle('');
      setModuleDesc('');
      setEditingModule(null);
      setShowModuleModal(false);
      fetchCurriculum();
    } catch (err) {
      alert('Failed to save module');
    }
  };

  const handleDeleteModule = async (moduleId) => {
    if (!window.confirm('Delete this module? All lessons inside will be deleted as well.')) return;
    try {
      await api.delete(`/api/modules/${moduleId}`);
      fetchCurriculum();
    } catch (err) {
      alert('Failed to delete module');
    }
  };

  // ----------------------------------------
  // LESSON CRUD
  // ----------------------------------------
  const handleSaveLesson = async (e) => {
    e.preventDefault();
    try {
      if (editingLesson) {
        await api.put(`/api/lessons/${editingLesson.id}`, {
          title: lessonTitle,
          content: lessonContent,
        });
      } else {
        await api.post('/api/lessons', {
          title: lessonTitle,
          content: lessonContent,
          module_id: activeModuleId,
        });
      }
      setLessonTitle('');
      setLessonContent('');
      setEditingLesson(null);
      setShowLessonModal(false);
      fetchCurriculum();
    } catch (err) {
      alert('Failed to save lesson');
    }
  };

  const handleDeleteLesson = async (lessonId) => {
    if (!window.confirm('Delete this lesson?')) return;
    try {
      await api.delete(`/api/lessons/${lessonId}`);
      fetchCurriculum();
    } catch (err) {
      alert('Failed to delete lesson');
    }
  };

  // ----------------------------------------
  // MEDIA UPLOADER
  // ----------------------------------------
  const handleUploadFileSubmit = async (e) => {
    e.preventDefault();
    if (!uploadFile) return;

    const formData = new FormData();
    formData.append('file', uploadFile);
    
    let endpoint = '';
    if (uploadType === 'video') {
      endpoint = `/api/lessons/${uploadingMediaId}/upload-video`;
    } else if (uploadType === 'pdf') {
      endpoint = `/api/lessons/${uploadingMediaId}/upload-pdf`;
    } else {
      endpoint = `/api/lessons/${uploadingMediaId}/attachments`;
      formData.append('title', uploadTitle || uploadFile.name);
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      await api.post(endpoint, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const percent = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(percent);
        }
      });
      setUploadFile(null);
      setUploadTitle('');
      setUploadingMediaId(null);
      setUploadType('');
      await fetchCurriculum();
    } catch (err) {
      alert(err.response?.data?.message || 'Upload failed');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleDeleteAttachment = async (lessonId, attachmentId) => {
    if (!window.confirm('Delete this attachment?')) return;
    try {
      await api.delete(`/api/lessons/${lessonId}/attachments/${attachmentId}`);
      await fetchCurriculum();
    } catch (err) {
      alert('Failed to delete attachment');
    }
  };

  const handleStartEditQuestion = (q) => {
    setEditingQuestionId(q.id);
    setEditQuestionText(q.question_text || q.question || '');
    setEditOptions(q.options.map(o => ({
      id: o.id,
      option_text: o.option_text || o.text || '',
      is_correct: o.is_correct || false
    })));
  };

  const handleCancelEditQuestion = () => {
    setEditingQuestionId(null);
    setEditQuestionText('');
    setEditOptions([]);
  };

  const handleSaveEditedQuestion = async (e) => {
    e.preventDefault();
    try {
      await api.put(`/api/quizzes/question/${editingQuestionId}`, {
        question_text: editQuestionText.trim(),
        options: editOptions.map(opt => ({
          id: opt.id,
          option_text: (opt.option_text || '').trim(),
          is_correct: Boolean(opt.is_correct)
        }))
      });
      toast.success('Question updated!');

      // Refresh quiz details modal view
      const quizRes = await api.get(`/api/quizzes/${currentQuiz.quiz.id}`);
      setCurrentQuiz(quizRes.data);
      handleCancelEditQuestion();
    } catch (err) {
      console.error('Update error:', err.response?.data);
      toast.error(err.response?.data?.message || 'Failed to update question');
    }
  };

  const handleDeleteQuestion = async (questionId) => {
    if (!window.confirm('Delete this question?')) return;
    try {
      await api.delete(`/api/quizzes/question/${questionId}`);
      // Refresh quiz details modal view
      const quizRes = await api.get(`/api/quizzes/${currentQuiz.quiz.id}`);
      setCurrentQuiz(quizRes.data);
    } catch (err) {
      alert('Failed to delete question');
    }
  };
  const handleOpenQuizBuilder = async (lesson) => {
    setQuizLessonId(lesson.id);
    setQuizTitle('');
    setQuizPassPercent(70);
    setQuestionText('');
    setOptions([
      { text: '', isCorrect: false },
      { text: '', isCorrect: false },
      { text: '', isCorrect: false },
      { text: '', isCorrect: false },
    ]);

    if (lesson.quiz) {
      try {
        const res = await api.get(`/api/quizzes/${lesson.quiz.id}`);
        setCurrentQuiz(res.data);
      } catch (err) {
        console.error(err);
      }
    } else {
      setCurrentQuiz(null);
    }
    setShowQuizModal(true);
  };

  const handleCreateQuiz = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post('/api/quizzes', {
        title: quizTitle || 'Lesson Quiz',
        lesson_id: quizLessonId,
        pass_percentage: Number(quizPassPercent),
      });
      setCurrentQuiz({ quiz: res.data, questions: [] });
      fetchCurriculum();
    } catch (err) {
      alert('Failed to create quiz');
    }
  };

  const handleAddQuestion = async (e) => {
    e.preventDefault();
    if (!questionText.trim()) return;

    // Check that at least one option is correct
    const hasCorrect = options.some((o) => o.isCorrect);
    if (!hasCorrect) {
      alert('Please check at least one correct option.');
      return;
    }

    try {

      const qRes = await api.post('/api/quizzes/question', {
        quiz_id: currentQuiz.quiz.id,
        question_text: questionText.trim(),
      });
      const qId = qRes.data.id;

      // 2. Add options
      await Promise.all(
        options
          .filter((o) => o.text.trim().length > 0)
          .map((o) =>
            api.post('/api/quizzes/option', {
              question_id: qId,
              option_text: o.text.trim(),
              is_correct: o.isCorrect,
            })
          )
      );
      const quizRes = await api.get(`/api/quizzes/${currentQuiz.quiz.id}`);
      setCurrentQuiz(quizRes.data);
      setQuestionText('');
      setOptions([
        { text: '', isCorrect: false },
        { text: '', isCorrect: false },
        { text: '', isCorrect: false },
        { text: '', isCorrect: false },
      ]);
    } catch (err) {
      alert('Failed to save question');
    }
  };

  const handleDeleteQuiz = async (quizId) => {
    const idToDelete = quizId || currentQuiz?.quiz?.id;
    if (!idToDelete) return;
    if (!window.confirm('Delete this quiz?')) return;
    try {
      await api.delete(`/api/quizzes/${idToDelete}`);
      setShowQuizModal(false);
      setCurrentQuiz(null);
      await fetchCurriculum();
      alert('Quiz deleted successfully');
    } catch (err) {
      alert('Failed to delete quiz');
      console.error(err);
    }
  };
  const removeVideo = async (lessonId) => {
  try {
    await api.put(`/api/lessons/${lessonId}`, {
      video_url: null,
    });

    await fetchCurriculum();
  } catch (err) {
    console.error(err);
    toast.error("Failed to remove video");
  }
};

const removePdf = async (lessonId) => {
  try {
    await api.put(`/api/lessons/${lessonId}`, {
      pdf_url: null,
    });

    await fetchCurriculum();
  } catch (err) {
    console.error(err);
    toast.error("Failed to remove PDF");
  }
};

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      
      {/* Header Toolbar */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
        <div className="flex items-center gap-3">
          <Link to={`/mentor/courses/${id}/detail`} className="p-2 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 text-slate-500">
          <ArrowLeft className="w-5 h-5" />
        </Link>
          <div>
            <h1 className="text-3xl font-extrabold text-slate-905 text-slate-900 tracking-tight">Curriculum Builder</h1>
            <p className="text-slate-500 mt-1">Course: <strong className="text-slate-700">{course?.title}</strong></p>
          </div>
        </div>

        <button
          onClick={() => {
            setEditingModule(null);
            setModuleTitle('');
            setModuleDesc('');
            setShowModuleModal(true);
          }}
          className="bg-indigo-650 bg-indigo-600 hover:bg-indigo-755 hover:bg-indigo-700 text-white font-bold text-xs px-5 py-2.5 rounded-xl transition-all shadow-md flex items-center gap-1.5 shrink-0"
        >
          <Plus className="w-4 h-4" /> Add Module
        </button>
      </div>

      {/* Modules List Accordion */}
      {modules.length === 0 ? (
        <div className="text-center py-20 bg-white border border-slate-100 p-8 rounded-3xl shadow-sm">
          <BookOpen className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h3 className="font-bold text-slate-800">Your curriculum is empty</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            Click the "Add Module" button above to establish your first content category drawer.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {modules.map((mod) => (
            <div key={mod.id} className="bg-white border border-slate-100 rounded-2xl shadow-sm overflow-hidden">
              
              {/* Module Header panel */}
              <div className="bg-slate-50/70 p-5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-50">
                <div>
                  <h3 className="font-bold text-slate-800 text-base">{mod.title}</h3>
                  <p className="text-xs text-slate-450 text-slate-400 mt-0.5">{mod.description || 'No description provided'}</p>
                </div>
                
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      setEditingModule(mod);
                      setModuleTitle(mod.title);
                      setModuleDesc(mod.description || '');
                      setShowModuleModal(true);
                    }}
                    className="p-2 bg-white border border-slate-200 rounded-lg text-slate-500 hover:text-indigo-600 hover:bg-slate-50 transition-all text-xs"
                    title="Edit Module Details"
                  >
                    <Edit className="w-4.5 h-4.5" />
                  </button>
                  <button
                    onClick={() => handleDeleteModule(mod.id)}
                    className="p-2 bg-white border border-slate-205 rounded-lg text-slate-500 hover:text-red-600 hover:bg-slate-50 transition-all text-xs"
                    title="Delete Module"
                  >
                    <Trash2 className="w-4.5 h-4.5" />
                  </button>
                  <button
                    onClick={() => {
                      setActiveModuleId(mod.id);
                      setEditingLesson(null);
                      setLessonTitle('');
                      setLessonContent('');
                      setShowLessonModal(true);
                    }}
                    className="bg-indigo-650 bg-indigo-600 hover:bg-indigo-755 hover:bg-indigo-700 text-white font-bold text-xs px-3.5 py-2 rounded-xl transition-all shadow-sm flex items-center gap-1"
                  >
                    <Plus className="w-3.5 h-3.5" /> Add Lesson
                  </button>
                </div>
              </div>

              {/* Module Lessons list */}
              <div className="divide-y divide-slate-100">
                {(mod.lessons || []).length === 0 ? (
                  <div className="p-5 text-xs text-slate-400 italic">No lessons have been created inside this module.</div>
                ) : (
                  (mod.lessons || []).map((les) => (
                    <div key={les.id} className="p-5 flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
                      
                      {/* Lesson title */}
                      <div className="min-w-0 flex items-center gap-3">
                        <div className="bg-slate-100 p-2.5 rounded-lg text-slate-500 shrink-0">
                          {les.pdf_url ? <FileText className="w-5 h-5" /> : <Video className="w-5 h-5" />}
                        </div>
                        <div>
                          <h4 className="font-bold text-slate-800 text-sm leading-snug">{les.title}</h4>
                          <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider block mt-0.5">
                            {les.pdf_url ? 'PDF Lecture' : les.video_url ? 'Video Lecture' : 'Text Lecture'}
                          </span>
                          {les.video_url && (
                          <div className="mt-2 p-2 bg-green-50 rounded border border-green-200 flex items-center gap-2 max-w-max">
                            <span className="text-green-700 text-xs font-semibold">
                              ✓ Video uploaded
                            </span>

                            <a
                              href={getFileUrl(les.video_url)}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-indigo-600 text-xs font-bold hover:underline"
                            >
                              Preview
                            </a>

                            <button
                              onClick={() => removeVideo(les.id)}
                              className="text-red-600 text-xs font-bold hover:underline"
                            >
                              Remove
                            </button>
                          </div>
                        )}
                            {les.pdf_url && (
                            <div className="mt-2 p-2 bg-blue-50 rounded border border-blue-200 flex items-center gap-2 max-w-max">
                              <span className="text-blue-700 text-xs font-semibold">
                                ✓ PDF uploaded
                              </span>

                              <a
                                href={getFileUrl(les.pdf_url)}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-indigo-600 text-xs font-bold hover:underline"
                              >
                                Preview
                              </a>

                              <button
                                onClick={() => removePdf(les.id)}
                                className="text-red-600 text-xs font-bold hover:underline"
                              >
                                Remove
                              </button>
                            </div>
                          )}

                          {les.attachments && les.attachments.length > 0 && (
                            <div className="mt-3 bg-slate-50 border border-slate-100 p-2.5 rounded-xl">
                              <p className="text-xs font-bold text-slate-700 mb-1">Attachments:</p>
                              <div className="space-y-1.5">
                                {les.attachments.map(att => (
                                  <div key={att.id} className="flex items-center gap-2">
                                    <a 
                                      href={att.file_url?.startsWith('/') ? `http://localhost:5000${att.file_url}` : att.file_url}
                                      target="_blank"
                                      rel="noreferrer"
                                      className="text-xs text-indigo-600 underline font-medium"
                                    >
                                      📎 {att.title || att.filename || 'Attachment'}
                                    </a>
                                    <button
                                      onClick={() => handleDeleteAttachment(les.id, att.id)}
                                      className="text-red-500 hover:text-red-700 text-[10px] font-bold"
                                    >
                                      Remove
                                    </button>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Lesson attachments & uploads panel */}
                      <div className="w-full lg:w-auto flex flex-wrap gap-2.5 items-center justify-start lg:justify-end">
                        
                        {/* Attachments pills */}
                        {les.attachments && les.attachments.length > 0 && (
                          <div className="flex gap-1.5 flex-wrap">
                            {les.attachments.map(att => (
                              <span key={att.id} className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-slate-100 border border-slate-200 text-[10px] text-slate-650 font-bold shrink-0 uppercase tracking-wider">
                                {att.title}
                                <button onClick={() => handleDeleteAttachment(les.id, att.id)} className="text-slate-400 hover:text-red-600 font-black ml-1 text-xs shrink-0">×</button>
                              </span>
                            ))}
                          </div>
                        )}

                        {/* File Upload buttons */}
                        <div className="flex gap-2 shrink-0">
                          <button
                            onClick={() => {
                              setUploadingMediaId(les.id);
                              setUploadType('video');
                              setShowLessonModal(false);
                            }}
                            className="bg-slate-55 border border-slate-200 hover:bg-slate-100 text-slate-700 font-bold text-[10px] px-2.5 py-1.5 rounded flex items-center gap-1"
                          >
                            <Video className="w-3.5 h-3.5" /> +Video
                          </button>
                          <button
                            onClick={() => {
                              setUploadingMediaId(les.id);
                              setUploadType('pdf');
                              setShowLessonModal(false);
                            }}
                            className="bg-slate-55 border border-slate-200 hover:bg-slate-100 text-slate-700 font-bold text-[10px] px-2.5 py-1.5 rounded flex items-center gap-1"
                          >
                            <FileText className="w-3.5 h-3.5" /> +PDF
                          </button>
                          <button
                            onClick={() => {
                              setUploadingMediaId(les.id);
                              setUploadType('attachment');
                              setShowLessonModal(false);
                            }}
                            className="bg-slate-55 border border-slate-200 hover:bg-slate-100 text-slate-700 font-bold text-[10px] px-2.5 py-1.5 rounded flex items-center gap-1"
                          >
                            Upload Attachment
                          </button>
                          <button
                            onClick={() => handleOpenQuizBuilder(les)}
                            className={`font-bold text-[10px] px-2.5 py-1.5 rounded flex items-center gap-1 ${
                              les.quiz 
                                ? 'bg-indigo-50 border border-indigo-200 text-indigo-700' 
                                : 'bg-slate-50 border border-slate-200 text-slate-700 hover:bg-slate-100'
                            }`}
                          >
                            <HelpCircle className="w-3.5 h-3.5" /> {les.quiz ? 'Manage Quiz' : '+Quiz'}
                          </button>
                        </div>

                        {/* Edit / Delete Buttons */}
                        <div className="flex gap-2 border-l border-slate-100 pl-2 shrink-0">
                          <button
                            onClick={() => {
                              setEditingLesson(les);
                              setLessonTitle(les.title);
                              setLessonContent(les.content || '');
                              setShowLessonModal(true);
                            }}
                            className="p-1.5 hover:bg-slate-100 text-slate-500 hover:text-indigo-600 rounded"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteLesson(les.id)}
                            className="p-1.5 hover:bg-slate-100 text-slate-500 hover:text-red-650 rounded"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>

                      </div>

                    </div>
                  ))
                )}
              </div>

            </div>
          ))}
        </div>
      )}

      {/* 4. Upload Floating Bar (If active) */}
      {uploadingMediaId && (
        <div className="fixed bottom-6 right-6 bg-white border border-slate-150 p-5 rounded-2xl shadow-2xl z-40 max-w-sm w-full space-y-4">
          <div className="flex justify-between items-center pb-2 border-b border-slate-100">
            <h4 className="font-bold text-xs uppercase text-slate-700 tracking-wider">
              Upload {uploadType === 'video' ? 'Video Lecture' : uploadType === 'pdf' ? 'PDF Slide' : 'Attachment File'}
            </h4>
            <button onClick={() => setUploadingMediaId(null)} disabled={isUploading}>
              <X className="w-4.5 h-4.5 text-slate-400 hover:text-slate-600" />
            </button>
          </div>

          <form onSubmit={handleUploadFileSubmit} className="space-y-3">
            {uploadType === 'attachment' && (
              <input
                type="text"
                required
                disabled={isUploading}
                placeholder="Attachment Label (e.g. Workbook)"
                value={uploadTitle}
                onChange={(e) => setUploadTitle(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 px-3 py-2 rounded-xl text-xs"
              />
            )}
            
            <input
              type="file"
              required
              disabled={isUploading}
              onChange={(e) => setUploadFile(e.target.files[0])}
              accept={
                uploadType === 'video' 
                  ? '.mp4,.mov,.avi' 
                  : uploadType === 'pdf' 
                  ? '.pdf' 
                  : '*'
              }
              className="w-full text-xs"
            />

            {isUploading ? (
              <div className="mt-2 bg-slate-50 p-3 rounded-xl border border-slate-100">
                <div className="flex justify-between text-xs mb-1 font-semibold text-slate-600">
                  <span>Uploading...</span>
                  <span>{uploadProgress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-indigo-600 h-full rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            ) : (
              <button
                type="submit"
                className="w-full bg-indigo-600 text-white font-bold text-xs py-2 rounded-xl flex items-center justify-center gap-1.5 hover:bg-indigo-700 transition-colors"
              >
                <Upload className="w-3.5 h-3.5" /> Start Upload
              </button>
            )}
          </form>
        </div>
      )}

      {/* 5. Module Modal dialog */}
      {showModuleModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm px-4">
          <form onSubmit={handleSaveModule} className="bg-white max-w-md w-full rounded-2xl p-6 shadow-2xl border border-slate-150 space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-slate-100">
              <h3 className="font-bold text-slate-800 text-sm">{editingModule ? 'Edit Module' : 'Create Module'}</h3>
              <button type="button" onClick={() => setShowModuleModal(false)}>
                <X className="w-5 h-5 text-slate-450 text-slate-400" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">Module Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Getting Started & Setup"
                  value={moduleTitle}
                  onChange={(e) => setModuleTitle(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-205 p-3 rounded-xl text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">Description</label>
                <textarea
                  rows={3}
                  placeholder="e.g. Basic initial workspace setups and instructions..."
                  value={moduleDesc}
                  onChange={(e) => setModuleDesc(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-205 p-3 rounded-xl text-sm"
                ></textarea>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-100 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowModuleModal(false)}
                className="px-4 py-2 border border-slate-200 text-slate-700 text-xs font-bold rounded-xl"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="bg-indigo-600 text-white px-5 py-2 rounded-xl text-xs font-bold shadow-md shadow-indigo-100"
              >
                Save Module
              </button>
            </div>
          </form>
        </div>
      )}

      {/* 6. Lesson Modal dialog */}
      {showLessonModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm px-4">
          <form onSubmit={handleSaveLesson} className="bg-white max-w-lg w-full rounded-2xl p-6 shadow-2xl border border-slate-150 space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-slate-100">
              <h3 className="font-bold text-slate-800 text-sm">{editingLesson ? 'Edit Lesson' : 'Create Lesson'}</h3>
              <button type="button" onClick={() => setShowLessonModal(false)}>
                <X className="w-5 h-5 text-slate-400" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">Lesson Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Introduction to Variables"
                  value={lessonTitle}
                  onChange={(e) => setLessonTitle(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-205 p-3 rounded-xl text-sm font-semibold"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">Lesson Text Content</label>
                <textarea
                  rows={5}
                  placeholder="Insert markdown or overview text notes for this lesson..."
                  value={lessonContent}
                  onChange={(e) => setLessonContent(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-205 p-3 rounded-xl text-sm"
                ></textarea>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-100 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowLessonModal(false)}
                className="px-4 py-2 border border-slate-200 text-slate-700 text-xs font-bold rounded-xl"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="bg-indigo-600 text-white px-5 py-2 rounded-xl text-xs font-bold shadow-md shadow-indigo-150"
              >
                Save Lesson
              </button>
            </div>
          </form>
        </div>
      )}

      {/* 7. Quiz Builder Modal dialog */}
      {showQuizModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm px-4">
          <div className="bg-white max-w-xl w-full rounded-2xl p-6 shadow-2xl border border-slate-150 flex flex-col justify-between max-h-[85vh] overflow-hidden">
            
            {/* Header */}
            <div className="flex justify-between items-center pb-4 border-b border-slate-100 shrink-0">
              <h3 className="font-bold text-slate-900 text-base">Quiz Builder</h3>
              <button onClick={() => setShowQuizModal(false)}>
                <X className="w-5 h-5 text-slate-400" />
              </button>
            </div>

            {/* Content area */}
            <div className="flex-1 overflow-y-auto custom-scrollbar py-4 space-y-6">
              
              {!currentQuiz ? (
                // Step 1: Create Quiz
                <form onSubmit={handleCreateQuiz} className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 mb-1">Quiz Title</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Module 1 Knowledge Check"
                      value={quizTitle}
                      onChange={(e) => setQuizTitle(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 p-3 rounded-xl text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 mb-1">Passing Grade (%)</label>
                    <input
                      type="number"
                      min={10}
                      max={100}
                      required
                      value={quizPassPercent}
                      onChange={(e) => setQuizPassPercent(Number(e.target.value))}
                      className="w-full bg-slate-50 border border-slate-200 p-3 rounded-xl text-sm"
                    />
                  </div>
                  <button
                    type="submit"
                    className="w-full bg-indigo-650 bg-indigo-600 text-white font-bold text-xs py-2.5 rounded-xl"
                  >
                    Establish Quiz Template
                  </button>
                </form>
              ) : (
                // Step 2: Add Questions & Options
                <div className="space-y-6">
                  
                  {/* Current Quiz details */}
                  <div className="bg-slate-50 p-4 border border-slate-100 rounded-xl flex justify-between items-center">
                    <div>
                      <h4 className="font-bold text-sm text-slate-800">{currentQuiz.quiz.title}</h4>
                      <p className="text-[10px] text-slate-400 font-semibold uppercase mt-0.5">Passing grade: {currentQuiz.quiz.pass_percentage}%</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleDeleteQuiz(currentQuiz?.quiz?.id)}
                      className="text-xs font-bold text-red-600 border border-red-200 bg-red-50/50 hover:bg-red-50 p-2 rounded-xl"
                    >
                      Delete Quiz
                    </button>
                  </div>

                  {/* Existing questions preview */}
                  <div className="space-y-3">
                    <h4 className="font-bold text-slate-800 text-xs uppercase tracking-wider">Existing Questions ({currentQuiz.questions?.length || 0})</h4>
                    {(currentQuiz.questions || []).map((q, idx) => {
                      const isEditing = editingQuestionId === q.id;
                      return (
                        <div key={q.id} className="p-3.5 border border-slate-100 rounded-xl text-xs space-y-2 bg-white">
                          {isEditing ? (
                            <form onSubmit={handleSaveEditedQuestion} className="space-y-3">
                              <div>
                                <label className="block text-[10px] font-semibold text-slate-500 mb-1">Edit Question Description</label>
                                <input
                                  type="text"
                                  required
                                  value={editQuestionText}
                                  onChange={(e) => setEditQuestionText(e.target.value)}
                                  className="w-full bg-slate-50 border border-slate-200 p-2.5 rounded-xl text-xs font-semibold"
                                />
                              </div>
                              <div className="space-y-2">
                                <label className="block text-[10px] font-semibold text-slate-500">Edit Options & Mark Correct</label>
                                {editOptions.map((opt, oIdx) => (
                                  <div key={opt.id} className="flex gap-2 items-center">
                                    <input
                                      type="radio"
                                      name={`edit-correct-${q.id}`}
                                      checked={opt.is_correct}
                                      onChange={() => {
                                        const updated = editOptions.map((o, index) => ({
                                          ...o,
                                          is_correct: index === oIdx
                                        }));
                                        setEditOptions(updated);
                                      }}
                                      className="w-3.5 h-3.5 accent-indigo-600 shrink-0"
                                    />
                                    <input
                                      type="text"
                                      value={opt.option_text}
                                      onChange={(e) => {
                                        const updated = [...editOptions];
                                        updated[oIdx].option_text = e.target.value;
                                        setEditOptions(updated);
                                      }}
                                      className="flex-1 bg-slate-50 border border-slate-200 p-2 rounded-xl text-xs font-medium"
                                      required
                                    />
                                  </div>
                                ))}
                              </div>
                              <div className="flex justify-end gap-2 pt-1 border-t border-slate-50">
                                <button
                                  type="button"
                                  onClick={handleCancelEditQuestion}
                                  className="px-3 py-1.5 border border-slate-200 text-slate-700 font-bold rounded-lg"
                                >
                                  Cancel
                                </button>
                                <button
                                  type="submit"
                                  className="bg-indigo-600 text-white font-bold px-4 py-1.5 rounded-lg shadow-sm"
                                >
                                  Save Question
                                </button>
                              </div>
                            </form>
                          ) : (
                            <>
                              <div className="flex justify-between items-start gap-2">
                                <p className="font-bold text-slate-800">
                                  {idx + 1}. {q.question_text || q.question}
                                </p>
                                <div className="flex gap-1.5 shrink-0">
                                  <button
                                    onClick={() => handleStartEditQuestion(q)}
                                    className="p-1 text-slate-400 hover:text-indigo-600 rounded"
                                    title="Edit Question"
                                    type="button"
                                  >
                                    <Edit className="w-3.5 h-3.5" />
                                  </button>
                                  <button
                                    onClick={() => handleDeleteQuestion(q.id)}
                                    className="p-1 text-slate-400 hover:text-red-600 rounded"
                                    title="Delete Question"
                                    type="button"
                                  >
                                    <Trash2 className="w-3.5 h-3.5" />
                                  </button>
                                </div>
                              </div>
                              <ul className="list-disc pl-4 text-slate-500 space-y-0.5">
                                {q.options.map((o) => (
                                  <li key={o.id} className={o.is_correct ? 'text-emerald-700 font-semibold' : ''}>
                                    {o.option_text || o.text} {o.is_correct && '(Correct)'}
                                  </li>
                                ))}
                              </ul>
                            </>
                          )}
                        </div>
                      );
                    })}
                  </div>

                  {/* Add question Form */}
                  <form onSubmit={handleAddQuestion} className="border-t border-slate-100 pt-6 space-y-4">
                    <h4 className="font-bold text-slate-800 text-xs uppercase tracking-wider">+ Add New Question</h4>
                    
                    <div>
                      <label className="block text-xs font-semibold text-slate-500 mb-1">Question Description</label>
                      <input
                        type="text"
                        required
                        placeholder="e.g. What is the output of print(2**3)?"
                        value={questionText}
                        onChange={(e) => setQuestionText(e.target.value)}
                        className="w-full bg-slate-50 border border-slate-200 p-3 rounded-xl text-sm font-semibold"
                      />
                    </div>

                    <div className="space-y-2">
                      <label className="block text-xs font-semibold text-slate-500">Provide Options & Check Correct Answer</label>
                      {options.map((opt, idx) => (
                        <div key={idx} className="flex gap-3 items-center">
                          <input
                            type="checkbox"
                            checked={opt.isCorrect}
                            onChange={(e) => {
                              const newOpts = [...options];
                              // Set only this as correct if it's single choice, or allow check
                              newOpts[idx].isCorrect = e.target.checked;
                              setOptions(newOpts);
                            }}
                            className="w-4 h-4 accent-indigo-650 shrink-0"
                          />
                          <input
                            type="text"
                            placeholder={`Option ${idx + 1}`}
                            value={opt.text}
                            required={idx < 2} // At least 2 options required
                            onChange={(e) => {
                              const newOpts = [...options];
                              newOpts[idx].text = e.target.value;
                              setOptions(newOpts);
                            }}
                            className="flex-1 bg-slate-50 border border-slate-200 p-2.5 rounded-xl text-xs font-medium"
                          />
                        </div>
                      ))}
                    </div>

                    <button
                      type="submit"
                      className="w-full bg-indigo-600 text-white font-bold text-xs py-2.5 rounded-xl flex items-center justify-center gap-1.5"
                    >
                      <CheckSquare className="w-4.5 h-4.5" /> Save Question
                    </button>
                  </form>

                </div>
              )}

            </div>

            {/* Footer */}
            <div className="pt-4 border-t border-slate-100 shrink-0">
              <button
                onClick={() => setShowQuizModal(false)}
                className="w-full bg-slate-900 text-white font-bold text-xs py-2.5 rounded-xl"
              >
                Close Builder
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};

export default Curriculum;
