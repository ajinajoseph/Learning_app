import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { logout } from '../store/authSlice';
import { setNotifications, setUnreadCount, addNotification } from '../store/notificationSlice';
import api from '../api/axios';
import NotificationDropdown from './NotificationDropdown';
import { io } from 'socket.io-client';
import { 
  BookOpen, Search, Bell, User, LogOut, LayoutDashboard, 
  Menu, X, BookCheck, Shield, ChevronDown, ListCollapse
} from 'lucide-react';
const BACKEND_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  const { isAuthenticated, user } = useSelector((state) => state.auth);
  const { unreadCount } = useSelector((state) => state.notifications);

  // UI state
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const autocompleteRef = useRef(null);
  const socketRef = useRef(null);

  // Socket.IO for notifications
  useEffect(() => {
    if (isAuthenticated && user) {
      try {
        const token = localStorage.getItem('token') || localStorage.getItem('access_token');
        // Connect to Socket.IO backend
        socketRef.current =io(BACKEND_URL, {
          transports: ['websocket', 'polling'],
          reconnection: true,
          reconnectionAttempts: 5,
          reconnectionDelay: 1000,
          auth: { token: token }
        });

        // Listen for notifications
        socketRef.current.on('notification', (newNotif) => {
          // Only add if it belongs to this user
          if (newNotif.user_id === user.id) {
            dispatch(addNotification(newNotif));
          }
        });
      } catch (err) {
        console.error('Socket connection error in Navbar:', err);
      }

      // Fetch initial notifications & unread count
      const fetchNotifications = async () => {
        try {
          const res = await api.get('/api/notifications');
          dispatch(setNotifications(res.data));
          
          const countRes = await api.get('/api/notifications/unread-count');
          dispatch(setUnreadCount(countRes.data.unread_count));
        } catch (err) {
          console.error('Failed to load notifications:', err);
        }
      };

      fetchNotifications();

      return () => {
        if (socketRef.current) {
          socketRef.current.disconnect();
        }
      };
    }
  }, [isAuthenticated, user, dispatch]);

  // Autocomplete search handler
  useEffect(() => {
    const fetchAutocomplete = async () => {
      if (searchQuery.trim().length > 1) {
        try {
          const res = await api.get(`/api/search/autocomplete?q=${searchQuery}`);
          // The endpoint returns list of courses / keywords
          setSuggestions(res.data);
          setShowSuggestions(true);
        } catch (err) {
          console.error(err);
        }
      } else {
        setSuggestions([]);
        setShowSuggestions(false);
      }
    };

    const timer = setTimeout(() => {
      fetchAutocomplete();
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Close dropdowns on outside click
  useEffect(() => {
    const handleOutsideClick = (e) => {
      if (autocompleteRef.current && !autocompleteRef.current.contains(e.target)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleOutsideClick);
    return () => document.removeEventListener('mousedown', handleOutsideClick);
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setShowSuggestions(false);
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  const handleLogout = () => {
    dispatch(logout());
    setIsProfileOpen(false);
    navigate('/login');
  };

  const getDashboardPath = () => {
    if (user?.role === 'admin') return '/admin/dashboard';
    if (user?.role === 'mentor') return '/mentor/dashboard';
    return '/dashboard';
  };

  return (
    <nav className="glass-nav sticky top-0 z-40 w-full transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center gap-4">
          
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 shrink-0">
            <div className="bg-indigo-600 p-2 rounded-lg text-white shadow-md shadow-indigo-200">
              <BookOpen className="w-6 h-6" />
            </div>
            <span className="font-extrabold text-2xl tracking-tight bg-gradient-to-r from-indigo-600 to-blue-600 bg-clip-text text-transparent">
              EduFlex
            </span>
          </Link>

          {/* Autocomplete Search Bar */}
          <form 
            onSubmit={handleSearchSubmit} 
            className="hidden md:flex relative flex-1 max-w-md"
            ref={autocompleteRef}
          >
            <input
              type="text"
              placeholder="Search courses or mentors..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => searchQuery.trim().length > 1 && setShowSuggestions(true)}
              className="w-full bg-slate-50 border border-slate-200 text-slate-700 placeholder-slate-400 pl-10 pr-4 py-2 rounded-full focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all text-sm"
            />
            <Search className="absolute left-3.5 top-2.5 w-4 h-4 text-slate-400" />
            
            {showSuggestions && suggestions.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-slate-100 rounded-xl shadow-2xl z-50 py-2 max-h-60 overflow-y-auto">
                {suggestions.map((item, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => {
                      setSearchQuery(item.title || item);
                      setShowSuggestions(false);
                      navigate(`/search?q=${encodeURIComponent(item.title || item)}`);
                    }}
                    className="w-full px-4 py-2 hover:bg-slate-50 text-left text-sm text-slate-700 flex items-center gap-2"
                  >
                    <Search className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    <span className="truncate">{item.title || item}</span>
                  </button>
                ))}
              </div>
            )}
          </form>

          {/* Right Navigation */}
          <div className="hidden md:flex items-center gap-4">
            <Link to="/courses" className="text-slate-600 hover:text-indigo-600 font-medium text-sm transition-colors">
              Explore Courses
            </Link>

            {isAuthenticated ? (
              <>
                {/* Dashboard Shortcut */}
                <Link 
                  to={getDashboardPath()} 
                  className="text-slate-600 hover:text-indigo-600 font-medium text-sm flex items-center gap-1.5 transition-colors"
                >
                  <LayoutDashboard className="w-4 h-4" />
                  Dashboard
                </Link>

                {/* Notifications Bell */}
                <div className="relative">
                  <button 
                    onClick={() => {
                      setIsNotifOpen(!isNotifOpen);
                      setIsProfileOpen(false);
                    }}
                    className="p-2 text-slate-500 hover:text-indigo-600 hover:bg-slate-50 rounded-full transition-all relative"
                  >
                    <Bell className="w-5 h-5" />
                    {unreadCount > 0 && (
                      <span className="absolute top-1.5 right-1.5 w-4.5 h-4.5 bg-red-500 text-white rounded-full text-[9px] font-bold flex items-center justify-center border-2 border-white min-w-[18px] px-0.5">
                        {unreadCount > 99 ? '99+' : unreadCount}
                      </span>
                    )}
                  </button>
                  <NotificationDropdown isOpen={isNotifOpen} onClose={() => setIsNotifOpen(false)} />
                </div>

                {/* User Profile Dropdown */}
                <div className="relative">
                  <button 
                    onClick={() => {
                      setIsProfileOpen(!isProfileOpen);
                      setIsNotifOpen(false);
                    }}
                    className="flex items-center gap-1.5 p-1 px-2.5 hover:bg-slate-50 rounded-full border border-slate-200 transition-all"
                  >
                    <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 font-semibold flex items-center justify-center text-sm uppercase shadow-sm">
                      {user?.name?.substring(0, 2)}
                    </div>
                    <span className="text-xs font-semibold text-slate-700 hidden lg:inline max-w-[100px] truncate">{user?.name}</span>
                    <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                  </button>

                  {isProfileOpen && (
                    <div className="absolute right-0 mt-3 w-56 bg-white rounded-xl shadow-2xl border border-slate-100 z-50 py-2 overflow-hidden">
                      <div className="px-4 py-2.5 border-b border-slate-50 bg-slate-50/50">
                        <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">Signed in as</p>
                        <p className="text-sm font-semibold text-slate-800 truncate">{user?.name}</p>
                        <span className="inline-block px-2 py-0.5 mt-1 text-[10px] font-bold uppercase rounded bg-indigo-50 text-indigo-600 border border-indigo-100">
                          {user?.role}
                        </span>
                      </div>
                      
                      {user?.role === 'student' && (
                        <>
                          <Link to="/my-courses" onClick={() => setIsProfileOpen(false)} className="px-4 py-2 hover:bg-slate-50 text-slate-700 text-sm flex items-center gap-2 transition-colors">
                            <BookCheck className="w-4 h-4 text-slate-400" /> My Learning
                          </Link>
                          <Link to="/certificates" onClick={() => setIsProfileOpen(false)} className="px-4 py-2 hover:bg-slate-50 text-slate-700 text-sm flex items-center gap-2 transition-colors">
                            <Shield className="w-4 h-4 text-slate-400" /> Certificates
                          </Link>
                        </>
                      )}

                      {user?.role === 'mentor' && (
                        <>
                          <Link to="/mentor/courses" onClick={() => setIsProfileOpen(false)} className="px-4 py-2 hover:bg-slate-50 text-slate-700 text-sm flex items-center gap-2 transition-colors">
                            <ListCollapse className="w-4 h-4 text-slate-400" /> My Courses
                          </Link>
                        </>
                      )}

                      <Link to="/profile" onClick={() => setIsProfileOpen(false)} className="px-4 py-2 hover:bg-slate-50 text-slate-700 text-sm flex items-center gap-2 transition-colors">
                        <User className="w-4 h-4 text-slate-400" /> Edit Profile
                      </Link>

                      <button
                        onClick={handleLogout}
                        className="w-full text-left px-4 py-2 hover:bg-red-50 text-red-600 border-t border-slate-50 text-sm flex items-center gap-2 transition-colors font-medium mt-1.5"
                      >
                        <LogOut className="w-4 h-4" /> Log Out
                      </button>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="flex items-center gap-3">
                <Link to="/login" className="text-slate-600 hover:text-indigo-600 font-semibold text-sm transition-colors px-3 py-2">
                  Sign In
                </Link>
                <Link to="/register" className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm px-4 py-2 rounded-full transition-all shadow-md shadow-indigo-100 hover:shadow-lg hover:shadow-indigo-200">
                  Register
                </Link>
              </div>
            )}
          </div>

          {/* Mobile hamburger menu */}
          <div className="flex md:hidden items-center gap-2">
            {isAuthenticated && (
              <div className="relative">
                <button 
                  onClick={() => setIsNotifOpen(!isNotifOpen)}
                  className="p-2 text-slate-500 hover:text-indigo-600 rounded-full transition-colors relative"
                >
                  <Bell className="w-5 h-5" />
                  {unreadCount > 0 && (
                    <span className="absolute top-1.5 right-1.5 w-4 h-4 bg-red-500 text-white rounded-full text-[9px] font-bold flex items-center justify-center">
                      {unreadCount}
                    </span>
                  )}
                </button>
                <NotificationDropdown isOpen={isNotifOpen} onClose={() => setIsNotifOpen(false)} />
              </div>
            )}

            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2 text-slate-600 hover:text-indigo-600 rounded-lg focus:outline-none"
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>

        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t border-slate-100 bg-white px-4 pt-2 pb-6 space-y-3">
          <form onSubmit={handleSearchSubmit} className="relative w-full my-2">
            <input
              type="text"
              placeholder="Search courses..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 pl-10 pr-4 py-2 rounded-full text-sm"
            />
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
          </form>

          <Link 
            to="/courses" 
            onClick={() => setIsMobileMenuOpen(false)}
            className="block text-slate-700 hover:text-indigo-600 font-medium py-2"
          >
            Explore Courses
          </Link>

          {isAuthenticated ? (
            <div className="space-y-2 pt-2 border-t border-slate-100">
              <div className="pb-2">
                <p className="text-xs text-slate-400 font-medium uppercase">Signed in as</p>
                <p className="font-semibold text-slate-800">{user?.name}</p>
              </div>

              <Link 
                to={getDashboardPath()}
                onClick={() => setIsMobileMenuOpen(false)}
                className="block text-slate-700 hover:text-indigo-600 font-medium py-2"
              >
                Dashboard
              </Link>

              {user?.role === 'student' && (
                <>
                  <Link to="/my-courses" onClick={() => setIsMobileMenuOpen(false)} className="block text-slate-700 hover:text-indigo-600 font-medium py-2">
                    My Learning
                  </Link>
                  <Link to="/certificates" onClick={() => setIsMobileMenuOpen(false)} className="block text-slate-700 hover:text-indigo-600 font-medium py-2">
                    Certificates
                  </Link>
                </>
              )}

              {user?.role === 'mentor' && (
                <Link to="/mentor/courses" onClick={() => setIsMobileMenuOpen(false)} className="block text-slate-700 hover:text-indigo-600 font-medium py-2">
                  My Courses
                </Link>
              )}

              <Link to="/profile" onClick={() => setIsMobileMenuOpen(false)} className="block text-slate-700 hover:text-indigo-600 font-medium py-2">
                Edit Profile
              </Link>

              <button
                onClick={handleLogout}
                className="w-full text-left font-medium py-2 text-red-600 border-t border-slate-100 mt-2"
              >
                Log Out
              </button>
            </div>
          ) : (
            <div className="flex flex-col gap-2 pt-2 border-t border-slate-100">
              <Link 
                to="/login" 
                onClick={() => setIsMobileMenuOpen(false)}
                className="text-center text-slate-700 font-semibold py-2.5 rounded-full hover:bg-slate-50 border border-slate-200"
              >
                Sign In
              </Link>
              <Link 
                to="/register" 
                onClick={() => setIsMobileMenuOpen(false)}
                className="text-center bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2.5 rounded-full"
              >
                Register
              </Link>
            </div>
          )}
        </div>
      )}
    </nav>
  );
};

export default Navbar;
