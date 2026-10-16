import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Settings, Store, Clock, Save, ShieldCheck, Mail, Phone, MapPin, Truck, CreditCard } from 'lucide-react';

export default function SettingsPage() {
  const [store, setStore] = useState({
    store_name: '',
    phone: '',
    whatsapp: '',
    email: '',
    address: '',
    shipping_policy: '',
    free_shipping_threshold: 500,
    payment_methods: '',
    return_policy: '',
    working_hours: {
      working_days: 'من السبت إلى الخميس',
      opening_time: '09:00',
      closing_time: '21:00'
    }
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get('/settings/store').then(res => {
      if (res.success) setStore(res.settings);
    }).catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await api.put('/settings/store', store);
      if (res.success) {
        alert('تم تحديث إعدادات المتجر العامة وساعات العمل بنجاح! 🌿');
      }
    } catch (err) {
      alert(err.message || 'فشل الحفظ');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">إعدادات العلامة التجارية والبيانات العامة (Settings)</h2>
          <p className="text-xs text-slate-500">تحديث بيانات متجر خام سينا، مواعيد العمل، الشحن، وطرق الدفع</p>
        </div>

        <button
          onClick={handleSave}
          disabled={saving}
          className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md shadow-emerald-600/20 flex items-center gap-2 transition-all self-start sm:self-auto disabled:opacity-50"
        >
          <Save className="w-4 h-4" /> {saving ? 'جاري الحفظ...' : 'حفظ التعديلات'}
        </button>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* General Store Information */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-4">
          <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
            <Store className="w-4 h-4 text-emerald-500" /> البيانات الأساسية لبراند "خام سينا"
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block font-semibold mb-1">اسم المتجر / العلامة</label>
              <input
                type="text"
                value={store.store_name}
                onChange={e => setStore({ ...store, store_name: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1">البريد الإلكتروني للإنذارات</label>
              <input
                type="email"
                value={store.email}
                onChange={e => setStore({ ...store, email: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1">رقم الهاتف والتواصل</label>
              <input
                type="text"
                value={store.phone}
                onChange={e => setStore({ ...store, phone: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1">رقم الواتساب الرسمي</label>
              <input
                type="text"
                value={store.whatsapp}
                onChange={e => setStore({ ...store, whatsapp: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold mb-1">العنوان الرئيسي والمقرات</label>
            <textarea
              rows="2"
              value={store.address}
              onChange={e => setStore({ ...store, address: e.target.value })}
              className="w-full p-3 rounded-xl bg-slate-100 dark:bg-slate-800 text-xs text-slate-900 dark:text-white outline-none"
            ></textarea>
          </div>
        </div>

        {/* Shipping & Payment Policies */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-4">
          <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
            <Truck className="w-4 h-4 text-indigo-500" /> سياسات الشحن والدفع والأعمال
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block font-semibold mb-1">حد الشحن المجاني (جنيه مصري)</label>
              <input
                type="number"
                value={store.free_shipping_threshold}
                onChange={e => setStore({ ...store, free_shipping_threshold: parseFloat(e.target.value) })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1">طرق الدفع المعتمده</label>
              <input
                type="text"
                value={store.payment_methods}
                onChange={e => setStore({ ...store, payment_methods: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold mb-1">نص سياسة الشحن والتوصيل للمحافظات</label>
            <textarea
              rows="2"
              value={store.shipping_policy}
              onChange={e => setStore({ ...store, shipping_policy: e.target.value })}
              className="w-full p-3 rounded-xl bg-slate-100 dark:bg-slate-800 text-xs text-slate-900 dark:text-white outline-none"
            ></textarea>
          </div>
        </div>

        {/* Business Working Hours */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-4">
          <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
            <Clock className="w-4 h-4 text-amber-500" /> مواعيد ورسميات العمل (Business Hours)
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="block font-semibold mb-1">أيام العمل</label>
              <input
                type="text"
                value={store.working_hours?.working_days || ''}
                onChange={e => setStore({ ...store, working_hours: { ...store.working_hours, working_days: e.target.value } })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
              />
            </div>
            <div>
              <label className="block font-semibold mb-1">ساعة الفتح</label>
              <input
                type="time"
                value={store.working_hours?.opening_time || '09:00'}
                onChange={e => setStore({ ...store, working_hours: { ...store.working_hours, opening_time: e.target.value } })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
              />
            </div>
            <div>
              <label className="block font-semibold mb-1">ساعة الإغلاق</label>
              <input
                type="time"
                value={store.working_hours?.closing_time || '21:00'}
                onChange={e => setStore({ ...store, working_hours: { ...store.working_hours, closing_time: e.target.value } })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
              />
            </div>
          </div>
        </div>
      </form>
    </div>
  );
}
