import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MessageSquareCode, Plus, Edit, Trash2, Check, X, Search, Zap } from 'lucide-react';

export default function QuickRepliesPage() {
  const [replies, setReplies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingReply, setEditingReply] = useState(null);

  const [formData, setFormData] = useState({
    title: '',
    shortcut: '',
    category: 'general',
    response_text: '',
    is_enabled: true
  });

  const token = localStorage.getItem('token');

  useEffect(() => {
    fetchReplies();
  }, []);

  const fetchReplies = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/api/quick-replies', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.data.success) {
        setReplies(res.data.quick_replies || []);
      }
    } catch (err) {
      console.error("Fetch quick replies error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      if (editingReply) {
        await axios.put(`/api/quick-replies/${editingReply.id}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else {
        await axios.post('/api/quick-replies', formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      setShowModal(false);
      resetForm();
      fetchReplies();
    } catch (err) {
      alert(err.response?.data?.error?.message || "حدث خطأ أثناء حفظ الرد السريع");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("هل أنت تأكد من حذف هذا الرد السريع؟")) return;
    try {
      await axios.delete(`/api/quick-replies/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchReplies();
    } catch (err) {
      alert("حدث خطأ أثناء الحذف");
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      shortcut: '',
      category: 'general',
      response_text: '',
      is_enabled: true
    });
    setEditingReply(null);
  };

  const openEditModal = (r) => {
    setEditingReply(r);
    setFormData({
      title: r.title,
      shortcut: r.shortcut,
      category: r.category,
      response_text: r.response_text,
      is_enabled: r.is_enabled
    });
    setShowModal(true);
  };

  const filteredReplies = replies.filter(r => 
    r.title.toLowerCase().includes(search.toLowerCase()) ||
    r.shortcut.toLowerCase().includes(search.toLowerCase()) ||
    r.response_text.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs">
        <div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Zap className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
            إدارة الردود السريعة (Quick Replies)
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            إعداد الردود الجاهزة والاختصارات (/payment, /order, /shipping, /human) لتوفير الوقت على موظفي خدمة العملاء
          </p>
        </div>
        <button
          onClick={() => { resetForm(); setShowModal(true); }}
          className="flex items-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold transition shadow-md shadow-emerald-600/20"
        >
          <Plus className="w-4 h-4" />
          إضافة رد سريع جديد
        </button>
      </div>

      {/* Search */}
      <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 flex items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute right-3 top-2.5 text-slate-400" />
          <input
            type="text"
            placeholder="بحث بالاسم أو الاختصار أو النقل..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pr-9 pl-3 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-hidden focus:border-emerald-500"
          />
        </div>
        <span className="text-xs text-slate-500 font-medium">إجمالي الردود: {filteredReplies.length}</span>
      </div>

      {/* List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : filteredReplies.length === 0 ? (
        <div className="text-center py-16 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800">
          <MessageSquareCode className="w-12 h-12 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
          <p className="text-sm font-bold text-slate-600 dark:text-slate-400">لا توجد ردود سريعة مطابقة</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredReplies.map((r) => (
            <div key={r.id} className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-3 hover:border-emerald-500/50 transition">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-sm text-slate-900 dark:text-white">{r.title}</span>
                  <span className="px-2.5 py-0.5 rounded-md bg-emerald-100 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 font-mono text-xs font-bold">
                    {r.shortcut}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <button onClick={() => openEditModal(r)} className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg text-slate-500 hover:text-slate-900 dark:hover:text-white">
                    <Edit className="w-4 h-4" />
                  </button>
                  <button onClick={() => handleDelete(r.id)} className="p-1.5 hover:bg-rose-100 dark:hover:bg-rose-950 rounded-lg text-slate-500 hover:text-rose-600">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/60 p-3 rounded-xl border border-slate-100 dark:border-slate-800">
                {r.response_text}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Create / Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <form onSubmit={handleSave} className="bg-white dark:bg-slate-900 rounded-2xl max-w-lg w-full p-6 border border-slate-200 dark:border-slate-800 space-y-4">
            <h3 className="text-base font-bold text-slate-900 dark:text-white">
              {editingReply ? 'تعديل رد سريع' : 'إضافة رد سريع جديد'}
            </h3>
            
            <div className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">عنوان الرد</label>
                <input
                  type="text"
                  required
                  placeholder="مثال: تأكيد استلام الدفع"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full p-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">الاختصار (Shortcut)</label>
                <input
                  type="text"
                  required
                  placeholder="مثال: /payment"
                  value={formData.shortcut}
                  onChange={(e) => setFormData({ ...formData, shortcut: e.target.value })}
                  className="w-full p-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white font-mono"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">التصنيف</label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full p-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white"
                >
                  <option value="welcome">👋 ترحب بالمشترك</option>
                  <option value="payment">💳 الدفع وإثبات التحويل</option>
                  <option value="order">📦 الطلبات والمتابعة</option>
                  <option value="shipping">🚚 الشحن والتوصيل</option>
                  <option value="products">🛒 المنتجات والأسعار</option>
                  <option value="customer_service">👤 خدمة العملاء</option>
                  <option value="closing">✅ إغلاق المحادثة</option>
                  <option value="general">عام</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">نص الرد الكامل</label>
                <textarea
                  rows={4}
                  required
                  placeholder="اكتب نص الرسالة التي ستظهر للموظف..."
                  value={formData.response_text}
                  onChange={(e) => setFormData({ ...formData, response_text: e.target.value })}
                  className="w-full p-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => { setShowModal(false); resetForm(); }}
                className="px-4 py-2 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-xl text-xs font-semibold hover:bg-slate-200"
              >
                إلغاء
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-emerald-600 text-white rounded-xl text-xs font-bold hover:bg-emerald-700"
              >
                حفظ الرد السريع
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
