import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { 
  Sparkles, 
  Plus, 
  Trash2, 
  Edit2, 
  CheckCircle2, 
  ShieldAlert, 
  Check, 
  Clock, 
  Layers, 
  ExternalLink,
  AlertCircle
} from 'lucide-react';

export default function ProductsPage() {
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingPkg, setEditingPkg] = useState(null);

  const [formData, setFormData] = useState({
    name: '',
    name_ar: '',
    slug: '',
    description: '',
    target_audience: '',
    indicative_price_min: '',
    indicative_price_max: '',
    indicative_price_text: '',
    currency: 'EGP',
    support_period: '',
    is_approved: false,
    is_popular: false,
    is_active: true,
    features: ['']
  });

  const loadPackages = () => {
    setLoading(true);
    api.get('/packages?active_only=false')
      .then(res => {
        if (res.success) {
          setPackages(res.packages || []);
        }
      })
      .catch(err => {
        console.error("Failed to load packages:", err);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadPackages();
  }, []);

  const resetForm = () => {
    setEditingPkg(null);
    setFormData({
      name: '',
      name_ar: '',
      slug: '',
      description: '',
      target_audience: '',
      indicative_price_min: '',
      indicative_price_max: '',
      indicative_price_text: '',
      currency: 'EGP',
      support_period: '',
      is_approved: false,
      is_popular: false,
      is_active: true,
      features: ['']
    });
  };

  const openCreateModal = () => {
    resetForm();
    setShowModal(true);
  };

  const openEditModal = (pkg) => {
    setEditingPkg(pkg);
    setFormData({
      name: pkg.name || '',
      name_ar: pkg.name_ar || '',
      slug: pkg.slug || '',
      description: pkg.description || '',
      target_audience: pkg.target_audience || '',
      indicative_price_min: pkg.indicative_price_min ?? '',
      indicative_price_max: pkg.indicative_price_max ?? '',
      indicative_price_text: pkg.indicative_price_text || '',
      currency: pkg.currency || 'EGP',
      support_period: pkg.support_period || '',
      is_approved: Boolean(pkg.is_approved),
      is_popular: Boolean(pkg.is_popular),
      is_active: Boolean(pkg.is_active),
      features: (pkg.features && pkg.features.length > 0) ? pkg.features : ['']
    });
    setShowModal(true);
  };

  const handleFeatureChange = (index, value) => {
    const updated = [...formData.features];
    updated[index] = value;
    setFormData({ ...formData, features: updated });
  };

  const addFeatureInput = () => {
    setFormData({ ...formData, features: [...formData.features, ''] });
  };

  const removeFeatureInput = (index) => {
    const updated = formData.features.filter((_, i) => i !== index);
    setFormData({ ...formData, features: updated.length ? updated : [''] });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      ...formData,
      features: formData.features.filter(f => f.trim())
    };

    try {
      if (editingPkg) {
        await api.put(`/packages/${editingPkg.id}`, payload);
      } else {
        await api.post('/packages', payload);
      }
      setShowModal(false);
      resetForm();
      loadPackages();
    } catch (err) {
      alert(err.message || 'فشل حفظ باقة الخدمة');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('هل أنت متأكد من حذف هذه الباقة؟')) return;
    try {
      await api.delete(`/packages/${id}`);
      loadPackages();
    } catch (err) {
      alert(err.message || 'فشل حذف الباقة');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-500" />
            باقات الخدمات البرمجية (Service Packages)
          </h2>
          <p className="text-xs text-slate-500">
            إدارة باقات NEXORA (Starter, Business, Enterprise)، ميزات العمل، والأسعار الاسترشادية
          </p>
        </div>

        <button
          onClick={openCreateModal}
          className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md shadow-blue-600/20 flex items-center gap-2 transition-all self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" /> إضافة باقة جديدة
        </button>
      </div>

      {/* Official Guidelines Callout */}
      <div className="p-4 rounded-2xl bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800/60 flex items-start gap-3">
        <ShieldAlert className="w-5 h-5 text-blue-600 dark:text-cyan-400 shrink-0 mt-0.5" />
        <div className="text-xs text-blue-900 dark:text-blue-200 space-y-1">
          <p className="font-bold">سياسة التسعير الاسترشادي لشركة NEXORA:</p>
          <p className="leading-relaxed opacity-90">
            الأسعار المعروضة للباقات هي تقديرات استرشادية أولية، ويتم تأكيد العرض المالي النهائي للعميل بدقة وفقاً لنطاق ومتطلبات مشروعه المحددة.
          </p>
        </div>
      </div>

      {/* Packages Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full py-12 text-center text-xs text-slate-400">
            جاري تحميل الباقات والخدمات...
          </div>
        ) : packages.length === 0 ? (
          <div className="col-span-full py-12 text-center text-xs text-slate-400">
            لا توجد باقات حالياً. انقر على "إضافة باقة جديدة".
          </div>
        ) : (
          packages.map((pkg) => (
            <div
              key={pkg.id}
              className={`bg-white dark:bg-slate-900 border rounded-3xl p-6 shadow-sm flex flex-col justify-between transition-all duration-200 relative ${
                pkg.is_popular
                  ? 'border-blue-500 ring-2 ring-blue-500/20'
                  : 'border-slate-200 dark:border-slate-800'
              }`}
            >
              {/* Badges */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-blue-600 dark:text-cyan-400">
                    {pkg.name}
                  </span>
                  {pkg.is_popular && (
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-500 text-white">
                      الأكثر طلباً ⭐
                    </span>
                  )}
                </div>

                <span
                  className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                    pkg.is_approved
                      ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300'
                      : 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300'
                  }`}
                >
                  {pkg.is_approved ? 'سعر معتمد ✅' : 'تقدير استرشادي ⏳'}
                </span>
              </div>

              {/* Title & Description */}
              <div className="space-y-2 mb-6">
                <h3 className="text-lg font-black text-slate-900 dark:text-white">
                  {pkg.name_ar}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed min-h-[36px]">
                  {pkg.description}
                </p>

                {/* Price Display */}
                <div className="pt-2">
                  <div className="text-xl font-black text-slate-900 dark:text-white">
                    {pkg.indicative_price_text || (pkg.indicative_price_min ? `${pkg.indicative_price_min} - ${pkg.indicative_price_max} ${pkg.currency}` : 'عرض سعر مخصص')}
                  </div>
                  {pkg.support_period && (
                    <div className="flex items-center gap-1.5 text-[11px] text-slate-400 mt-1">
                      <Clock className="w-3.5 h-3.5 text-blue-500" />
                      <span>فترة الدعم: {pkg.support_period}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Features List */}
              <div className="border-t border-slate-100 dark:border-slate-800/80 pt-4 mb-6 flex-1">
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-3">
                  الميزات المشمولة:
                </span>
                <ul className="space-y-2">
                  {(pkg.features || []).map((feat, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-xs text-slate-700 dark:text-slate-300">
                      <Check className="w-3.5 h-3.5 text-cyan-500 shrink-0 mt-0.5" />
                      <span>{feat}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Card Actions */}
              <div className="pt-4 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between gap-2">
                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => openEditModal(pkg)}
                    className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 transition"
                    title="تعديل الباقة"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(pkg.id)}
                    className="p-2 rounded-xl bg-rose-50 hover:bg-rose-100 dark:bg-rose-950/40 dark:hover:bg-rose-900/60 text-rose-600 dark:text-rose-400 transition"
                    title="حذف الباقة"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <span className="text-[11px] text-slate-400">
                  {pkg.is_active ? 'متاحة للعملاء 🟢' : 'معطلة ⚪'}
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Package Form Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl max-w-lg w-full p-6 shadow-2xl my-8">
            <h3 className="font-bold text-base text-slate-900 dark:text-white mb-4">
              {editingPkg ? 'تعديل باقة الخدمة' : 'إضافة باقة خدمة جديدة'}
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-500 mb-1">الاسم بالإنجليزي *</label>
                  <input
                    type="text"
                    required
                    placeholder="Starter"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-500 mb-1">الاسم بالعربي *</label>
                  <input
                    type="text"
                    required
                    placeholder="باقة الانطلاق"
                    value={formData.name_ar}
                    onChange={(e) => setFormData({ ...formData, name_ar: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">المعرف (Slug) *</label>
                <input
                  type="text"
                  required
                  placeholder="starter"
                  value={formData.slug}
                  onChange={(e) => setFormData({ ...formData, slug: e.target.value.toLowerCase() })}
                  className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">الوصف المختصر</label>
                <textarea
                  rows="2"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="مثالية للأفراد والأنشطة الناشئة التي تحتاج حضوراً رقمياً أنيقاً..."
                  className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                ></textarea>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-500 mb-1">الحد الأدنى للسعر (ج.م)</label>
                  <input
                    type="number"
                    value={formData.indicative_price_min}
                    onChange={(e) => setFormData({ ...formData, indicative_price_min: e.target.value })}
                    placeholder="8000"
                    className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-500 mb-1">الحد الأقصى للسعر (ج.م)</label>
                  <input
                    type="number"
                    value={formData.indicative_price_max}
                    onChange={(e) => setFormData({ ...formData, indicative_price_max: e.target.value })}
                    placeholder="12000"
                    className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">فترة الدعم الفني</label>
                <input
                  type="text"
                  value={formData.support_period}
                  onChange={(e) => setFormData({ ...formData, support_period: e.target.value })}
                  placeholder="أسبوعين بعد الإطلاق"
                  className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                />
              </div>

              {/* Features List input */}
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">ميزات ونطاق الباقة</label>
                <div className="space-y-2 max-h-36 overflow-y-auto">
                  {formData.features.map((feat, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <input
                        type="text"
                        value={feat}
                        onChange={(e) => handleFeatureChange(index, e.target.value)}
                        placeholder={`ميزة رقم ${index + 1}`}
                        className="flex-1 px-3 py-1.5 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                      />
                      <button
                        type="button"
                        onClick={() => removeFeatureInput(index)}
                        className="p-1.5 text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-lg"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
                <button
                  type="button"
                  onClick={addFeatureInput}
                  className="mt-2 text-xs font-bold text-blue-600 dark:text-cyan-400 hover:underline flex items-center gap-1"
                >
                  <Plus className="w-3.5 h-3.5" /> إضافة ميزة أخرى
                </button>
              </div>

              {/* Toggles */}
              <div className="flex items-center gap-4 pt-2">
                <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-700 dark:text-slate-300">
                  <input
                    type="checkbox"
                    checked={formData.is_approved}
                    onChange={(e) => setFormData({ ...formData, is_approved: e.target.checked })}
                    className="w-4 h-4 rounded text-blue-600"
                  />
                  <span>السعر معتمد رسمياً</span>
                </label>

                <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-700 dark:text-slate-300">
                  <input
                    type="checkbox"
                    checked={formData.is_popular}
                    onChange={(e) => setFormData({ ...formData, is_popular: e.target.checked })}
                    className="w-4 h-4 rounded text-blue-600"
                  />
                  <span>تمييز كـ "الأكثر طلباً"</span>
                </label>

                <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-700 dark:text-slate-300">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="w-4 h-4 rounded text-blue-600"
                  />
                  <span>متاحة ونشطة</span>
                </label>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
                >
                  إلغاء
                </button>
                <button
                  type="submit"
                  className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md shadow-blue-600/20 transition"
                >
                  حفظ الباقة
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
