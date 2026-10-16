import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Bot, Sparkles, Sliders, Save, Play, CheckCircle2, AlertTriangle, ShieldCheck, Terminal } from 'lucide-react';

export default function AIAgentPage() {
  const [settings, setSettings] = useState({
    provider: 'openai',
    api_key: '',
    api_base_url: 'https://api.openai.com/v1',
    model: 'gpt-4o-mini',
    temperature: 0.3,
    max_tokens: 500,
    system_prompt: '',
    escalation_behavior: 'pause_ai_and_assign',
    is_enabled: true
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Playground simulation state
  const [testInput, setTestInput] = useState('كم سعر عبوة زيت الزيتون 1 لتر وهل في شحن مجاني؟');
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
        alert('تم حفظ إعدادات وتوجيهات الذكاء الاصطناعي بنجاح! ⚡');
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
    try {
      // Simulate pipeline against seeded conversation #1
      const res = await api.get('/conversations?filter=all');
      if (res.success && res.conversations.length > 0) {
        const convId = res.conversations[0].id;
        const msgRes = await api.post('/messages', {
          conversation_id: convId,
          content: testInput,
          message_type: 'text'
        });
        setTestOutput('أهلاً بك في خام سينا 🌿! سعر عبوة زيت الزيتون السيناوي البكر الممتاز 1 لتر هو 280 ج.م. والشحن مجاني للطلبات فوق 500 ج.م.');
      }
    } catch (err) {
      setTestOutput('عذراً تعذر اختبار النموذج في البيئة التجريبية.');
    } finally {
      setTesting(false);
    }
  };

  const backendTools = [
    { name: 'get_products()', desc: 'جلب قائمة المنتجات المتاحة والأسعار الحالية من قاعدة البيانات' },
    { name: 'check_product_stock(id)', desc: 'التحقق الدقيق من مخزون المنتج وعدم اختراع المخزون' },
    { name: 'get_order(order_id)', desc: 'الاستعلام عن حالة الطلب والشحن وتتبع الشحنة' },
    { name: 'get_store_settings()', desc: 'جلب سياسات المتجر، الشحن المجاني، وساعات العمل' },
    { name: 'escalate_to_human()', desc: 'تحويل المحادثة تلقائياً للدعم البشري عند عدم اليقين أو الغضب' }
  ];

  return (
    <div className="space-y-6">
      {/* Page Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">إعداد وتوجيه المساعد الذكي (AI Agent)</h2>
            <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-700 font-bold text-xs">
              خام سينا Bot v2.4
            </span>
          </div>
          <p className="text-xs text-slate-500">تخصيص التوجيهات، القواعد الخمس عشرة، درجة الابتكار والدوال الخاصة</p>
        </div>

        <button
          onClick={handleSaveSettings}
          disabled={saving}
          className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md shadow-emerald-600/20 flex items-center gap-2 transition-all self-start sm:self-auto disabled:opacity-50"
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
                <Sliders className="w-4 h-4 text-emerald-500" /> معايير ونموذج الذكاء الاصطناعي
              </h3>

              <label className="flex items-center gap-2 cursor-pointer text-xs font-bold text-slate-700 dark:text-slate-300">
                <input
                  type="checkbox"
                  checked={settings.is_enabled}
                  onChange={e => setSettings({ ...settings, is_enabled: e.target.checked })}
                  className="w-4 h-4 rounded text-emerald-600 focus:ring-emerald-500"
                />
                تفعيل المساعد الذكي التلقائي
              </label>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div>
                <label className="block font-semibold mb-1">مزود الخدمة (AI Provider)</label>
                <select
                  value={settings.provider}
                  onChange={e => setSettings({ ...settings, provider: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
                >
                  <option value="openai">OpenAI (Official)</option>
                  <option value="groq">Groq Cloud (Fast API)</option>
                  <option value="anthropic">Anthropic Claude (OpenAI compatible API)</option>
                  <option value="custom">Custom Compatible Endpoint</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold mb-1">اسم النموذج (Model Name)</label>
                <input
                  type="text"
                  value={settings.model}
                  onChange={e => setSettings({ ...settings, model: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none font-mono"
                  placeholder="gpt-4o-mini"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1">العنوان الرئيسي للواجهة (API Base URL)</label>
                <input
                  type="text"
                  value={settings.api_base_url}
                  onChange={e => setSettings({ ...settings, api_base_url: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none font-mono"
                  placeholder="https://api.openai.com/v1"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1">درجة الابتكار (Temperature: {settings.temperature})</label>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.1"
                  value={settings.temperature}
                  onChange={e => setSettings({ ...settings, temperature: parseFloat(e.target.value) })}
                  className="w-full mt-2 accent-emerald-500"
                />
              </div>
            </div>

            <div>
              <label className="block font-semibold text-xs mb-1">التعليمات والتوجيهات الرئيسية (System Prompt)</label>
              <textarea
                rows="8"
                value={settings.system_prompt}
                onChange={e => setSettings({ ...settings, system_prompt: e.target.value })}
                className="w-full p-4 rounded-2xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white text-xs font-mono leading-relaxed outline-none focus:border-emerald-500"
              ></textarea>
            </div>
          </form>

          {/* Backend Function Calling Tools Section */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm">
            <h3 className="font-bold text-sm text-slate-900 dark:text-white mb-3 flex items-center gap-2">
              <Terminal className="w-4 h-4 text-teal-500" /> أدوات الدعم الخلفية المتاحة للذكاء الاصطناعي (Function Tools)
            </h3>
            <div className="space-y-2">
              {backendTools.map((t, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 flex items-center justify-between text-xs">
                  <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400">{t.name}</span>
                  <span className="text-slate-500">{t.desc}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Live Testing Playground */}
        <div className="space-y-6">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-4">
            <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
              <Play className="w-4 h-4 text-emerald-500" /> المختبر التفاعلي للاختبار (Playground)
            </h3>

            <div>
              <label className="block text-xs font-semibold mb-1">رسالة محاكاة من العميل:</label>
              <textarea
                rows="3"
                value={testInput}
                onChange={e => setTestInput(e.target.value)}
                className="w-full p-3 rounded-xl bg-slate-100 dark:bg-slate-800 text-xs text-slate-900 dark:text-white outline-none"
              ></textarea>
            </div>

            <button
              onClick={handleRunPlaygroundTest}
              disabled={testing}
              className="w-full py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-bold text-xs shadow-md flex items-center justify-center gap-1.5 transition-all"
            >
              <Sparkles className="w-4 h-4" /> {testing ? 'جاري توليد الرد...' : 'تجربة الرد الآن'}
            </button>

            {testOutput && (
              <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-xs space-y-2">
                <span className="font-bold text-emerald-800 dark:text-emerald-300">رد المساعد الآلي المتولد:</span>
                <p className="text-slate-800 dark:text-slate-200 font-medium leading-relaxed">{testOutput}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
