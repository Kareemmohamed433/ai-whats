import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Lock, Mail, ArrowLeft, ShieldCheck, ExternalLink } from 'lucide-react';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('admin@nexorasolutions.com');
  const [password, setPassword] = useState('Nexora#Secure2026');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'بيانات الدخول غير صحيحة.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#04060D] px-4 py-12 relative overflow-hidden text-slate-100">
      {/* Background Decorative Tech Gradients */}
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-blue-600/15 rounded-full blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-[140px] pointer-events-none"></div>

      <div className="w-full max-w-md relative z-10">
        <div className="bg-[#0B1222]/90 backdrop-blur-xl border border-blue-500/25 rounded-3xl p-8 shadow-[0_10px_40px_rgba(30,107,255,0.15)]">
          {/* Brand Logo Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 text-white font-black text-3xl shadow-xl shadow-blue-500/30 mb-4 tracking-wider">
              N
            </div>
            <h1 className="text-2xl font-black text-white tracking-wide uppercase mb-1">NEXORA</h1>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-[11px] font-semibold text-cyan-400 mb-2">
              <Sparkles className="w-3 h-3 text-cyan-400" /> Ideas → Code → Impact
            </div>
            <p className="text-xs text-slate-400">منصة خدمة العملاء الموحدة بالذكاء الاصطناعي</p>
          </div>

          {error && (
            <div className="mb-6 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs text-center font-medium">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-2">البريد الإلكتروني المهني</label>
              <div className="relative">
                <Mail className="w-4 h-4 absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="admin@nexorasolutions.com"
                  className="w-full pl-4 pr-10 py-3 rounded-xl text-xs bg-slate-900/90 border border-slate-700/80 focus:border-cyan-400 focus:bg-slate-900 text-white placeholder-slate-500 outline-none transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-2">كلمة المرور</label>
              <div className="relative">
                <Lock className="w-4 h-4 absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••"
                  className="w-full pl-4 pr-10 py-3 rounded-xl text-xs bg-slate-900/90 border border-slate-700/80 focus:border-cyan-400 focus:bg-slate-900 text-white placeholder-slate-500 outline-none transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-bold text-xs shadow-lg shadow-blue-500/30 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <>
                  <span>تسجيل الدخول للمنصة</span>
                  <ArrowLeft className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Portfolio & Security Note */}
          <div className="mt-8 pt-6 border-t border-slate-800 text-center space-y-2">
            <a
              href="https://company-pi-two.vercel.app/"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs text-cyan-400 hover:text-cyan-300 font-semibold transition"
            >
              <span>استعرض بورتفوليو وسابقة أعمال NEXORA</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
            <div className="flex items-center justify-center gap-1.5 text-[11px] text-slate-500">
              <ShieldCheck className="w-3.5 h-3.5 text-blue-500" />
              <span>نظام آمن ومشفر لإدارة استفسارات ومشاريع العملاء</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
