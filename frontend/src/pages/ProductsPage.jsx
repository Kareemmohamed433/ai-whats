import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { ShoppingBag, Plus, Trash2, Edit2, CheckCircle2, Tag, Layers, Search } from 'lucide-react';

export default function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    sku: '',
    category: 'زيت زيتون سيناوي',
    price: '',
    original_price: '',
    stock: '',
    packaging_type: 'عبوة زجاجية 1 لتر',
    description: '',
    image_url: ''
  });

  const loadProducts = () => {
    api.get(`/products?search=${encodeURIComponent(search)}`).then(res => {
      if (res.success) setProducts(res.products);
    }).catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadProducts();
  }, [search]);

  const handleCreateProduct = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post('/products', formData);
      if (res.success) {
        setShowModal(false);
        setFormData({
          name: '',
          sku: '',
          category: 'زيت زيتون سيناوي',
          price: '',
          original_price: '',
          stock: '',
          packaging_type: 'عبوة زجاجية 1 لتر',
          description: '',
          image_url: ''
        });
        loadProducts();
      }
    } catch (err) {
      alert(err.message || 'فشل إضافة المنتج');
    }
  };

  const handleDeleteProduct = async (id) => {
    if (!window.confirm('هل تود حذف هذا المنتج من الكتالوج؟')) return;
    try {
      const res = await api.delete(`/products/${id}`);
      if (res.success) loadProducts();
    } catch (err) {
      alert(err.message || 'فشل الحذف');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">كتالوج المنتجات والأسعار السيناوية (Products)</h2>
          <p className="text-xs text-slate-500">إدارة أسعار الزيت، العسل، والأعشاب التي يقرأها الذكاء الاصطناعي لحساب الطلبات</p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md flex items-center gap-1.5 transition-all self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" /> إضافة منتج جديد
        </button>
      </div>

      {/* Search Bar */}
      <div className="relative max-w-md">
        <Search className="w-4 h-4 absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          placeholder="بحث بالاسم، كود SKU، أو الفئة..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pr-10 pl-4 py-2.5 rounded-xl text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white outline-none focus:border-emerald-500"
        />
      </div>

      {/* Products Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {loading ? (
          <div className="col-span-full py-12 text-center text-xs text-slate-400">جاري تحميل كتالوج المنتجات...</div>
        ) : products.length === 0 ? (
          <div className="col-span-full py-12 text-center text-xs text-slate-400">لا توجد منتجات مضافة حتى الآن</div>
        ) : (
          products.map(product => (
            <div key={product.id} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl overflow-hidden shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
              <div>
                <div className="relative h-44 bg-slate-100 dark:bg-slate-800 overflow-hidden">
                  <img
                    src={product.image_url || "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500&auto=format&fit=crop&q=80"}
                    alt={product.name}
                    className="w-full h-full object-cover"
                  />
                  <span className="absolute top-3 right-3 px-2.5 py-1 rounded-full bg-slate-900/80 backdrop-blur-md text-white font-bold text-[10px]">
                    {product.category}
                  </span>
                  <span className="absolute bottom-3 right-3 px-2.5 py-1 rounded-full bg-emerald-500/90 backdrop-blur-md text-white font-bold text-[10px]">
                    {product.packaging_type}
                  </span>
                </div>

                <div className="p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono text-slate-400">{product.sku}</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      product.stock > 0 ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300' : 'bg-rose-100 text-rose-700'
                    }`}>
                      المخزون: {product.stock} قطعة
                    </span>
                  </div>

                  <h3 className="font-bold text-sm text-slate-900 dark:text-white leading-snug">{product.name}</h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2">{product.description}</p>
                </div>
              </div>

              <div className="p-4 pt-0 flex items-center justify-between border-t border-slate-100 dark:border-slate-800/60 mt-2">
                <div>
                  <span className="text-base font-extrabold text-emerald-600 dark:text-emerald-400">{product.price} ج.م</span>
                  {product.original_price > product.price && (
                    <span className="text-xs text-slate-400 line-through mr-2">{product.original_price} ج.م</span>
                  )}
                </div>

                <button
                  onClick={() => handleDeleteProduct(product.id)}
                  className="p-2 text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-xl transition-colors"
                  title="حذف المنتج"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Add Product Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 w-full max-w-lg shadow-2xl space-y-4">
            <h3 className="font-bold text-base text-slate-900 dark:text-white">إضافة منتج جديد للكتالوج</h3>
            <form onSubmit={handleCreateProduct} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold mb-1">اسم المنتج</label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={e => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
                    placeholder="مثال: زيت زيتون بكر 1 لتر"
                  />
                </div>
                <div>
                  <label className="block font-semibold mb-1">كود SKU</label>
                  <input
                    type="text"
                    required
                    value={formData.sku}
                    onChange={e => setFormData({ ...formData, sku: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none font-mono"
                    placeholder="KS-OIL-1L"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block font-semibold mb-1">السعر (ج.م)</label>
                  <input
                    type="number"
                    step="0.1"
                    required
                    value={formData.price}
                    onChange={e => setFormData({ ...formData, price: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
                  />
                </div>
                <div>
                  <label className="block font-semibold mb-1">السعر الأصلي</label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.original_price}
                    onChange={e => setFormData({ ...formData, original_price: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
                  />
                </div>
                <div>
                  <label className="block font-semibold mb-1">المخزون المتوفر</label>
                  <input
                    type="number"
                    required
                    value={formData.stock}
                    onChange={e => setFormData({ ...formData, stock: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold mb-1">رابط صورة المنتج</label>
                <input
                  type="url"
                  value={formData.image_url}
                  onChange={e => setFormData({ ...formData, image_url: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
                  placeholder="https://..."
                />
              </div>

              <div>
                <label className="block font-semibold mb-1">وصف المنتج المفصل</label>
                <textarea
                  rows="3"
                  value={formData.description}
                  onChange={e => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white outline-none"
                ></textarea>
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
                  حفظ المنتج
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
