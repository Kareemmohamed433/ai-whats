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
  FolderPlus,
  Tag,
  FileText,
  AlertCircle,
  X
} from 'lucide-react';

export default function ProductsPage() {
  const [packages, setPackages] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [loading, setLoading] = useState(true);

  // Service Modal state
  const [showModal, setShowModal] = useState(false);
  const [editingPkg, setEditingPkg] = useState(null);

  // Category Management Modal state
  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [newCategoryData, setNewCategoryData] = useState({
    name: '',
    name_ar: '',
    slug: '',
    description: '',
    icon: ''
  });

  const [formData, setFormData] = useState({
    name: '',
    name_ar: '',
    slug: '',
    category_id: '',
    description: '',
    pricing_type: 'range', // quotation_only, fixed, starting_at, range
    fixed_price: '',
    starting_price: '',
    indicative_price_min: '',
    indicative_price_max: '',
    indicative_price_text: '',
    quotation_required: false,
    pricing_notes: '',
    delivery_estimate: '',
    requirements_text: '',
    currency: 'EGP',
    support_period: '',
    is_approved: true,
    is_popular: false,
    is_active: true,
    features: ['']
  });

  const loadCategories = () => {
    api.get('/packages/categories')
      .then(res => {
        if (res.success) {
          setCategories(res.categories || []);
        }
      })
      .catch(err => console.error("Failed to load categories:", err));
  };

  const loadPackages = () => {
    setLoading(true);
    let url = '/packages?active_only=false';
    if (selectedCategory && selectedCategory !== 'all') {
      url += `&category=${selectedCategory}`;
    }
    api.get(url)
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
    loadCategories();
  }, []);

  useEffect(() => {
    loadPackages();
  }, [selectedCategory]);

  const resetForm = () => {
    setEditingPkg(null);
    setFormData({
      name: '',
      name_ar: '',
      slug: '',
      category_id: categories.length > 0 ? categories[0].id : '',
      description: '',
      pricing_type: 'range',
      fixed_price: '',
      starting_price: '',
      indicative_price_min: '',
      indicative_price_max: '',
      indicative_price_text: '',
      quotation_required: false,
      pricing_notes: '',
      delivery_estimate: '',
      requirements_text: '',
      currency: 'EGP',
      support_period: '',
      is_approved: true,
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
      category_id: pkg.category_id || '',
      description: pkg.description || '',
      pricing_type: pkg.pricing_type || (pkg.fixed_price ? 'fixed' : pkg.starting_price ? 'starting_at' : (pkg.indicative_price_min || pkg.indicative_price_max) ? 'range' : 'quotation_only'),
      fixed_price: pkg.fixed_price ?? '',
      starting_price: pkg.starting_price ?? '',
      indicative_price_min: pkg.indicative_price_min ?? '',
      indicative_price_max: pkg.indicative_price_max ?? '',
      indicative_price_text: pkg.indicative_price_text || '',
      quotation_required: Boolean(pkg.quotation_required),
      pricing_notes: pkg.pricing_notes || '',
      delivery_estimate: pkg.delivery_estimate || '',
      requirements_text: pkg.requirements_text || '',
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

    // Prepare payload based on pricing type
    const payload = {
      ...formData,
      category_id: formData.category_id ? parseInt(formData.category_id) : null,
      fixed_price: formData.pricing_type === 'fixed' && formData.fixed_price !== '' ? parseFloat(formData.fixed_price) : null,
      starting_price: formData.pricing_type === 'starting_at' && formData.starting_price !== '' ? parseFloat(formData.starting_price) : null,
      indicative_price_min: formData.pricing_type === 'range' && formData.indicative_price_min !== '' ? parseFloat(formData.indicative_price_min) : null,
      indicative_price_max: formData.pricing_type === 'range' && formData.indicative_price_max !== '' ? parseFloat(formData.indicative_price_max) : null,
      quotation_required: formData.pricing_type === 'quotation_only' ? true : Boolean(formData.quotation_required),
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

  const handleCreateCategory = async (e) => {
    e.preventDefault();
    if (!newCategoryData.name_ar || !newCategoryData.slug) {
      alert('الاسم بالعربي والمعرف مطلوبان');
      return;
    }
    try {
      await api.post('/packages/categories', newCategoryData);
      setNewCategoryData({ name: '', name_ar: '', slug: '', description: '', icon: '' });
      loadCategories();
      alert('تم إضافة التصنيف بنجاح');
    } catch (err) {
      alert(err.message || 'فشل إضافة التصنيف');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-500" />
            دليل خدمات Black & White (Service Catalog)
          </h2>
          <p className="text-xs text-slate-500">
            إدارة خدمات التصميم الجرافيكي، الدعاية والتسويق، والديكور الداخلي مع سياسات التسعير المرنة
          </p>
        </div>

        <div className="flex items-center gap-2.5 self-start sm:self-auto">
          <button
            onClick={() => setShowCategoryModal(true)}
            className="px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-bold text-xs flex items-center gap-1.5 transition"
          >
            <FolderPlus className="w-4 h-4" /> إدارة التصنيفات
          </button>

          <button
            onClick={openCreateModal}
            className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md shadow-blue-600/20 flex items-center gap-2 transition-all"
          >
            <Plus className="w-4 h-4" /> إضافة خدمة جديدة
          </button>
        </div>
      </div>

      {/* Categories Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar">
        <button
          onClick={() => setSelectedCategory('all')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition shrink-0 ${
            selectedCategory === 'all'
              ? 'bg-blue-600 text-white shadow-sm'
              : 'bg-white dark:bg-slate-800/80 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-100'
          }`}
        >
          جميع الخدمات ({packages.length})
        </button>
        {categories.map(cat => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.slug)}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-1.5 shrink-0 ${
              selectedCategory === cat.slug
                ? 'bg-blue-600 text-white shadow-sm'
                : 'bg-white dark:bg-slate-800/80 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-100'
            }`}
          >
            <span>{cat.icon || '📁'}</span>
            <span>{cat.name_ar}</span>
          </button>
        ))}
      </div>

      {/* Official Guidelines Callout */}
      <div className="p-4 rounded-2xl bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800/60 flex items-start gap-3">
        <ShieldAlert className="w-5 h-5 text-blue-600 dark:text-cyan-400 shrink-0 mt-0.5" />
        <div className="text-xs text-blue-900 dark:text-blue-200 space-y-1">
          <p className="font-bold">سياسة التسعير المعتمدة لشركة Black & White:</p>
          <p className="leading-relaxed opacity-90">
            الذكاء الاصطناعي يستقي الأسعار مباشرة من هذا الدليل. في حال عدم وجود سعر محدد أو كانت الخدمة تتطلب كوتيشن مخصص، يشرح المساعد للعميل أن السعر يعتمد على المتطلبات ويقوم بجمعها لإحالتها للموظف المسؤول.
          </p>
        </div>
      </div>

      {/* Packages Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full py-12 text-center text-xs text-slate-400">
            جاري تحميل الخدمات...
          </div>
        ) : packages.length === 0 ? (
          <div className="col-span-full py-12 text-center text-xs text-slate-400">
            لا توجد خدمات مطابقة لهذا التصنيف حالياً. انقر على "إضافة خدمة جديدة".
          </div>
        ) : (
          packages.map((pkg) => {
            // Price Display Logic
            let priceLabel = 'عرض سعر مخصص';
            if (pkg.pricing_type === 'fixed' && pkg.fixed_price != null) {
              priceLabel = `${pkg.fixed_price} ${pkg.currency || 'EGP'} (سعر ثابت)`;
            } else if (pkg.pricing_type === 'starting_at' && pkg.starting_price != null) {
              priceLabel = `يبدأ من ${pkg.starting_price} ${pkg.currency || 'EGP'}`;
            } else if (pkg.pricing_type === 'range' && (pkg.indicative_price_min != null || pkg.indicative_price_max != null)) {
              priceLabel = `${pkg.indicative_price_min || 0} - ${pkg.indicative_price_max || 0} ${pkg.currency || 'EGP'}`;
            } else if (pkg.indicative_price_text) {
              priceLabel = pkg.indicative_price_text;
            }

            return (
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
                    {pkg.category_rel && (
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                        {pkg.category_rel.icon || '🏷️'} {pkg.category_rel.name_ar}
                      </span>
                    )}
                    {pkg.is_popular && (
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-500 text-white">
                        الأكثر طلباً ⭐
                      </span>
                    )}
                  </div>

                  <span
                    className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      pkg.quotation_required || pkg.pricing_type === 'quotation_only'
                        ? 'bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-300'
                        : pkg.is_approved
                        ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300'
                        : 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300'
                    }`}
                  >
                    {pkg.quotation_required || pkg.pricing_type === 'quotation_only'
                      ? 'طلب عرض سعر 📋'
                      : pkg.is_approved
                      ? 'سعر معتمد ✅'
                      : 'تقدير استرشادي ⏳'}
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
                      {priceLabel}
                    </div>

                    {pkg.delivery_estimate && (
                      <div className="flex items-center gap-1.5 text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                        <Clock className="w-3.5 h-3.5 text-blue-500" />
                        <span>مدة التنفيذ المتوقعة: {pkg.delivery_estimate}</span>
                      </div>
                    )}
                  </div>

                  {/* Pricing notes preview */}
                  {pkg.pricing_notes && (
                    <div className="text-[11px] text-slate-400 bg-slate-50 dark:bg-slate-800/40 p-2 rounded-xl border border-slate-100 dark:border-slate-800">
                      <span className="font-semibold text-slate-500 dark:text-slate-300">ملاحظات التسعير: </span>
                      {pkg.pricing_notes}
                    </div>
                  )}
                </div>

                {/* Features List */}
                <div className="border-t border-slate-100 dark:border-slate-800/80 pt-4 mb-6 flex-1">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-3">
                    الميزات ونطاق العمل:
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
                      title="تعديل الخدمة"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(pkg.id)}
                      className="p-2 rounded-xl bg-rose-50 hover:bg-rose-100 dark:bg-rose-950/40 dark:hover:bg-rose-900/60 text-rose-600 dark:text-rose-400 transition"
                      title="حذف الخدمة"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <span className="text-[11px] text-slate-400">
                    {pkg.is_active ? 'متاحة للعملاء 🟢' : 'معطلة ⚪'}
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Category Management Modal */}
      {showCategoryModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl max-w-lg w-full p-6 shadow-2xl my-8">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800 mb-4">
              <h3 className="font-bold text-base text-slate-900 dark:text-white flex items-center gap-2">
                <FolderPlus className="w-5 h-5 text-blue-500" />
                إدارة تصنيفات الخدمات (Service Categories)
              </h3>
              <button onClick={() => setShowCategoryModal(false)} className="p-1 rounded-lg text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Existing Categories List */}
            <div className="space-y-2 mb-6 max-h-48 overflow-y-auto">
              {categories.map(cat => (
                <div key={cat.id} className="flex items-center justify-between p-2.5 bg-slate-50 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="text-base">{cat.icon || '📁'}</span>
                    <div>
                      <span className="font-bold text-slate-900 dark:text-white block">{cat.name_ar}</span>
                      <span className="text-[10px] text-slate-400 font-mono">{cat.slug}</span>
                    </div>
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 font-bold">
                    نشط
                  </span>
                </div>
              ))}
            </div>

            {/* Add Category Form */}
            <form onSubmit={handleCreateCategory} className="space-y-3 pt-3 border-t border-slate-200 dark:border-slate-800">
              <h4 className="text-xs font-bold text-slate-700 dark:text-slate-300">إضافة تصنيف جديد:</h4>
              <div className="grid grid-cols-2 gap-2">
                <input
                  type="text"
                  required
                  placeholder="الاسم بالعربي (مثال: ديكور داخلي)"
                  value={newCategoryData.name_ar}
                  onChange={(e) => setNewCategoryData({ ...newCategoryData, name_ar: e.target.value })}
                  className="px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                />
                <input
                  type="text"
                  required
                  placeholder="المعرف (slug: interior-decoration)"
                  value={newCategoryData.slug}
                  onChange={(e) => setNewCategoryData({ ...newCategoryData, slug: e.target.value.toLowerCase().replace(/\s+/g, '-') })}
                  className="px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500 font-mono"
                />
              </div>

              <div className="grid grid-cols-3 gap-2">
                <input
                  type="text"
                  placeholder="الأيقونة (🎨, 📢, 🏠)"
                  value={newCategoryData.icon}
                  onChange={(e) => setNewCategoryData({ ...newCategoryData, icon: e.target.value })}
                  className="px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500 text-center"
                />
                <input
                  type="text"
                  placeholder="الاسم بالإنجليزي (اختياري)"
                  value={newCategoryData.name}
                  onChange={(e) => setNewCategoryData({ ...newCategoryData, name: e.target.value })}
                  className="col-span-2 px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                />
              </div>

              <button
                type="submit"
                className="w-full py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded-xl shadow-md transition"
              >
                + إضافة التصنيف
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Package Form Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl max-w-lg w-full p-6 shadow-2xl my-8">
            <h3 className="font-bold text-base text-slate-900 dark:text-white mb-4">
              {editingPkg ? 'تعديل تفاصيل الخدمة' : 'إضافة خدمة جديدة'}
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Category Selection */}
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">التصنيف الرئيسي *</label>
                <select
                  value={formData.category_id}
                  onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                >
                  <option value="">بدون تصنيف (عام)</option>
                  {categories.map(cat => (
                    <option key={cat.id} value={cat.id}>
                      {cat.icon || '📁'} {cat.name_ar}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-500 mb-1">الاسم بالإنجليزي *</label>
                  <input
                    type="text"
                    required
                    placeholder="Logo Design"
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
                    placeholder="تصميم لوجو وهوية بصرية"
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
                  placeholder="logo-design"
                  value={formData.slug}
                  onChange={(e) => setFormData({ ...formData, slug: e.target.value.toLowerCase().replace(/\s+/g, '-') })}
                  className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">الوصف الموجه للعميل</label>
                <textarea
                  rows="2"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="تصميم شعار احترافي ومبتكر يعبر عن هوية نشاطك التجاري بدقة..."
                  className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                ></textarea>
              </div>

              {/* Pricing Type Selector */}
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">نموذج التسعير *</label>
                <select
                  value={formData.pricing_type}
                  onChange={(e) => setFormData({ ...formData, pricing_type: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                >
                  <option value="quotation_only">طلب عرض سعر مخصص فقط (حسب متطلبات العميل)</option>
                  <option value="fixed">سعر ثابت محدد</option>
                  <option value="starting_at">سعر يبدأ من قيمة محددة</option>
                  <option value="range">نطاق سعري (من - إلى)</option>
                </select>
              </div>

              {/* Dynamic Price Inputs based on pricing_type */}
              {formData.pricing_type === 'fixed' && (
                <div>
                  <label className="block text-xs font-semibold text-slate-500 mb-1">السعر الثابت ({formData.currency})</label>
                  <input
                    type="number"
                    value={formData.fixed_price}
                    onChange={(e) => setFormData({ ...formData, fixed_price: e.target.value })}
                    placeholder="1500"
                    className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                  />
                </div>
              )}

              {formData.pricing_type === 'starting_at' && (
                <div>
                  <label className="block text-xs font-semibold text-slate-500 mb-1">السعر يبدأ من ({formData.currency})</label>
                  <input
                    type="number"
                    value={formData.starting_price}
                    onChange={(e) => setFormData({ ...formData, starting_price: e.target.value })}
                    placeholder="2500"
                    className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                  />
                </div>
              )}

              {formData.pricing_type === 'range' && (
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 mb-1">الحد الأدنى ({formData.currency})</label>
                    <input
                      type="number"
                      value={formData.indicative_price_min}
                      onChange={(e) => setFormData({ ...formData, indicative_price_min: e.target.value })}
                      placeholder="3000"
                      className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 mb-1">الحد الأقصى ({formData.currency})</label>
                    <input
                      type="number"
                      value={formData.indicative_price_max}
                      onChange={(e) => setFormData({ ...formData, indicative_price_max: e.target.value })}
                      placeholder="8000"
                      className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                    />
                  </div>
                </div>
              )}

              {/* Delivery Estimate */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-500 mb-1">مدة التنفيذ المتوقعة</label>
                  <input
                    type="text"
                    value={formData.delivery_estimate}
                    onChange={(e) => setFormData({ ...formData, delivery_estimate: e.target.value })}
                    placeholder="3-5 أيام عمل"
                    className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-500 mb-1">فترة التعديل / الدعم</label>
                  <input
                    type="text"
                    value={formData.support_period}
                    onChange={(e) => setFormData({ ...formData, support_period: e.target.value })}
                    placeholder="أسبوع للمراجعات"
                    className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Pricing Notes & Requirements */}
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">ملاحظات وشروط التسعير</label>
                <input
                  type="text"
                  value={formData.pricing_notes}
                  onChange={(e) => setFormData({ ...formData, pricing_notes: e.target.value })}
                  placeholder="يشمل نسختين مبدئيتين وتعديلين مجانيين..."
                  className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">متطلبات البدء من العميل</label>
                <input
                  type="text"
                  value={formData.requirements_text}
                  onChange={(e) => setFormData({ ...formData, requirements_text: e.target.value })}
                  placeholder="شعار النشاط، كود الألوان، نبذة عن المشروع..."
                  className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:border-blue-500"
                />
              </div>

              {/* Features List input */}
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">ميزات ونطاق الخدمة</label>
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
              <div className="flex flex-wrap items-center gap-4 pt-2">
                <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-700 dark:text-slate-300">
                  <input
                    type="checkbox"
                    checked={formData.quotation_required}
                    onChange={(e) => setFormData({ ...formData, quotation_required: e.target.checked })}
                    className="w-4 h-4 rounded text-purple-600"
                  />
                  <span>يتطلب كوتيشن إجباري 📋</span>
                </label>

                <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-700 dark:text-slate-300">
                  <input
                    type="checkbox"
                    checked={formData.is_popular}
                    onChange={(e) => setFormData({ ...formData, is_popular: e.target.checked })}
                    className="w-4 h-4 rounded text-blue-600"
                  />
                  <span>الأكثر طلباً ⭐</span>
                </label>

                <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-700 dark:text-slate-300">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="w-4 h-4 rounded text-blue-600"
                  />
                  <span>متاحة ونشطة 🟢</span>
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
                  حفظ الخدمة
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
