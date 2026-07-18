import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './store/store';

// Layout & guards
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ProtectedRoute from './components/ProtectedRoute';

// Public pages
import Landing from './pages/Landing';
import CourseList from './pages/CourseList';
import CourseDetail from './pages/CourseDetail';
import Login from './pages/Login';
import ForgotPassword from './pages/ForgotPassword';
import Register from './pages/Register';
import Search from './pages/Search';

// Student pages
import StudentDashboard from './pages/student/Dashboard';
import StudentMyCourses from './pages/student/MyCourses';
import StudentLearnPage from './pages/student/LearnPage';
import Success from './pages/Success';
import Certificates from './pages/student/Certificates';
import StudentPaymentHistory from './pages/student/PaymentHistory';
import StudentProfile from './pages/student/Profile';

// Mentor pages
import MentorDashboard from './pages/mentor/Dashboard';
import MentorMyCourses from './pages/mentor/MyCourses';
import CourseForm from './pages/mentor/CourseForm';
import Curriculum from './pages/mentor/Curriculum';
import MentorAnalytics from './pages/mentor/Analytics';
import MentorCourseDetail from './pages/mentor/MentorCourseDetail';

// Admin pages
import AdminDashboard from './pages/admin/Dashboard';
import AdminUsers from './pages/admin/Users';
import AdminCourses from './pages/admin/Courses';
import AdminMentors from './pages/admin/Mentors';
import AdminReviews from './pages/admin/Reviews';

function AppContent() {
  const location = useLocation();
  const hideNavAndFooter = ['/login', '/register', '/forgot-password'].includes(location.pathname);

  return (
    <div className="flex flex-col min-h-screen bg-[#F9FAFB]">
      {!hideNavAndFooter && <Navbar />}
      
      {/* Main Content Area */}
      <main className="flex-grow">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Landing />} />
          <Route path="/courses" element={<CourseList />} />
          <Route path="/courses/:id" element={<CourseDetail />} />
          <Route path="/login" element={<Login />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/register" element={<Register />} />
          <Route path="/search" element={<Search />} />

          {/* Student Routes */}
          <Route element={<ProtectedRoute allowedRoles={['student']} />}>
            <Route path="/dashboard" element={<StudentDashboard />} />
            <Route path="/my-courses" element={<StudentMyCourses />} />
            <Route path="/learn/:courseId" element={<StudentLearnPage />} />
            <Route path="/certificates" element={<Certificates />} />
            <Route path="/payments" element={<StudentPaymentHistory />} />
            <Route path="/profile" element={<StudentProfile />} />
            <Route path="/success" element={<Success />} />
          </Route>

          {/* Mentor Routes */}
          <Route element={<ProtectedRoute allowedRoles={['mentor']} />}>
            <Route path="/mentor/dashboard" element={<MentorDashboard />} />
            <Route path="/mentor/courses" element={<MentorMyCourses />} />
            <Route path="/mentor/courses/new" element={<CourseForm />} />
            <Route path="/mentor/courses/:id/edit" element={<CourseForm />} />
            <Route path="/mentor/courses/:id/curriculum" element={<Curriculum />} />
            <Route path="/mentor/courses/:id/analytics" element={<MentorAnalytics />} />
            <Route path="/mentor/courses/:courseId/detail" element={<MentorCourseDetail />} />
          </Route>

          {/* Admin Routes */}
          <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
            <Route path="/admin/dashboard" element={<AdminDashboard />} />
            <Route path="/admin/users" element={<AdminUsers />} />
            <Route path="/admin/courses" element={<AdminCourses />} />
            <Route path="/admin/mentors" element={<AdminMentors />} />
            <Route path="/admin/reviews" element={<AdminReviews />} />
          </Route>

          {/* Fallback Catch-All */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      {!hideNavAndFooter && <Footer />}
    </div>
  );
}

function App() {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </Provider>
  );
}

export default App;
