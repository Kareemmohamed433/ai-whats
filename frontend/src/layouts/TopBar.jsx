import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { 
  Search, 
  Bell, 
  Sun, 
  Moon, 
  Menu, 
  LogOut, 
  ExternalLink,
  Settings,
  X
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function TopBar({ toggleSidebar }) {
  const { user, logout } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [showNotifications, setShowNotifications] = useState(false);
  const [userStatus, setUserStatus] = useState(user?.status || 'online');

  const notifications = [
    { id: 1, title: 'رسالة جديدة من واتساب', body: 'استفسار عن تطوير موقع عقاري وشات بوت ذكي', time: 'منذ دقيقتين', unread: true },
    { id: 2, title: 'تصعيد استفسار للدعم البشري', body: 'طلب عميل مناقشة متطلبات أتمتة العمليات والـ CRM', time: 'منذ 15 دقيقة', unread: true },
    { id: 3, title: 'طلب مشروع جديد (New Lead)', body: 'شركة الأفق للاستثمار - باقة الأعمال (Business)', time: 'منذ ساعة', unread: false }
  ];

  return (
    <header className="sticky top-0 z-30 h-16 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 px-4 lg:px-6 flex items-center justify-between gap-4">
      {/* Right side: Toggle & Search */}
      <div className="flex items-center gap-3 flex-1">
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-xl lg:hidden text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="relative max-w-md w-full hidden sm:block">
          <Search className="w-4 h-4 absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="بحث في الرسائل، طلبات المشروعات، والباقات..."
            className="w-full pl-4 pr-10 py-2 rounded-xl text-xs bg-slate-100 dark:bg-slate-800/80 border border-transparent focus:border-blue-500 focus:bg-white dark:focus:bg-slate-900 text-slate-800 dark:text-slate-100 placeholder-slate-400 outline-none transition-all"
          />
        </div>
      </div>

      {/* Left side: Controls, Portfolio Link, Notifications & User */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Quick Portfolio Button */}
        <a
          href="https://company-pi-two.vercel.app/"
          target="_blank"
          rel="noopener noreferrer"
          className="hidden md:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800/50 hover:bg-blue-100 dark:hover:bg-blue-900/50 transition"
          title="استعراض بورتفوليو وسابقة أعمال NEXORA الرسمية"
        >
          <ExternalLink className="w-3.5 h-3.5" />
          <span>البورتفوليو الرسمي</span>
        </a>

        {/* Dark Mode Toggle */}
        <button
          onClick={toggleTheme}
          title={isDark ? "تفعيل الوضع الفاتح" : "تفعيل الوضع الداكن"}
          className="p-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
        >
          {isDark ? <Sun className="w-5 h-5 text-amber-400" /> : <Moon className="w-5 h-5 text-slate-600" />}
        </button>

        {/* Notifications Popup */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-blue-500 rounded-full ring-2 ring-white dark:ring-slate-900 animate-pulse"></span>
          </button>

          {showNotifications && (
            <div className="absolute left-0 mt-2 w-80 sm:w-90 bg-white dark:bg-slate-900 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-800 overflow-hidden z-50">
              <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
                <h3 className="font-bold text-sm text-slate-900 dark:text-white">الإشعارات والتنبيهات</h3>
                <button onClick={() => setShowNotifications(false)} className="text-slate-400 hover:text-slate-600">
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="divide-y divide-slate-100 dark:divide-slate-800/60 max-h-80 overflow-y-auto">
                {notifications.map(n => (
                  <div key={n.id} className="p-3.5 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer">
                    <div className="flex items-center justify-between text-xs font-semibold text-slate-800 dark:text-slate-200 mb-1">
                      <span>{n.title}</span>
                      <span className="text-[10px] text-slate-400 font-normal">{n.time}</span>
                    </div>
                    <p className="text-xs text-slate-500 dark:text-slate-400">{n.body}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Settings button */}
        <button
          onClick={() => navigate('/settings')}
          className="p-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors hidden sm:flex"
        >
          <Settings className="w-5 h-5" />
        </button>

        {/* User Profile & Status */}
        <div className="flex items-center gap-2 pl-2 border-r border-slate-200 dark:border-slate-800 pr-2">
          <img
            src={user?.avatar || "https://ui-avatars.com/api/?name=Admin&background=1E6BFF&color=fff"}
            alt={user?.name}
            className="w-9 h-9 rounded-xl object-cover ring-2 ring-blue-500/20"
          />
          <div className="hidden md:block">
            <h4 className="text-xs font-bold text-slate-900 dark:text-white leading-tight">{user?.name || "فريق NEXORA"}</h4>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span className={`w-2 h-2 rounded-full ${userStatus === 'online' ? 'bg-blue-500' : 'bg-amber-500'}`}></span>
              <span className="text-[10px] text-slate-500 dark:text-slate-400 font-medium">
                {userStatus === 'online' ? 'متصل الآن' : 'مشغول'}
              </span>
            </div>
          </div>

          <button
            onClick={logout}
            title="تسجيل الخروج"
            className="p-2 mr-1 rounded-xl text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
