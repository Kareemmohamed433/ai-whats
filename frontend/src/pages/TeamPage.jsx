import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { UserCheck, Plus, Trash2, Edit2, Shield, Mail, CheckCircle2, Clock, ArrowUpDown, MessageSquare, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

function formatRelativeArabic(dateStr) {
  if (!dateStr) return null;
  const date = new Date(dateStr);
  const now = new Date();
  const diffSec = Math.floor((now - date) / 1000);

  if (isNaN(diffSec) || diffSec < 0) return 'منذ لحظات';
  if (diffSec < 60) return 'منذ لحظات';
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `منذ ${diffMin} دقيقة`;
  const diffHours = Math.floor(diffMin / 60);
  if (diffHours < 24) return `منذ ${diffHours} ساعة`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays === 1) return `أمس ${date.toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' })}`;
  if (diffDays < 7) return `منذ ${diffDays} أيام`;

  return date.toLocaleDateString('ar-EG', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
}

export default function TeamPage() {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [sortBy, setSortBy] = useState('recent'); // recent, name, role
  const [formData, setFormData] = useState({ name: '', email: '', password: '', role: 'agent' });

  const loadUsers = (isSilent = false) => {
    if (!isSilent) setLoading(true);
    api.get('/users').then(res => {
      if (res.success) setUsers(res.users || []);
    }).catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadUsers();

    // Heartbeat every 45s
    api.post('/auth/heartbeat').catch(() => {});
    const heartbeatInterval = setInterval(() => {
      api.post('/auth/heartbeat').catch(() => {});
      loadUsers(true);
    }, 45000);

    return () => clearInterval(heartbeatInterval);
  }, []);

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post('/users', formData);
      if (res.success) {
        setShowModal(false);
        setFormData({ name: '', email: '', password: '', role: 'agent' });
        loadUsers();
      }
    } catch (err) {
      alert(err.message || 'فشل إضافة الموظف');
    }
  };

  const handleDeleteUser = async (id) => {
    if (!window.confirm('هل تود حذف هذا الموظف من فريق العمل؟')) return;
    try {
      const res = await api.delete(`/users/${id}`);
      if (res.success) loadUsers();
    } catch (err) {
      alert(err.message || 'فشل الحذف');
    }
  };

  const sortedUsers = [...users].sort((a, b) => {
    if (sortBy === 'recent') {
      const getLatestTime = u => {
        const t1 = u.last_reply_at ? new Date(u.last_reply_at).getTime() : 0;
        const t2 = u.last_login_at ? new Date(u.last_login_at).getTime() : 0;
        const t3 = u.last_seen_at ? new Date(u.last_seen_at).getTime() : 0;
        return Math.max(t1, t2, t3);
      };
      return getLatestTime(b) - getLatestTime(a);
    }
    if (sortBy === 'name') return a.name.localeCompare(b.name, 'ar');
    return a.id - b.id;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">إدارة فريق العمل والأدوار (Team Management)</h2>
          <p className="text-xs text-slate-500">إدارة حسابات المسؤولين (Admin)، المشرفين (Manager)، وموظفي الدعم (Agent) وتتبع نشاطهم المباشر</p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <button
            onClick={() => loadUsers(false)}
            className="p-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 transition"
            title="تحديث القائمة"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>

          <button
            onClick={() => setShowModal(true)}
            className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md flex items-center gap-1.5 transition-all"
          >
            <Plus className="w-4 h-4" /> إضافة عضو جديد بالفريق
          </button>
        </div>
      </div>

      {/* Toolbar / Sorting */}
      <div className="flex items-center justify-between bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl px-5 py-3 text-xs">
        <span className="font-bold text-slate-600 dark:text-slate-400">إجمالي أعضاء الفريق: {users.length}</span>
        
        <div className="flex items-center gap-2">
          <ArrowUpDown className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-slate-500 font-semibold">ترتيب حسب:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 rounded-lg px-2.5 py-1 font-bold outline-none cursor-pointer"
          >
            <option value="recent">أحدث نشاط</option>
            <option value="name">الاسم</option>
          </select>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-right text-xs">
            <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500 font-bold border-b border-slate-200 dark:border-slate-800">
              <tr>
                <th className="p-4">الموظف</th>
                <th className="p-4">البريد الإلكتروني</th>
                <th className="p-4">الدور والصلاحيات</th>
                <th className="p-4">الحالة الحالية</th>
                <th className="p-4">آخر نشاط (Last Activity)</th>
                <th className="p-4">تاريخ الانضمام</th>
                <th className="p-4">الإجراءات</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {loading && users.length === 0 ? (
                <tr><td colSpan="7" className="p-8 text-center text-slate-400">جاري تحميل فريق العمل...</td></tr>
              ) : (
                sortedUsers.map(u => {
                  const status = u.computed_status || u.status || 'offline';
                  const isOnline = status === 'online';

                  // Calculate last activity summary
                  let activityLabel = 'لا يوجد نشاط';
                  let activityTooltip = 'لم يتم تسجيل دخول أو ردود سابقة';

                  const lastReplyMs = u.last_reply_at ? new Date(u.last_reply_at).getTime() : 0;
                  const lastLoginMs = u.last_login_at ? new Date(u.last_login_at).getTime() : 0;
                  
                  if (isOnline) {
                    activityLabel = 'نشط الآن';
                    activityTooltip = u.last_seen_at ? `متواجد حالياً (${new Date(u.last_seen_at).toLocaleTimeString('ar-EG')})` : 'متصل الآن';
                  } else if (lastReplyMs > 0 || lastLoginMs > 0) {
                    if (lastReplyMs >= lastLoginMs && u.last_reply_at) {
                      const rel = formatRelativeArabic(u.last_reply_at);
                      activityLabel = u.last_reply_customer_name 
                        ? `رد على (${u.last_reply_customer_name}) ${rel}` 
                        : `قام بالرد ${rel}`;
                      activityTooltip = `تاريخ آخر رد: ${new Date(u.last_reply_at).toLocaleString('ar-EG')}`;
                    } else if (u.last_login_at) {
                      const rel = formatRelativeArabic(u.last_login_at);
                      activityLabel = `تسجيل دخول ${rel}`;
                      activityTooltip = `تاريخ آخر دخول: ${new Date(u.last_login_at).toLocaleString('ar-EG')}`;
                    }
                  }

                  return (
                    <tr key={u.id} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition-colors">
                      <td className="p-4">
                        <div className="flex items-center gap-3">
                          <img src={u.avatar} alt={u.name} className="w-9 h-9 rounded-xl object-cover" />
                          <div>
                            <div className="flex items-center gap-2">
                              <h4 className="font-bold text-slate-900 dark:text-white">{u.name}</h4>
                              {u.replies_today_count > 0 && (
                                <span className="px-1.5 py-0.2 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold">
                                  {u.replies_today_count} رد اليوم
                                </span>
                              )}
                            </div>
                            <span className="text-[10px] text-slate-400">#EMP-{u.id}</span>
                          </div>
                        </div>
                      </td>

                      <td className="p-4 text-slate-700 dark:text-slate-300 font-mono">
                        {u.email}
                      </td>

                      <td className="p-4">
                        <span className={`inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                          u.role === 'admin' ? 'bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-300' :
                          u.role === 'manager' ? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300' :
                          'bg-teal-100 text-teal-700 dark:bg-teal-950 dark:text-teal-300'
                        }`}>
                          {u.role === 'admin' ? 'مدير نظام (Admin)' : u.role === 'manager' ? 'مشرف (Manager)' : 'موظف دعم (Agent)'}
                        </span>
                      </td>

                      <td className="p-4 font-bold">
                        <span className={`inline-flex items-center gap-1.5 ${
                          status === 'online' ? 'text-emerald-500' :
                          status === 'busy' ? 'text-rose-500' :
                          status === 'away' ? 'text-amber-500' : 'text-slate-400'
                        }`}>
                          <span className={`w-2 h-2 rounded-full ${
                            status === 'online' ? 'bg-emerald-500' :
                            status === 'busy' ? 'bg-rose-500' :
                            status === 'away' ? 'bg-amber-500' : 'bg-slate-400'
                          }`}></span>
                          {status === 'online' ? 'متصل' : status === 'busy' ? 'مشغول' : status === 'away' ? 'بعيد' : 'غير متصل'}
                        </span>
                      </td>

                      <td className="p-4" title={activityTooltip}>
                        <div className="flex items-center gap-1.5">
                          <Clock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                          <span className={`text-xs font-semibold ${isOnline ? 'text-emerald-600 dark:text-emerald-400 font-bold' : 'text-slate-600 dark:text-slate-300'}`}>
                            {activityLabel}
                          </span>
                        </div>
                      </td>

                      <td className="p-4 text-slate-400">
                        {new Date(u.created_at).toLocaleDateString('ar-EG')}
                      </td>

                      <td className="p-4">
                        <button
                          onClick={() => handleDeleteUser(u.id)}
                          className="p-1.5 text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-xl"
                          title="حذف"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add User Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 w-full max-w-md shadow-2xl space-y-4">
            <h3 className="font-bold text-base text-slate-900 dark:text-white">إضافة عضو جديد لفريق NEXORA</h3>
            <form onSubmit={handleCreateUser} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold mb-1">الاسم الكامل</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={e => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
                  placeholder="محمد طارق"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1">البريد الإلكتروني</label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={e => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
                  placeholder="agent@khams-sinaa.eg"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1">كلمة المرور</label>
                <input
                  type="password"
                  required
                  value={formData.password}
                  onChange={e => setFormData({ ...formData, password: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
                  placeholder="••••••••"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1">الدور والصلاحية</label>
                <select
                  value={formData.role}
                  onChange={e => setFormData({ ...formData, role: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
                >
                  <option value="agent">موظف دعم (Agent)</option>
                  <option value="manager">مشرف (Manager)</option>
                  <option value="admin">مدير نظام (Admin)</option>
                </select>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold"
                >
                  إلغاء
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-emerald-600 text-white font-bold"
                >
                  حفظ العضو
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
