import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Inbox, 
  Users, 
  Bot, 
  BookOpen, 
  Sparkles, 
  Package, 
  BarChart3, 
  MessageSquareCode, 
  Share2, 
  UserCheck, 
  Settings,
  ExternalLink
} from 'lucide-react';

const navItems = [
  { name: 'لوحة التحكم', path: '/dashboard', icon: LayoutDashboard },
  { name: 'الرسائل والمحادثات', path: '/inbox', icon: Inbox, badge: 'جديد' },
  { name: 'العملاء والجهات', path: '/contacts', icon: Users },
  { name: 'مساعد AI الذكي', path: '/ai-agent', icon: Bot, isAi: true },
  { name: 'باقات الخدمات البرمجية', path: '/products', icon: Sparkles },
  { name: 'طلبات المشاريع (Leads)', path: '/orders', icon: Package },
  { name: 'قاعدة المعرفة والـ FAQs', path: '/knowledge', icon: BookOpen },
  { name: 'الردود السريعة', path: '/quick-replies', icon: MessageSquareCode },
  { name: 'التحليلات والتقارير', path: '/analytics', icon: BarChart3 },
  { name: 'قنوات الربط والتكامل', path: '/integrations', icon: Share2 },
  { name: 'فريق العمل', path: '/team', icon: UserCheck },
  { name: 'الإعدادات العامة', path: '/settings', icon: Settings },
];

export default function Sidebar({ isOpen, setIsOpen }) {
  const location = useLocation();

  return (
    <aside className={`fixed inset-y-0 right-0 z-40 w-64 bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 transition-transform duration-300 ease-in-out lg:static lg:translate-x-0 ${isOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0'}`}>
      <div className="flex flex-col h-full">
        {/* NEXORA Brand Header */}
        <div className="flex items-center justify-between h-16 px-5 border-b border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 flex items-center justify-center text-white shadow-md shadow-blue-500/20 font-black text-xl tracking-wider">
              N
            </div>
            <div>
              <h1 className="font-extrabold text-base text-slate-900 dark:text-white leading-tight uppercase tracking-wide">NEXORA</h1>
              <p className="text-[10px] text-blue-600 dark:text-cyan-400 font-semibold flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span> Ideas → Code → Impact
              </p>
            </div>
          </div>
        </div>

        {/* Portfolio Showcase Direct Link */}
        <div className="px-3 pt-3">
          <a
            href="https://company-pi-two.vercel.app/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-between px-3.5 py-2 rounded-xl text-xs font-bold text-blue-700 dark:text-cyan-300 bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-950/40 dark:to-cyan-950/40 border border-blue-200/70 dark:border-blue-800/50 hover:scale-[1.02] transition-transform duration-200"
          >
            <div className="flex items-center gap-2">
              <span className="text-sm">🌐</span>
              <span>معرض الأعمال (Portfolio)</span>
            </div>
            <ExternalLink className="w-3.5 h-3.5 text-blue-500" />
          </a>
        </div>

        {/* Navigation List */}
        <nav className="flex-1 overflow-y-auto px-3 py-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => setIsOpen && setIsOpen(false)}
                className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/25 font-semibold'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-5 h-5 ${isActive ? 'text-white' : item.isAi ? 'text-cyan-500' : 'text-slate-500 dark:text-slate-400'}`} />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${isActive ? 'bg-white/20 text-white' : 'bg-blue-100 dark:bg-blue-950 text-blue-600 dark:text-blue-400'}`}>
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Brand Footer Info */}
        <div className="p-4 m-3 rounded-2xl bg-blue-50 dark:bg-blue-950/40 border border-blue-200/50 dark:border-blue-800/40">
          <div className="flex items-center gap-2 text-blue-700 dark:text-cyan-300 font-bold text-xs mb-1">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
            ذكاء اصطناعي نشط 24/7
          </div>
          <p className="text-[11px] text-blue-900/80 dark:text-blue-300/70 leading-relaxed">
            يجيب على استفسارات البرمجيات، باقات الخدمات، ورابط البورتفوليو آلياً.
          </p>
        </div>
      </div>
    </aside>
  );
}
