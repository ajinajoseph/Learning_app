import React, { useState, useEffect } from 'react';
import api from '../../api/axios';
import { Award, Download, AlertCircle, ShieldCheck } from 'lucide-react';

const Certificates = () => {
  const [certificates, setCertificates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCertificates = async () => {
      setLoading(true);
      try {
        const res = await api.get('/api/certificates/my');
        setCertificates(res.data);
      } catch (err) {
        console.error('Failed to load certificates:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchCertificates();
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-10">
      
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
          <Award className="w-8 h-8 text-indigo-600" /> My Certificates
        </h1>
        <p className="text-slate-500 mt-1">View, share, or download your earned credentials.</p>
      </div>

      {loading ? (
        <div className="space-y-4">
          {Array(2).fill(0).map((_, idx) => (
            <div key={idx} className="bg-white border border-slate-100 p-6 rounded-2xl animate-pulse h-20"></div>
          ))}
        </div>
      ) : certificates.length === 0 ? (
        <div className="text-center py-16 bg-white border border-slate-100 rounded-3xl p-8 shadow-sm">
          <AlertCircle className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h3 className="font-bold text-slate-800">No certificates earned yet</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            Certificates are automatically generated when you achieve 100% completion checkmarks on your enrolled courses. Keep studying!
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {certificates.map((cert) => (
            <div 
              key={cert.id} 
              className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4"
            >
              <div className="flex gap-4 items-center">
                <div className="bg-indigo-50 p-3 rounded-xl text-indigo-600 shrink-0">
                  <ShieldCheck className="w-7 h-7" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-800 text-sm sm:text-base leading-snug">{cert.course_name || 'Course Certificate'}</h3>
                  <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider block mt-1">
                    Award ID: {cert.id} • Issued on {new Date(cert.issued_at).toLocaleDateString()}
                  </span>
                </div>
              </div>

              <a
                href={cert.certificate_url}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full sm:w-auto bg-indigo-650 bg-indigo-600 hover:bg-indigo-750 text-white font-bold text-xs px-5 py-3 rounded-xl transition-all shadow-md flex items-center justify-center gap-1.5 shrink-0"
              >
                <Download className="w-4 h-4" /> Download PDF
              </a>
            </div>
          ))}
        </div>
      )}

    </div>
  );
};

export default Certificates;
