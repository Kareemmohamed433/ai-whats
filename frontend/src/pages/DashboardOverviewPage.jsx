import React, { useEffect, useState, useRef } from 'react';
import api from '../services/api';
import socket from '../services/socket';
import { 
  MessageSquare, 
  Bot, 
  UserCheck, 
  CreditCard, 
  AlertTriangle, 
  ArrowUpRight, 
  Sparkles,
  RefreshCw,
  AlertCircle
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function DashboardOverviewPage() {
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState(null);
  const [humanRequests, setHumanRequests] = useState([]);
  const [pendingPayments, setPendingPayments] = useState([]);
  const [recentConvs, setRecentConvs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);

  const fetchDashboardData = async (isSilent = false) => {
    if (!isSilent) setLoading(true);
    setErrorMsg(null);

    const [analyticsRes, humanRes, paymentRes, convsRes] = await Promise.allSettled([
      api.get('/analytics'),
      api.get('/conversations?filter=human_requests'),
      api.get('/payment-reviews?status=pending'),
      api.get('/conversations?filter=all')
    ]);

    let hasErrors = false;

    if (analyticsRes.status === 'fulfilled' && analyticsRes.value?.success) {
      setMetrics(analyticsRes.value.metrics);
    } else if (analyticsRes.status === 'rejected') {
      hasErrors = true;
    }

    if (humanRes.status === 'fulfilled' && humanRes.value?.success) {
      setHumanRequests(humanRes.value.conversations || []);
    }

    if (paymentRes.status === 'fulfilled' && paymentRes.value?.success) {
      setPendingPayments(paymentRes.value.payment_reviews || []);
    }

    if (convsRes.status === 'fulfilled' && convsRes.value?.success) {
      setRecentConvs((convsRes.value.conversations || []).slice(0, 5));
    }

    if (hasErrors && !analyticsRes.value?.success) {
      setErrorMsg('تعذر جلب بعض البيانات التفاعلية. يرجى التأكد من اتصال السيرفر.');
    }

    setLoading(false);
  };

  useEffect(() => {
    fetchDashboardData();

    // Polling every 15 seconds for live data sync
    const interval = setInterval(() => {
      fetchDashboardData(true);
    }, 15000);

    // Send heartbeat for team status tracking
    api.post('/auth/heartbeat').catch(() => {});

    // Listen to real-time events via Socket.io
    const handleNewMessage = () => fetchDashboardData(true);
    const handleConvUpdate = () => fetchDashboardData(true);

    if (socket) {
      socket.on('new_message', handleNewMessage);
      socket.on('conversation_updated', handleConvUpdate);
    }

    return () => {
      clearInterval(interval);
      if (socket) {
        socket.off('new_message', handleNewMessage);
        socket.off('conversation_updated', handleConvUpdate);
      }
    };
  }, []);

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="relative rounded-3xl bg-gradient-to-r from-teal-800 via-emerald-800 to-slate-900 text-white p-6 sm:p-8 shadow-xl overflow-hidden">
        <div className="absolute top-0 left-0 w-80 h-80 bg-white/10 rounded-full blur-3xl"></div>
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/15 backdrop-blur-md text-xs font-semibold text-emerald-200">
              <Sparkles className="w-3.5 h-3.5" /> منصة خدمة العملاء الموحدة 2026
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
              مرحباً بك في لوحة تحكم خام سينا 🌿
            </h2>
            <p className="text-sm text-slate-200 leading-relaxed">
              منصة مركزية تجمع WhatsApp, Instagram, Telegram, و TikTok مع مساعد الذكاء الاصطناعي والدعم البشري المباشر.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => fetchDashboardData(false)}
              className="p-3.5 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-bold text-xs transition"
              title="تحديث البيانات"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={() => navigate('/inbox')}
              className="px-6 py-3.5 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm shadow-lg shadow-emerald-500/30 flex items-center justify-center gap-2 transition-all whitespace-nowrap"
            >
              فتح صندوق الرسائل <ArrowUpRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <div onClick={() => navigate('/inbox?filter=open')} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs cursor-pointer hover:border-teal-500 transition">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500">المحادثات النشطة</span>
            <div className="w-9 h-9 rounded-xl bg-blue-500/10 text-blue-600 flex items-center justify-center font-bold">
              <MessageSquare className="w-5 h-5" />
            </div>
          </div>
          <h3 className="text-2xl font-black text-slate-900 dark:text-white">
            {metrics?.conversations?.open ?? recentConvs.filter(c => c.conversation_status === 'open').length}
          </h3>
        </div>

        <div onClick={() => navigate('/inbox?filter=ai')} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs cursor-pointer hover:border-emerald-500 transition">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500">محادثات AI</span>
            <div className="w-9 h-9 rounded-xl bg-emerald-500/10 text-emerald-600 flex items-center justify-center font-bold">
              <Bot className="w-5 h-5" />
            </div>
          </div>
          <h3 className="text-2xl font-black text-slate-900 dark:text-white">
            {metrics?.ai?.ai_handled ?? recentConvs.filter(c => c.ai_status === 'active').length}
          </h3>
        </div>

        <div onClick={() => navigate('/inbox?filter=human')} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs cursor-pointer hover:border-amber-500 transition">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500">محادثات بشرية</span>
            <div className="w-9 h-9 rounded-xl bg-amber-500/10 text-amber-600 flex items-center justify-center font-bold">
              <UserCheck className="w-5 h-5" />
            </div>
          </div>
          <h3 className="text-2xl font-black text-slate-900 dark:text-white">
            {metrics?.ai?.human_handled ?? recentConvs.filter(c => c.ai_status === 'human_handled').length}
          </h3>
        </div>

        <div onClick={() => navigate('/inbox?filter=human_requests')} className="bg-white dark:bg-slate-900 border border-rose-200 dark:border-rose-950 rounded-2xl p-5 shadow-xs cursor-pointer hover:border-rose-500 transition">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-rose-600">طلبات الموظف</span>
            <div className="w-9 h-9 rounded-xl bg-rose-500/10 text-rose-600 flex items-center justify-center font-bold">
              <AlertTriangle className="w-5 h-5 animate-pulse" />
            </div>
          </div>
          <h3 className="text-2xl font-black text-rose-600 dark:text-rose-400">
            {metrics?.conversations?.human_requests ?? humanRequests.length}
          </h3>
        </div>

        <div onClick={() => navigate('/payment-reviews')} className="bg-white dark:bg-slate-900 border border-purple-200 dark:border-purple-950 rounded-2xl p-5 shadow-xs cursor-pointer hover:border-purple-500 transition">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-purple-600">دفعات بانتظار المراجعة</span>
            <div className="w-9 h-9 rounded-xl bg-purple-500/10 text-purple-600 flex items-center justify-center font-bold">
              <CreditCard className="w-5 h-5" />
            </div>
          </div>
          <h3 className="text-2xl font-black text-purple-600 dark:text-purple-400">
            {metrics?.customer_service?.pending_payments ?? pendingPayments.length}
          </h3>
        </div>
      </div>

      {/* Main Overview Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Human Requests Queue */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-500" />
              طلبات الدعم البشري (Human Requests)
            </h3>
            <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-rose-100 dark:bg-rose-950 text-rose-600">
              {humanRequests.length}
            </span>
          </div>

          <div className="space-y-2 max-h-80 overflow-y-auto">
            {loading && humanRequests.length === 0 ? (
              <p className="text-center py-8 text-xs text-slate-400">جاري تحميل البيانات...</p>
            ) : humanRequests.length === 0 ? (
              <div className="text-center py-8 space-y-1">
                <p className="text-xs text-slate-400">لا توجد طلبات دعم بشري حالياً</p>
                <p className="text-[11px] text-slate-500">سيتم تنبيه الموظف فور طلب العميل التحدث لموظف</p>
              </div>
            ) : (
              humanRequests.map(conv => (
                <div
                  key={conv.id}
                  onClick={() => navigate('/inbox')}
                  className="p-3 bg-slate-50 dark:bg-slate-800 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-700/60 cursor-pointer transition flex items-center justify-between"
                >
                  <div>
                    <h4 className="text-xs font-bold text-slate-900 dark:text-white">{conv.customer?.name || 'عميل'}</h4>
                    <p className="text-[11px] text-slate-500 truncate max-w-[160px]">{conv.last_message?.content || 'طلب تدخل بشري'}</p>
                  </div>
                  <span className="text-[10px] font-bold text-teal-600 flex items-center gap-0.5">
                    فتح المحادثة <ArrowUpRight className="w-3 h-3" />
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Pending Payment Reviews */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
              <CreditCard className="w-4 h-4 text-purple-500" />
              مراجعة الدفعات المعلقة (Payment Reviews)
            </h3>
            <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-purple-100 dark:bg-purple-950 text-purple-600">
              {pendingPayments.length}
            </span>
          </div>

          <div className="space-y-2 max-h-80 overflow-y-auto">
            {loading && pendingPayments.length === 0 ? (
              <p className="text-center py-8 text-xs text-slate-400">جاري تحميل البيانات...</p>
            ) : pendingPayments.length === 0 ? (
              <div className="text-center py-8 space-y-1">
                <p className="text-xs text-slate-400">لا توجد إثباتات دفع بانتظار المراجعة</p>
                <p className="text-[11px] text-slate-500">تظهر الإثباتات المستلمة عبر واتساب وتيليجرام هنا</p>
              </div>
            ) : (
              pendingPayments.map(rev => (
                <div
                  key={rev.id}
                  onClick={() => navigate('/payment-reviews')}
                  className="p-3 bg-slate-50 dark:bg-slate-800 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-700/60 cursor-pointer transition flex items-center justify-between"
                >
                  <div>
                    <h4 className="text-xs font-bold text-slate-900 dark:text-white">{rev.customer_name}</h4>
                    <p className="text-[11px] text-emerald-600 font-bold">المبلغ: {rev.detected_amount || rev.expected_amount || 0} ج.م</p>
                  </div>
                  <span className="text-[10px] font-bold text-purple-600 flex items-center gap-0.5">
                    مراجعة الآن <ArrowUpRight className="w-3 h-3" />
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Latest Conversations */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-teal-500" />
              أحدث المحادثات (أحدث 5 محادثات)
            </h3>
            <button onClick={() => navigate('/inbox')} className="text-xs text-teal-600 font-bold hover:underline">
              عرض الكل
            </button>
          </div>

          <div className="space-y-2 max-h-80 overflow-y-auto">
            {loading && recentConvs.length === 0 ? (
              <p className="text-center py-8 text-xs text-slate-400">جاري تحميل المحادثات...</p>
            ) : recentConvs.length === 0 ? (
              <div className="text-center py-8 space-y-1">
                <p className="text-xs text-slate-400">لا توجد محادثات مسجلة بعد</p>
              </div>
            ) : (
              recentConvs.map(conv => (
                <div
                  key={conv.id}
                  onClick={() => navigate('/inbox')}
                  className="p-3 bg-slate-50 dark:bg-slate-800 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-700/60 cursor-pointer transition flex items-center justify-between text-xs"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-bold text-slate-900 dark:text-white">{conv.customer?.name || 'عميل'}</h4>
                      <span className={`px-1.5 py-0.2 rounded text-[9px] font-semibold ${
                        conv.platform === 'whatsapp' ? 'bg-emerald-100 text-emerald-700' :
                        conv.platform === 'instagram' ? 'bg-pink-100 text-pink-700' :
                        conv.platform === 'telegram' ? 'bg-sky-100 text-sky-700' : 'bg-slate-200 text-slate-700'
                      }`}>
                        {conv.platform}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 truncate max-w-[180px] mt-0.5">
                      {conv.last_message?.content || 'لا توجد رسائل'}
                    </p>
                  </div>
                  <div className="text-left">
                    <span className="text-[10px] text-slate-400 block">
                      {conv.last_message_at ? new Date(conv.last_message_at).toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' }) : ''}
                    </span>
                    <span className={`text-[9px] font-bold ${conv.ai_status === 'active' ? 'text-emerald-500' : 'text-amber-500'}`}>
                      {conv.ai_status === 'active' ? 'AI نشط' : 'تحويل بشري'}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
