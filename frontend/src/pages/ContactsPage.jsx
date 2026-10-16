import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Search, Plus, UserCheck, Phone, Mail, MessageSquare, Tag, Globe } from 'lucide-react';

export default function ContactsPage() {
  const [customers, setCustomers] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({ name: '', phone: '', email: '', notes: '', platform: 'whatsapp', platform_user_id: '' });

  const loadCustomers = () => {
    api.get(`/customers?search=${encodeURIComponent(search)}`).then(res => {
      if (res.success) setCustomers(res.customers);
    }).catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadCustomers();
  }, [search]);

  const handleCreateCustomer = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post('/customers', formData);
      if (res.success) {
        setShowModal(false);
        setFormData({ name: '', phone: '', email: '', notes: '', platform: 'whatsapp', platform_user_id: '' });
        loadCustomers();
      }
    } catch (err) {
      alert(err.message || 'فشل إضافة العميل');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">سجل العملاء ودليل الاتصال الموحد</h2>
          <p className="text-xs text-slate-500">إدارة الملفات الشخصية والحسابات المرتبطة عبر مختلف المنصات</p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md flex items-center gap-1.5 transition-all self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" /> إضافة عميل جديد
        </button>
      </div>

      {/* Search Bar */}
      <div className="relative max-w-md">
        <Search className="w-4 h-4 absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          placeholder="بحث بالاسم، رقم الهاتف، البريد..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pr-10 pl-4 py-2.5 rounded-xl text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white outline-none focus:border-emerald-500"
        />
      </div>

      {/* Customers Table / Grid */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-right text-xs">
            <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500 font-bold border-b border-slate-200 dark:border-slate-800">
              <tr>
                <th className="p-4">العميل</th>
                <th className="p-4">الهاتف والبريد</th>
                <th className="p-4">الحسابات المرتبطة</th>
                <th className="p-4">إجمالي المحادثات</th>
                <th className="p-4">الوسوم والملاحظات</th>
                <th className="p-4">تاريخ التسجيل</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {loading ? (
                <tr>
                  <td colSpan="6" className="p-8 text-center text-slate-400">جاري تحميل سجل العملاء...</td>
                </tr>
              ) : customers.length === 0 ? (
                <tr>
                  <td colSpan="6" className="p-8 text-center text-slate-400">لا يوجد عملاء مضافين حالياً</td>
                </tr>
              ) : (
                customers.map(c => (
                  <tr key={c.id} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition-colors">
                    <td className="p-4">
                      <div className="flex items-center gap-3">
                        <img src={c.avatar} alt={c.name} className="w-9 h-9 rounded-xl object-cover" />
                        <div>
                          <h4 className="font-bold text-slate-900 dark:text-white">{c.name}</h4>
                          <span className="text-[10px] text-slate-400">#CUST-{c.id}</span>
                        </div>
                      </div>
                    </td>

                    <td className="p-4 space-y-1">
                      <div className="flex items-center gap-1.5 text-slate-700 dark:text-slate-300">
                        <Phone className="w-3 h-3 text-slate-400" /> {c.phone || '—'}
                      </div>
                      {c.email && (
                        <div className="flex items-center gap-1.5 text-slate-500">
                          <Mail className="w-3 h-3 text-slate-400" /> {c.email}
                        </div>
                      )}
                    </td>

                    <td className="p-4">
                      <div className="flex items-center gap-1 flex-wrap">
                        {c.identities?.map(id => (
                          <span key={id.id} className="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-[10px] font-mono">
                            {id.platform}: {id.username || id.platform_user_id}
                          </span>
                        ))}
                      </div>
                    </td>

                    <td className="p-4 font-bold text-emerald-600">
                      {c.total_conversations} محادثات / {c.total_orders} طلبات
                    </td>

                    <td className="p-4 max-w-xs truncate text-slate-500">
                      {c.notes || 'بدون ملاحظات'}
                    </td>

                    <td className="p-4 text-slate-400">
                      {new Date(c.created_at).toLocaleDateString('ar-EG')}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Customer Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 w-full max-w-md shadow-2xl space-y-4">
            <h3 className="font-bold text-base text-slate-900 dark:text-white">إضافة عميل جديد</h3>
            <form onSubmit={handleCreateCustomer} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold mb-1">اسم العميل</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={e => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
                  placeholder="مثال: أحمد السيناوي"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1">رقم الهاتف</label>
                <input
                  type="text"
                  value={formData.phone}
                  onChange={e => setFormData({ ...formData, phone: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
                  placeholder="+201000000000"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1">المنصة والمعرف</label>
                <div className="flex gap-2">
                  <select
                    value={formData.platform}
                    onChange={e => setFormData({ ...formData, platform: e.target.value })}
                    className="px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
                  >
                    <option value="whatsapp">واتساب</option>
                    <option value="instagram">إنستغرام</option>
                    <option value="telegram">تيليجرام</option>
                    <option value="tiktok">تيك توك</option>
                  </select>
                  <input
                    type="text"
                    placeholder="معرف العميل أو اسم المستخدم"
                    value={formData.platform_user_id}
                    onChange={e => setFormData({ ...formData, platform_user_id: e.target.value })}
                    className="flex-1 px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold mb-1">ملاحظات خاصة</label>
                <textarea
                  value={formData.notes}
                  onChange={e => setFormData({ ...formData, notes: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none h-20"
                ></textarea>
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
                  حفظ العميل
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
