import React from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Github, Twitter, Linkedin, Mail, Phone, MapPin } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-slate-900 text-slate-300 border-t border-slate-800 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12">
          
          {/* Brand */}
          <div className="space-y-4">
            <Link to="/" className="flex items-center gap-2">
              <div className="bg-indigo-600 p-2 rounded-lg text-white">
                <BookOpen className="w-6 h-6" />
              </div>
              <span className="font-extrabold text-2xl tracking-tight text-white">
                EduFlex
              </span>
            </Link>
            <p className="text-sm text-slate-400 leading-relaxed">
              EduFlex is a modern online learning platform offering high-quality courses curated by industry experts. Empowering learners worldwide.
            </p>
            <div className="flex gap-4 pt-2">
              <a href="#" className="hover:text-indigo-400 transition-colors"><Twitter className="w-5 h-5" /></a>
              <a href="#" className="hover:text-indigo-400 transition-colors"><Github className="w-5 h-5" /></a>
              <a href="#" className="hover:text-indigo-400 transition-colors"><Linkedin className="w-5 h-5" /></a>
            </div>
          </div>

          {/* Popular Categories */}
          <div>
            <h3 className="text-white font-semibold text-sm uppercase tracking-wider mb-4">Popular Topics</h3>
            <ul className="space-y-2.5 text-sm">
              <li><Link to="/courses?level=beginner" className="hover:text-indigo-400 transition-colors">Web Development</Link></li>
              <li><Link to="/courses?level=intermediate" className="hover:text-indigo-400 transition-colors">Data Science</Link></li>
              <li><Link to="/courses" className="hover:text-indigo-400 transition-colors">Business & Marketing</Link></li>
              <li><Link to="/courses" className="hover:text-indigo-400 transition-colors">Design & UX</Link></li>
            </ul>
          </div>

          {/* Platform Links */}
          <div>
            <h3 className="text-white font-semibold text-sm uppercase tracking-wider mb-4">Quick Links</h3>
            <ul className="space-y-2.5 text-sm">
              <li><Link to="/courses" className="hover:text-indigo-400 transition-colors">Browse Courses</Link></li>
              <li><Link to="/register" className="hover:text-indigo-400 transition-colors">Become a Mentor</Link></li>
              <li><Link to="/login" className="hover:text-indigo-400 transition-colors">Sign In</Link></li>
              <li><Link to="/register" className="hover:text-indigo-400 transition-colors">Create Account</Link></li>
            </ul>
          </div>

          {/* Contact Details */}
          <div>
            <h3 className="text-white font-semibold text-sm uppercase tracking-wider mb-4">Support & Contact</h3>
            <ul className="space-y-3 text-sm text-slate-400">
              <li className="flex items-start gap-2.5">
                <MapPin className="w-4 h-4 text-indigo-400 mt-0.5 shrink-0" />
                <span>100 Innovation Way, Tech Suite 400, San Francisco, CA</span>
              </li>
              <li className="flex items-center gap-2.5">
                <Phone className="w-4 h-4 text-indigo-400 shrink-0" />
                <span>+1 (555) 019-2834</span>
              </li>
              <li className="flex items-center gap-2.5">
                <Mail className="w-4 h-4 text-indigo-400 shrink-0" />
                <a href="mailto:support@eduflex.com" className="hover:text-indigo-400 transition-colors">support@eduflex.com</a>
              </li>
            </ul>
          </div>

        </div>

        <div className="border-t border-slate-800 mt-12 pt-8 flex flex-col sm:flex-row justify-between items-center gap-4 text-xs text-slate-500">
          <p>© {new Date().getFullYear()} EduFlex Inc. All rights reserved.</p>
          <div className="flex gap-6">
            <a href="#" className="hover:text-slate-400 transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-slate-400 transition-colors">Terms of Service</a>
            <a href="#" className="hover:text-slate-400 transition-colors">Cookie Settings</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
