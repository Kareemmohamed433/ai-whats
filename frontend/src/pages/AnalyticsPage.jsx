import React, { useState, useEffect } from 'react';
import api from '../services/api';
import socket from '../services/socket';
import { BarChart3, Bot, Clock, MessageSquare, TrendingUp, Users, CheckCircle2, RefreshCw, AlertCircle } from 'lucide-react';

export default function AnalyticsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);

  const fetchAnalytics = async (isSilent = false) => {
    if (!isSilent) setLoading(true);
    setErrorMsg(null);

    try {
      const res = await api.get('/analytics');
      if (res.success) {
        setData(res.metrics);
      } else {
        setErrorMsg('تعذر تحميل بيانات التحليلات.');
      }
    } catch (err) {
      console.error(err);
      setErrorMsg('حدث خطأ أثناء الاتصال بالسيرفر لجلب التحليلات.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();

    const interval = setInterval(() => {
      fetchAnalytics(true);
    }, 15000);

    const handleUpdate = () => fetchAnalytics(true);
    if (socket) {
      socket.on('new_message', handleUpdate);
      socket.on('conversation_updated', handleUpdate);
    }

    return () => {
      clearInterval(interval);
      if (socket) {
        socket.off('new_message', handleUpdate);
        socket.off('conversation_updated', handleUpdate);
      }
    };
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">التحليلات والتقارير الإحصائية (Analytics)</h2>
          <p className="text-xs text-slate-500">تقارير أداء الذكاء الاصطناعي، معدل استجابة المهندسين، وتوزيع قنوات خدمة عملاء NEXORA</p>
        </div>
        <button
          onClick={() => fetchAnalytics(false)}
          className="px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 font-bold text-xs flex items-center gap-2 self-start sm:self-auto transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> تحديث البيانات
        </button>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Primary KPI Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm">
          <span className="text-xs font-semibold text-slate-400">إجمالي المحادثات</span>
          <h3 className="text-2xl font-bold text-slate-900 dark:text-white mt-1">
            {loading && !data ? '...' : (data?.conversations?.total ?? 0)}
          </h3>
          <p className="text-[11px] text-emerald-500 font-bold mt-2">محادثات موحدة عبر المنصات</p>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm">
          <span className="text-xs font-semibold text-slate-400">نسبة حسم الذكاء الاصطناعي</span>
          <h3 className="text-2xl font-bold text-teal-600 dark:text-teal-400 mt-1">
            {loading && !data ? '...' : `${data?.ai?.ai_resolution_rate ?? 0}%`}
          </h3>
          <p className="text-[11px] text-slate-400 mt-2">إجابة دقيقة دون تدخل بشري</p>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm">
          <span className="text-xs font-semibold text-slate-400">معدل التحويل للتدخل البشري</span>
          <h3 className="text-2xl font-bold text-amber-600 dark:text-amber-400 mt-1">
            {loading && !data ? '...' : `${data?.ai?.human_escalation_rate ?? 0}%`}
          </h3>
          <p className="text-[11px] text-slate-400 mt-2">تصعيد أوتوماتيكي للموظفين</p>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm">
          <span className="text-xs font-semibold text-slate-400">متوسط الرسائل لكل محادثة</span>
          <h3 className="text-2xl font-bold text-indigo-600 dark:text-indigo-400 mt-1">
            {loading && !data ? '...' : (data?.customer_service?.messages_per_conversation ?? 0)}
          </h3>
          <p className="text-[11px] text-slate-400 mt-2">سرعة إنجاز الاستفسار</p>
        </div>
      </div>

      {/* Platform Distribution & Visual Bars */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm">
          <h3 className="font-bold text-sm text-slate-900 dark:text-white mb-6">توزيع المحادثات حسب المنصة (Platform Breakdown)</h3>
          <div className="space-y-4">
            {data?.platforms?.map(p => {
              const total = data.conversations.total || 0;
              const percentage = total > 0 ? Math.round((p.count / total) * 100) : 0;
              return (
                <div key={p.platform} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-bold">
                    <span className="text-slate-800 dark:text-slate-200">{p.name}</span>
                    <span className="text-slate-500">{p.count} محادثة ({percentage}%)</span>
                  </div>
                  <div className="w-full h-3 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{ width: `${total > 0 ? Math.max(5, percentage) : 0}%`, backgroundColor: p.color }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* AI Performance Breakdown */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-4">
          <h3 className="font-bold text-sm text-slate-900 dark:text-white mb-2">مؤشرات الاستجابة وجودة الخدمة</h3>
          <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 flex items-center justify-between">
            <div className="space-y-1">
              <span className="text-xs font-bold text-slate-700 dark:text-slate-300">سرعة رد المساعد الذكي (AI Latency):</span>
              <p className="text-xs text-slate-400">استجابة فورية عبر السيرفر</p>
            </div>
            <span className="font-extrabold text-base text-emerald-600">{data?.ai?.avg_ai_response_time || '0 ثانية'}</span>
          </div>

          <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 flex items-center justify-between">
            <div className="space-y-1">
              <span className="text-xs font-bold text-slate-700 dark:text-slate-300">متوسط زمن الاستجابة البشرية:</span>
              <p className="text-xs text-slate-400">عند استلام المحادثة المعلقة</p>
            </div>
            <span className="font-extrabold text-base text-indigo-600">{data?.customer_service?.avg_human_response_time || '0 دقيقة'}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
