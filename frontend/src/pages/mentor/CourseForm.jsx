import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../../api/axios';
import { BookOpen, ArrowLeft, Plus, CheckCircle, AlertCircle } from 'lucide-react';

const CourseForm = () => {
  const { id } = useParams(); // undefined for create, contains courseId for edit
  const navigate = useNavigate();
  const isEditMode = !!id;

  // Form Fields
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState(0);
  const [level, setLevel] = useState('beginner');
  const [durationHours, setDurationHours] = useState(10);
  const [language, setLanguage] = useState('english');
  const [tagsInput, setTagsInput] = useState('');

  const [loading, setLoading] = useState(false);
  const [fetchLoading, setFetchLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Fetch course details for editing
  useEffect(() => {
    if (isEditMode) {
      const fetchCourse = async () => {
        setFetchLoading(true);
        try {
          const res = await api.get(`/api/courses/${id}`);
          const c = res.data;
          setTitle(c.title);
          setDescription(c.description);
          setPrice(c.price);
          setLevel(c.level || 'beginner');
          setDurationHours(c.duration_hours || 10);
          setLanguage(c.language || 'english');
          setTagsInput((c.tags || []).join(', '));
        } catch (err) {
          setError('Failed to fetch course details for editing');
        } finally {
          setFetchLoading(false);
        }
      };
      fetchCourse();
    }
  }, [id, isEditMode]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    // Format tags array
    const tags = tagsInput
      .split(',')
      .map((t) => t.trim())
      .filter((t) => t.length > 0);

    const payload = {
      title: title.trim(),
      description: description.trim(),
      price: Number(price),
      level,
      duration_hours: Number(durationHours),
      language: language.toLowerCase().trim(),
      tags,
    };

    try {
      if (isEditMode) {
        await api.put(`/api/courses/${id}`, payload);
        setSuccess('Course details updated successfully!');
      } else {
        const res = await api.post('/api/courses', payload);
        setSuccess('Course draft created successfully!');
        setTimeout(() => {
          // Navigate to curriculum builder for newly created course
          navigate(`/mentor/courses/${res.data.id}/curriculum`);
        }, 1500);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to submit course metadata.');
    } finally {
      setLoading(false);
    }
  };

  if (fetchLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-10">
      
      {/* Back Button */}
      <Link 
        to="/mentor/dashboard" 
        className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-indigo-600 mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </Link>

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          {isEditMode ? 'Edit Course Details' : 'Create Course Draft'}
        </h1>
        <p className="text-slate-500 mt-1">
          {isEditMode 
            ? 'Update your course branding, level, pricing, or tag groupings.' 
            : 'Fill in the course branding parameters. You can build curriculum modules on the next page.'}
        </p>
      </div>

      {/* Feedback elements */}
      {error && (
        <div className="bg-red-50 text-red-700 border border-red-100 rounded-xl p-4 flex gap-3 items-start text-sm mb-6">
          <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="bg-emerald-50 text-emerald-700 border border-emerald-100 rounded-xl p-4 flex gap-3 items-start text-sm mb-6">
          <CheckCircle className="w-5 h-5 shrink-0 mt-0.5" />
          <span>{success}</span>
        </div>
      )}

      {/* Form Card */}
      <form onSubmit={handleSubmit} className="bg-white border border-slate-100 p-6 sm:p-8 rounded-2xl shadow-sm space-y-6">
        
        {/* Title */}
        <div>
          <label className="block text-xs font-bold text-slate-450 text-slate-405 uppercase tracking-wider mb-1.5">
            Course Title
          </label>
          <input
            type="text"
            required
            placeholder="e.g. Master Python Programming from Scratch"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 text-slate-750 p-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all text-sm font-semibold"
          />
        </div>

        {/* Description */}
        <div>
          <label className="block text-xs font-bold text-slate-405 uppercase tracking-wider mb-1.5">
            Course Overview Description
          </label>
          <textarea
            required
            rows={5}
            placeholder="Explain what students will learn, project details, and why they should enroll..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 text-slate-750 p-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all text-sm font-medium"
          ></textarea>
        </div>

        {/* Level, Price, Hours grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          
          {/* Level Selection */}
          <div>
            <label className="block text-xs font-bold text-slate-405 uppercase tracking-wider mb-1.5">
              Course Level
            </label>
            <select
              value={level}
              onChange={(e) => setLevel(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 text-slate-750 p-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 select-none text-sm font-semibold"
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>

          {/* Pricing */}
          <div>
            <label className="block text-xs font-bold text-slate-405 uppercase tracking-wider mb-1.5">
              Price (USD)
            </label>
            <input
              type="number"
              min={0}
              required
              placeholder="0 for Free"
              value={price}
              onChange={(e) => setPrice(Number(e.target.value))}
              className="w-full bg-slate-50 border border-slate-200 text-slate-750 p-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all text-sm font-semibold"
            />
          </div>

          {/* Duration */}
          <div>
            <label className="block text-xs font-bold text-slate-405 uppercase tracking-wider mb-1.5">
              Total Duration (Hours)
            </label>
            <input
              type="number"
              min={1}
              required
              value={durationHours}
              onChange={(e) => setDurationHours(Number(e.target.value))}
              className="w-full bg-slate-50 border border-slate-200 text-slate-750 p-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all text-sm font-semibold"
            />
          </div>

        </div>

        {/* Language & Tags grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          
          {/* Language */}
          <div>
            <label className="block text-xs font-bold text-slate-405 uppercase tracking-wider mb-1.5">
              Language
            </label>
            <input
              type="text"
              required
              placeholder="e.g. English, Spanish, French"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 text-slate-750 p-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all text-sm font-semibold"
            />
          </div>

          {/* Tags */}
          <div>
            <label className="block text-xs font-bold text-slate-405 uppercase tracking-wider mb-1.5">
              Tag Keywords (Comma separated)
            </label>
            <input
              type="text"
              placeholder="e.g. programming, code, web, basic"
              value={tagsInput}
              onChange={(e) => setTagsInput(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 text-slate-755 p-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all text-sm font-semibold"
            />
          </div>

        </div>

        {/* Form buttons */}
        <div className="pt-6 border-t border-slate-50 flex justify-end gap-3">
          <Link
            to="/mentor/dashboard"
            className="px-5 py-3 border border-slate-200 text-slate-700 font-bold text-xs rounded-xl hover:bg-slate-50"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={loading}
            className="bg-indigo-650 bg-indigo-600 hover:bg-indigo-755 hover:bg-indigo-700 text-white font-bold text-xs px-6 py-3 rounded-xl transition-all shadow-md shadow-indigo-100 hover:shadow-lg"
          >
            {loading ? 'Submitting...' : isEditMode ? 'Save Changes' : 'Build Curriculum'}
          </button>
        </div>

      </form>

    </div>
  );
};

export default CourseForm;
