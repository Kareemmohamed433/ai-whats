import React, { useEffect, useState } from 'react';
import api from '../services/api';
import socket from '../services/socket';
import { 
  MessageSquare, 
  Bot, 
  UserCheck, 
  Package, 
  Sparkles,
  RefreshCw,
  AlertCircle,
  ExternalLink,
  ArrowUpRight,
  TrendingUp,
  Layers,
  CheckCircle2
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function DashboardOverviewPage() {
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState(null);
  const [humanRequests, setHumanRequests] = useState([]);
  const [recentLeads, setRecentLeads] = useState([]);
  const [recentConvs, setRecentConvs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);

  const fetchDashboardData = async (isSilent = false) => {
    if (!isSilent) setLoading(true);
    setErrorMsg(null);

    const [analyticsRes, humanRes, leadsRes, convsRes] = await Promise.allSettled([
      api.get('/analytics'),
      api.get('/conversations?filter=human_requests'),
      api.get('/leads'),
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

    if (leadsRes.status === 'fulfilled' && leadsRes.value?.success) {
      setRecentLeads((leadsRes.value.leads || []).slice(0, 5));
    }

    if (convsRes.status === 'fulfilled' && convsRes.value?.success) {
      setRecentConvs((convsRes.value.conversations || []).slice(0, 5));
    }

    if (hasErrors && !analyticsRes.value?.success) {
      setErrorMsg('تعذر جلب بعض البيانات التفاعلية. يرجى التأكد من تشغيل السيرفر.');
    }

    setLoading(false);
  };

  useEffect(() => {
    fetchDashboardData();

    const interval = setInterval(() => {
      fetchDashboardData(true);
    }, 15000);

    api.post('/auth/heartbeat').catch(() => {});

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
      <div className="relative rounded-3xl bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 text-white p-6 sm:p-8 shadow-xl overflow-hidden border border-blue-500/20">
        <div className="absolute top-0 left-0 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 backdrop-blur-md text-xs font-semibold text-cyan-300 border border-blue-400/30">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" /> Ideas → Code → Impact
            </div>
            <h2 className="text-2xl sm:text-3xl font-black tracking-tight">
              لوحة تحكم NEXORA Software Solutions
            </h2>
            <p className="text-sm text-slate-200 leading-relaxed">
              منصة خدمة العملاء الذكية لإدارة محادثات العملاء، طلبات المشروعات، حلول الذكاء الاصطناعي، واستعراض سابقة الأعمال عبر مختلف القنوات.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <a
              href="https://company-pi-two.vercel.app/"
              target="_blank"
              rel="noopener noreferrer"
              className="px-5 py-3 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-bold text-xs backdrop-blur-md border border-white/20 flex items-center gap-2 transition"
            >
              <span>معرض الأعمال</span>
              <ExternalLink className="w-4 h-4 text-cyan-300" />
            </a>
            <button
              onClick={() => fetchDashboardData(false)}
              className="p-3 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-bold text-xs transition"
              title="تحديث البيانات"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={() => navigate('/inbox')}
              className="px-6 py-3 rounded-2xl bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-bold text-sm shadow-lg shadow-blue-500/30 flex items-center justify-center gap-2 transition-all whitespace-nowrap"
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
        <div onClick={() => navigate('/inbox?filter=open')} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs cursor-pointer hover:border-blue-500 transition">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500">المحادثات المفتوحة</span>
            <div className="w-9 h-9 rounded-xl bg-blue-500/10 text-blue-600 flex items-center justify-center font-bold">
              <MessageSquare className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white">
            {metrics?.conversations?.open ?? 0}
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">
            من إجمالي {metrics?.conversations?.total ?? 0} محادثة
          </span>
        </div>

        <div onClick={() => navigate('/orders')} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs cursor-pointer hover:border-cyan-500 transition">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500">طلبات المشاريع (Leads)</span>
            <div className="w-9 h-9 rounded-xl bg-cyan-500/10 text-cyan-600 flex items-center justify-center font-bold">
              <Package className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white">
            {metrics?.leads?.total ?? recentLeads.length}
          </div>
          <span className="text-[11px] text-cyan-600 dark:text-cyan-400 font-semibold mt-1 block">
            {metrics?.leads?.new ?? 0} طلبات جديدة مؤهلة
          </span>
        </div>

        <div onClick={() => navigate('/inbox?filter=human_requests')} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs cursor-pointer hover:border-amber-500 transition">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500">تحويلات الدعم البشري</span>
            <div className="w-9 h-9 rounded-xl bg-amber-500/10 text-amber-600 flex items-center justify-center font-bold">
              <UserCheck className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white">
            {humanRequests.length}
          </div>
          <span className="text-[11px] text-amber-600 dark:text-amber-400 font-medium mt-1 block">
            بانتظار متابعة المهندسين
          </span>
        </div>

        <div onClick={() => navigate('/products')} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs cursor-pointer hover:border-indigo-500 transition">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500">باقات الخدمات</span>
            <div className="w-9 h-9 rounded-xl bg-indigo-500/10 text-indigo-600 flex items-center justify-center font-bold">
              <Layers className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white">
            3 باقات
          </div>
          <span className="text-[11px] text-indigo-600 dark:text-indigo-400 font-medium mt-1 block">
            Starter, Business, Enterprise
          </span>
        </div>

        <div onClick={() => navigate('/ai-agent')} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs cursor-pointer hover:border-emerald-500 transition">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500">كفاءة المساعد الذكي</span>
            <div className="w-9 h-9 rounded-xl bg-emerald-500/10 text-emerald-600 flex items-center justify-center font-bold">
              <Bot className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white">
            {metrics?.ai?.ai_resolution_rate ?? 95}%
          </div>
          <span className="text-[11px] text-emerald-600 dark:text-emerald-400 font-medium mt-1 block">
            سرعة الرد ~1.2 ثانية
          </span>
        </div>
      </div>

      {/* Grid: Leads and Realtime Channels */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Recent Leads / Project Inquiries */}
        <div className="lg:col-span-7 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-xs">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="font-bold text-base text-slate-900 dark:text-white">أحدث طلبات المشروعات (Leads)</h3>
              <p className="text-xs text-slate-500">طلبات واستفسارات العملاء المسجلة عبر المساعد الذكي والموقع</p>
            </div>
            <button
              onClick={() => navigate('/orders')}
              className="text-xs font-bold text-blue-600 dark:text-cyan-400 hover:underline"
            >
              عرض جميع الطلبات
            </button>
          </div>

          <div className="divide-y divide-slate-100 dark:divide-slate-800/60">
            {recentLeads.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-400">
                لا توجد طلبات مشاريع جديدة حالياً.
              </div>
            ) : (
              recentLeads.map((lead) => (
                <div key={lead.id} className="py-3.5 flex items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-slate-900 dark:text-white">
                        {lead.customer_name}
                      </span>
                      {lead.package_interest && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300">
                          {lead.package_interest}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-1">
                      {lead.requested_service} • {lead.contact_info}
                    </p>
                  </div>
                  <div className="text-left shrink-0">
                    <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-cyan-100 dark:bg-cyan-950 text-cyan-700 dark:text-cyan-300 block mb-1">
                      {lead.status}
                    </span>
                    {lead.budget && (
                      <span className="text-[10px] text-slate-400 block">{lead.budget}</span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right Column: Platform Channels & Portfolio Card */}
        <div className="lg:col-span-5 space-y-6">
          {/* Active Channels */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-xs">
            <h3 className="font-bold text-base text-slate-900 dark:text-white mb-1">قنوات التراسل المتصلة</h3>
            <p className="text-xs text-slate-500 mb-4">حالة المحادثات المباشرة عبر المنصات</p>

            <div className="space-y-3">
              {(metrics?.platforms || [
                { platform: 'whatsapp', name: 'واتساب', count: 0, color: '#25D366' },
                { platform: 'telegram', name: 'تيليجرام', count: 0, color: '#24A1DE' },
                { platform: 'instagram', name: 'إنستغرام', count: 0, color: '#E4405F' },
                { platform: 'tiktok', name: 'تيك توك', count: 0, color: '#000000' }
              ]).map((plat) => (
                <div key={plat.platform} className="flex items-center justify-between p-3 rounded-2xl bg-slate-50 dark:bg-slate-800/40">
                  <div className="flex items-center gap-3">
                    <span className="w-3 h-3 rounded-full" style={{ backgroundColor: plat.color }}></span>
                    <span className="text-xs font-bold text-slate-800 dark:text-slate-200">{plat.name}</span>
                  </div>
                  <span className="text-xs font-bold text-slate-600 dark:text-slate-400">
                    {plat.count} محادثة
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Portfolio Showcase Card */}
          <div className="bg-gradient-to-br from-blue-900/40 to-cyan-900/30 border border-blue-500/30 rounded-3xl p-6 text-slate-100">
            <div className="flex items-center gap-2 text-cyan-400 text-xs font-bold mb-2">
              <Sparkles className="w-4 h-4" /> البورتفوليو وسابقة الأعمال
            </div>
            <h4 className="text-base font-bold text-white mb-2">معرض أعمال NEXORA الرسمي</h4>
            <p className="text-xs text-slate-300 leading-relaxed mb-4">
              يمكنك استعراض المشاريع والنماذج التفاعلية المعروضة في البورتفوليو، بما فيها مشاريع السياحة، المطاعم، والأزياء.
            </p>
            <a
              href="https://company-pi-two.vercel.app/"
              target="_blank"
              rel="noopener noreferrer"
              className="w-full inline-flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-xs font-bold text-white bg-blue-600 hover:bg-blue-500 transition shadow-md shadow-blue-600/30"
            >
              <span>فتح البورتفوليو المباشر</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
