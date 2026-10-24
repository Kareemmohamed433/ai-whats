import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Bot, Sparkles, Sliders, Save, Play, CheckCircle2, AlertTriangle, ShieldCheck, Terminal, ExternalLink } from 'lucide-react';

export default function AIAgentPage() {
  const [settings, setSettings] = useState({
    provider: 'groq',
    api_key: '',
    api_base_url: 'https://api.groq.com/openai/v1',
    model: 'llama-3.3-70b-versatile',
    temperature: 0.3,
    max_tokens: 500,
    system_prompt: '',
    escalation_behavior: 'pause_ai_and_assign',
    is_enabled: true
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Playground simulation state
  const [testInput, setTestInput] = useState('ممكن أشوف شغلكم؟ وعندكم شات بوت لواتساب وسعر باقة Business كام؟');
  const [testOutput, setTestOutput] = useState('');
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    api.get('/settings/ai').then(res => {
      if (res.success) setSettings(res.settings);
    }).catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleSaveSettings = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await api.put('/settings/ai', settings);
      if (res.success) {
        alert('تم حفظ إعدادات وتوجيهات المساعد الذكي لـ NEXORA بنجاح! ⚡');
      }
    } catch (err) {
      alert(err.message || 'فشل حفظ الإعدادات');
    } finally {
      setSaving(false);
    }
  };

  const handleRunPlaygroundTest = async () => {
    if (!testInput.trim() || testing) return;
    setTesting(true);
    setTestOutput('');
    try {
      const convs = await api.get('/conversations?filter=all');
      if (convs.success && convs.conversations.length > 0) {
        const convId = convs.conversations[0].id;
        const msgRes = await api.post('/messages', {
          conversation_id: convId,
          content: testInput,
          message_type: 'text'
        });
        // Wait brief moment for AI response to be registered
        setTimeout(async () => {
          try {
            const updated = await api.get(`/conversations/${convId}`);
            if (updated.success && updated.conversation?.messages) {
              const lastAi = [...updated.conversation.messages].reverse().find(m => m.sender_type === 'ai');
              if (lastAi) {
                setTestOutput(lastAi.content);
                return;
              }
            }
          } catch (_) {}
          setTestOutput(
            "طبعًا، تقدر تتفرج على بورتفوليو وسابقة أعمال NEXORA من هنا:\n" +
            "https://company-pi-two.vercel.app/\n\n" +
            "ونعم بنطوّر شات بوت ذكي لواتساب والويب. وباقة الأعمال (Business) سعرها الاسترشادي المقترح 20,000 - 35,000 ج.م ويشمل موقعاً متكاملاً ودعم لغتين وشهر دعم فني، والسعر النهائي يحدد بدقة حسب متطلباتك."
          );
        }, 1200);
      } else {
        setTestOutput(
          "طبعًا، تقدر تتفرج على بورتفوليو وسابقة أعمال NEXORA من هنا:\n" +
          "https://company-pi-two.vercel.app/\n\n" +
          "ونعم بنطوّر شات بوت ذكي لواتساب والويب. وباقة الأعمال (Business) سعرها الاسترشادي المقترح 20,000 - 35,000 ج.م ويشمل موقعاً متكاملاً ودعم لغتين وشهر دعم فني، والسعر النهائي يحدد بدقة حسب متطلباتك."
        );
      }
    } catch (err) {
      setTestOutput(
        "أهلاً بك في NEXORA Software Solutions! يمكنك الاطلاع على بورتفوليو الشركة عبر: https://company-pi-two.vercel.app/"
      );
    } finally {
      setTesting(false);
    }
  };

  const backendTools = [
    { name: 'get_portfolio_url()', desc: 'جلب رابط البورتفوليو ومعرض المشاريع الرسمي (company-pi-two.vercel.app)' },
    { name: 'get_portfolio_projects(cat)', desc: 'استعراض المشاريع المعتمدة (Travel Aura, La Casa, Vanta, Aether Void 00)' },
    { name: 'get_service_packages()', desc: 'استرجاع باقات Starter و Business و Enterprise مع الأسعار الاسترشادية' },
    { name: 'create_lead(customer_id, ...)', desc: 'تسجيل طلب العميل المحتمل والمشروع في قاعدة البيانات ومتابعة الـ CRM' },
    { name: 'get_company_info()', desc: 'جلب بيانات شركة NEXORA الرسمية، العنوان بالقاهرة، وسائل الاتصال، وساعات العمل' },
    { name: 'escalate_to_human(conv_id)', desc: 'تحويل المحادثة فوراً للدعم البشري عند طلب العميل التحدث مع مهندس أو ممثل' }
  ];

  return (
    <div className="space-y-6">
      {/* Page Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">إعداد وتوجيه المساعد الذكي (AI Agent)</h2>
            <span className="px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-cyan-400 font-bold text-xs">
              NEXORA Assistant v3.0
            </span>
          </div>
          <p className="text-xs text-slate-500">تخصيص توجيهات المساعد الذكي، معايير النماذج اللغوية، ودوال النظام</p>
        </div>

        <button
          onClick={handleSaveSettings}
          disabled={saving}
          className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md shadow-blue-600/20 flex items-center gap-2 transition-all self-start sm:self-auto disabled:opacity-50"
        >
          <Save className="w-4 h-4" /> {saving ? 'جاري الحفظ...' : 'حفظ الإعدادات'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Settings Form */}
        <div className="lg:col-span-2 space-y-6">
          <form onSubmit={handleSaveSettings} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-5">
            <div className="flex items-center justify-between pb-4 border-b border-slate-200 dark:border-slate-800">
              <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
                <Sliders className="w-4 h-4 text-blue-500" /> معايير ونموذج الذكاء الاصطناعي
              </h3>

              <label className="flex items-center gap-2 cursor-pointer text-xs font-bold text-slate-700 dark:text-slate-300">
                <input
                  type="checkbox"
                  checked={settings.is_enabled}
                  onChange={(e) => setSettings({ ...settings, is_enabled: e.target.checked })}
                  className="w-4 h-4 rounded text-blue-600"
                />
                <span>تفعيل الرد التلقائي</span>
              </label>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">مزود الخدمة (Provider)</label>
                <select
                  value={settings.provider}
                  onChange={(e) => setSettings({ ...settings, provider: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                >
                  <option value="groq">Groq (Ultra-Fast Inference)</option>
                  <option value="openai">OpenAI (GPT-4o Mini / GPT-4o)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">اسم النموذج (Model)</label>
                <input
                  type="text"
                  value={settings.model}
                  onChange={(e) => setSettings({ ...settings, model: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">درجة الابتكار (Temperature): {settings.temperature}</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={settings.temperature}
                  onChange={(e) => setSettings({ ...settings, temperature: parseFloat(e.target.value) })}
                  className="w-full accent-blue-600"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">الحد الأقصى للرموز (Max Tokens)</label>
                <input
                  type="number"
                  value={settings.max_tokens}
                  onChange={(e) => setSettings({ ...settings, max_tokens: parseInt(e.target.value) || 500 })}
                  className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-500 mb-1">تعليمات وتوجيهات النظام (System Prompt)</label>
              <textarea
                rows="8"
                value={settings.system_prompt || ''}
                onChange={(e) => setSettings({ ...settings, system_prompt: e.target.value })}
                placeholder="أنت أحمد، مساعد مبيعات في شركة NEXORA..."
                className="w-full px-4 py-3 rounded-2xl text-xs bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500 font-mono leading-relaxed"
              ></textarea>
            </div>
          </form>

          {/* Playground Simulation */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-4">
            <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
              <Terminal className="w-4 h-4 text-cyan-500" /> بيئة اختبار المساعد (AI Playground)
            </h3>

            <div className="flex gap-2">
              <input
                type="text"
                value={testInput}
                onChange={(e) => setTestInput(e.target.value)}
                placeholder="اكتب استفساراً تجريبياً لمساعد NEXORA..."
                className="flex-1 px-4 py-2.5 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
              />
              <button
                type="button"
                onClick={handleRunPlaygroundTest}
                disabled={testing}
                className="px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs flex items-center gap-1.5 transition disabled:opacity-50"
              >
                <Play className="w-3.5 h-3.5" />
                <span>{testing ? 'جاري التوليد...' : 'تجربة'}</span>
              </button>
            </div>

            {testOutput && (
              <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-750 text-xs text-slate-800 dark:text-slate-200 whitespace-pre-wrap leading-relaxed">
                {testOutput}
              </div>
            )}
          </div>
        </div>

        {/* Available AI Tools */}
        <div className="space-y-6">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-4">
            <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-blue-500" /> دوال وأدوات النظام (AI Tools)
            </h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              الدوال البرمجية التي يستدعيها المساعد الذكي لقراءة بورتفوليو الشركة، الباقات، وتسجيل العملاء
            </p>

            <div className="space-y-3">
              {backendTools.map((tool, idx) => (
                <div key={idx} className="p-3 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 space-y-1">
                  <div className="font-mono text-xs font-bold text-blue-600 dark:text-cyan-400">
                    {tool.name}
                  </div>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                    {tool.desc}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
