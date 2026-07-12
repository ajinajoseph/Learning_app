import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { markNotificationRead } from '../store/notificationSlice';
import api from '../api/axios';
import { Bell, CheckCircle2, MessageSquare, BookOpen, AlertCircle } from 'lucide-react';

const NotificationDropdown = ({ isOpen, onClose }) => {
  const dispatch = useDispatch();
  const { notifications } = useSelector((state) => state.notifications);

  const handleMarkAsRead = async (id) => {
    try {
      await api.put(`/api/notifications/read/${id}`);
      dispatch(markNotificationRead(id));
    } catch (err) {
      console.error('Failed to mark notification as read:', err);
    }
  };

  const getIcon = (title = '') => {
    const t = title.toLowerCase();
    if (t.includes('chat') || t.includes('message') || t.includes('q&a')) {
      return <MessageSquare className="w-5 h-5 text-blue-500" />;
    }
    if (t.includes('approve') || t.includes('success') || t.includes('complete')) {
      return <CheckCircle2 className="w-5 h-5 text-emerald-500" />;
    }
    if (t.includes('course') || t.includes('lesson')) {
      return <BookOpen className="w-5 h-5 text-indigo-500" />;
    }
    return <AlertCircle className="w-5 h-5 text-amber-500" />;
  };

  if (!isOpen) return null;

  return (
    <div className="absolute right-0 mt-3 w-80 sm:w-96 bg-white rounded-xl shadow-2xl border border-slate-100 z-50 overflow-hidden">
      <div className="p-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
        <h3 className="font-semibold text-slate-800 flex items-center gap-2">
          <Bell className="w-4 h-4 text-indigo-600" /> Notifications
        </h3>
        <button 
          onClick={onClose}
          className="text-xs text-indigo-600 hover:text-indigo-800 font-medium"
        >
          Close
        </button>
      </div>

      <div className="max-h-[360px] overflow-y-auto custom-scrollbar">
        {notifications.length === 0 ? (
          <div className="py-12 text-center text-slate-400 flex flex-col items-center justify-center gap-2">
            <Bell className="w-8 h-8 text-slate-300" />
            <p className="text-sm font-medium">All caught up!</p>
            <p className="text-xs">You'll see alerts and updates here.</p>
          </div>
        ) : (
          notifications.map((notification) => (
            <div
              key={notification.id}
              onClick={() => !notification.is_read && handleMarkAsRead(notification.id)}
              className={`p-4 border-b border-slate-50 flex gap-3 transition-colors cursor-pointer ${
                notification.is_read ? 'hover:bg-slate-50' : 'bg-indigo-50/40 hover:bg-indigo-50/70'
              }`}
            >
              <div className="mt-0.5 shrink-0">
                {getIcon(notification.title)}
              </div>
              <div className="flex-1">
                <div className="flex justify-between items-baseline mb-0.5">
                  <h4 className={`text-sm ${notification.is_read ? 'font-medium text-slate-700' : 'font-semibold text-slate-900'}`}>
                    {notification.title}
                  </h4>
                  {!notification.is_read && (
                    <span className="w-2 h-2 bg-indigo-600 rounded-full shrink-0"></span>
                  )}
                </div>
                <p className="text-xs text-slate-500 leading-relaxed">
                  {notification.message}
                </p>
                <span className="text-[10px] text-slate-400 block mt-1">
                  {new Date(notification.created_at || Date.now()).toLocaleDateString(undefined, {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default NotificationDropdown;
