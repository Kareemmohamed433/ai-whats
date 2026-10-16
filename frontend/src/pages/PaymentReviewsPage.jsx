import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { CreditCard, CheckCircle2, XCircle, Search, Filter, Eye, AlertCircle, RefreshCw, Image as ImageIcon } from 'lucide-react';

export default function PaymentReviewsPage() {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('pending');
  const [search, setSearch] = useState('');
  const [selectedReview, setSelectedReview] = useState(null);
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  const token = localStorage.getItem('token');

  useEffect(() => {
    fetchReviews();
  }, [statusFilter]);

  const fetchReviews = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`/api/payment-reviews?status=${statusFilter}&search=${search}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.data.success) {
        setReviews(res.data.payment_reviews || []);
      }
    } catch (err) {
      console.error("Fetch payment reviews error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (reviewId) => {
    setActionLoading(true);
    try {
      const res = await axios.put(`/api/payment-reviews/${reviewId}/approve`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.data.success) {
        fetchReviews();
        if (selectedReview?.id === reviewId) setSelectedReview(null);
      }
    } catch (err) {
      alert("حدث خطأ أثناء اعتماد الإثبات");
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!selectedReview) return;
    setActionLoading(true);
    try {
      const res = await axios.put(`/api/payment-reviews/${selectedReview.id}/reject`, {
        reason: rejectReason || 'إثبات الدفع غير مقبول'
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.data.success) {
        setShowRejectModal(false);
        setRejectReason('');
        setSelectedReview(null);
        fetchReviews();
      }
    } catch (err) {
      alert("حدث خطأ أثناء رفض الإثبات");
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs">
        <div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <CreditCard className="w-6 h-6 text-teal-600 dark:text-teal-400" />
            مراجعة إثباتات الدفع (Payment Reviews)
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            مراجعة واعتماد صور التحويلات البنكية وإثباتات InstaPay وفودافون كاش
          </p>
        </div>
        <button
          onClick={fetchReviews}
          className="flex items-center gap-2 px-4 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-xl text-xs font-semibold transition"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          تحديث
        </button>
      </div>

      {/* Filters Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800">
        <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0">
          {[
            { id: 'pending', name: 'بانتظار المراجعة' },
            { id: 'approved', name: 'المعتمدة' },
            { id: 'rejected', name: 'المرقوضة' },
            { id: '', name: 'الكل' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setStatusFilter(tab.id)}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition whitespace-nowrap ${
                statusFilter === tab.id
                  ? 'bg-teal-600 text-white shadow-md shadow-teal-600/20'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'
              }`}
            >
              {tab.name}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 absolute right-3 top-2.5 text-slate-400" />
          <input
            type="text"
            placeholder="بحث بالاسم أو رقم التليفون..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && fetchReviews()}
            className="w-full pr-9 pl-3 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-hidden focus:border-teal-500"
          />
        </div>
      </div>

      {/* Reviews Grid / Table */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : reviews.length === 0 ? (
        <div className="text-center py-16 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800">
          <CheckCircle2 className="w-12 h-12 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
          <p className="text-sm font-bold text-slate-600 dark:text-slate-400">لا توجد إثباتات دفع للعرض</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reviews.map((rev) => (
            <div
              key={rev.id}
              className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-5 space-y-4 hover:border-teal-500/50 transition shadow-xs flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900 dark:text-white">
                    {rev.customer_name}
                  </span>
                  <span className={`text-[10px] font-bold px-2.5 py-1 rounded-full ${
                    rev.status === 'approved'
                      ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400'
                      : rev.status === 'rejected'
                      ? 'bg-rose-100 dark:bg-rose-950 text-rose-600 dark:text-rose-400'
                      : 'bg-amber-100 dark:bg-amber-950 text-amber-600 dark:text-amber-400'
                  }`}>
                    {rev.status === 'approved' ? 'معتمد' : rev.status === 'rejected' ? 'مرفوض' : 'بانتظار المراجعة'}
                  </span>
                </div>

                <div className="text-xs text-slate-500 dark:text-slate-400 space-y-1">
                  <p>📞 الهاتف: <span className="font-semibold text-slate-700 dark:text-slate-300">{rev.customer_phone || 'غير مسجل'}</span></p>
                  <p>📦 رقم الطلب: <span className="font-semibold text-teal-600 dark:text-teal-400">{rev.order_number || 'غير متاح'}</span></p>
                  <p>💰 المبلغ المتوقع/المكتشف: <span className="font-bold text-emerald-600 dark:text-emerald-400">{rev.detected_amount || rev.expected_amount || 0} ج.م</span></p>
                  <p>📅 التاريخ: {new Date(rev.created_at).toLocaleString('ar-EG')}</p>
                </div>

                {rev.screenshot_url ? (
                  <div
                    onClick={() => setSelectedReview(rev)}
                    className="relative group cursor-pointer rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800 h-32 bg-slate-100 dark:bg-slate-800 flex items-center justify-center"
                  >
                    <img src={rev.screenshot_url} alt="إثبات الدفع" className="w-full h-full object-cover group-hover:scale-105 transition duration-300" />
                    <div className="absolute inset-0 bg-slate-900/40 opacity-0 group-hover:opacity-100 transition flex items-center justify-center text-white text-xs font-bold gap-1">
                      <Eye className="w-4 h-4" /> معاينة الصورة
                    </div>
                  </div>
                ) : (
                  <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-dashed border-slate-200 dark:border-slate-700 text-center text-xs text-slate-400 flex items-center justify-center gap-1">
                    <ImageIcon className="w-4 h-4" /> لا توجد صورة مرفقة
                  </div>
                )}
              </div>

              {rev.status === 'pending' && (
                <div className="flex items-center gap-2 pt-2 border-t border-slate-100 dark:border-slate-800">
                  <button
                    disabled={actionLoading}
                    onClick={() => handleApprove(rev.id)}
                    className="flex-1 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-1 shadow-xs"
                  >
                    <CheckCircle2 className="w-4 h-4" /> اعتماد الدفع
                  </button>
                  <button
                    disabled={actionLoading}
                    onClick={() => { setSelectedReview(rev); setShowRejectModal(true); }}
                    className="flex-1 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-1 shadow-xs"
                  >
                    <XCircle className="w-4 h-4" /> رفض
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Reject Modal */}
      {showRejectModal && selectedReview && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-md w-full p-6 border border-slate-200 dark:border-slate-800 space-y-4">
            <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-rose-500" />
              سبب رفض إثبات الدفع
            </h3>
            <textarea
              rows={3}
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="اكتب سبب الرفض للعميل..."
              className="w-full p-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-hidden focus:border-rose-500"
            />
            <div className="flex items-center justify-end gap-2">
              <button
                onClick={() => setShowRejectModal(false)}
                className="px-4 py-2 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-xl text-xs font-semibold hover:bg-slate-200"
              >
                إلغاء
              </button>
              <button
                disabled={actionLoading}
                onClick={handleReject}
                className="px-4 py-2 bg-rose-600 text-white rounded-xl text-xs font-bold hover:bg-rose-700"
              >
                تأكيد الرفض
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
