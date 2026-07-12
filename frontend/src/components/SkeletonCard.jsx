import React from 'react';

const SkeletonCard = () => {
  return (
    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden flex flex-col h-full animate-pulse">
      {/* Thumbnail aspect-video placeholder */}
      <div className="bg-slate-200 aspect-video w-full"></div>

      {/* Body placeholders */}
      <div className="p-5 flex flex-col flex-1 space-y-3">
        {/* Level & Tags line */}
        <div className="flex gap-2">
          <div className="bg-slate-200 h-4 w-12 rounded"></div>
          <div className="bg-slate-200 h-4 w-16 rounded"></div>
        </div>

        {/* Title line */}
        <div className="space-y-2">
          <div className="bg-slate-200 h-5 w-full rounded"></div>
          <div className="bg-slate-200 h-5 w-4/5 rounded"></div>
        </div>

        {/* Info row */}
        <div className="flex gap-4">
          <div className="bg-slate-200 h-3 w-16 rounded"></div>
          <div className="bg-slate-200 h-3 w-20 rounded"></div>
        </div>

        {/* Rating line */}
        <div className="bg-slate-200 h-4 w-28 rounded"></div>

        {/* Footer row */}
        <div className="border-t border-slate-50 pt-4 flex justify-between items-center mt-auto">
          <div className="space-y-1">
            <div className="bg-slate-200 h-2.5 w-14 rounded"></div>
            <div className="bg-slate-200 h-5 w-16 rounded"></div>
          </div>
          <div className="bg-slate-200 h-9 w-28 rounded-full"></div>
        </div>
      </div>
    </div>
  );
};

export default SkeletonCard;
