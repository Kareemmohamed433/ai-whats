import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Zap, Plus, Play, Pause, Trash2, CheckCircle2, Sliders } from 'lucide-react';

export default function AutomationPage() {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    trigger_event: 'message_received',
    reply_content: '',
    pause_ai: false
  });

  const loadRules = () => {
    api.get('/automations').then(res => {
      if (res.success) setRules(res.automations);
    }).catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadRules();
  }, []);

  const handleToggle = async (id) => {
    try {
      const res = await api.post(`/automations/${id}/toggle`);
      if (res.success) loadRules();
    } catch (err) {
      alert(err.message || 'فشل التعديل');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('هل أنت تأكد من حذف هذه القاعدة؟')) return;
    try {
      const res = await api.delete(`/automations/${id}`);
      if (res.success) loadRules();
    } catch (err) {
      alert(err.message || 'فشل الحذف');
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const actions = [];
      if (formData.reply_content) {
        actions.push({ type: 'send_reply', content: formData.reply_content });
      }
      if (formData.pause_ai) {
        actions.push({ type: 'pause_ai' });
      }

      const res = await api.post('/automations', {
        name: formData.name,
        trigger_event: formData.trigger_event,
        actions: actions
      });

      if (res.success) {
        setShowModal(false);
        setFormData({ name: '', trigger_event: 'message_received', reply_content: '', pause_ai: false });
        loadRules();
      }
    } catch (err) {
      alert(err.message || 'فشل إنشاء القاعدة');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">قواعد الأتمتة والسلوك التلقائي (Automation Rules)</h2>
          <p className="text-xs text-slate-500">إنشاء قواعد وتنبيهات داخلية مباشرة في Flask دون الحاجة لأية منصات خارجية مثل n8n</p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md flex items-center gap-1.5 transition-all self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" /> إنشاء قاعدة جديدة
        </button>
      </div>

      {/* Rules List */}
      <div className="space-y-4">
        {loading ? (
          <p className="text-xs text-slate-400 py-8 text-center">جاري تحميل قواعد الأتمتة...</p>
        ) : rules.length === 0 ? (
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-8 text-center text-slate-400 text-xs">
            لا توجد قواعد أتمتة مضافة حالياً. اضغط "إنشاء قاعدة جديدة" لإضافة أول قاعدة تلقائية.
          </div>
        ) : (
          rules.map(rule => (
            <div key={rule.id} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-5 shadow-sm flex items-center justify-between gap-4">
              <div className="space-y-1.5">
                <div className="flex items-center gap-2">
                  <span className={`w-2.5 h-2.5 rounded-full ${rule.is_active ? 'bg-emerald-500' : 'bg-slate-400'}`}></span>
                  <h3 className="font-bold text-sm text-slate-900 dark:text-white">{rule.name}</h3>
                  <span className="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-[10px] font-mono font-bold text-slate-600 dark:text-slate-300">
                    عند: {rule.trigger_event}
                  </span>
                </div>

                <div className="text-xs text-slate-500 flex items-center gap-2">
                  <span>الإجراءات:</span>
                  {rule.actions?.map((act, i) => (
                    <span key={i} className="px-2 py-0.5 rounded-md bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 font-medium">
                      {act.type === 'send_reply' ? `إرسال: "${act.content}"` : act.type === 'pause_ai' ? 'إيقاف AI وتصعيد' : act.type}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleToggle(rule.id)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                    rule.is_active ? 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300' : 'bg-emerald-100 text-emerald-700'
                  }`}
                >
                  {rule.is_active ? 'تعطيل' : 'تفعيل'}
                </button>
                <button
                  onClick={() => handleDelete(rule.id)}
                  className="p-2 text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-xl"
                  title="حذف"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Add Automation Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 w-full max-w-md shadow-2xl space-y-4">
            <h3 className="font-bold text-base text-slate-900 dark:text-white">إنشاء قاعدة أتمتة جديدة</h3>
            <form onSubmit={handleCreate} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold mb-1">اسم القاعدة</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={e => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
                  placeholder="مثال: الرد التلقائي في عطلة نهاية الأسبوع"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1">حدث المشغل (Trigger Event)</label>
                <select
                  value={formData.trigger_event}
                  onChange={e => setFormData({ ...formData, trigger_event: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
                >
                  <option value="message_received">عند استلام أية رسالة جديدة</option>
                  <option value="outside_hours">عند الاستلام خارج مواعيد العمل الرسمية</option>
                  <option value="human_requested">عند طلب العميل التحدث لموظف بشري</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold mb-1">نص الرد التلقائي (اختياري)</label>
                <textarea
                  rows="3"
                  value={formData.reply_content}
                  onChange={e => setFormData({ ...formData, reply_content: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
                  placeholder="أدخل الرسالة التي سيتم إرسالها تلقائياً..."
                ></textarea>
              </div>

              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="pause_ai_cb"
                  checked={formData.pause_ai}
                  onChange={e => setFormData({ ...formData, pause_ai: e.target.checked })}
                  className="w-4 h-4 text-emerald-600 rounded"
                />
                <label htmlFor="pause_ai_cb" className="font-semibold text-slate-700 dark:text-slate-300">
                  إيقاف AI وتصعيد المحادثة للبشري تلقائياً
                </label>
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
                  حفظ القاعدة
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
