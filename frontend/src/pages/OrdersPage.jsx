import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { 
  Package, 
  Search, 
  Clock, 
  CheckCircle2, 
  AlertCircle, 
  UserCheck, 
  MessageSquare, 
  Phone, 
  Briefcase,
  Layers,
  ArrowUpRight
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const LEAD_STATUSES = [
  { id: '', label: 'جميع الطلبات' },
  { id: 'New', label: 'طلب جديد (New)' },
  { id: 'Qualified', label: 'مؤهل (Qualified)' },
  { id: 'Awaiting Human Review', label: 'بانتظار المراجعة' },
  { id: 'Contacted', label: 'تم التواصل (Contacted)' },
  { id: 'Closed', label: 'مغلق ومكتمل (Closed)' }
];

export default function OrdersPage() {
  const navigate = useNavigate();
  const [leads, setLeads] = useState([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);

  const loadLeads = () => {
    let url = `/leads?search=${encodeURIComponent(search)}`;
    if (statusFilter) url += `&status=${encodeURIComponent(statusFilter)}`;

    api.get(url)
      .then(res => {
        if (res.success) setLeads(res.leads || []);
      })
      .catch(err => {
        console.error("Failed to load leads:", err);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadLeads();
  }, [search, statusFilter]);

  const handleUpdateStatus = async (leadId, newStatus) => {
    try {
      const res = await api.put(`/leads/${leadId}/status`, { status: newStatus });
      if (res.success) {
        loadLeads();
      }
    } catch (err) {
      alert(err.message || 'فشل تحديث حالة الطلب');
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'New':
        return 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300 border-blue-200 dark:border-blue-800';
      case 'Qualified':
        return 'bg-cyan-100 text-cyan-700 dark:bg-cyan-950 dark:text-cyan-300 border-cyan-200 dark:border-cyan-800';
      case 'Awaiting Human Review':
        return 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300 border-amber-200 dark:border-amber-800';
      case 'Contacted':
        return 'bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-300 border-purple-200 dark:border-purple-800';
      case 'Closed':
        return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800';
      default:
        return 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Package className="w-5 h-5 text-blue-500" />
            طلبات المشروعات والعملاء المحتملين (Project Leads)
          </h2>
          <p className="text-xs text-slate-500">
            متابعة طلبات تطوير المواقع، استفسارات حلول الذكاء الاصطناعي، ونظام إدارة الـ Leads لشركة NEXORA
          </p>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="relative max-w-md w-full">
          <Search className="w-4 h-4 absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="بحث باسم العميل، الهاتف، النشاط، أو متطلبات المشروع..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pr-10 pl-4 py-2.5 rounded-xl text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white outline-none focus:border-blue-500"
          />
        </div>

        <div className="flex items-center gap-1.5 overflow-x-auto text-xs font-semibold">
          {LEAD_STATUSES.map((st) => (
            <button
              key={st.id}
              onClick={() => setStatusFilter(st.id)}
              className={`px-3 py-2 rounded-xl transition whitespace-nowrap ${
                statusFilter === st.id
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              {st.label}
            </button>
          ))}
        </div>
      </div>

      {/* Leads Table / Cards */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl overflow-hidden shadow-xs">
        {loading ? (
          <div className="py-16 text-center text-xs text-slate-400">جاري تحميل طلبات المشاريع...</div>
        ) : leads.length === 0 ? (
          <div className="py-16 text-center text-xs text-slate-400">
            لم يتم العثور على طلبات مشاريع تطابق البحث.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-right text-xs">
              <thead className="bg-slate-50 dark:bg-slate-800/50 text-slate-500 font-bold border-b border-slate-200 dark:border-slate-800">
                <tr>
                  <th className="p-4">العميل ومعلومات الاتصال</th>
                  <th className="p-4">الخدمة المطلوبة / الباقة</th>
                  <th className="p-4">تفاصيل وفكرة المشروع</th>
                  <th className="p-4">الميزانية / الجدول</th>
                  <th className="p-4">الحالة</th>
                  <th className="p-4">إجراءات</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                {leads.map((lead) => (
                  <tr key={lead.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-850/50 transition">
                    <td className="p-4">
                      <div className="font-bold text-slate-900 dark:text-white text-sm">
                        {lead.customer_name}
                      </div>
                      <div className="text-[11px] text-slate-400 flex items-center gap-1.5 mt-0.5">
                        <Phone className="w-3 h-3 text-blue-500" />
                        <span>{lead.contact_info}</span>
                      </div>
                      {lead.business_name && (
                        <div className="text-[11px] text-blue-600 dark:text-cyan-400 font-medium mt-0.5">
                          {lead.business_name} {lead.industry ? `(${lead.industry})` : ''}
                        </div>
                      )}
                    </td>

                    <td className="p-4">
                      <div className="font-semibold text-slate-800 dark:text-slate-200">
                        {lead.requested_service}
                      </div>
                      {lead.package_interest && (
                        <span className="inline-block mt-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-cyan-400 border border-blue-200 dark:border-blue-800/50">
                          باقة {lead.package_interest}
                        </span>
                      )}
                    </td>

                    <td className="p-4 max-w-xs">
                      <p className="text-slate-600 dark:text-slate-300 line-clamp-2 leading-relaxed">
                        {lead.project_description || 'استفسار أولي مسجل من المحادثة.'}
                      </p>
                    </td>

                    <td className="p-4">
                      <div className="font-bold text-slate-900 dark:text-white">
                        {lead.budget || 'غير محدد'}
                      </div>
                      {lead.expected_timeline && (
                        <div className="text-[11px] text-slate-400 mt-0.5">
                          الجدول: {lead.expected_timeline}
                        </div>
                      )}
                    </td>

                    <td className="p-4">
                      <select
                        value={lead.status}
                        onChange={(e) => handleUpdateStatus(lead.id, e.target.value)}
                        className={`px-3 py-1.5 rounded-xl text-xs font-bold border outline-none cursor-pointer transition ${getStatusBadge(lead.status)}`}
                      >
                        <option value="New">طلب جديد</option>
                        <option value="Qualified">مؤهل</option>
                        <option value="Awaiting Human Review">بانتظار المراجعة</option>
                        <option value="Contacted">تم التواصل</option>
                        <option value="Closed">مغلق / مكتمل</option>
                      </select>
                    </td>

                    <td className="p-4">
                      <button
                        onClick={() => navigate('/inbox')}
                        className="px-3 py-1.5 rounded-xl bg-blue-50 hover:bg-blue-100 dark:bg-blue-950/40 dark:hover:bg-blue-900/60 text-blue-600 dark:text-cyan-400 font-bold text-xs flex items-center gap-1 transition"
                      >
                        <MessageSquare className="w-3.5 h-3.5" />
                        <span>فتح المحادثة</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
