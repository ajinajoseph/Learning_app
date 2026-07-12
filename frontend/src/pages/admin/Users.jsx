import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/axios';
import { ArrowLeft, User, Shield, AlertCircle } from 'lucide-react';

const Users = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/admin/users');
      setUsers(res.data);
    } catch (err) {
      console.error('Failed to load users:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleRoleChange = async (userId, newRole) => {
    if (!window.confirm(`Are you sure you want to change this user's role to ${newRole.toUpperCase()}?`)) {
      return;
    }
    try {
      await api.put(`/api/admin/users/${userId}/role`, { role: newRole });
      // Update local state
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, role: newRole } : u))
      );
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to update role');
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10">
      
      {/* Back Button */}
      <Link 
        to="/admin/dashboard" 
        className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-indigo-650 mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Administration
      </Link>

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
          <User className="w-8 h-8 text-indigo-600" /> Users Directory
        </h1>
        <p className="text-slate-500 mt-1">Review active student registries, update mentor profiles, or assign admin status.</p>
      </div>

      {loading ? (
        <div className="bg-white border border-slate-100 p-12 rounded-2xl animate-pulse"></div>
      ) : users.length === 0 ? (
        <div className="text-center py-16 bg-white border border-slate-100 rounded-3xl p-8">
          <AlertCircle className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <p className="font-bold text-slate-805">No users found</p>
        </div>
      ) : (
        <div className="bg-white border border-slate-100 rounded-2xl shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs sm:text-sm">
              <thead className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider text-[10px] border-b border-slate-100">
                <tr>
                  <th className="px-6 py-4">User Details</th>
                  <th className="px-6 py-4">Email</th>
                  <th className="px-6 py-4">Current Role</th>
                  <th className="px-6 py-4 text-right">Edit Role</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {users.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50/50">
                    <td className="px-6 py-4 font-bold text-slate-900 flex items-center gap-2">
                      <div className="w-8 h-8 bg-slate-100 rounded-full flex items-center justify-center font-bold uppercase text-slate-500 shrink-0 text-xs">
                        {item.name?.substring(0, 2)}
                      </div>
                      <span className="truncate max-w-[150px]">{item.name}</span>
                    </td>
                    <td className="px-6 py-4 text-slate-500 font-semibold">{item.email}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-block px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                        item.role === 'admin' 
                          ? 'bg-purple-50 text-purple-700 border border-purple-100' 
                          : item.role === 'mentor'
                          ? 'bg-blue-50 text-blue-700 border border-blue-100'
                          : 'bg-slate-100 text-slate-705 text-slate-700'
                      }`}>
                        {item.role}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <select
                        value={item.role}
                        onChange={(e) => handleRoleChange(item.id, e.target.value)}
                        className="bg-slate-50 border border-slate-205 p-2 rounded-xl text-xs font-semibold focus:outline-none"
                      >
                        <option value="student">Student</option>
                        <option value="mentor">Mentor</option>
                        <option value="admin">Admin</option>
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

    </div>
  );
};

export default Users;
