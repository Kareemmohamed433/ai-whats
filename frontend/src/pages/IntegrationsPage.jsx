import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Share2, CheckCircle2, AlertTriangle, ShieldAlert, RefreshCw, Zap, ExternalLink } from 'lucide-react';

export default function IntegrationsPage() {
  const [integrations, setIntegrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [testingProvider, setTestingProvider] = useState(null);
  const [testResult, setTestResult] = useState(null);

  const loadIntegrations = () => {
    api.get('/integrations').then(res => {
      if (res.success) setIntegrations(res.integrations);
    }).catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadIntegrations();
  }, []);

  const handleTestConnection = async (provider) => {
    setTestingProvider(provider);
    setTestResult(null);
    try {
      const res = await api.post(`/integrations/${provider}/test`);
      setTestResult({ provider, success: res.success, message: res.message, reason: res.reason });
    } catch (err) {
      setTestResult({ provider, success: false, message: err.message || 'فشل الفحص' });
    } finally {
      setTestingProvider(null);
    }
  };

  const getPlatformMeta = (provider) => {
    switch (provider) {
      case 'whatsapp':
        return { name: 'واتساب الأعمال (WhatsApp Business Cloud API)', desc: 'ربط الحساب الرسمي لاستقبال إشعارات وتأكيدات الشراء التلقائية.', icon: '💬', color: 'border-emerald-500/40 bg-emerald-500/5' };
      case 'instagram':
        return { name: 'إنستغرام (Instagram Direct Graph API)', desc: 'الرد على الرسائل المباشرة DMs والتعليقات التلقائية عبر Meta Graph API.', icon: '📸', color: 'border-pink-500/40 bg-pink-500/5' };
      case 'telegram':
        return { name: 'تيليجرام (Telegram Bot API)', desc: 'ربط البوت لتتبع الطلبات والإجابة على الاستفسارات الفورية.', icon: '🤖', color: 'border-sky-500/40 bg-sky-500/5' };
      case 'tiktok':
        return { name: 'تيك توك (TikTok Business Messaging)', desc: 'التراسل عبر TikTok Messaging API وتوثيق حساب المتجر الرسمي.', icon: '🎵', color: 'border-slate-700/40 bg-slate-800/5' };
      case 'ai_provider':
        return { name: 'مزود الذكاء الاصطناعي (OpenAI / Groq API)', desc: 'المحرك البرمجي لتوليد الإجابات الذكية وتفسير الاستفسارات.', icon: '⚡', color: 'border-teal-500/40 bg-teal-500/5' };
      default:
        return { name: provider, desc: '', icon: '🔗', color: '' };
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-white">ربط المنصات وقنوات التواصل (Integrations)</h2>
        <p className="text-xs text-slate-500">حالة الاتصال الحقيقية وإعدادات الويب هوكس والربط الرسمي مع الشبكات</p>
      </div>

      {testResult && (
        <div className={`p-4 rounded-2xl border text-xs flex items-center justify-between ${
          testResult.success ? 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-300 text-emerald-800 dark:text-emerald-200' : 'bg-rose-50 dark:bg-rose-950/40 border-rose-300 text-rose-800 dark:text-rose-200'
        }`}>
          <div className="flex items-center gap-2">
            {testResult.success ? <CheckCircle2 className="w-5 h-5 text-emerald-500" /> : <AlertTriangle className="w-5 h-5 text-rose-500" />}
            <div>
              <span className="font-bold">{testResult.message}</span>
              {testResult.reason && <p className="text-[11px] mt-0.5 opacity-90">{testResult.reason}</p>}
            </div>
          </div>
          <button onClick={() => setTestResult(null)} className="font-bold underline text-[11px]">إغلاق</button>
        </div>
      )}

      {/* Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full py-12 text-center text-xs text-slate-400">جاري فحص وتحديث حالات الاتصال...</div>
        ) : (
          integrations.map(item => {
            const meta = getPlatformMeta(item.provider);
            const isTikTok = item.provider === 'tiktok';
            const isConnected = item.status === 'connected';

            return (
              <div key={item.provider} className={`bg-white dark:bg-slate-900 border ${meta.color} rounded-3xl p-6 shadow-sm flex flex-col justify-between space-y-4`}>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">{meta.icon}</span>
                      <h3 className="font-bold text-sm text-slate-900 dark:text-white">{meta.name}</h3>
                    </div>

                    <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold ${
                      isConnected ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300' :
                      isTikTok ? 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300' :
                      'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400'
                    }`}>
                      {isConnected ? 'متصل 🟢' : isTikTok ? 'غير متاح حالياً 🟡' : 'غير متصل ⚪'}
                    </span>
                  </div>

                  <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">{meta.desc}</p>

                  {/* TikTok Specific Real Warning */}
                  {isTikTok && (
                    <div className="p-3 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-[11px] text-amber-900 dark:text-amber-200 space-y-1">
                      <div className="font-bold flex items-center gap-1">
                        <ShieldAlert className="w-3.5 h-3.5 text-amber-600" /> تنبيه التوثيق الرسمي:
                      </div>
                      <p className="leading-normal">
                        "Messaging is not currently available for this TikTok account/API configuration."
                      </p>
                    </div>
                  )}
                </div>

                <div className="pt-3 border-t border-slate-100 dark:border-slate-800/60 flex items-center justify-between gap-2">
                  <button
                    onClick={() => handleTestConnection(item.provider)}
                    disabled={testingProvider === item.provider}
                    className="px-3 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 font-bold text-xs flex items-center gap-1.5 transition-all"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${testingProvider === item.provider ? 'animate-spin' : ''}`} />
                    اختبار الاتصال
                  </button>

                  <button
                    onClick={() => alert(`تكوين إعدادات البيئة المفاتيح لـ ${meta.name} يتم من ملف .env الخاص بالسيرفر.`)}
                    className="px-3 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition-all"
                  >
                    {isConnected ? 'تعديل الضبط' : 'ربط الحساب'}
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
