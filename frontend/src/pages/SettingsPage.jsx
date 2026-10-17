import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { notificationService, playNotificationChime } from '../services/notificationService';
import { 
  Building2, 
  Clock, 
  Save, 
  Globe, 
  Sparkles, 
  Bell, 
  Smartphone, 
  Volume2, 
  Eye, 
  Trash2, 
  Send, 
  AlertCircle, 
  CheckCircle2, 
  Share2, 
  ShieldCheck,
  Info
} from 'lucide-react';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('notifications'); // 'notifications' | 'company'

  // Company settings state
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

  // Push notifications state
  const [pushStatus, setPushStatus] = useState(null);
  const [permission, setPermission] = useState('default');
  const [isIOS, setIsIOS] = useState(false);
  const [isStandalone, setIsStandalone] = useState(false);
  const [subscribing, setSubscribing] = useState(false);
  const [testingPush, setTestingPush] = useState(false);
  const [actionMessage, setActionMessage] = useState(null);
  const [actionError, setActionError] = useState(null);

  const [savingCompany, setSavingCompany] = useState(false);
  const [savingPrefs, setSavingPrefs] = useState(false);

  useEffect(() => {
    // Detect environment
    setIsIOS(notificationService.isIOS());
    setIsStandalone(notificationService.isStandalone());
    setPermission(notificationService.getPermission());

    // Load company settings
    api.get('/settings/company').then(res => {
      if (res.success && res.settings) {
        setCompany(prev => ({
          ...prev,
          ...res.settings,
          working_hours: res.settings.working_hours || prev.working_hours
        }));
      }
    }).catch(err => console.error(err));

    // Load notification status & preferences
    loadNotificationStatus();
  }, []);

  const loadNotificationStatus = async () => {
    try {
      const data = await notificationService.getStatus();
      setPushStatus(data);
    } catch (err) {
      console.warn('Could not load notification status:', err);
    }
  };

  // Enable Push Subscription
  const handleEnablePush = async () => {
    setSubscribing(true);
    setActionMessage(null);
    setActionError(null);

    try {
      const result = await notificationService.subscribe();
      setPermission(notificationService.getPermission());
      setActionMessage('تم تفعيل وتوثيق إشعارات Web Push بنجاح لهذا الجهاز! 🎉');
      await loadNotificationStatus();
    } catch (err) {
      console.error(err);
      setActionError(err.message || 'فشل تفعيل الإشعارات. يرجى التحقق من أذونات المتصفح.');
      setPermission(notificationService.getPermission());
    } finally {
      setSubscribing(false);
    }
  };

  // Disable Push Subscription
  const handleDisablePush = async () => {
    setSubscribing(true);
    setActionMessage(null);
    setActionError(null);

    try {
      await notificationService.unsubscribe();
      setActionMessage('تم إلغاء تفعيل إشعارات Push لهذا الجهاز.');
      await loadNotificationStatus();
    } catch (err) {
      setActionError(err.message || 'فشل إلغاء الاشتراك.');
    } finally {
      setSubscribing(false);
    }
  };

  // Trigger test push
  const handleTestPush = async () => {
    setTestingPush(true);
    setActionMessage(null);
    setActionError(null);

    try {
      playNotificationChime();
      const res = await notificationService.sendTestPush();
      setActionMessage(res.message || 'تم إرسال الإشعار التجريبي بنجاح!');
    } catch (err) {
      setActionError(err.response?.data?.message || err.message || 'فشل إرسال الإشعار التجريبي.');
    } finally {
      setTestingPush(false);
    }
  };

  // Delete registered device
  const handleDeleteDevice = async (deviceId) => {
    if (!window.confirm('هل أنت متأكد من حذف هذا الجهاز المسجل؟')) return;
    try {
      await notificationService.deleteDevice(deviceId);
      await loadNotificationStatus();
    } catch (err) {
      alert('فشل حذف الجهاز');
    }
  };

  // Save updated preferences
  const handleUpdatePreferences = async (newPrefs) => {
    setSavingPrefs(true);
    try {
      const res = await notificationService.updatePreferences(newPrefs);
      setPushStatus(prev => ({
        ...prev,
        preferences: res.preferences
      }));
    } catch (err) {
      alert('فشل حفظ التفضيلات');
    } finally {
      setSavingPrefs(false);
    }
  };

  // Save company identity
  const handleSaveCompany = async (e) => {
    e.preventDefault();
    setSavingCompany(true);
    try {
      const res = await api.put('/settings/company', company);
      if (res.success) {
        alert('تم تحديث إعدادات وهوية شركة NEXORA بنجاح! 🚀');
      }
    } catch (err) {
      alert(err.message || 'فشل الحفظ');
    } finally {
      setSavingCompany(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-12">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5">
            <Smartphone className="w-6 h-6 text-blue-600 dark:text-cyan-400" />
            <span>مركز الإعدادات والإشعارات</span>
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            إدارة إشعارات Web Push للآيفون والكمبيوتر، إعدادات وهوية NEXORA، ومواعيد العمل.
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-2 bg-slate-200/80 dark:bg-slate-800 p-1 rounded-2xl self-start sm:self-auto">
          <button
            onClick={() => setActiveTab('notifications')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-1.5 ${
              activeTab === 'notifications'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Bell className="w-4 h-4" />
            <span>إشعارات Web Push</span>
          </button>

          <button
            onClick={() => setActiveTab('company')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-1.5 ${
              activeTab === 'company'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Building2 className="w-4 h-4" />
            <span>هوية الشركة</span>
          </button>
        </div>
      </div>

      {/* Action Messages */}
      {actionMessage && (
        <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 text-xs font-bold flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
          <span>{actionMessage}</span>
        </div>
      )}

      {actionError && (
        <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-300 text-xs font-bold flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-500 shrink-0" />
          <span>{actionError}</span>
        </div>
      )}

      {/* ======================================================== */}
      {/* TAB 1: NOTIFICATIONS & WEB PUSH                         */}
      {/* ======================================================== */}
      {activeTab === 'notifications' && (
        <div className="space-y-6">
          {/* iOS Standalone Guide Alert (Crucial for iOS 16.4+) */}
          {isIOS && !isStandalone && (
            <div className="bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent border border-amber-500/30 rounded-3xl p-5 space-y-3">
              <div className="flex items-center gap-2 text-amber-800 dark:text-amber-300 font-extrabold text-sm">
                <Smartphone className="w-5 h-5 text-amber-600 shrink-0" />
                <span>خطوة ضرورية لتفعيل الإشعارات على أجهزة iPhone (iOS 16.4+)</span>
              </div>
              <p className="text-xs text-amber-900/80 dark:text-amber-200/80 leading-relaxed">
                وفقاً لسياسات شركة Apple، إشعارات Web Push على أجهزة iPhone تتطلب تشغيل الموقع كتطبيق ويب مثبت من الشاشة الرئيسية (Standalone PWA):
              </p>
              <ol className="list-decimal list-inside text-xs text-amber-900/90 dark:text-amber-200 space-y-1.5 font-medium pr-1">
                <li>اضغط على زر المشاركة <span className="font-bold">Share (مربع بسهم لأعلى)</span> في أسفل متصفح Safari.</li>
                <li>اختر <span className="font-bold">"إضافة إلى الصفحة الرئيسية" (Add to Home Screen)</span>.</li>
                <li>افتح تطبيق <span className="font-bold">NEXORA</span> من شاشة هاتفك الرئيسية، ثم ارجع لهذه الصفحة واضغط على زر تفعيل الإشعارات.</li>
              </ol>
            </div>
          )}

          {/* Device & Permission Status Card */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-5 sm:p-6 shadow-xs space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h3 className="font-extrabold text-sm sm:text-base text-slate-900 dark:text-white flex items-center gap-2">
                  <Bell className="w-5 h-5 text-blue-600 dark:text-cyan-400" />
                  <span>حالة إشعارات هذا الجهاز</span>
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  تلقي تنبيهات فورية عند وصول أي رسالة جديدة من العملاء حتى عندما يكون المتصفح مغلقاً.
                </p>
              </div>

              {/* Status Badge */}
              <div className="flex items-center gap-2">
                <span className={`px-3 py-1.5 rounded-xl text-xs font-extrabold flex items-center gap-1.5 ${
                  permission === 'granted'
                    ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 border border-emerald-500/20'
                    : permission === 'denied'
                    ? 'bg-rose-100 dark:bg-rose-950 text-rose-700 dark:text-rose-300 border border-rose-500/20'
                    : 'bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300 border border-amber-500/20'
                }`}>
                  <span className={`w-2 h-2 rounded-full ${
                    permission === 'granted' ? 'bg-emerald-500' : permission === 'denied' ? 'bg-rose-500' : 'bg-amber-500'
                  }`} />
                  <span>
                    {permission === 'granted' ? 'الإذن مفعّل (Granted)' : permission === 'denied' ? 'الإذن محظور (Blocked)' : 'في انتظار التفعيل'}
                  </span>
                </span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-3 flex-wrap pt-2 border-t border-slate-100 dark:border-slate-800">
              <button
                onClick={handleEnablePush}
                disabled={subscribing}
                className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md shadow-blue-600/20 flex items-center gap-2 transition disabled:opacity-50"
              >
                <Smartphone className="w-4 h-4" />
                <span>{subscribing ? 'جاري التفعيل والتسجيل...' : 'تفعيل الإشعارات على هذا الجهاز'}</span>
              </button>

              <button
                onClick={handleTestPush}
                disabled={testingPush}
                className="px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 font-bold text-xs transition flex items-center gap-2 disabled:opacity-50"
              >
                <Send className="w-3.5 h-3.5 text-blue-500" />
                <span>{testingPush ? 'جاري الإرسال...' : 'إرسال إشعار تجريبي (Test Push)'}</span>
              </button>

              <button
                onClick={handleDisablePush}
                disabled={subscribing}
                className="px-4 py-2.5 rounded-xl text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 text-xs font-semibold transition"
              >
                إلغاء التفعيل
              </button>
            </div>
          </div>

          {/* Notification Preferences Switches */}
          {pushStatus?.preferences && (
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-5 sm:p-6 shadow-xs space-y-4">
              <h3 className="font-extrabold text-sm sm:text-base text-slate-900 dark:text-white flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-blue-600 dark:text-cyan-400" />
                <span>تفضيلات التنبيهات والخصوصية</span>
              </h3>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                {/* Desktop Switch */}
                <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 flex items-center justify-between">
                  <div>
                    <h4 className="font-bold text-slate-900 dark:text-white mb-0.5">إشعارات المتصفح والكمبيوتر</h4>
                    <p className="text-slate-500 text-[11px]">إظهار تنبيهات سطح المكتب عند فتح لوحة التحكم</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={pushStatus.preferences.desktop_enabled}
                    onChange={(e) => handleUpdatePreferences({ desktop_enabled: e.target.checked })}
                    className="w-5 h-5 accent-blue-600 rounded cursor-pointer"
                  />
                </div>

                {/* Mobile Web Push Switch */}
                <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 flex items-center justify-between">
                  <div>
                    <h4 className="font-bold text-slate-900 dark:text-white mb-0.5">إشعارات الموبايل والآيفون (Web Push)</h4>
                    <p className="text-slate-500 text-[11px]">إرسال إشعارات فورية عبر نظام VAPID Push</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={pushStatus.preferences.mobile_push_enabled}
                    onChange={(e) => handleUpdatePreferences({ mobile_push_enabled: e.target.checked })}
                    className="w-5 h-5 accent-blue-600 rounded cursor-pointer"
                  />
                </div>

                {/* Sound Chime Switch */}
                <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 flex items-center justify-between">
                  <div>
                    <h4 className="font-bold text-slate-900 dark:text-white mb-0.5 flex items-center gap-1.5">
                      <Volume2 className="w-4 h-4 text-blue-500" />
                      <span>نغمة وتنبيه صوتي (Audio Chime)</span>
                    </h4>
                    <p className="text-slate-500 text-[11px]">تشغيل نغمة مميزة عند وصول رسالة جديدة</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={pushStatus.preferences.sound_enabled}
                    onChange={(e) => handleUpdatePreferences({ sound_enabled: e.target.checked })}
                    className="w-5 h-5 accent-blue-600 rounded cursor-pointer"
                  />
                </div>

                {/* Privacy Preview Switch */}
                <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 flex items-center justify-between">
                  <div>
                    <h4 className="font-bold text-slate-900 dark:text-white mb-0.5 flex items-center gap-1.5">
                      <Eye className="w-4 h-4 text-blue-500" />
                      <span>معاينة نص الرسالة (Lockscreen Preview)</span>
                    </h4>
                    <p className="text-slate-500 text-[11px]">إظهار مقتطف من نص الرسالة واسم العميل في الإشعار</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={pushStatus.preferences.preview_enabled}
                    onChange={(e) => handleUpdatePreferences({ preview_enabled: e.target.checked })}
                    className="w-5 h-5 accent-blue-600 rounded cursor-pointer"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Registered Devices List */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-5 sm:p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-extrabold text-sm sm:text-base text-slate-900 dark:text-white flex items-center gap-2">
                <Smartphone className="w-5 h-5 text-blue-600 dark:text-cyan-400" />
                <span>الأجهزة المسجلة لحسابك ({pushStatus?.devices_count || 0})</span>
              </h3>
            </div>

            {!pushStatus?.devices || pushStatus.devices.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-400 border border-dashed border-slate-200 dark:border-slate-800 rounded-2xl">
                لا توجد أجهزة مسجلة حالياً. اضغط على "تفعيل الإشعارات على هذا الجهاز" أعلاه لتسجيل جهازك.
              </div>
            ) : (
              <div className="divide-y divide-slate-100 dark:divide-slate-800">
                {pushStatus.devices.map(device => (
                  <div key={device.id} className="py-3 flex items-center justify-between gap-3 text-xs">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-900 dark:text-white">{device.device_name}</span>
                        <span className="text-[10px] bg-emerald-100 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 font-extrabold px-1.5 py-0.2 rounded-md">
                          نشط
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400">
                        تاريخ التسجيل: {device.created_at ? new Date(device.created_at).toLocaleDateString('ar-EG') : 'غير محدد'} • آخر نشاط: {device.last_used_at ? new Date(device.last_used_at).toLocaleTimeString('ar-EG') : 'الآن'}
                      </p>
                    </div>

                    <button
                      onClick={() => handleDeleteDevice(device.id)}
                      title="حذف الجهاز وإلغاء إرسال الإشعارات له"
                      className="p-2 rounded-xl text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* TAB 2: COMPANY IDENTITY & DETAILS                       */}
      {/* ======================================================== */}
      {activeTab === 'company' && (
        <form onSubmit={handleSaveCompany} className="space-y-6">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-5 sm:p-6 shadow-xs space-y-4">
            <h3 className="font-extrabold text-sm sm:text-base text-slate-900 dark:text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-blue-600 dark:text-cyan-400" />
              <span>الهوية الرسمية والعلامة التجارية</span>
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
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-5 sm:p-6 shadow-xs space-y-4">
            <h3 className="font-extrabold text-sm sm:text-base text-slate-900 dark:text-white flex items-center gap-2">
              <Globe className="w-5 h-5 text-blue-600 dark:text-cyan-400" />
              <span>معرض الأعمال والروابط الرسمية</span>
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
                <label className="block font-semibold mb-1">عنوان سيرفر تيليجرام</label>
                <input
                  type="url"
                  value={company.telegram_endpoint}
                  onChange={e => setCompany({ ...company, telegram_endpoint: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
                />
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={savingCompany}
            className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md shadow-blue-600/20 flex items-center gap-2 transition disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            <span>{savingCompany ? 'جاري الحفظ...' : 'حفظ تعديلات الهوية'}</span>
          </button>
        </form>
      )}
    </div>
  );
}
