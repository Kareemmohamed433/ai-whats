import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { BookOpen, Plus, HelpCircle, Store, Trash2, Edit2, CheckCircle2 } from 'lucide-react';

export default function KnowledgeBasePage() {
  const [faqs, setFaqs] = useState([]);
  const [storeInfo, setStoreInfo] = useState({});
  const [loading, setLoading] = useState(true);

  // New FAQ form
  const [showFaqModal, setShowFaqModal] = useState(false);
  const [newQuestion, setNewQuestion] = useState('');
  const [newAnswer, setNewAnswer] = useState('');

  const loadKnowledge = () => {
    Promise.all([
      api.get('/knowledge/faqs'),
      api.get('/settings/store')
    ]).then(([faqsRes, storeRes]) => {
      if (faqsRes.success) setFaqs(faqsRes.faqs);
      if (storeRes.success) setStoreInfo(storeRes.settings);
    }).catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadKnowledge();
  }, []);

  const handleAddFaq = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post('/knowledge/faqs', {
        question: newQuestion,
        answer: newAnswer
      });
      if (res.success) {
        setShowFaqModal(false);
        setNewQuestion('');
        setNewAnswer('');
        loadKnowledge();
      }
    } catch (err) {
      alert(err.message || 'فشل إضافة السؤال');
    }
  };

  const handleDeleteFaq = async (id) => {
    if (!window.confirm('هل أنت تأكد من حذف هذا السؤال الشائع؟')) return;
    try {
      const res = await api.delete(`/knowledge/faqs/${id}`);
      if (res.success) loadKnowledge();
    } catch (err) {
      alert(err.message || 'فشل الحذف');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">قاعدة المعرفة والأسئلة الشائعة (Knowledge Base)</h2>
          <p className="text-xs text-slate-500">إدارة الإجابات الشائعة وسياسات المتجر التي يقرأها الذكاء الاصطناعي للإجابة على العملاء</p>
        </div>

        <button
          onClick={() => setShowFaqModal(true)}
          className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md flex items-center gap-1.5 transition-all self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" /> إضافة سؤال شائع جديد
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* FAQs List */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm">
            <h3 className="font-bold text-sm text-slate-900 dark:text-white mb-4 flex items-center gap-2">
              <HelpCircle className="w-4 h-4 text-emerald-500" /> الأسئلة والأجوبة الشائعة ({faqs.length})
            </h3>

            <div className="space-y-3">
              {loading ? (
                <p className="text-xs text-slate-400 py-4">جاري تحميل الأسئلة الشائعة...</p>
              ) : faqs.length === 0 ? (
                <p className="text-xs text-slate-400 py-4">لا توجد أسئلة شائعة مضافة</p>
              ) : (
                faqs.map(faq => (
                  <div key={faq.id} className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60 space-y-2">
                    <div className="flex items-start justify-between gap-3">
                      <h4 className="font-bold text-xs text-slate-900 dark:text-white">س: {faq.question}</h4>
                      <button
                        onClick={() => handleDeleteFaq(faq.id)}
                        className="text-rose-500 hover:text-rose-600 p-1"
                        title="حذف"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">ج: {faq.answer}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Store Info Card */}
        <div>
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-4">
            <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
              <Store className="w-4 h-4 text-amber-500" /> معلومات وسياسات المتجر النشطة
            </h3>

            <div className="space-y-3 text-xs">
              <div>
                <span className="font-bold text-slate-500 block">اسم العلامة التجارية:</span>
                <span className="font-semibold text-slate-900 dark:text-white">{storeInfo.store_name}</span>
              </div>
              <div>
                <span className="font-bold text-slate-500 block">سياسة الشحن والتوصيل:</span>
                <span className="text-slate-700 dark:text-slate-300">{storeInfo.shipping_policy}</span>
              </div>
              <div>
                <span className="font-bold text-slate-500 block">حد الشحن المجاني:</span>
                <span className="text-emerald-600 font-bold">{storeInfo.free_shipping_threshold} جنيه مصري</span>
              </div>
              <div>
                <span className="font-bold text-slate-500 block">طرق الدفع المعتمده:</span>
                <span className="text-slate-700 dark:text-slate-300">{storeInfo.payment_methods}</span>
              </div>
              <div>
                <span className="font-bold text-slate-500 block">سياسة الاسترجاع:</span>
                <span className="text-slate-700 dark:text-slate-300">{storeInfo.return_policy}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Add FAQ Modal */}
      {showFaqModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 w-full max-w-md shadow-2xl space-y-4">
            <h3 className="font-bold text-base text-slate-900 dark:text-white">إضافة سؤال شائع جديد</h3>
            <form onSubmit={handleAddFaq} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold mb-1">السؤال</label>
                <input
                  type="text"
                  required
                  value={newQuestion}
                  onChange={e => setNewQuestion(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
                  placeholder="مثال: كم سعر التوصيل للقاهرة؟"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1">الإجابة</label>
                <textarea
                  rows="4"
                  required
                  value={newAnswer}
                  onChange={e => setNewAnswer(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
                  placeholder="أدخل الإجابة الدقيقة التي سيعتمد عليها AI..."
                ></textarea>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowFaqModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold"
                >
                  إلغاء
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-emerald-600 text-white font-bold"
                >
                  حفظ السؤال
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
