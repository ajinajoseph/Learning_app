import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import api from '../api/axios';

const Success = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState('loading'); // loading, success, error
  const [message, setMessage] = useState('Verifying your payment and securing your enrollment...');
  const [courseTitle, setCourseTitle] = useState('');
  const [error, setError] = useState('');

  const sessionId = searchParams.get('session_id');
  const provider = searchParams.get('provider');
  const token = searchParams.get('token');

  useEffect(() => {
    const confirmPayment = async () => {
      try {
        if (provider === 'paypal') {
          // PayPal Flow
          if (!token) {
            setStatus('error');
            setMessage('PayPal token is missing.');
            return;
          }
          const res = await api.post(`/api/payments/paypal/capture/${token}`);
          setStatus('success');
          setMessage('Payment captured! Your enrollment is now active.');
        } else {
          // Stripe Flow
          if (!sessionId) {
            setStatus('error');
            setMessage('Missing Stripe session ID.');
            return;
          }
          const res = await api.post(`/api/payments/stripe/confirm/${sessionId}`);
          if (res.data && res.data.success) {
            setStatus('success');
            setMessage('Enrollment confirmed successfully!');
            if (res.data.course_title) {
              setCourseTitle(res.data.course_title);
            }
          } else {
            setStatus('error');
            setMessage(res.data?.message || 'Payment verification failed.');
          }
        }
      } catch (error) {
        console.error('Payment confirmation error:', error);
        console.log("Full error:", error.response?.data);
        setStatus('error');
        setError(error.response?.data?.message || error.message || "Verification failed");
        if (error.response?.status === 401) {
          // If token expired or unauthorized, prompt login redirect
          setTimeout(() => {
            navigate('/login');
          }, 4000);
        }
      }
    };

    confirmPayment();
  }, [sessionId, provider, token, navigate]);

  return (
    <div className="flex min-h-[80vh] items-center justify-center bg-gray-50/50 px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8 rounded-2xl border border-gray-100 bg-white p-8 shadow-xl text-center">
        {status === 'loading' && (
          <div className="flex flex-col items-center justify-center space-y-6 py-6">
            {/* Spinning Circle */}
            <div className="relative h-16 w-16">
              <div className="absolute inset-0 rounded-full border-4 border-indigo-100"></div>
              <div className="absolute inset-0 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent"></div>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Processing Payment</h2>
              <p className="mt-2 text-sm text-gray-500 max-w-xs mx-auto leading-relaxed">{message}</p>
            </div>
          </div>
        )}

        {status === 'success' && (
          <div className="flex flex-col items-center justify-center space-y-6 py-4">
            {/* Animated Success Check */}
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-green-50 animate-bounce">
              <svg className="h-10 w-10 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            
            <div className="space-y-2">
              <h2 className="text-2xl font-bold text-gray-900 tracking-tight">Enrollment Confirmed!</h2>
              <p className="text-sm text-gray-600 font-medium">{message}</p>
            </div>

            {courseTitle && (
              <div className="w-full rounded-xl bg-indigo-50/60 border border-indigo-100/50 p-4 mt-2">
                <span className="text-xs uppercase tracking-wider font-semibold text-indigo-600">Enrolled In</span>
                <p className="mt-1 text-base font-bold text-indigo-900 leading-snug">{courseTitle}</p>
              </div>
            )}

            <div className="w-full pt-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="w-full rounded-xl bg-indigo-600 px-6 py-3.5 text-sm font-semibold text-white shadow-md transition-all hover:bg-indigo-700 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 active:scale-[0.98]"
              >
                Go to My Learning
              </button>
            </div>
          </div>
        )}

        {status === 'error' && (
          <div className="flex flex-col items-center justify-center space-y-6 py-4">
            {/* Animated Error Cross */}
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-red-50 animate-pulse">
              <svg className="h-10 w-10 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>

            <div className="space-y-2">
              <h2 className="text-2xl font-bold text-gray-900 tracking-tight">Verification Failed</h2>
              <p className="text-sm text-red-600 font-medium bg-red-50/40 rounded-lg p-3 leading-relaxed">{error}</p>
            </div>

            <div className="w-full pt-4 space-y-3">
              <button
                onClick={() => window.location.reload()}
                className="w-full rounded-xl bg-gray-900 px-6 py-3.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-gray-800 focus:outline-none"
              >
                Try Again
              </button>
              <button
                onClick={() => navigate('/courses')}
                className="w-full rounded-xl border border-gray-200 bg-white px-6 py-3.5 text-sm font-semibold text-gray-700 hover:bg-gray-50 focus:outline-none"
              >
                Browse Other Courses
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Success;
