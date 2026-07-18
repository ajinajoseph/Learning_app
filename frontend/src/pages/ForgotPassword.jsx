import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Mail, KeyRound, Lock, Eye, EyeOff, ArrowLeft, CheckCircle2 } from 'lucide-react';

const STEPS = {
  EMAIL: 'email',
  OTP: 'otp',
  NEW_PASSWORD: 'new_password',
  SUCCESS: 'success'
};

const ForgotPassword = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(STEPS.EMAIL);
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [resendTimer, setResendTimer] = useState(0);

  // ── Step 1: Send OTP ──────────────────────────────────────
  const handleSendOTP = async (e) => {
    e.preventDefault();
    setError('');
    if (!email.trim()) {
      setError('Please enter your email address');
      return;
    }
    setLoading(true);
    try {
      await axios.post(
        'http://localhost:5000/api/auth/forgot-password',
        { email: email.trim().toLowerCase() }
      );
      setStep(STEPS.OTP);
      startResendTimer();
    } catch (err) {
      setError(
        err.response?.data?.message || 'Failed to send OTP. Try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const startResendTimer = () => {
    setResendTimer(60);
    const interval = setInterval(() => {
      setResendTimer((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  // ── OTP input handling ────────────────────────────────────
  const handleOtpChange = (value, index) => {
    if (!/^\d*$/.test(value)) return; // digits only
    const newOtp = [...otp];
    newOtp[index] = value.slice(-1); // one digit per box
    setOtp(newOtp);

    // Auto-focus next box
    if (value && index < 5) {
      document.getElementById(`otp-${index + 1}`)?.focus();
    }
  };

  const handleOtpKeyDown = (e, index) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      document.getElementById(`otp-${index - 1}`)?.focus();
    }
  };

  const handleOtpPaste = (e) => {
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    if (pasted.length === 6) {
      setOtp(pasted.split(''));
    }
  };

  // ── Step 2: Verify OTP ────────────────────────────────────
  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    setError('');
    const otpString = otp.join('');
    if (otpString.length !== 6) {
      setError('Please enter the complete 6-digit OTP');
      return;
    }
    setLoading(true);
    try {
      await axios.post(
        'http://localhost:5000/api/auth/verify-reset-otp',
        { email, otp: otpString }
      );
      setStep(STEPS.NEW_PASSWORD);
    } catch (err) {
      setError(
        err.response?.data?.message || 'Invalid OTP. Please try again.'
      );
      setOtp(['', '', '', '', '', '']);
      document.getElementById('otp-0')?.focus();
    } finally {
      setLoading(false);
    }
  };

  // ── Step 3: Reset Password ────────────────────────────────
  const handleResetPassword = async (e) => {
    e.preventDefault();
    setError('');

    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      await axios.post(
        'http://localhost:5000/api/auth/reset-password',
        {
          email,
          new_password: newPassword,
          confirm_password: confirmPassword
        }
      );
      setStep(STEPS.SUCCESS);
    } catch (err) {
      setError(
        err.response?.data?.message || 'Failed to reset password. Try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleResendOTP = async () => {
    if (resendTimer > 0) return;
    setError('');
    setLoading(true);
    try {
      await axios.post(
        'http://localhost:5000/api/auth/forgot-password',
        { email }
      );
      setOtp(['', '', '', '', '', '']);
      startResendTimer();
    } catch (err) {
      setError('Failed to resend OTP');
    } finally {
      setLoading(false);
    }
  };

  // ── Progress indicator ────────────────────────────────────
  const steps = [
    { key: STEPS.EMAIL, label: 'Email' },
    { key: STEPS.OTP, label: 'Verify OTP' },
    { key: STEPS.NEW_PASSWORD, label: 'New Password' },
  ];

  const currentStepIndex = steps.findIndex((s) => s.key === step);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-slate-50 
      flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">

        {/* Back to login */}
        <Link
          to="/login"
          className="inline-flex items-center gap-1.5 text-slate-500 
            hover:text-indigo-600 text-sm font-semibold mb-8 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Sign In
        </Link>

        <div className="bg-white rounded-3xl shadow-xl border border-slate-100 p-8">

          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-14 h-14 bg-indigo-100 rounded-2xl flex items-center 
              justify-center mx-auto mb-4">
              <KeyRound className="w-7 h-7 text-indigo-600" />
            </div>
            <h1 className="text-2xl font-extrabold text-slate-900">
              {step === STEPS.SUCCESS
                ? 'Password Reset!'
                : 'Forgot Password?'}
            </h1>
            <p className="text-slate-500 text-sm mt-1.5">
              {step === STEPS.EMAIL &&
                "Enter your email and we'll send you a reset code."}
              {step === STEPS.OTP &&
                `Enter the 6-digit OTP sent to ${email}`}
              {step === STEPS.NEW_PASSWORD &&
                'Choose a strong new password.'}
              {step === STEPS.SUCCESS &&
                'Your password has been updated successfully.'}
            </p>
          </div>

          {/* Progress steps — hide on success */}
          {step !== STEPS.SUCCESS && (
            <div className="flex items-center justify-center gap-2 mb-8">
              {steps.map((s, idx) => (
                <React.Fragment key={s.key}>
                  <div className="flex flex-col items-center gap-1">
                    <div className={`w-8 h-8 rounded-full flex items-center 
                      justify-center text-xs font-bold transition-all
                      ${idx < currentStepIndex
                        ? 'bg-indigo-600 text-white'
                        : idx === currentStepIndex
                        ? 'bg-indigo-600 text-white ring-4 ring-indigo-100'
                        : 'bg-slate-100 text-slate-400'
                      }`}
                    >
                      {idx < currentStepIndex ? '✓' : idx + 1}
                    </div>
                    <span className={`text-[10px] font-semibold hidden sm:block
                      ${idx <= currentStepIndex
                        ? 'text-indigo-600'
                        : 'text-slate-400'
                      }`}
                    >
                      {s.label}
                    </span>
                  </div>
                  {idx < steps.length - 1 && (
                    <div className={`flex-1 h-0.5 mb-5 max-w-[40px] transition-all
                      ${idx < currentStepIndex
                        ? 'bg-indigo-600'
                        : 'bg-slate-200'
                      }`}
                    />
                  )}
                </React.Fragment>
              ))}
            </div>
          )}

          {/* Error message */}
          {error && (
            <div className="bg-red-50 border border-red-100 text-red-700 
              text-sm px-4 py-3 rounded-xl mb-5 font-medium">
              ⚠ {error}
            </div>
          )}

          {/* ── STEP 1: Email ── */}
          {step === STEPS.EMAIL && (
            <form onSubmit={handleSendOTP} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-600 
                  mb-1.5 uppercase tracking-wide">
                  Email Address
                </label>
                <div className="relative">
                  <input
                    type="email"
                    required
                    autoFocus
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full border border-slate-200 bg-slate-50 
                      pl-10 pr-4 py-3 rounded-xl text-sm focus:outline-none 
                      focus:ring-2 focus:ring-indigo-500 focus:bg-white 
                      transition-all"
                  />
                  <Mail className="absolute left-3 top-3.5 w-4 h-4 text-slate-400" />
                </div>
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-indigo-600 hover:bg-indigo-700 
                  disabled:opacity-60 text-white font-bold py-3 rounded-xl 
                  transition-all shadow-md shadow-indigo-100 text-sm"
              >
                {loading ? 'Sending OTP...' : 'Send Reset OTP'}
              </button>
            </form>
          )}

          {/* ── STEP 2: OTP Verification ── */}
          {step === STEPS.OTP && (
            <form onSubmit={handleVerifyOTP} className="space-y-6">
              {/* 6-box OTP input */}
              <div>
                <label className="block text-xs font-bold text-slate-600 
                  mb-3 uppercase tracking-wide text-center">
                  Enter 6-Digit OTP
                </label>
                <div
                  className="flex justify-center gap-2"
                  onPaste={handleOtpPaste}
                >
                  {otp.map((digit, idx) => (
                    <input
                      key={idx}
                      id={`otp-${idx}`}
                      type="text"
                      inputMode="numeric"
                      maxLength={1}
                      value={digit}
                      onChange={(e) => handleOtpChange(e.target.value, idx)}
                      onKeyDown={(e) => handleOtpKeyDown(e, idx)}
                      className={`w-11 h-12 text-center text-lg font-bold 
                        border-2 rounded-xl focus:outline-none transition-all
                        ${digit
                          ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                          : 'border-slate-200 bg-slate-50 text-slate-800'
                        }
                        focus:border-indigo-500 focus:bg-white`}
                    />
                  ))}
                </div>
              </div>

              <button
                type="submit"
                disabled={loading || otp.join('').length !== 6}
                className="w-full bg-indigo-600 hover:bg-indigo-700 
                  disabled:opacity-60 text-white font-bold py-3 rounded-xl 
                  transition-all shadow-md shadow-indigo-100 text-sm"
              >
                {loading ? 'Verifying...' : 'Verify OTP'}
              </button>

              {/* Resend OTP */}
              <p className="text-center text-xs text-slate-500">
                Didn't receive the code?{' '}
                <button
                  type="button"
                  onClick={handleResendOTP}
                  disabled={resendTimer > 0 || loading}
                  className="font-bold text-indigo-600 hover:text-indigo-700 
                    disabled:text-slate-400 disabled:cursor-not-allowed"
                >
                  {resendTimer > 0
                    ? `Resend in ${resendTimer}s`
                    : 'Resend OTP'}
                </button>
              </p>
            </form>
          )}

          {/* ── STEP 3: New Password ── */}
          {step === STEPS.NEW_PASSWORD && (
            <form onSubmit={handleResetPassword} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-600 
                  mb-1.5 uppercase tracking-wide">
                  New Password
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    autoFocus
                    placeholder="Min. 8 characters"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="w-full border border-slate-200 bg-slate-50 
                      pl-10 pr-10 py-3 rounded-xl text-sm focus:outline-none 
                      focus:ring-2 focus:ring-indigo-500 focus:bg-white 
                      transition-all"
                  />
                  <Lock className="absolute left-3 top-3.5 w-4 h-4 text-slate-400" />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-3.5 text-slate-400 
                      hover:text-slate-600"
                  >
                    {showPassword
                      ? <EyeOff className="w-4 h-4" />
                      : <Eye className="w-4 h-4" />}
                  </button>
                </div>

                {/* Password strength indicator */}
                {newPassword && (
                  <div className="mt-2 flex gap-1">
                    {[1, 2, 3, 4].map((level) => (
                      <div
                        key={level}
                        className={`flex-1 h-1 rounded-full transition-all
                          ${newPassword.length >= level * 3
                            ? level <= 1
                              ? 'bg-red-400'
                              : level <= 2
                              ? 'bg-amber-400'
                              : level <= 3
                              ? 'bg-blue-400'
                              : 'bg-emerald-500'
                            : 'bg-slate-200'
                          }`}
                      />
                    ))}
                  </div>
                )}
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-600 
                  mb-1.5 uppercase tracking-wide">
                  Confirm Password
                </label>
                <div className="relative">
                  <input
                    type={showConfirm ? 'text' : 'password'}
                    required
                    placeholder="Repeat new password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className={`w-full border bg-slate-50 pl-10 pr-10 py-3 
                      rounded-xl text-sm focus:outline-none focus:ring-2 
                      focus:ring-indigo-500 focus:bg-white transition-all
                      ${confirmPassword && confirmPassword !== newPassword
                        ? 'border-red-300 focus:ring-red-400'
                        : confirmPassword && confirmPassword === newPassword
                        ? 'border-emerald-300 focus:ring-emerald-400'
                        : 'border-slate-200'
                      }`}
                  />
                  <Lock className="absolute left-3 top-3.5 w-4 h-4 text-slate-400" />
                  <button
                    type="button"
                    onClick={() => setShowConfirm(!showConfirm)}
                    className="absolute right-3 top-3.5 text-slate-400 
                      hover:text-slate-600"
                  >
                    {showConfirm
                      ? <EyeOff className="w-4 h-4" />
                      : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                {confirmPassword && confirmPassword !== newPassword && (
                  <p className="text-xs text-red-500 mt-1 font-medium">
                    Passwords do not match
                  </p>
                )}
                {confirmPassword && confirmPassword === newPassword && (
                  <p className="text-xs text-emerald-600 mt-1 font-medium">
                    ✓ Passwords match
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={
                  loading ||
                  newPassword.length < 8 ||
                  newPassword !== confirmPassword
                }
                className="w-full bg-indigo-600 hover:bg-indigo-700 
                  disabled:opacity-60 text-white font-bold py-3 rounded-xl 
                  transition-all shadow-md shadow-indigo-100 text-sm mt-2"
              >
                {loading ? 'Resetting...' : 'Reset Password'}
              </button>
            </form>
          )}

          {/* ── STEP 4: Success ── */}
          {step === STEPS.SUCCESS && (
            <div className="text-center space-y-6">
              <div className="w-20 h-20 bg-emerald-100 rounded-full flex 
                items-center justify-center mx-auto">
                <CheckCircle2 className="w-10 h-10 text-emerald-600" />
              </div>
              <div className="space-y-2">
                <p className="text-slate-600 text-sm leading-relaxed">
                  Your password has been reset successfully. You can now 
                  sign in with your new password.
                </p>
              </div>
              <button
                onClick={() => navigate('/login')}
                className="w-full bg-indigo-600 hover:bg-indigo-700 
                  text-white font-bold py-3 rounded-xl transition-all 
                  shadow-md shadow-indigo-100 text-sm"
              >
                Go to Sign In
              </button>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;