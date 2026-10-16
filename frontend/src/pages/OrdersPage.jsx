import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Package, Search, Truck, CheckCircle2, Clock, AlertCircle, RefreshCw } from 'lucide-react';

export default function OrdersPage() {
  const [orders, setOrders] = useState([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);

  const loadOrders = () => {
    let url = `/orders?search=${encodeURIComponent(search)}`;
    if (statusFilter) url += `&status=${statusFilter}`;

    api.get(url).then(res => {
      if (res.success) setOrders(res.orders);
    }).catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadOrders();
  }, [search, statusFilter]);

  const handleUpdateStatus = async (orderId, newStatus) => {
    try {
      const res = await api.put(`/orders/${orderId}/status`, { order_status: newStatus });
      if (res.success) loadOrders();
    } catch (err) {
      alert(err.message || 'فشل التحديث');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">إدارة الطلبات والشحنات (Orders)</h2>
          <p className="text-xs text-slate-500">تتبع مبيعات خام سينا، حالات الشحن، وتأكيد الدفع لعملاء المحافظات</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="relative max-w-md w-full">
          <Search className="w-4 h-4 absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="بحث برقم الطلب، اسم العميل، الهاتف، أو المدينة..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pr-10 pl-4 py-2.5 rounded-xl text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white outline-none focus:border-emerald-500"
          />
        </div>

        <div className="flex items-center gap-1.5 overflow-x-auto text-xs font-semibold">
          {[
            { id: '', label: 'جميع الطلبات' },
            { id: 'pending', label: 'قيد الانتظار' },
            { id: 'confirmed', label: 'مؤكد' },
            { id: 'processing', label: 'جاري التحضير' },
            { id: 'shipped', label: 'تم الشحن' },
            { id: 'delivered', label: 'تم التسليم' },
            { id: 'cancelled', label: 'ملغي' },
          ].map(st => (
            <button
              key={st.id}
              onClick={() => setStatusFilter(st.id)}
              className={`px-3 py-1.5 rounded-xl transition-all ${
                statusFilter === st.id
                  ? 'bg-emerald-600 text-white font-bold'
                  : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300'
              }`}
            >
              {st.label}
            </button>
          ))}
        </div>
      </div>

      {/* Orders Table */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-right text-xs">
            <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500 font-bold border-b border-slate-200 dark:border-slate-800">
              <tr>
                <th className="p-4">رقم الطلب</th>
                <th className="p-4">العميل</th>
                <th className="p-4">المنتجات المطلوبة</th>
                <th className="p-4">إجمالي المبلغ</th>
                <th className="p-4">طريقة الدفع والحالة</th>
                <th className="p-4">حالة الشحن</th>
                <th className="p-4">تحديث الحالة</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {loading ? (
                <tr><td colSpan="7" className="p-8 text-center text-slate-400">جاري تحميل الطلبات...</td></tr>
              ) : orders.length === 0 ? (
                <tr><td colSpan="7" className="p-8 text-center text-slate-400">لا توجد طلبات متطابقة</td></tr>
              ) : (
                orders.map(order => (
                  <tr key={order.id} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition-colors">
                    <td className="p-4 font-mono font-bold text-slate-900 dark:text-white">
                      {order.order_number}
                    </td>

                    <td className="p-4">
                      <div className="font-bold text-slate-900 dark:text-white">{order.customer_name}</div>
                      <div className="text-[10px] text-slate-400">{order.customer_phone} ({order.city})</div>
                    </td>

                    <td className="p-4 space-y-1">
                      {order.items?.map(it => (
                        <div key={it.id} className="text-slate-700 dark:text-slate-300 font-medium">
                          • {it.product_name} × {it.quantity}
                        </div>
                      ))}
                    </td>

                    <td className="p-4 font-extrabold text-emerald-600 text-sm">
                      {order.total_amount} ج.م
                    </td>

                    <td className="p-4 space-y-1">
                      <span className="inline-block px-2.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-[10px] font-semibold">
                        {order.payment_method === 'cash_on_delivery' ? 'الدفع عند الاستلام' : order.payment_method}
                      </span>
                      <div className="text-[10px] text-emerald-600 font-bold">{order.payment_status.toUpperCase()}</div>
                    </td>

                    <td className="p-4">
                      <span className={`inline-block px-2.5 py-1 rounded-full text-[10px] font-bold ${
                        order.order_status === 'shipped' ? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300' :
                        order.order_status === 'delivered' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300' :
                        'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300'
                      }`}>
                        {order.order_status.toUpperCase()}
                      </span>
                    </td>

                    <td className="p-4">
                      <select
                        value={order.order_status}
                        onChange={(e) => handleUpdateStatus(order.id, e.target.value)}
                        className="text-xs px-2.5 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 outline-none font-medium"
                      >
                        <option value="pending">قيد الانتظار</option>
                        <option value="confirmed">مؤكد</option>
                        <option value="processing">جاري التحضير</option>
                        <option value="shipped">تم الشحن</option>
                        <option value="delivered">تم التسليم</option>
                        <option value="cancelled">إلغاء</option>
                      </select>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
