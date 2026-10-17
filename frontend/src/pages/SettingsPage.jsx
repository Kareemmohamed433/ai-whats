import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Settings, Building2, Clock, Save, ShieldCheck, Mail, Phone, MapPin, ExternalLink, Globe, Sparkles } from 'lucide-react';

export default function SettingsPage() {
  const [company, setCompany] = useState({
    company_name: 'NEXORA Software Solutions',
    tagline: 'Ideas → Code → Impact',
    phone: '+201556441133',
    whatsapp: '+201556441133',
    email: 'contact@nexorasolutions.com',
    address: 'القاهرة، مصر',
    portfolio_url: 'https://company-pi-two.vercel.app/',
    facebook_url: 'https://www.facebook.com/profile.php?id=61595024167397',
    instagram_url: 'https://www.instagram.com/nexorasoftwarre/',
    telegram_endpoint: 'https://ai-whats-production.up.railway.app/',
    services_summary: 'تطوير المواقع والمنصات، حلول الذكاء الاصطناعي والشات بوت، أتمتة العمليات والربط البرمجي، وتطوير البرمجيات المخصصة.',
    working_hours: {
      working_days: 'الأحد - الخميس',
      opening_time: '09:00',
      closing_time: '18:00'
    }
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get('/settings/company').then(res => {
      if (res.success && res.settings) {
        setCompany(prev => ({
          ...prev,
          ...res.settings,
          working_hours: res.settings.working_hours || prev.working_hours
        }));
      }
    }).catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await api.put('/settings/company', company);
      if (res.success) {
        alert('تم تحديث إعدادات وهوية شركة NEXORA بنجاح! 🚀');
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
          <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Building2 className="w-5 h-5 text-blue-500" />
            إعدادات وهوية الشركة والمقر (NEXORA Company Settings)
          </h2>
          <p className="text-xs text-slate-500">تحديث بيانات وهوية شركة NEXORA، البورتفوليو، الروابط الرسمية، ومواعيد العمل</p>
        </div>

        <button
          onClick={handleSave}
          disabled={saving}
          className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md shadow-blue-600/20 flex items-center gap-2 transition-all self-start sm:self-auto disabled:opacity-50"
        >
          <Save className="w-4 h-4" /> {saving ? 'جاري الحفظ...' : 'حفظ التعديلات'}
        </button>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Core Company Identity */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-4">
          <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-cyan-500" /> الهوية الرسمية والعلامة التجارية
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block font-semibold mb-1">اسم الشركة الرسمي</label>
              <input
                type="text"
                value={company.company_name}
                onChange={e => setCompany({ ...company, company_name: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1">شعار العلامة (Tagline)</label>
              <input
                type="text"
                value={company.tagline}
                onChange={e => setCompany({ ...company, tagline: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1">البريد الإلكتروني المعتمد</label>
              <input
                type="email"
                value={company.email}
                onChange={e => setCompany({ ...company, email: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1">رقم الهاتف والتواصل / واتساب</label>
              <input
                type="text"
                value={company.phone}
                onChange={e => setCompany({ ...company, phone: e.target.value, whatsapp: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold mb-1">المقر الرئيسي</label>
            <input
              type="text"
              value={company.address}
              onChange={e => setCompany({ ...company, address: e.target.value })}
              className="w-full p-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-xs text-slate-900 dark:text-white outline-none"
            />
          </div>
        </div>

        {/* Official Web & Social Links */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-4">
          <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
            <Globe className="w-4 h-4 text-blue-500" /> البورتفوليو والروابط الرقمية الرسمية
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block font-semibold mb-1">رابط معرض الأعمال والبورتفوليو الرسمي</label>
              <input
                type="url"
                value={company.portfolio_url}
                onChange={e => setCompany({ ...company, portfolio_url: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1">رابط فيسبوك الرسمي</label>
              <input
                type="url"
                value={company.facebook_url}
                onChange={e => setCompany({ ...company, facebook_url: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1">رابط إنستغرام الرسمي</label>
              <input
                type="url"
                value={company.instagram_url}
                onChange={e => setCompany({ ...company, instagram_url: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1">عنوان سيرفر تيليجرام / الويب هوك</label>
              <input
                type="url"
                value={company.telegram_endpoint}
                onChange={e => setCompany({ ...company, telegram_endpoint: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
              />
            </div>
          </div>
        </div>

        {/* Business Working Hours */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-4">
          <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
            <Clock className="w-4 h-4 text-amber-500" /> ساعات ومواعيد العمل الرسمية (Cairo Time)
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="block font-semibold mb-1">أيام العمل</label>
              <input
                type="text"
                value={company.working_hours?.working_days || 'الأحد - الخميس'}
                onChange={e => setCompany({ ...company, working_hours: { ...company.working_hours, working_days: e.target.value } })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
              />
            </div>
            <div>
              <label className="block font-semibold mb-1">بدء العمل</label>
              <input
                type="time"
                value={company.working_hours?.opening_time || '09:00'}
                onChange={e => setCompany({ ...company, working_hours: { ...company.working_hours, opening_time: e.target.value } })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
              />
            </div>
            <div>
              <label className="block font-semibold mb-1">نهاية العمل</label>
              <input
                type="time"
                value={company.working_hours?.closing_time || '18:00'}
                onChange={e => setCompany({ ...company, working_hours: { ...company.working_hours, closing_time: e.target.value } })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
              />
            </div>
          </div>
        </div>
      </form>
    </div>
  );
}
