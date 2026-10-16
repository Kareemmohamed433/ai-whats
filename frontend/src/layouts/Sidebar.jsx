import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Inbox, 
  Users, 
  Bot, 
  BookOpen, 
  ShoppingBag, 
  Package, 
  BarChart3, 
  CreditCard,
  MessageSquareCode, 
  Share2, 
  UserCheck, 
  Settings,
  Sparkles
} from 'lucide-react';

const navItems = [
  { name: 'لوحة التحكم', path: '/dashboard', icon: LayoutDashboard },
  { name: 'الرسائل والمحادثات', path: '/inbox', icon: Inbox, badge: 'جديد' },
  { name: 'العملاء', path: '/contacts', icon: Users },
  { name: 'مساعد AI الذكي', path: '/ai-agent', icon: Bot, isAi: true },
  { name: 'قاعدة المعرفة', path: '/knowledge', icon: BookOpen },
  { name: 'المنتجات والأسعار', path: '/products', icon: ShoppingBag },
  { name: 'الطلبات والمبيعات', path: '/orders', icon: Package },
  { name: 'مراجعة الدفعات', path: '/payment-reviews', icon: CreditCard },
  { name: 'الردود السريعة', path: '/quick-replies', icon: MessageSquareCode },
  { name: 'التحليلات والتقارير', path: '/analytics', icon: BarChart3 },
  { name: 'الربط والتكامل', path: '/integrations', icon: Share2 },
  { name: 'فريق العمل', path: '/team', icon: UserCheck },
  { name: 'الإعدادات العامة', path: '/settings', icon: Settings },
];

export default function Sidebar({ isOpen, setIsOpen }) {
  const location = useLocation();

  return (
    <aside className={`fixed inset-y-0 right-0 z-40 w-64 bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 transition-transform duration-300 ease-in-out lg:static lg:translate-x-0 ${isOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0'}`}>
      <div className="flex flex-col h-full">
        {/* Brand Header */}
        <div className="flex items-center justify-between h-16 px-5 border-b border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-600 via-emerald-500 to-amber-500 flex items-center justify-center text-white shadow-md shadow-emerald-500/20 font-bold text-lg">
              خـ
            </div>
            <div>
              <h1 className="font-bold text-base text-slate-900 dark:text-white leading-tight">خام سينا</h1>
              <p className="text-xs text-emerald-600 dark:text-emerald-400 font-medium flex items-center gap-1">
                <Sparkles className="w-3 h-3" /> نظام خدمة العملاء
              </p>
            </div>
          </div>
        </div>

        {/* Navigation List */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
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
                    ? 'bg-teal-600 text-white shadow-md shadow-teal-600/20 font-semibold'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-5 h-5 ${isActive ? 'text-white' : item.isAi ? 'text-emerald-500' : 'text-slate-500 dark:text-slate-400'}`} />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${isActive ? 'bg-white/20 text-white' : 'bg-emerald-100 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400'}`}>
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Brand Footer Info */}
        <div className="p-4 m-3 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200/50 dark:border-emerald-800/40">
          <div className="flex items-center gap-2 text-emerald-700 dark:text-emerald-300 font-bold text-xs mb-1">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
            ذكاء اصطناعي متصل
          </div>
          <p className="text-[11px] text-emerald-800/80 dark:text-emerald-300/70 leading-relaxed">
            يجيب على أسعار زيت الزيتون والمنتجات وسياسات الشحن آلياً.
          </p>
        </div>
      </div>
    </aside>
  );
}
