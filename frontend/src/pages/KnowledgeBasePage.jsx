import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { BookOpen, Plus, HelpCircle, Building2, Trash2, Edit2, ExternalLink, ShieldCheck, Clock } from 'lucide-react';

export default function KnowledgeBasePage() {
  const [faqs, setFaqs] = useState([]);
  const [companyInfo, setCompanyInfo] = useState({});
  const [loading, setLoading] = useState(true);

  // New FAQ form
  const [showFaqModal, setShowFaqModal] = useState(false);
  const [newQuestion, setNewQuestion] = useState('');
  const [newAnswer, setNewAnswer] = useState('');
  const [newCategory, setNewCategory] = useState('الخدمات والأسئلة العامة');

  const loadKnowledge = () => {
    Promise.all([
      api.get('/knowledge/faqs?active_only=true'),
      api.get('/settings/company')
    ]).then(([faqsRes, compRes]) => {
      if (faqsRes.success) setFaqs(faqsRes.faqs || []);
      if (compRes.success) setCompanyInfo(compRes.settings || {});
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
        answer: newAnswer,
        category: newCategory
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
    if (!window.confirm('هل أنت متأكد من حذف هذا السؤال الشائع؟')) return;
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
          <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-blue-500" />
            قاعدة المعرفة والأسئلة الشائعة (NEXORA Knowledge Base)
          </h2>
          <p className="text-xs text-slate-500">
            إدارة الأسئلة الشائعة، معلومات الشركة المعتمدة، والبورتفوليو التي يعتمد عليها المساعد الذكي
          </p>
        </div>

        <button
          onClick={() => setShowFaqModal(true)}
          className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md shadow-blue-600/20 flex items-center gap-1.5 transition-all self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" /> إضافة سؤال شائع جديد
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* FAQs List */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm">
            <h3 className="font-bold text-sm text-slate-900 dark:text-white mb-4 flex items-center gap-2">
              <HelpCircle className="w-4 h-4 text-cyan-500" /> الأسئلة والأجوبة الشائعة المعتمدة ({faqs.length})
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
                      <div>
                        <span className="text-[10px] font-bold text-blue-600 dark:text-cyan-400 bg-blue-50 dark:bg-blue-950/60 px-2 py-0.5 rounded-full inline-block mb-1">
                          {faq.category || 'عام'}
                        </span>
                        <h4 className="font-bold text-xs text-slate-900 dark:text-white">س: {faq.question}</h4>
                      </div>
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

        {/* Company Knowledge Card */}
        <div>
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-4">
            <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
              <Building2 className="w-4 h-4 text-blue-500" /> بيانات الشركة الرسمية
            </h3>

            <div className="space-y-3 text-xs">
              <div>
                <span className="font-bold text-slate-500 block">اسم الشركة:</span>
                <span className="font-semibold text-slate-900 dark:text-white">{companyInfo.company_name || 'NEXORA Software Solutions'}</span>
              </div>
              <div>
                <span className="font-bold text-slate-500 block">شعار العلامة التجارية:</span>
                <span className="text-blue-600 dark:text-cyan-400 font-bold">{companyInfo.tagline || 'Ideas → Code → Impact'}</span>
              </div>
              <div>
                <span className="font-bold text-slate-500 block">البورتفوليو الرسمي:</span>
                <a
                  href={companyInfo.portfolio_url || 'https://company-pi-two.vercel.app/'}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-cyan-500 hover:underline flex items-center gap-1 font-semibold mt-0.5"
                >
                  <span>{companyInfo.portfolio_url || 'https://company-pi-two.vercel.app/'}</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
              <div>
                <span className="font-bold text-slate-500 block">رقم الهاتف / واتساب:</span>
                <span className="text-slate-700 dark:text-slate-300 font-mono">{companyInfo.phone || '+201556441133'}</span>
              </div>
              <div>
                <span className="font-bold text-slate-500 block">البريد الإلكتروني:</span>
                <span className="text-slate-700 dark:text-slate-300 font-mono">{companyInfo.email || 'contact@nexorasolutions.com'}</span>
              </div>
              <div>
                <span className="font-bold text-slate-500 block">المقر الرئيسي:</span>
                <span className="text-slate-700 dark:text-slate-300">{companyInfo.address || 'القاهرة، مصر'}</span>
              </div>
              <div>
                <span className="font-bold text-slate-500 block">مواعيد وساعات العمل:</span>
                <span className="text-slate-700 dark:text-slate-300">
                  {companyInfo.working_hours ? `${companyInfo.working_hours.working_days}: ${companyInfo.working_hours.opening_time} - ${companyInfo.working_hours.closing_time} (${companyInfo.working_hours.timezone || 'توقيت القاهرة'})` : 'الأحد - الخميس: 9:00 ص - 6:00 م (توقيت القاهرة)'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Add FAQ Modal */}
      {showFaqModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 w-full max-w-md shadow-2xl space-y-4">
            <h3 className="font-bold text-base text-slate-900 dark:text-white">إضافة سؤال شائع لـ NEXORA</h3>
            <form onSubmit={handleAddFaq} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold mb-1">تصنيف السؤال</label>
                <select
                  value={newCategory}
                  onChange={e => setNewCategory(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
                >
                  <option value="الخدمات والأسئلة العامة">الخدمات والأسئلة العامة</option>
                  <option value="تطوير المواقع والمنصات">تطوير المواقع والمنصات</option>
                  <option value="حلول الذكاء الاصطناعي">حلول الذكاء الاصطناعي</option>
                  <option value="الأسعار والباقات">الأسعار والباقات</option>
                  <option value="البورتفوليو وسابقة الأعمال">البورتفوليو وسابقة الأعمال</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold mb-1">السؤال</label>
                <input
                  type="text"
                  required
                  value={newQuestion}
                  onChange={e => setNewQuestion(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
                  placeholder="مثال: هل توفرون شات بوت ذكي لواتساب؟"
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
                  placeholder="أدخل الإجابة الدقيقة والمعتمدة..."
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
                  className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold"
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
