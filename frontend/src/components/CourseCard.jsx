import React from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Star, Globe, Clock, User } from 'lucide-react';

export const getCourseThumbnail = (title = '') => {
  const t = title.toLowerCase();
  if (t.includes('react') || t.includes('javascript') || t.includes('frontend') || t.includes('node')) {
    return 'https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=400&auto=format&fit=crop&q=80';
  }
  if (t.includes('python') || t.includes('django') || t.includes('backend') || t.includes('flask')) {
    return 'https://images.unsplash.com/photo-1649180556628-9ba704115795?q=80&w=400&auto=format&fit=crop';
  }
  if (t.includes('design') || t.includes('ux') || t.includes('ui') || t.includes('figma')) {
    return 'https://images.unsplash.com/photo-1587440871875-191322ee64b0?q=80&w=400&auto=format&fit=crop';
  }
  if (t.includes('business') || t.includes('marketing') || t.includes('finance') || t.includes('sales')) {
    return 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&auto=format&fit=crop&q=80';
  }
  if (t.includes('data') || t.includes('machine') || t.includes('ai') || t.includes('science') || t.includes('database')) {
    return 'https://plus.unsplash.com/premium_photo-1661878265739-da90bc1af051?q=80&w=400&auto=format&fit=crop';
  }
  return 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&auto=format&fit=crop&q=80';
};
const CourseCard = ({ course, progress, isMentorView,onView }) => {
  const { id, title, price, level, duration_hours, language, tags } = course;

  const getLevelColor = (lvl) => {
    const l = lvl?.toLowerCase();
    if (l === 'beginner') return 'bg-emerald-50 text-emerald-700 border-emerald-100';
    if (l === 'intermediate') return 'bg-blue-50 text-blue-700 border-blue-100';
    return 'bg-purple-50 text-purple-700 border-purple-100';
  };

  const thumbnail = getCourseThumbnail(title);

  return (
    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden flex flex-col card-hover h-full">
      {/* Thumbnail */}
      <div className="relative aspect-video w-full overflow-hidden bg-slate-100 shrink-0">
        <img
          src={thumbnail}
          alt={title}
          className="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
          loading="lazy"
        />
        <div className="absolute top-3 left-3 flex gap-2">
          <span className={`px-2.5 py-0.5 text-xs font-semibold rounded-full border uppercase tracking-wider ${getLevelColor(level)}`}>
            {level}
          </span>
        </div>
      </div>

      {/* Body */}
      <div className="p-5 flex flex-col flex-1">
        <div className="flex gap-2 flex-wrap mb-2">
          {(tags || []).slice(0, 2).map((tag, idx) => (
            <span key={idx} className="bg-slate-100 text-slate-600 text-[10px] font-semibold px-2 py-0.5 rounded uppercase">
              {tag}
            </span>
          ))}
        </div>

        <h3 className="font-bold text-slate-800 text-base leading-snug line-clamp-2 mb-1.5 hover:text-indigo-600 transition-colors">
          {title}
        </h3>

        <div className="flex items-center gap-1.5 mb-3 text-slate-500 text-xs">
          <span className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5" />
            {duration_hours || '12'} hrs
          </span>
          <span className="w-1 h-1 bg-slate-300 rounded-full"></span>
          <span className="flex items-center gap-1 capitalize">
            <Globe className="w-3.5 h-3.5" />
            {language}
          </span>
        </div>

        {/* Rating Placeholder */}
        <div className="flex items-center gap-1 mb-4">
          <Star className="w-4 h-4 fill-amber-400 text-amber-400 shrink-0" />
          <span className="text-sm font-bold text-slate-800">4.7</span>
          <span className="text-xs text-slate-400 font-medium">(184 reviews)</span>
        </div>

        {/* Action / Progress Row */}
        <div className="mt-auto border-t border-slate-50 pt-4 flex items-center justify-between gap-4">
          {progress !== undefined ? (
  <div className="w-full space-y-3">
    <div>
      <div className="flex justify-between items-center mb-1 text-xs font-semibold text-slate-600">
        <span>Progress</span>
        <span className="text-indigo-600">{Math.round(progress)}%</span>
      </div>

      <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
        <div
          className="bg-indigo-600 h-full rounded-full transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>

    <Link
  to={`/learn/${id}`}
  className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition text-center"
>
  Continue Learning
</Link>
  </div>
) : (
            <>
              <div className="flex flex-col">
                <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Course Price</span>
                <span className="text-lg font-extrabold text-slate-800">
                  {price === 0 ? (
                    <span className="text-emerald-600 font-bold">Free</span>
                  ) : (
                    `$${price.toFixed(2)}`
                  )}
                </span>
              </div>
              
              {isMentorView ? (
  <Link
    to={`/mentor/courses/${id}/curriculum`}
    className="bg-indigo-50 text-indigo-600 hover:bg-indigo-600 hover:text-white font-bold text-xs px-4 py-2.5 rounded-full transition-all flex items-center gap-1.5 hover:shadow-md"
  >
    <BookOpen className="w-3.5 h-3.5" />
    Build Curriculum
  </Link>
) : (
  <button
    onClick={() => onView && onView(id)}
    className="bg-indigo-50 text-indigo-600 hover:bg-indigo-600 hover:text-white font-bold text-xs px-4 py-2.5 rounded-full transition-all flex items-center gap-1.5 hover:shadow-md"
  >
    <BookOpen className="w-3.5 h-3.5" />
    View Course
  </button>
)}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default CourseCard;
