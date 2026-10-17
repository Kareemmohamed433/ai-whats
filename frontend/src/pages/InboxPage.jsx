import React, { useState, useEffect, useRef } from 'react';
import api from '../services/api';
import { socket } from '../services/socket';
import { useAuth } from '../context/AuthContext';
import { 
  Search, 
  Send, 
  Paperclip, 
  Bot, 
  UserCheck, 
  CheckCircle2, 
  XCircle,
  Play,
  UserX,
  Sparkles,
  RefreshCw,
  Pin,
  CreditCard,
  Zap,
  User,
  Clock,
  ShoppingBag,
  DollarSign,
  FileText,
  Activity,
  ChevronRight,
  ChevronLeft,
  AlertTriangle,
  Smile,
  ShieldAlert
} from 'lucide-react';

export default function InboxPage() {
  const { user: currentUser } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [selectedConv, setSelectedConv] = useState(null);
  const [messages, setMessages] = useState([]);
  const [pinnedMessages, setPinnedMessages] = useState([]);
  const [quickReplies, setQuickReplies] = useState([]);
  const [suggestedReplies, setSuggestedReplies] = useState([]);

  // Filters (Requirement #17)
  const [filter, setFilter] = useState('all'); // all, unread, ai, human, human_requests, pending_payments, open, closed
  const [platformFilter, setPlatformFilter] = useState(''); // whatsapp, instagram, telegram, tiktok
  const [search, setSearch] = useState('');

  // UI state
  const [inputText, setInputText] = useState('');
  const [showShortcutMenu, setShowShortcutMenu] = useState(false);
  const [showCustomer360, setShowCustomer360] = useState(true);
  const [customer360Data, setCustomer360Data] = useState(null);
  const [newNoteText, setNewNoteText] = useState('');
  const [agents, setAgents] = useState([]);
  const [loadingConvs, setLoadingConvs] = useState(true);
  const [sending, setSending] = useState(false);

  const messagesEndRef = useRef(null);
  const token = localStorage.getItem('token');

  // Audio chime notification (Requirement #19)
  const playNotificationSound = () => {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5 note
      gain.gain.setValueAtTime(0.1, ctx.currentTime);
      osc.start();
      osc.stop(ctx.currentTime + 0.2);
    } catch (e) {
      console.log("Audio play suppressed:", e);
    }
  };

  useEffect(() => {
    api.get('/users').then(res => {
      if (res.success) setAgents(res.users);
    }).catch(() => {});

    fetchQuickReplies();
  }, []);

  const fetchQuickReplies = async () => {
    try {
      const res = await api.get('/quick-replies');
      if (res.success) setQuickReplies(res.quick_replies || []);
    } catch (err) {}
  };

  const loadConversations = () => {
    let url = `/conversations?filter=${filter}&search=${encodeURIComponent(search)}`;
    if (platformFilter) url += `&platform=${platformFilter}`;

    api.get(url).then(res => {
      if (res.success) {
        setConversations(res.conversations);
        if (!selectedConv && res.conversations.length > 0) {
          loadConversationDetail(res.conversations[0].id);
        }
      }
    }).catch(err => console.error(err))
      .finally(() => setLoadingConvs(false));
  };

  useEffect(() => {
    loadConversations();
  }, [filter, platformFilter, search]);

  const loadConversationDetail = (id) => {
    api.get(`/conversations/${id}`).then(res => {
      if (res.success) {
        setSelectedConv(res.conversation);
        setMessages(res.conversation.messages || []);
        loadPinnedMessages(id);
        loadCustomer360(res.conversation.customer_id);
        loadSuggestedReplies(id);
      }
    }).catch(err => console.error(err));
  };

  const loadPinnedMessages = (convId) => {
    api.get(`/conversations/${convId}/pinned`).then(res => {
      if (res.success) setPinnedMessages(res.pinned_messages || []);
    }).catch(() => {});
  };

  const loadCustomer360 = (customerId) => {
    if (!customerId) return;
    api.get(`/customers/${customerId}`).then(res => {
      if (res.success) setCustomer360Data(res.customer);
    }).catch(() => {});
  };

  const loadSuggestedReplies = (convId) => {
    api.get(`/quick-replies/suggested?conversation_id=${convId}`).then(res => {
      if (res.success) setSuggestedReplies(res.suggested || []);
    }).catch(() => {});
  };

  // Real-time Socket.IO Listeners (Requirement #18)
  useEffect(() => {
    const handleNewMessage = (data) => {
      if (selectedConv && data.conversation_id === selectedConv.id) {
        setMessages(prev => {
          if (prev.some(m => m.id === data.message.id)) return prev;
          return [...prev, data.message];
        });
      }
      loadConversations();
    };

    const handleHumanHandoff = (data) => {
      playNotificationSound();
      if (Notification.permission === 'granted') {
        new Notification("🚨 طلب دعم بشري جديد (Human Request)", {
          body: `العميل في المحادثة #${data.conversation_id} طلب التحدث مع موظف خدمة العملاء.`
        });
      }
      loadConversations();
    };

    const handlePaymentReviewCreated = (data) => {
      playNotificationSound();
      if (Notification.permission === 'granted') {
        new Notification("💳 إثبات دفع جديد (Payment Review)", {
          body: `وصل إثبات دفع جديد بانتظار المراجعة للعميل ${data.payment_review?.customer_name || ''}.`
        });
      }
      loadConversations();
    };

    const handleConversationUpdated = (data) => {
      if (selectedConv && data.conversation.id === selectedConv.id) {
        setSelectedConv(prev => ({ ...prev, ...data.conversation }));
      }
      setConversations(prev => prev.map(c => c.id === data.conversation.id ? { ...c, ...data.conversation } : c));
    };

    const handleStatusChanged = (data) => {
      if (selectedConv && data.conversation_id === selectedConv.id) {
        setSelectedConv(prev => ({ ...prev, ...data.conversation }));
      }
      loadConversations();
    };

    socket.on('new_message', handleNewMessage);
    socket.on('agent_message', handleNewMessage);
    socket.on('conversation_updated', handleConversationUpdated);
    socket.on('conversation_status_changed', handleStatusChanged);
    socket.on('ai_status_changed', handleStatusChanged);
    socket.on('human_handoff', handleHumanHandoff);
    socket.on('payment_review_created', handlePaymentReviewCreated);

    return () => {
      socket.off('new_message', handleNewMessage);
      socket.off('agent_message', handleNewMessage);
      socket.off('conversation_updated', handleConversationUpdated);
      socket.off('conversation_status_changed', handleStatusChanged);
      socket.off('ai_status_changed', handleStatusChanged);
      socket.off('human_handoff', handleHumanHandoff);
      socket.off('payment_review_created', handlePaymentReviewCreated);
    };
  }, [selectedConv]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Actions: Send Agent Message (Requirement #4)
  const handleSendMessage = (e) => {
    e?.preventDefault();
    if (!inputText.trim() || !selectedConv || sending) return;

    setSending(true);
    api.post('/messages', {
      conversation_id: selectedConv.id,
      content: inputText
    }).then(res => {
      if (res.success) {
        setMessages(prev => {
          if (prev.some(m => m.id === res.message.id)) return prev;
          return [...prev, res.message];
        });
        setInputText('');
        setShowShortcutMenu(false);
      }
    }).catch(err => alert("حدث خطأ أثناء إرسال الرسالة"))
      .finally(() => setSending(false));
  };

  // Actions: Conversation Status Updates (Requirement #5 & #14)
  const handleStatusUpdate = (newConvStatus, newAiStatus) => {
    if (!selectedConv) return;
    const body = {};
    if (newConvStatus) body.conversation_status = newConvStatus;
    if (newAiStatus) body.ai_status = newAiStatus;

    api.put(`/conversations/${selectedConv.id}/status`, body).then(res => {
      if (res.success) {
        setSelectedConv(res.conversation);
        loadConversations();
      }
    }).catch(() => alert("تحديث حالة المحادثة فشل"));
  };

  // Assign Agent (Requirement #26)
  const handleAssignAgent = (agentId) => {
    if (!selectedConv) return;
    api.put(`/conversations/${selectedConv.id}/assign`, { assigned_agent_id: agentId }).then(res => {
      if (res.success) {
        setSelectedConv(res.conversation);
        loadConversations();
      }
    });
  };

  // Pin / Unpin Message (Requirement #20)
  const handleTogglePin = (messageId) => {
    if (!selectedConv) return;
    api.post(`/conversations/${selectedConv.id}/pin`, { message_id: messageId }).then(res => {
      if (res.success) {
        loadPinnedMessages(selectedConv.id);
      }
    });
  };

  // Add Customer Note (Requirement #2 & #28)
  const handleAddNote = (e) => {
    e.preventDefault();
    if (!newNoteText.trim() || !selectedConv?.customer_id) return;
    api.post(`/customers/${selectedConv.customer_id}/notes`, { note_text: newNoteText }).then(res => {
      if (res.success) {
        setNewNoteText('');
        loadCustomer360(selectedConv.customer_id);
      }
    });
  };

  // Composer Quick Reply Selection (Requirement #2 & #26)
  const handleSelectQuickReply = (text) => {
    const agentName = currentUser?.name || 'موظف الدعم';
    const customerName = selectedConv?.customer?.name || 'العميل';
    const processed = text.replace(/\{\{agent_name\}\}/g, agentName).replace(/\{\{customer_name\}\}/g, customerName);
    setInputText(processed);
    setShowShortcutMenu(false);
  };

  const handleInputChange = (e) => {
    const val = e.target.value;
    setInputText(val);
    if (val.startsWith('/')) {
      setShowShortcutMenu(true);
    } else {
      setShowShortcutMenu(false);
    }
  };

  return (
    <div className="h-[calc(100vh-6rem)] flex bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden">
      {/* 1. LEFT SIDEBAR: Unified Inbox List */}
      <div className="w-80 md:w-96 border-l border-slate-200 dark:border-slate-800 flex flex-col h-full bg-slate-50/50 dark:bg-slate-900/50">
        
        {/* Search & Header */}
        <div className="p-3.5 border-b border-slate-200 dark:border-slate-800 space-y-2.5">
          <div className="flex items-center justify-between">
            <h2 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-1.5">
              <span>صندوق المحادثات</span>
              <span className="text-[10px] bg-teal-100 dark:bg-teal-950 text-teal-600 dark:text-teal-400 font-extrabold px-2 py-0.5 rounded-full">
                {conversations.length}
              </span>
            </h2>
            <button onClick={loadConversations} className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-white">
              <RefreshCw className={`w-3.5 h-3.5 ${loadingConvs ? 'animate-spin' : ''}`} />
            </button>
          </div>

          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute right-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="بحث باسم العميل، الهاتف، المعرف..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pr-8 pl-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-hidden focus:border-teal-500"
            />
          </div>

          {/* Filter Tabs (Requirement #17) */}
          <div className="flex items-center gap-1 overflow-x-auto pb-1 text-[11px] font-semibold text-slate-500">
            {[
              { id: 'all', name: 'الكل' },
              { id: 'unread', name: 'غير مقروء' },
              { id: 'human_requests', name: '🚨 طلب موظف' },
              { id: 'pending_payments', name: '💳 دفعات معلقة' },
              { id: 'ai', name: '🤖 AI' },
              { id: 'human', name: '👤 موظف' },
              { id: 'open', name: 'مفتوحة' },
              { id: 'closed', name: 'مغلقة' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setFilter(tab.id)}
                className={`px-2.5 py-1 rounded-lg transition whitespace-nowrap ${
                  filter === tab.id
                    ? 'bg-teal-600 text-white font-bold'
                    : 'bg-white dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400'
                }`}
              >
                {tab.name}
              </button>
            ))}
          </div>

          {/* Platform Filters */}
          <div className="flex items-center gap-1 overflow-x-auto text-[10px]">
            {[
              { id: '', name: 'جميع القنوات' },
              { id: 'whatsapp', name: 'WhatsApp' },
              { id: 'telegram', name: 'Telegram' },
              { id: 'instagram', name: 'Instagram' },
              { id: 'tiktok', name: 'TikTok' }
            ].map(p => (
              <button
                key={p.id}
                onClick={() => setPlatformFilter(p.id)}
                className={`px-2 py-0.5 rounded-md transition whitespace-nowrap ${
                  platformFilter === p.id
                    ? 'bg-slate-800 dark:bg-slate-200 text-white dark:text-slate-900 font-bold'
                    : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-300'
                }`}
              >
                {p.name}
              </button>
            ))}
          </div>
        </div>

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-800/60">
          {loadingConvs ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-6 h-6 border-2 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
          ) : conversations.length === 0 ? (
            <div className="text-center py-12 text-slate-400 text-xs">لا توجد محادثات مطابقة للفلاتر</div>
          ) : (
            conversations.map((conv) => {
              const isSelected = selectedConv?.id === conv.id;
              const customerName = conv.customer?.name || 'عميل';
              const lastMsgText = conv.last_message?.content || 'بدء المحادثة';

              return (
                <div
                  key={conv.id}
                  onClick={() => loadConversationDetail(conv.id)}
                  className={`p-3.5 cursor-pointer transition flex items-start gap-3 relative ${
                    isSelected
                      ? 'bg-teal-500/10 dark:bg-teal-950/40 border-r-4 border-teal-600'
                      : 'hover:bg-slate-100/60 dark:hover:bg-slate-800/50'
                  }`}
                >
                  <div className="relative">
                    <img
                      src={conv.customer?.avatar || `https://ui-avatars.com/api/?name=${customerName}`}
                      alt={customerName}
                      className="w-10 h-10 rounded-full object-cover border border-slate-200 dark:border-slate-700"
                    />
                    <span className="absolute -bottom-1 -right-1 text-[10px] px-1 py-0.2 rounded-full font-bold bg-slate-900 text-white capitalize border border-white dark:border-slate-900">
                      {conv.platform[0]?.toUpperCase()}
                    </span>
                  </div>

                  <div className="flex-1 min-w-0 space-y-1">
                    <div className="flex items-center justify-between gap-1">
                      <h4 className="font-bold text-xs text-slate-900 dark:text-white truncate">
                        {customerName}
                      </h4>
                      <span className="text-[10px] text-slate-400">
                        {conv.last_message_at ? new Date(conv.last_message_at).toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' }) : ''}
                      </span>
                    </div>

                    <p className="text-[11px] text-slate-500 dark:text-slate-400 truncate">
                      {lastMsgText}
                    </p>

                    {/* Status Badges (Requirement #11) */}
                    <div className="flex items-center gap-1.5 pt-1 flex-wrap">
                      <span className={`text-[9px] font-extrabold px-2 py-0.5 rounded-md ${
                        conv.ai_status === 'active'
                          ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400'
                          : conv.ai_status === 'human_handled'
                          ? 'bg-amber-100 dark:bg-amber-950 text-amber-600 dark:text-amber-400'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-500'
                      }`}>
                        {conv.ai_status === 'active' ? '🟢 AI Active' : conv.ai_status === 'human_handled' ? '🟠 Human Handled' : '⚪ AI Disabled'}
                      </span>

                      <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded-md ${
                        conv.conversation_status === 'open'
                          ? 'bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-400'
                      }`}>
                        {conv.conversation_status === 'open' ? 'Open' : 'Closed'}
                      </span>

                      {conv.requires_human && (
                        <span className="text-[9px] font-bold px-1.5 py-0.5 rounded-md bg-rose-100 dark:bg-rose-950 text-rose-600 dark:text-rose-400 flex items-center gap-0.5">
                          <AlertTriangle className="w-2.5 h-2.5" /> طلب موظف
                        </span>
                      )}
                    </div>
                  </div>

                  {conv.unread_count > 0 && (
                    <span className="w-5 h-5 rounded-full bg-teal-600 text-white font-bold text-[10px] flex items-center justify-center">
                      {conv.unread_count}
                    </span>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* 2. CENTER AREA: Conversation View & Composer */}
      {selectedConv ? (
        <div className="flex-1 flex flex-col h-full bg-white dark:bg-slate-900 min-w-0">
          
          {/* Header & Controls (Requirement #5 & #14) */}
          <div className="p-3.5 border-b border-slate-200 dark:border-slate-800 flex flex-wrap items-center justify-between gap-3 bg-slate-50/50 dark:bg-slate-900/50">
            <div className="flex items-center gap-3">
              <img
                src={selectedConv.customer?.avatar || `https://ui-avatars.com/api/?name=${selectedConv.customer?.name}`}
                alt={selectedConv.customer?.name}
                className="w-10 h-10 rounded-full object-cover border border-slate-200 dark:border-slate-700"
              />
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-bold text-sm text-slate-900 dark:text-white">
                    {selectedConv.customer?.name}
                  </h3>
                  <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                    {selectedConv.platform}
                  </span>
                </div>

                <div className="flex items-center gap-2 mt-0.5 text-xs">
                  <span className={`font-bold ${
                    selectedConv.ai_status === 'active' ? 'text-emerald-500' : 'text-amber-500'
                  }`}>
                    {selectedConv.ai_status === 'active' ? '🟢 AI Active' : '🟠 Human Handled'}
                  </span>
                  <span className="text-slate-400">•</span>
                  <span className="text-slate-500 capitalize">{selectedConv.conversation_status}</span>
                </div>
              </div>
            </div>

            {/* Action Control Buttons (Requirement #5) */}
            <div className="flex items-center gap-2 flex-wrap">
              <button
                onClick={() => handleStatusUpdate('open', 'human_handled')}
                className="px-3 py-1.5 bg-amber-500/10 hover:bg-amber-500/20 text-amber-700 dark:text-amber-300 border border-amber-500/30 rounded-xl text-xs font-bold transition flex items-center gap-1"
              >
                <UserCheck className="w-3.5 h-3.5" /> 👤 تحويل لموظف
              </button>

              <button
                onClick={() => handleStatusUpdate('open', 'active')}
                className="px-3 py-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30 rounded-xl text-xs font-bold transition flex items-center gap-1"
              >
                <Bot className="w-3.5 h-3.5" /> 🤖 تفعيل AI
              </button>

              <button
                onClick={() => handleStatusUpdate('closed', selectedConv.ai_status)}
                className="px-3 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-xl text-xs font-bold transition"
              >
                🔒 إغلاق المحادثة
              </button>

              <button
                onClick={() => handleStatusUpdate('closed', 'active')}
                className="px-3 py-1.5 bg-teal-600 hover:bg-teal-700 text-white rounded-xl text-xs font-bold transition shadow-xs"
              >
                إغلاق المحادثة وإعادة تفعيل AI
              </button>

              {/* Assign Agent Dropdown */}
              <select
                value={selectedConv.assigned_agent_id || 0}
                onChange={(e) => handleAssignAgent(Number(e.target.value))}
                className="px-2.5 py-1.5 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-700 dark:text-slate-300 font-semibold"
              >
                <option value={0}>تحديد الموظف...</option>
                {agents.map(a => (
                  <option key={a.id} value={a.id}>{a.name}</option>
                ))}
              </select>

              <button
                onClick={() => setShowCustomer360(!showCustomer360)}
                className="p-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-xl text-slate-600 dark:text-slate-300 text-xs font-bold flex items-center gap-1"
              >
                {showCustomer360 ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
                Customer 360
              </button>
            </div>
          </div>

          {/* Pinned Messages Section (Requirement #20) */}
          {pinnedMessages.length > 0 && (
            <div className="bg-amber-500/10 border-b border-amber-500/20 p-2.5 px-4 flex items-center justify-between text-xs text-amber-800 dark:text-amber-300">
              <div className="flex items-center gap-2 overflow-x-auto">
                <Pin className="w-4 h-4 text-amber-600 shrink-0 fill-amber-600" />
                <span className="font-bold shrink-0">مثبت (Pinned):</span>
                <span className="truncate">{pinnedMessages[0]?.message?.content}</span>
              </div>
              <span className="text-[10px] opacity-75">{pinnedMessages.length} رسالة مثبتة</span>
            </div>
          )}

          {/* Messages View */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/30 dark:bg-slate-900/30">
            {messages.map((m) => {
              const isCustomer = m.sender_type === 'customer';
              const isAi = m.sender_type === 'ai';
              const isAgent = m.sender_type === 'agent';

              return (
                <div
                  key={m.id}
                  className={`flex flex-col ${isCustomer ? 'items-start' : 'items-end'}`}
                >
                  <div className="flex items-center gap-1.5 mb-1 text-[10px] text-slate-400">
                    <span>{isCustomer ? (selectedConv.customer?.name || 'عميل') : isAi ? '🤖 NEXORA AI' : `👤 ${m.sender_name || 'موظف الدعم'}`}</span>
                    <span>•</span>
                    <span>{new Date(m.created_at).toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' })}</span>
                    <button onClick={() => handleTogglePin(m.id)} className="hover:text-amber-500 p-0.5">
                      <Pin className="w-3 h-3" />
                    </button>
                  </div>

                  <div
                    className={`max-w-md p-3.5 rounded-2xl text-xs leading-relaxed shadow-xs ${
                      isCustomer
                        ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white rounded-tr-none border border-slate-200 dark:border-slate-700'
                        : isAi
                        ? 'bg-gradient-to-r from-teal-600 to-emerald-600 text-white rounded-tl-none font-medium'
                        : 'bg-slate-800 text-white rounded-tl-none dark:bg-slate-700 font-medium'
                    }`}
                  >
                    {m.media_url && (
                      <img src={m.media_url} alt="مرفق" className="max-w-xs rounded-xl mb-2 border border-white/20" />
                    )}
                    <p className="whitespace-pre-wrap">{m.content}</p>
                  </div>
                </div>
              );
            })}
            <div ref={messagesEndRef} />
          </div>

          {/* 3. COMPOSER AREA: Quick Replies & Composer */}
          <div className="p-3.5 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-2 relative">
            
            {/* Suggested Quick Replies (Requirement #24) */}
            {suggestedReplies.length > 0 && (
              <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
                <span className="text-[11px] font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-1 shrink-0">
                  <Zap className="w-3.5 h-3.5" /> ⚡ مقترحة:
                </span>
                {suggestedReplies.map(sr => (
                  <button
                    key={sr.id}
                    onClick={() => handleSelectQuickReply(sr.response_text)}
                    className="px-2.5 py-1 bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 rounded-xl text-[11px] font-semibold hover:bg-emerald-100 transition whitespace-nowrap"
                  >
                    {sr.title}
                  </button>
                ))}
              </div>
            )}

            {/* Quick Reply Pills Bar (Requirement #21) */}
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
              <span className="text-[11px] font-bold text-slate-400 shrink-0">⚡ الردود السريعة:</span>
              {quickReplies.map(qr => (
                <button
                  key={qr.id}
                  onClick={() => handleSelectQuickReply(qr.response_text)}
                  className="px-2.5 py-1 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-xl text-[11px] font-bold transition whitespace-nowrap"
                >
                  {qr.title}
                </button>
              ))}
            </div>

            {/* Shortcut Autocomplete Dropdown (Requirement #22) */}
            {showShortcutMenu && (
              <div className="absolute bottom-16 right-4 z-30 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-xl p-2 max-w-xs w-full space-y-1">
                <p className="text-[10px] font-bold text-slate-400 px-2 py-1">اختر اختصار رد سريع:</p>
                {quickReplies.map(qr => (
                  <div
                    key={qr.id}
                    onClick={() => handleSelectQuickReply(qr.response_text)}
                    className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg cursor-pointer flex items-center justify-between text-xs"
                  >
                    <span className="font-bold text-teal-600 font-mono">{qr.shortcut}</span>
                    <span className="text-slate-600 dark:text-slate-300 text-[11px] truncate max-w-[140px]">{qr.title}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Main Message Input Form */}
            <form onSubmit={handleSendMessage} className="flex items-center gap-2">
              <input
                type="text"
                placeholder="اكتب ردك هنا... (اكتب / للاختصارات)"
                value={inputText}
                onChange={handleInputChange}
                className="flex-1 p-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-hidden focus:border-teal-500"
              />

              <button
                type="submit"
                disabled={sending || !inputText.trim()}
                className="px-5 py-3 bg-teal-600 hover:bg-teal-700 text-white rounded-xl text-xs font-bold transition flex items-center gap-1 shadow-md shadow-teal-600/20 disabled:opacity-50"
              >
                <Send className="w-4 h-4" /> إرسال
              </button>
            </form>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center text-slate-400 text-sm">
          اختر محادثة من القائمة للبدء
        </div>
      )}

      {/* 4. RIGHT SIDEBAR: Customer 360 (Requirement #2 & #28) */}
      {selectedConv && showCustomer360 && (
        <div className="w-80 border-r border-slate-200 dark:border-slate-800 flex flex-col h-full bg-slate-50/50 dark:bg-slate-900/50 overflow-y-auto p-4 space-y-5">
          
          {/* Customer Profile Header */}
          <div className="text-center space-y-2 bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs">
            <img
              src={customer360Data?.avatar || `https://ui-avatars.com/api/?name=${selectedConv.customer?.name}`}
              alt={customer360Data?.name}
              className="w-16 h-16 rounded-full mx-auto object-cover border-2 border-teal-500"
            />
            <h3 className="font-bold text-sm text-slate-900 dark:text-white">
              {customer360Data?.name || selectedConv.customer?.name}
            </h3>
            <p className="text-xs text-slate-500 font-mono">
              {customer360Data?.phone || 'بدون تليفون مسجل'}
            </p>

            <div className="flex items-center justify-center gap-1 flex-wrap pt-1">
              {customer360Data?.identities?.map(id => (
                <span key={id.id} className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 capitalize">
                  {id.platform}: {id.platform_user_id}
                </span>
              ))}
            </div>
          </div>

          {/* Customer 360 Commercial Stats */}
          <div className="grid grid-cols-2 gap-2">
            <div className="bg-white dark:bg-slate-900 p-3 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
              <span className="text-[10px] font-bold text-slate-400 block">إجمالي الطلبات</span>
              <span className="text-sm font-extrabold text-teal-600 dark:text-teal-400">
                {customer360Data?.total_orders || 0} طلبات
              </span>
            </div>

            <div className="bg-white dark:bg-slate-900 p-3 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
              <span className="text-[10px] font-bold text-slate-400 block">إجمالي الإنفاق</span>
              <span className="text-sm font-extrabold text-emerald-600 dark:text-emerald-400">
                {customer360Data?.total_spent || 0} ج.م
              </span>
            </div>
          </div>

          {/* Current / Last Order Info */}
          {customer360Data?.last_order && (
            <div className="bg-white dark:bg-slate-900 p-3.5 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-900 dark:text-white flex items-center gap-1">
                  <ShoppingBag className="w-3.5 h-3.5 text-teal-600" /> آخر طلب #{customer360Data.last_order.order_number}
                </span>
                <span className="text-[10px] font-bold text-emerald-600 uppercase">
                  {customer360Data.last_order.order_status}
                </span>
              </div>
              <p className="text-[11px] text-slate-500">
                المبلغ الإجمالي: <span className="font-bold text-slate-800 dark:text-slate-200">{customer360Data.last_order.total_amount} ج.م</span>
              </p>
            </div>
          )}

          {/* Customer Notes (Requirement #2 & #28) */}
          <div className="bg-white dark:bg-slate-900 p-3.5 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-3">
            <h4 className="font-bold text-xs text-slate-900 dark:text-white flex items-center gap-1">
              <FileText className="w-3.5 h-3.5 text-teal-600" /> ملاحظات العميل (Notes)
            </h4>

            <form onSubmit={handleAddNote} className="space-y-2">
              <input
                type="text"
                placeholder="إضافة ملاحظة جديدة..."
                value={newNoteText}
                onChange={(e) => setNewNoteText(e.target.value)}
                className="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs"
              />
            </form>

            <div className="space-y-2 max-h-36 overflow-y-auto">
              {customer360Data?.notes_list?.map(n => (
                <div key={n.id} className="p-2 bg-slate-50 dark:bg-slate-800/60 rounded-xl text-[11px] space-y-0.5">
                  <p className="font-medium text-slate-800 dark:text-slate-200">{n.note_text}</p>
                  <p className="text-[9px] text-slate-400">{n.author_name} • {new Date(n.created_at).toLocaleDateString('ar-EG')}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Customer Activity Timeline (Requirement #28) */}
          <div className="bg-white dark:bg-slate-900 p-3.5 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-3">
            <h4 className="font-bold text-xs text-slate-900 dark:text-white flex items-center gap-1">
              <Activity className="w-3.5 h-3.5 text-teal-600" /> سجّل النشاط (Activity Timeline)
            </h4>

            <div className="space-y-3 relative before:absolute before:right-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200 dark:before:bg-slate-800 pr-4">
              {customer360Data?.activities?.map(act => (
                <div key={act.id} className="relative text-[11px] space-y-0.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-teal-500 absolute -right-4 top-1"></div>
                  <p className="font-semibold text-slate-800 dark:text-slate-200">{act.description}</p>
                  <p className="text-[9px] text-slate-400">{new Date(act.created_at).toLocaleString('ar-EG')}</p>
                </div>
              ))}
            </div>
          </div>

        </div>
      )}
    </div>
  );
}
