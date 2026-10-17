import React, { useState, useEffect } from 'react';
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
  X,
  Volume2,
  VolumeX,
  Smartphone
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { socket } from '../services/socket';
import { playNotificationChime } from '../services/notificationService';

export default function TopBar({ toggleSidebar }) {
  const { user, logout } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [showNotifications, setShowNotifications] = useState(false);
  const [unreadAlerts, setUnreadAlerts] = useState([]);
  const [soundEnabled, setSoundEnabled] = useState(true);

  // Listen for real-time incoming messages for toast notifications & sound
  useEffect(() => {
    const handleIncomingAlert = (data) => {
      if (soundEnabled) {
        playNotificationChime();
      }

      const alertItem = {
        id: Date.now(),
        title: `رسالة جديدة من ${data.customer_name || 'عميل'} (${data.platform || 'شات'})`,
        body: data.preview || 'لديك رسالة واردة جديدة',
        time: 'الآن',
        conversationId: data.conversation_id
      };

      setUnreadAlerts(prev => [alertItem, ...prev.slice(0, 9)]);

      // If page is hidden, show browser notification if permitted
      if (document.hidden && 'Notification' in window && Notification.permission === 'granted') {
        try {
          new Notification(alertItem.title, {
            body: alertItem.body,
            icon: '/icon-192.png',
            tag: `conv-${data.conversation_id}`
          });
        } catch (e) {
          console.warn('Native notification display error:', e);
        }
      }
    };

    socket.on('incoming_message_notification', handleIncomingAlert);
    return () => {
      socket.off('incoming_message_notification', handleIncomingAlert);
    };
  }, [soundEnabled]);

  return (
    <header className="sticky top-0 z-30 h-16 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 px-3 sm:px-4 lg:px-6 flex items-center justify-between gap-2 sm:gap-4 select-none">
      {/* Right side: Toggle & Search */}
      <div className="flex items-center gap-2 sm:gap-3 flex-1 min-w-0">
        <button
          onClick={toggleSidebar}
          aria-label="القائمة الجانبية"
          className="p-2 rounded-xl lg:hidden text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Brand Monogram on Mobile when sidebar is closed */}
        <div className="lg:hidden flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-600 to-cyan-400 flex items-center justify-center text-white font-black text-sm shadow-sm">
            N
          </div>
          <span className="font-extrabold text-sm text-slate-900 dark:text-white hidden xs:inline">NEXORA</span>
        </div>

        <div className="relative max-w-md w-full hidden md:block">
          <Search className="w-4 h-4 absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="بحث في الرسائل، طلبات المشروعات، والباقات..."
            className="w-full pl-4 pr-10 py-2 rounded-xl text-xs bg-slate-100 dark:bg-slate-800/80 border border-transparent focus:border-blue-500 focus:bg-white dark:focus:bg-slate-900 text-slate-800 dark:text-slate-100 placeholder-slate-400 outline-none transition-all"
          />
        </div>
      </div>

      {/* Left side: Controls, Portfolio Link, Notifications & User */}
      <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
        {/* Quick Portfolio Button */}
        <a
          href="https://company-pi-two.vercel.app/"
          target="_blank"
          rel="noopener noreferrer"
          className="hidden xl:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800/50 hover:bg-blue-100 dark:hover:bg-blue-900/50 transition"
          title="استعراض سابقة أعمال NEXORA"
        >
          <ExternalLink className="w-3.5 h-3.5" />
          <span>البورتفوليو</span>
        </a>

        {/* Audio Mute/Unmute quick toggle */}
        <button
          onClick={() => setSoundEnabled(!soundEnabled)}
          title={soundEnabled ? "كتم صوت التنبيهات" : "تفعيل صوت التنبيهات"}
          className="p-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
        >
          {soundEnabled ? <Volume2 className="w-4 h-4 text-blue-500" /> : <VolumeX className="w-4 h-4 text-slate-400" />}
        </button>

        {/* Dark Mode Toggle */}
        <button
          onClick={toggleTheme}
          title={isDark ? "تفعيل الوضع الفاتح" : "تفعيل الوضع الداكن"}
          className="p-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
        >
          {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
        </button>

        {/* Notifications Popup */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            aria-label="التنبيهات"
            className="relative p-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
          >
            <Bell className="w-4 h-4 sm:w-5 sm:h-5" />
            {unreadAlerts.length > 0 && (
              <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-blue-600 rounded-full ring-2 ring-white dark:ring-slate-900 animate-pulse"></span>
            )}
          </button>

          {showNotifications && (
            <div className="absolute left-0 mt-2 w-72 sm:w-84 bg-white dark:bg-slate-900 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-800 overflow-hidden z-50">
              <div className="p-3.5 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <h3 className="font-bold text-xs text-slate-900 dark:text-white">التنبيهات المباشرة</h3>
                  {unreadAlerts.length > 0 && (
                    <span className="text-[10px] bg-blue-100 dark:bg-blue-950 text-blue-600 dark:text-blue-400 px-1.5 py-0.5 rounded-full font-bold">
                      {unreadAlerts.length}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => navigate('/settings')}
                    title="إعدادات الإشعارات"
                    className="text-[10px] text-blue-600 dark:text-cyan-400 hover:underline flex items-center gap-1 font-semibold"
                  >
                    <Smartphone className="w-3 h-3" /> إعدادات Push
                  </button>
                  <button onClick={() => setShowNotifications(false)} className="text-slate-400 hover:text-slate-600">
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              <div className="divide-y divide-slate-100 dark:divide-slate-800/60 max-h-72 overflow-y-auto">
                {unreadAlerts.length === 0 ? (
                  <div className="p-6 text-center text-xs text-slate-400">
                    لا توجد تنبيهات جديدة حالياً
                  </div>
                ) : (
                  unreadAlerts.map(n => (
                    <div
                      key={n.id}
                      onClick={() => {
                        setShowNotifications(false);
                        navigate(`/inbox?conversationId=${n.conversationId}`);
                      }}
                      className="p-3 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition cursor-pointer"
                    >
                      <div className="flex items-center justify-between text-xs font-semibold text-slate-800 dark:text-slate-200 mb-0.5">
                        <span className="truncate">{n.title}</span>
                        <span className="text-[10px] text-slate-400 font-normal shrink-0 mr-1">{n.time}</span>
                      </div>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-2">{n.body}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* User Profile & Logout */}
        <div className="flex items-center gap-1.5 pl-1 border-r border-slate-200 dark:border-slate-800 pr-1.5">
          <img
            src={user?.avatar || "https://ui-avatars.com/api/?name=Admin&background=1E6BFF&color=fff"}
            alt={user?.name}
            className="w-8 h-8 rounded-xl object-cover ring-2 ring-blue-500/20"
          />
          <button
            onClick={logout}
            title="تسجيل الخروج"
            className="p-1.5 rounded-xl text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
