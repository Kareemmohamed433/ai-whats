import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import api, { resolveMediaUrl } from '../services/api';
import { socket } from '../services/socket';
import { useAuth } from '../context/AuthContext';
import { playNotificationChime } from '../services/notificationService';
import {
  Search,
  Send,
  Bot,
  UserCheck,
  Sparkles,
  RefreshCw,
  Pin,
  Clock,
  ShoppingBag,
  FileText,
  Activity,
  ChevronRight,
  ChevronLeft,
  AlertTriangle,
  X,
  Phone,
  MessageSquare,
  ShieldCheck,
  Check,
  CheckCheck,
  Paperclip,
  Download,
  Image as ImageIcon,
  Film,
  UploadCloud
} from 'lucide-react';

// Safe helpers: the backend may return objects where the UI expects strings/arrays
const toArray = (v) => (Array.isArray(v) ? v : []);
const toText = (v) => {
  if (v === null || v === undefined) return '';
  if (typeof v === 'string' || typeof v === 'number') return String(v);
  if (typeof v === 'object') return v.response_text || v.content || v.title || v.name || v.text || '';
  return String(v);
};

function ImageAttachmentPreview({ src, alt, downloadUrl, onClick, className = '' }) {
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const imgRef = useRef(null);

  const resolvedSrc = resolveMediaUrl(src);
  const resolvedDownload = resolveMediaUrl(downloadUrl || src);

  // Reset state whenever the image source changes
  useEffect(() => {
    setHasError(false);
    setIsLoading(true);
  }, [resolvedSrc]);

  // Handle images that finished loading from cache before React attached onLoad
  useEffect(() => {
    const el = imgRef.current;
    if (el && el.complete && el.naturalWidth > 0) {
      setIsLoading(false);
    }
  }, [resolvedSrc]);

  if (!resolvedSrc || hasError) {
    return (
      <div className="flex flex-col items-center justify-center p-3 rounded-xl bg-black/20 dark:bg-white/5 border border-black/10 dark:border-white/10 text-center gap-2 text-xs">
        <div className="flex items-center gap-1.5 text-amber-300">
          <ImageIcon className="w-4 h-4 opacity-75 shrink-0" />
          <span className="font-medium truncate max-w-[180px] sm:max-w-xs">{alt || 'صورة مرفقة'}</span>
        </div>
        <p className="text-[11px] opacity-75">تعذر تحميل المعاينة المباشرة</p>
        {resolvedDownload ? (
          <a
            href={resolvedDownload}
            download={alt || 'image'}
            target="_blank"
            rel="noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="inline-flex items-center gap-1.5 px-3 py-1 bg-white/20 hover:bg-white/30 text-white rounded-lg text-xs transition"
          >
            <Download className="w-3.5 h-3.5" />
            <span>تحميل الصورة</span>
          </a>
        ) : null}
      </div>
    );
  }

  return (
    <div className="relative group rounded-xl overflow-hidden max-h-60 bg-black/10 border border-black/10">
      {isLoading && (
        <div className="w-full h-36 bg-black/10 dark:bg-white/5 animate-pulse flex items-center justify-center text-xs opacity-60">
          <ImageIcon className="w-5 h-5 opacity-40 mr-1 animate-pulse" />
          <span>جاري التحميل...</span>
        </div>
      )}
      {/*
        FIX: no loading="lazy" and no display:none while loading.
        A lazy image with display:none is never fetched by the browser,
        so onLoad never fires and the placeholder stays forever.
        We hide it visually (absolute + opacity-0) instead.
      */}
      <img
        ref={imgRef}
        src={resolvedSrc}
        alt={alt || 'صورة مرفقة'}
        onLoad={() => setIsLoading(false)}
        onError={() => {
          setIsLoading(false);
          setHasError(true);
        }}
        onClick={() => {
          if (onClick) onClick(resolvedSrc, alt);
        }}
        className={`w-full h-auto object-cover max-h-60 cursor-pointer hover:scale-[1.02] transition duration-200 ${isLoading ? 'absolute inset-0 opacity-0 pointer-events-none' : 'block'
          } ${className}`}
      />
      {!isLoading && resolvedDownload && (
        <div className="absolute top-2 left-2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition">
          <a
            href={resolvedDownload}
            download={alt || 'image'}
            className="p-1.5 bg-black/70 hover:bg-black text-white rounded-lg text-xs flex items-center gap-1"
            title="تحميل الصورة"
            onClick={(e) => e.stopPropagation()}
          >
            <Download className="w-3.5 h-3.5" />
          </a>
        </div>
      )}
    </div>
  );
}

export default function InboxPage() {
  const { user: currentUser } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const targetConvIdFromUrl = searchParams.get('conversationId');

  const [conversations, setConversations] = useState([]);
  const [selectedConv, setSelectedConv] = useState(null);
  const [messages, setMessages] = useState([]);
  const [pinnedMessages, setPinnedMessages] = useState([]);
  const [quickReplies, setQuickReplies] = useState([]);
  const [suggestedReplies, setSuggestedReplies] = useState([]);

  // Mobile View state: 'list' (conversation list) or 'chat' (active chat thread)
  const [mobileView, setMobileView] = useState('list');

  // Drafts per conversation ID (Preserves message drafts during navigation)
  const [drafts, setDrafts] = useState({});

  // Filters
  const [filter, setFilter] = useState('all');
  const [platformFilter, setPlatformFilter] = useState('');
  const [search, setSearch] = useState('');

  // UI state
  const [inputText, setInputText] = useState('');
  const [showShortcutMenu, setShowShortcutMenu] = useState(false);
  const [showCustomer360, setShowCustomer360] = useState(false); // Mobile drawer / desktop panel
  const [customer360Data, setCustomer360Data] = useState(null);
  const [newNoteText, setNewNoteText] = useState('');
  const [agents, setAgents] = useState([]);
  const [loadingConvs, setLoadingConvs] = useState(true);
  const [sending, setSending] = useState(false);
  const [pendingAttachments, setPendingAttachments] = useState([]);
  const [uploadingAttachment, setUploadingAttachment] = useState(false);
  const [isDraggingOver, setIsDraggingOver] = useState(false);
  const [previewModalUrl, setPreviewModalUrl] = useState(null);
  const [previewModalName, setPreviewModalName] = useState('');

  const messagesEndRef = useRef(null);
  const chatScrollRef = useRef(null);
  const fileInputRef = useRef(null);


  // Latest-value refs (avoid stale closures in async callbacks / socket handlers)
  const selectedConvRef = useRef(null);
  const inputTextRef = useRef('');
  const draftsRef = useRef({});
  const urlConvHandledRef = useRef(false);
  selectedConvRef.current = selectedConv;
  inputTextRef.current = inputText;
  draftsRef.current = drafts;

  useEffect(() => {
    api.get('/users').then(res => {
      if (res.success) setAgents(toArray(res.users));
    }).catch(() => { });

    fetchQuickReplies();

    // Listen for Service Worker navigation events
    const handleSwMessage = (event) => {
      if (event.data && event.data.type === 'SELECT_CONVERSATION') {
        loadConversationDetail(event.data.conversationId);
        setMobileView('chat');
      }
    };
    if (navigator.serviceWorker) {
      navigator.serviceWorker.addEventListener('message', handleSwMessage);
      return () => navigator.serviceWorker.removeEventListener('message', handleSwMessage);
    }
  }, []);

  const fetchQuickReplies = async () => {
    try {
      const res = await api.get('/quick-replies');
      if (res.success) setQuickReplies(toArray(res.quick_replies));
    } catch (err) { }
  };

  const loadConversations = useCallback(() => {
    let url = `/conversations?filter=${filter}&search=${encodeURIComponent(search)}`;
    if (platformFilter) url += `&platform=${platformFilter}`;

    api.get(url).then(res => {
      if (res && res.success) {
        const list = toArray(res.conversations);
        setConversations(list);

        // Auto-select conversation from URL param (only once, not on every refresh)
        if (targetConvIdFromUrl && !urlConvHandledRef.current) {
          const matched = list.find(c => String(c.id) === String(targetConvIdFromUrl));
          if (matched) {
            urlConvHandledRef.current = true;
            loadConversationDetail(matched.id);
            setMobileView('chat');
            return;
          }
        }

        // On desktop, auto-select first conversation if none selected
        if (!selectedConvRef.current && list.length > 0 && window.innerWidth >= 768) {
          loadConversationDetail(list[0].id);
        }
      }
    }).catch(err => console.error(err))
      .finally(() => setLoadingConvs(false));
  }, [filter, platformFilter, search, targetConvIdFromUrl]);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  // Keep a ref to the latest loadConversations for socket handlers
  const loadConversationsRef = useRef(loadConversations);
  loadConversationsRef.current = loadConversations;

  const loadConversationDetail = (id) => {
    api.get(`/conversations/${id}`).then(res => {
      if (res && res.success && res.conversation) {
        // Save draft of the previously selected conversation
        const prev = selectedConvRef.current;
        const nextDrafts = { ...draftsRef.current };
        if (prev && prev.id !== res.conversation.id) {
          nextDrafts[prev.id] = inputTextRef.current;
          setDrafts(nextDrafts);
        }

        setSelectedConv(res.conversation);
        setMessages(toArray(res.conversation.messages));
        loadPinnedMessages(id);
        loadCustomer360(res.conversation.customer_id);
        loadSuggestedReplies(id);

        // Restore draft for the newly selected conversation
        setInputText(nextDrafts[res.conversation.id] || '');
      }
    }).catch(err => console.error(err));
  };

  const loadPinnedMessages = (convId) => {
    api.get(`/conversations/${convId}/pinned`).then(res => {
      if (res.success) setPinnedMessages(toArray(res.pinned_messages));
    }).catch(() => { });
  };

  const loadCustomer360 = (customerId) => {
    if (!customerId) return;
    api.get(`/customers/${customerId}`).then(res => {
      if (res.success) setCustomer360Data(res.customer);
    }).catch(() => { });
  };

  const loadSuggestedReplies = (convId) => {
    api.get(`/quick-replies/suggested?conversation_id=${convId}`).then(res => {
      if (res.success) setSuggestedReplies(toArray(res.suggested));
    }).catch(() => { });
  };

  // Real-time Socket.IO Listeners
  useEffect(() => {
    const handleNewMessage = (data) => {
      if (selectedConv && data && data.message && data.conversation_id === selectedConv.id) {
        setMessages(prev => {
          if (prev.some(m => m.id === data.message.id)) return prev;
          return [...prev, data.message];
        });
      }
      loadConversationsRef.current();
    };

    const handleHumanHandoff = (data) => {
      playNotificationChime();
      loadConversationsRef.current();
    };

    const handleConversationUpdated = (data) => {
      if (!data || !data.conversation) return;
      if (selectedConv && data.conversation.id === selectedConv.id) {
        setSelectedConv(prev => ({ ...prev, ...data.conversation }));
      }
      setConversations(prev => prev.map(c => c.id === data.conversation.id ? { ...c, ...data.conversation } : c));
    };

    const handleStatusChanged = (data) => {
      if (selectedConv && data.conversation_id === selectedConv.id && data.conversation) {
        setSelectedConv(prev => ({ ...prev, ...data.conversation }));
      }
      loadConversationsRef.current();
    };

    socket.on('new_message', handleNewMessage);
    socket.on('agent_message', handleNewMessage);
    socket.on('conversation_updated', handleConversationUpdated);
    socket.on('conversation_status_changed', handleStatusChanged);
    socket.on('ai_status_changed', handleStatusChanged);
    socket.on('human_handoff', handleHumanHandoff);

    return () => {
      socket.off('new_message', handleNewMessage);
      socket.off('agent_message', handleNewMessage);
      socket.off('conversation_updated', handleConversationUpdated);
      socket.off('conversation_status_changed', handleStatusChanged);
      socket.off('ai_status_changed', handleStatusChanged);
      socket.off('human_handoff', handleHumanHandoff);
    };
  }, [selectedConv]);

  // Scroll to bottom when new messages arrive without jumping view
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // File Attachments Management
  const handleFileSelect = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    await uploadFiles(Array.from(files));
    e.target.value = '';
  };

  const uploadFiles = async (fileList) => {
    if (!fileList || fileList.length === 0) return;
    setUploadingAttachment(true);
    for (const file of fileList) {
      const formData = new FormData();
      formData.append('file', file);
      if (selectedConv) {
        formData.append('conversation_id', selectedConv.id);
      }
      try {
        const res = await api.post('/attachments/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        if (res && res.success && res.attachment) {
          setPendingAttachments(prev => [...prev, res.attachment]);
        }
      } catch (err) {
        alert(err.message || `فشل رفع الملف: ${file.name}`);
      }
    }
    setUploadingAttachment(false);
  };

  const removePendingAttachment = (index) => {
    setPendingAttachments(prev => prev.filter((_, i) => i !== index));
  };

  // Send human message (Supports text, attachments, or both)
  const handleSendMessage = (e) => {
    e?.preventDefault();
    if ((!inputText.trim() && pendingAttachments.length === 0) || !selectedConv || sending || uploadingAttachment) return;

    const messageText = inputText.trim();
    const attachmentsToSend = [...pendingAttachments];
    setSending(true);

    api.post('/messages', {
      conversation_id: selectedConv.id,
      content: messageText,
      attachments: attachmentsToSend
    }).then(res => {
      if (res.success) {
        setMessages(prev => (res.message && !prev.some(m => m.id === res.message.id) ? [...prev, res.message] : prev));
        setInputText('');
        setPendingAttachments([]);
        // Clear saved draft for this conversation
        setDrafts(prev => {
          const copy = { ...prev };
          delete copy[selectedConv.id];
          return copy;
        });
      }
    }).catch(err => {
      alert(err.message || 'فشل إرسال الرسالة');
    }).finally(() => {
      setSending(false);
    });
  };


  // Status updates: Human handoff, AI reactivation, Close
  const handleStatusUpdate = (newConvStatus, newAiStatus) => {
    if (!selectedConv) return;
    api.put(`/conversations/${selectedConv.id}/status`, {
      conversation_status: newConvStatus,
      ai_status: newAiStatus
    }).then(res => {
      if (res.success) {
        setSelectedConv(prev => ({ ...prev, ...res.conversation }));
        loadConversations();
      }
    }).catch(err => alert(err.message || 'فشل تحديث الحالة'));
  };

  const handleAssignAgent = (agentId) => {
    if (!selectedConv) return;
    api.put(`/conversations/${selectedConv.id}/assign`, {
      agent_id: agentId || null
    }).then(res => {
      if (res.success) {
        setSelectedConv(prev => ({ ...prev, assigned_agent_id: agentId }));
        loadConversations();
      }
    }).catch(err => alert(err.message || 'فشل تعيين الموظف'));
  };

  const handleAddNote = (e) => {
    e.preventDefault();
    if (!newNoteText.trim() || !customer360Data) return;
    api.post(`/customers/${customer360Data.id}/notes`, {
      note_text: newNoteText
    }).then(res => {
      if (res.success) {
        setNewNoteText('');
        loadCustomer360(customer360Data.id);
      }
    }).catch(err => alert(err.message || 'فشل حفظ الملاحظة'));
  };

  // Quick reply input handling
  const handleInputChange = (e) => {
    const val = e.target.value;
    setInputText(val);
    if (selectedConv) {
      setDrafts(prev => ({ ...prev, [selectedConv.id]: val }));
    }
    if (val.startsWith('/')) {
      setShowShortcutMenu(true);
    } else {
      setShowShortcutMenu(false);
    }
  };

  const handleSelectQuickReply = (text) => {
    setInputText(text);
    if (selectedConv) {
      setDrafts(prev => ({ ...prev, [selectedConv.id]: text }));
    }
    setShowShortcutMenu(false);
  };

  // Channel badge helper
  const getChannelBadge = (platform) => {
    const badges = {
      whatsapp: { label: 'واتساب', color: 'bg-emerald-500 text-white' },
      telegram: { label: 'تيليجرام', color: 'bg-sky-500 text-white' },
      instagram: { label: 'إنستغرام', color: 'bg-pink-600 text-white' },
      messenger: { label: 'ماسنجر', color: 'bg-blue-600 text-white' },
      tiktok: { label: 'تيك توك', color: 'bg-slate-900 text-white' }
    };
    return badges[platform] || { label: platform, color: 'bg-slate-700 text-white' };
  };

  return (
    <div className="flex-1 flex h-full w-full bg-white dark:bg-slate-900 rounded-none md:rounded-2xl border-0 md:border border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden relative">

      {/* ======================================================== */}
      {/* 1. CONVERSATION LIST (Full-width on Mobile if list view)  */}
      {/* ======================================================== */}
      <div className={`
        ${mobileView === 'list' ? 'flex' : 'hidden md:flex'}
        w-full md:w-80 lg:w-96 flex-col h-full bg-slate-50/70 dark:bg-slate-900/70 border-l border-slate-200 dark:border-slate-800 shrink-0
      `}>
        {/* Top Header & Search */}
        <div className="p-3.5 border-b border-slate-200 dark:border-slate-800 space-y-2.5">
          <div className="flex items-center justify-between">
            <h2 className="font-extrabold text-sm text-slate-900 dark:text-white flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-blue-600 dark:text-cyan-400" />
              <span>صندوق المحادثات</span>
              <span className="text-[10px] bg-blue-100 dark:bg-blue-950 text-blue-600 dark:text-blue-400 font-extrabold px-2 py-0.5 rounded-full">
                {conversations.length}
              </span>
            </h2>
            <button
              onClick={loadConversations}
              aria-label="تحديث المحادثات"
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-white hover:bg-slate-200 dark:hover:bg-slate-800 transition"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loadingConvs ? 'animate-spin text-blue-600' : ''}`} />
            </button>
          </div>

          {/* Search Input */}
          <div className="relative">
            <Search className="w-4 h-4 absolute right-3 top-2.5 text-slate-400" />
            <input
              type="text"
              name="conversation-search"
              id="conversation-search"
              placeholder="بحث بالاسم، الهاتف، المنصة..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pr-9 pl-3 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white placeholder-slate-400 focus:outline-hidden focus:border-blue-500 transition"
            />
          </div>

          {/* Filter Chips */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-[11px] font-semibold no-scrollbar">
            {[
              { id: 'all', name: 'الكل' },
              { id: 'unread', name: 'غير مقروء' },
              { id: 'human_requests', name: '🚨 طلب موظف' },
              { id: 'ai', name: '🤖 AI نشط' },
              { id: 'human', name: '👤 مستلم بشرياً' },
              { id: 'open', name: 'مفتوحة' },
              { id: 'closed', name: 'مغلقة' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setFilter(tab.id)}
                className={`px-2.5 py-1 rounded-lg transition whitespace-nowrap text-xs font-bold ${filter === tab.id
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'bg-white dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400'
                  }`}
              >
                {tab.name}
              </button>
            ))}
          </div>

          {/* Platform Filters */}
          <div className="flex items-center gap-1.5 overflow-x-auto text-[10px] no-scrollbar">
            {[
              { id: '', name: 'جميع القنوات' },
              { id: 'whatsapp', name: 'WhatsApp' },
              { id: 'telegram', name: 'Telegram' },
              { id: 'instagram', name: 'Instagram' },
              { id: 'messenger', name: 'Messenger' }
            ].map(p => (
              <button
                key={p.id}
                onClick={() => setPlatformFilter(p.id)}
                className={`px-2 py-0.5 rounded-md transition whitespace-nowrap font-medium ${platformFilter === p.id
                  ? 'bg-slate-800 dark:bg-slate-200 text-white dark:text-slate-900 font-bold'
                  : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-300'
                  }`}
              >
                {p.name}
              </button>
            ))}
          </div>
        </div>

        {/* Conversation Cards List */}
        <div className="flex-1 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-800/60">
          {loadingConvs ? (
            <div className="flex flex-col items-center justify-center py-16 space-y-3">
              <div className="w-7 h-7 border-3 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
              <p className="text-xs text-slate-400 font-medium">جاري تحميل المحادثات...</p>
            </div>
          ) : conversations.length === 0 ? (
            <div className="text-center py-16 text-slate-400 text-xs space-y-1">
              <p className="font-bold">لا توجد محادثات مطابقة للفلاتر</p>
              <p className="text-[11px] opacity-75">ستظهر المحادثات الجديدة فور إرسال العملاء رسائل.</p>
            </div>
          ) : (
            conversations.map((conv) => {
              const isSelected = selectedConv?.id === conv.id;
              const customerName = toText(conv.customer?.name) || 'عميل جديد';
              const lastMsgText = toText(conv.last_message) || 'بدء المحادثة';
              const badge = getChannelBadge(conv.platform);
              const hasDraft = !!drafts[conv.id];

              return (
                <div
                  key={conv.id}
                  onClick={() => {
                    loadConversationDetail(conv.id);
                    setMobileView('chat');
                  }}
                  className={`p-3 sm:p-3.5 cursor-pointer transition flex items-start gap-3 relative select-none ${isSelected
                    ? 'bg-blue-500/10 dark:bg-blue-950/40 border-r-4 border-blue-600'
                    : 'hover:bg-slate-100/70 dark:hover:bg-slate-800/50'
                    }`}
                >
                  <div className="relative shrink-0">
                    <img
                      src={conv.customer?.avatar || `https://ui-avatars.com/api/?name=${customerName}&background=1E6BFF&color=fff`}
                      alt={customerName}
                      className="w-11 h-11 rounded-full object-cover border border-slate-200 dark:border-slate-700 shadow-xs"
                    />
                    <span className={`absolute -bottom-1 -right-1 text-[9px] px-1.5 py-0.2 rounded-full font-bold shadow-xs ${badge.color}`}>
                      {badge.label}
                    </span>
                  </div>

                  <div className="flex-1 min-w-0 space-y-1">
                    <div className="flex items-center justify-between gap-1">
                      <h4 className="font-bold text-xs text-slate-900 dark:text-white truncate">
                        {customerName}
                      </h4>
                      <span className="text-[10px] text-slate-400 shrink-0 font-mono">
                        {conv.last_message_at ? new Date(conv.last_message_at).toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' }) : ''}
                      </span>
                    </div>

                    <p className="text-[11px] text-slate-500 dark:text-slate-400 truncate leading-relaxed">
                      {hasDraft ? <span className="text-amber-500 font-bold ml-1">[مسودة]</span> : null}
                      {lastMsgText}
                    </p>

                    {/* Status Tags */}
                    <div className="flex items-center gap-1.5 pt-0.5 flex-wrap">
                      <span className={`text-[9px] font-extrabold px-1.5 py-0.5 rounded-md ${conv.ai_status === 'active'
                        ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400'
                        : conv.ai_status === 'human_handled'
                          ? 'bg-amber-100 dark:bg-amber-950 text-amber-600 dark:text-amber-400'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-500'
                        }`}>
                        {conv.ai_status === 'active' ? '🤖 AI نشط' : conv.ai_status === 'human_handled' ? '👤 موظف' : '⚪ معطل'}
                      </span>

                      {conv.requires_human && (
                        <span className="text-[9px] font-extrabold px-1.5 py-0.5 rounded-md bg-rose-100 dark:bg-rose-950 text-rose-600 dark:text-rose-400 flex items-center gap-0.5 animate-pulse">
                          <AlertTriangle className="w-2.5 h-2.5" /> طلب موظف
                        </span>
                      )}
                    </div>
                  </div>

                  {conv.unread_count > 0 && (
                    <span className="w-5 h-5 rounded-full bg-blue-600 text-white font-extrabold text-[10px] flex items-center justify-center shrink-0 shadow-xs">
                      {conv.unread_count}
                    </span>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* ======================================================== */}
      {/* 2. ACTIVE CHAT THREAD (Full-width on Mobile in chat view) */}
      {/* ======================================================== */}
      {selectedConv ? (
        <div className={`
          ${mobileView === 'chat' ? 'flex' : 'hidden md:flex'}
          flex-1 flex-col h-full bg-white dark:bg-slate-900 min-w-0 overflow-hidden relative
        `}>

          {/* Mobile & Desktop Header */}
          <div className="p-3 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between gap-2 bg-slate-50/80 dark:bg-slate-900/80 backdrop-blur-md shrink-0">
            <div className="flex items-center gap-2 sm:gap-3 min-w-0">
              {/* Mobile Back Button: Returns to Conversation List View */}
              <button
                onClick={() => setMobileView('list')}
                className="md:hidden flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 text-xs font-bold hover:bg-slate-200 transition shrink-0"
                aria-label="العودة لصندوق المحادثات"
              >
                <ChevronRight className="w-4 h-4 rtl:rotate-0 ltr:rotate-180" />
                <span>المحادثات</span>
              </button>

              <img
                src={selectedConv.customer?.avatar || `https://ui-avatars.com/api/?name=${selectedConv.customer?.name}&background=1E6BFF&color=fff`}
                alt={selectedConv.customer?.name}
                className="w-9 h-9 sm:w-10 sm:h-10 rounded-full object-cover border border-slate-200 dark:border-slate-700 shrink-0"
              />

              <div className="min-w-0">
                <div className="flex items-center gap-1.5">
                  <h3 className="font-bold text-xs sm:text-sm text-slate-900 dark:text-white truncate">
                    {toText(selectedConv.customer?.name) || 'عميل'}
                  </h3>
                  <span className={`text-[9px] font-bold px-1.5 py-0.2 rounded-full capitalize ${getChannelBadge(selectedConv.platform).color}`}>
                    {toText(selectedConv.platform)}
                  </span>
                </div>

                <div className="flex items-center gap-1.5 text-[10px] sm:text-xs">
                  <span className={`font-bold ${selectedConv.ai_status === 'active' ? 'text-emerald-500' : 'text-amber-500'
                    }`}>
                    {selectedConv.ai_status === 'active' ? '🟢 AI نشط' : '🟠 موظف'}
                  </span>
                  <span className="text-slate-400">•</span>
                  <span className="text-slate-500 capitalize">{selectedConv.conversation_status}</span>
                </div>
              </div>
            </div>

            {/* Action Bar Controls */}
            <div className="flex items-center gap-1.5 shrink-0">
              {/* Quick AI Toggle */}
              {selectedConv.ai_status === 'active' ? (
                <button
                  onClick={() => handleStatusUpdate('open', 'human_handled')}
                  title="استلام المحادثة وإيقاف الرد الآلي مؤقتاً"
                  className="px-2.5 py-1.5 bg-amber-500/10 hover:bg-amber-500/20 text-amber-700 dark:text-amber-300 border border-amber-500/30 rounded-xl text-xs font-bold transition flex items-center gap-1"
                >
                  <UserCheck className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">تحويل لموظف</span>
                </button>
              ) : (
                <button
                  onClick={() => handleStatusUpdate('open', 'active')}
                  title="إعادة تشغيل الذكاء الاصطناعي للمحادثة"
                  className="px-2.5 py-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30 rounded-xl text-xs font-bold transition flex items-center gap-1"
                >
                  <Bot className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">تفعيل AI</span>
                </button>
              )}

              {/* Close Conversation */}
              <button
                onClick={() => handleStatusUpdate('closed', 'active')}
                title="إغلاق المحادثة وإعادة تفعيل AI"
                className="px-2.5 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-xl text-xs font-bold transition hidden sm:inline-flex"
              >
                🔒 إغلاق
              </button>

              {/* Customer 360 Toggle Button */}
              <button
                onClick={() => setShowCustomer360(!showCustomer360)}
                title="بيانات العميل 360"
                className={`p-1.5 sm:px-2.5 sm:py-1.5 rounded-xl text-xs font-bold flex items-center gap-1 transition ${showCustomer360
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200'
                  }`}
              >
                <Phone className="w-3.5 h-3.5" />
                <span className="hidden md:inline">العميل 360</span>
              </button>
            </div>
          </div>

          {/* Pinned Messages Banner */}
          {pinnedMessages.length > 0 && (
            <div className="bg-amber-500/10 border-b border-amber-500/20 py-2 px-3 flex items-center justify-between text-xs text-amber-800 dark:text-amber-300 shrink-0">
              <div className="flex items-center gap-2 overflow-x-auto min-w-0">
                <Pin className="w-3.5 h-3.5 text-amber-600 shrink-0 fill-amber-600" />
                <span className="font-bold shrink-0">مثبت:</span>
                <span className="truncate">{toText(pinnedMessages[0]?.message?.content ?? pinnedMessages[0]?.message ?? pinnedMessages[0])}</span>
              </div>
            </div>
          )}

          {/* Messages Scroll Area with Drag & Drop */}
          <div
            ref={chatScrollRef}
            onDragOver={(e) => { e.preventDefault(); setIsDraggingOver(true); }}
            onDragLeave={(e) => { e.preventDefault(); setIsDraggingOver(false); }}
            onDrop={(e) => {
              e.preventDefault();
              setIsDraggingOver(false);
              if (e.dataTransfer?.files?.length > 0) {
                uploadFiles(Array.from(e.dataTransfer.files));
              }
            }}
            className="flex-1 overflow-y-auto p-3 sm:p-4 space-y-3.5 bg-slate-50/40 dark:bg-slate-950/40 relative"
          >
            {/* Drag Overlay indicator */}
            {isDraggingOver && (
              <div className="absolute inset-0 z-40 bg-blue-600/20 backdrop-blur-xs border-2 border-dashed border-blue-500 rounded-2xl flex flex-col items-center justify-center text-blue-600 dark:text-blue-300 font-bold text-sm pointer-events-none">
                <UploadCloud className="w-12 h-12 mb-2 animate-bounce" />
                <span>أفلت الملفات هنا لإرفاقها بالمحادثة</span>
              </div>
            )}

            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20 text-slate-400 space-y-2">
                <MessageSquare className="w-8 h-8 opacity-40 text-blue-500" />
                <p className="text-xs font-medium">لا توجد رسائل سابقة في هذه المحادثة.</p>
              </div>
            ) : (
              messages.map((m) => {
                const isCustomer = m.sender_type === 'customer';
                const isAi = m.sender_type === 'ai';
                const isAgent = m.sender_type === 'agent';

                return (
                  <div
                    key={m.id}
                    className={`flex flex-col ${isCustomer ? 'items-start' : 'items-end'}`}
                  >
                    {/* Sender Label */}
                    <div className="flex items-center gap-1.5 mb-1 text-[10px] text-slate-400 px-1 font-medium">
                      <span>{isCustomer ? (selectedConv.customer?.name || 'العميل') : isAi ? '🤖 BLACK & WHITE AI' : `👤 ${m.sender_name || 'موظف الدعم'}`}</span>
                      <span>•</span>
                      <span className="font-mono">{m.created_at ? new Date(m.created_at).toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' }) : ''}</span>
                    </div>

                    {/* Message Bubble */}
                    <div
                      className={`max-w-[85%] sm:max-w-md p-3 rounded-2xl text-xs sm:text-sm leading-relaxed shadow-xs break-words whitespace-pre-wrap ${isCustomer
                        ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 rounded-tr-xs border border-slate-200/80 dark:border-slate-700/80'
                        : isAi
                          ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-tl-xs shadow-blue-600/20'
                          : 'bg-emerald-600 text-white rounded-tl-xs shadow-emerald-600/20'
                        }`}
                      dir="auto"
                    >
                      {/* Attachments rendering */}
                      {m.attachments && m.attachments.length > 0 && (
                        <div className="space-y-2 mb-2">
                          {m.attachments.map(att => {
                            const isImage = att.file_type === 'image' || att.mime_type?.startsWith('image/');
                            const isVideo = att.file_type === 'video' || att.mime_type?.startsWith('video/');
                            const previewUrl = att.file_url || (att.storage_key ? `/api/attachments/preview/${att.storage_key}` : `/api/attachments/${att.id}/preview`);
                            const downloadUrl = att.storage_key ? `/api/attachments/download/${att.storage_key}` : `/api/attachments/${att.id}/download`;

                            if (isImage) {
                              return (
                                <ImageAttachmentPreview
                                  key={att.id}
                                  src={previewUrl}
                                  alt={att.file_name || 'صورة مرفقة'}
                                  downloadUrl={downloadUrl}
                                  onClick={(resolvedSrc, name) => {
                                    setPreviewModalUrl(resolvedSrc);
                                    setPreviewModalName(name || att.file_name || 'صورة مرفقة');
                                  }}
                                />
                              );
                            }

                            if (isVideo) {
                              return (
                                <div key={att.id} className="rounded-xl overflow-hidden bg-black/20 max-w-full">
                                  <video src={resolveMediaUrl(previewUrl)} controls className="w-full max-h-60 rounded-xl" />
                                </div>
                              );
                            }

                            return (
                              <div key={att.id} className="flex items-center justify-between p-2.5 bg-black/10 dark:bg-white/5 rounded-xl border border-black/10 dark:border-white/10 gap-3 text-xs">
                                <div className="flex items-center gap-2 min-w-0">
                                  <div className="p-2 bg-blue-500/20 text-blue-300 rounded-lg shrink-0">
                                    <FileText className="w-4 h-4" />
                                  </div>
                                  <div className="min-w-0">
                                    <p className="font-semibold truncate max-w-[160px] sm:max-w-xs">{att.file_name || 'مستند مرفق'}</p>
                                    <p className="text-[10px] opacity-70">
                                      {att.file_size ? `${(att.file_size / 1024).toFixed(1)} KB` : ''}
                                    </p>
                                  </div>
                                </div>
                                <a
                                  href={resolveMediaUrl(downloadUrl)}
                                  download={att.file_name || 'document'}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="p-1.5 bg-white/20 hover:bg-white/30 rounded-lg text-xs flex items-center gap-1 shrink-0"
                                  title="تحميل الملف"
                                >
                                  <Download className="w-3.5 h-3.5" />
                                  <span className="hidden sm:inline">تحميل</span>
                                </a>
                              </div>
                            );
                          })}
                        </div>
                      )}

                      {/* Standalone media_url if no attachments array */}
                      {(!m.attachments || m.attachments.length === 0) && m.media_url && (
                        <div className="mb-2">
                          <ImageAttachmentPreview
                            src={m.media_url}
                            alt="مرفق"
                            onClick={(resolvedSrc, name) => {
                              setPreviewModalUrl(resolvedSrc);
                              setPreviewModalName(name || 'مرفق');
                            }}
                          />
                        </div>
                      )}

                      <div>{toText(m.content)}</div>

                      {/* Delivery Status Indicator */}
                      {!isCustomer && (
                        <div className="flex items-center justify-end gap-1 mt-1 text-[9px] opacity-80 font-mono">
                          {m.status === 'sent' || m.status === 'delivered' ? (
                            <CheckCheck className="w-3 h-3 text-cyan-200" />
                          ) : (
                            <Check className="w-3 h-3 text-white/70" />
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })
            )}
            <div ref={messagesEndRef} />
          </div>


          {/* AI Suggested Replies Chips */}
          {suggestedReplies.length > 0 && (
            <div className="px-3 py-1.5 bg-blue-50/70 dark:bg-blue-950/30 border-t border-blue-100 dark:border-blue-900/40 flex items-center gap-2 overflow-x-auto no-scrollbar shrink-0">
              <span className="text-[10px] font-bold text-blue-600 dark:text-cyan-400 flex items-center gap-1 shrink-0">
                <Sparkles className="w-3 h-3" /> اقتراحات AI:
              </span>
              {suggestedReplies.map((sug, idx) => {
                const text = toText(sug);
                const label = typeof sug === 'string' ? sug : (toText(sug?.title) || toText(sug?.shortcut) || text);
                return (
                  <button
                    key={typeof sug === 'object' && sug?.id != null ? sug.id : idx}
                    onClick={() => handleSelectQuickReply(text)}
                    title={text}
                    className="px-2.5 py-1 bg-white dark:bg-slate-800 border border-blue-200 dark:border-blue-800 rounded-lg text-xs text-blue-700 dark:text-cyan-300 whitespace-nowrap hover:bg-blue-100 transition shrink-0 font-medium"
                  >
                    {label}
                  </button>
                );
              })}
            </div>
          )}

          {/* Message Composer (Safe for mobile virtual keyboards) */}
          <div className="p-2.5 sm:p-3 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shrink-0 safe-bottom">
            {/* Shortcuts Dropdown popup */}
            {showShortcutMenu && quickReplies.length > 0 && (
              <div className="mb-2 p-2 bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-slate-200 dark:border-slate-700 max-h-40 overflow-y-auto space-y-1">
                {quickReplies.map(qr => (
                  <div
                    key={qr.id}
                    onClick={() => handleSelectQuickReply(qr.response_text)}
                    className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg cursor-pointer flex items-center justify-between text-xs"
                  >
                    <span className="font-bold text-blue-600 font-mono">{qr.shortcut}</span>
                    <span className="text-slate-600 dark:text-slate-300 text-[11px] truncate max-w-[200px]">{qr.title}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Pending Attachments Strip */}
            {pendingAttachments.length > 0 && (
              <div className="mb-2 p-2 bg-blue-50/80 dark:bg-blue-950/40 rounded-xl border border-blue-200 dark:border-blue-900/50 flex items-center gap-2 overflow-x-auto">
                <span className="text-[11px] font-bold text-blue-700 dark:text-blue-300 shrink-0">المرفقات:</span>
                {pendingAttachments.map((att, idx) => (
                  <div key={idx} className="flex items-center gap-1.5 px-2.5 py-1 bg-white dark:bg-slate-800 border border-blue-200 dark:border-blue-800 rounded-lg text-xs shrink-0">
                    <FileText className="w-3.5 h-3.5 text-blue-500" />
                    <span className="font-medium truncate max-w-[120px]">{att.file_name}</span>
                    <button
                      type="button"
                      onClick={() => removePendingAttachment(idx)}
                      className="p-0.5 text-slate-400 hover:text-red-500 rounded-full"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Hidden File Input */}
            <input
              type="file"
              name="attachment-file"
              id="attachment-file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              multiple
              className="hidden"
              accept="image/*,video/*,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.csv,.ai,.psd,.eps,.zip"
            />

            {/* Input & Send Form */}
            <form onSubmit={handleSendMessage} className="flex items-center gap-2">
              {/* Attachment Picker Button */}
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploadingAttachment}
                title="إرفاق ملف (صور، مستندات، تصاميم، فيديو)"
                className="p-2.5 sm:p-3 text-slate-500 hover:text-blue-600 dark:text-slate-400 dark:hover:text-blue-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition shrink-0"
              >
                {uploadingAttachment ? (
                  <RefreshCw className="w-4 h-4 animate-spin text-blue-500" />
                ) : (
                  <Paperclip className="w-4 h-4" />
                )}
              </button>

              <input
                type="text"
                name="message-input"
                id="message-input"
                placeholder="اكتب ردك هنا... (اكتب / للردود السريعة أو أرفق ملفات)"
                value={inputText}
                onChange={handleInputChange}
                // text-base on mobile prevents iOS automatic viewport zoom!
                className="flex-1 p-2.5 sm:p-3 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-base sm:text-xs text-slate-900 dark:text-white placeholder-slate-400 focus:outline-hidden focus:border-blue-500 transition"
              />

              <button
                type="submit"
                disabled={sending || uploadingAttachment || (!inputText.trim() && pendingAttachments.length === 0)}
                className="px-4 sm:px-5 py-2.5 sm:py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs sm:text-sm font-bold transition flex items-center gap-1.5 shadow-md shadow-blue-600/20 disabled:opacity-50 shrink-0"
              >
                {sending ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4 rtl:rotate-180" />
                )}
                <span className="hidden sm:inline">إرسال</span>
              </button>
            </form>
          </div>


        </div>
      ) : (
        <div className="hidden md:flex flex-1 flex-col items-center justify-center p-8 text-center text-slate-400 space-y-3">
          <div className="w-16 h-16 rounded-2xl bg-blue-50 dark:bg-blue-950/40 flex items-center justify-center text-blue-500">
            <MessageSquare className="w-8 h-8" />
          </div>
          <h3 className="font-bold text-base text-slate-800 dark:text-slate-200">صندوق محادثات Black & White</h3>
          <p className="text-xs max-w-sm text-slate-500 leading-relaxed">
            اختر محادثة من القائمة للرد على العملاء أو إدارة حالة الذكاء الاصطناعي والمرفقات.
          </p>
        </div>
      )}


      {/* ======================================================== */}
      {/* 3. CUSTOMER 360 PANEL (Drawer on mobile, column on desktop) */}
      {/* ======================================================== */}
      {selectedConv && showCustomer360 && (
        <>
          {/* Mobile Backdrop */}
          <div
            onClick={() => setShowCustomer360(false)}
            className="md:hidden fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs"
          />

          <div className={`
            fixed md:static inset-y-0 left-0 z-50 md:z-auto
            w-80 sm:w-88 flex flex-col h-full bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 shadow-2xl md:shadow-none overflow-y-auto p-4 space-y-4 shrink-0
          `}>
            {/* Mobile Header with close button */}
            <div className="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-slate-800">
              <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-blue-500" />
                <span>ملف العميل 360</span>
              </h3>
              <button
                onClick={() => setShowCustomer360(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Profile Card */}
            <div className="text-center space-y-2 bg-slate-50 dark:bg-slate-800/50 p-4 rounded-2xl border border-slate-200 dark:border-slate-800">
              <img
                src={customer360Data?.avatar || `https://ui-avatars.com/api/?name=${selectedConv.customer?.name}&background=1E6BFF&color=fff`}
                alt={customer360Data?.name}
                className="w-16 h-16 rounded-full mx-auto object-cover border-2 border-blue-500 shadow-xs"
              />
              <h3 className="font-bold text-sm text-slate-900 dark:text-white">
                {customer360Data?.name || selectedConv.customer?.name}
              </h3>
              <p className="text-xs text-slate-500 font-mono">
                {customer360Data?.phone || 'بدون هاتف مسجل'}
              </p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-xl border border-slate-200 dark:border-slate-800 text-center">
                <span className="text-[10px] font-bold text-slate-400 block mb-1">الطلبات والمشاريع</span>
                <span className="text-sm font-extrabold text-blue-600 dark:text-cyan-400">
                  {customer360Data?.total_orders || 0}
                </span>
              </div>

              <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-xl border border-slate-200 dark:border-slate-800 text-center">
                <span className="text-[10px] font-bold text-slate-400 block mb-1">إجمالي التعاقدات</span>
                <span className="text-sm font-extrabold text-emerald-600 dark:text-emerald-400">
                  {customer360Data?.total_spent || 0} ج.م
                </span>
              </div>
            </div>

            {/* Notes Section */}
            <div className="bg-slate-50 dark:bg-slate-800/50 p-3.5 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-2.5">
              <h4 className="font-bold text-xs text-slate-900 dark:text-white flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-blue-500" /> ملاحظات الفريق (Notes)
              </h4>

              <form onSubmit={handleAddNote} className="space-y-2">
                <input
                  type="text"
                  name="new-note"
                  id="new-note"
                  placeholder="إضافة ملاحظة جديدة..."
                  value={newNoteText}
                  onChange={(e) => setNewNoteText(e.target.value)}
                  className="w-full p-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white"
                />
              </form>

              <div className="space-y-1.5 max-h-36 overflow-y-auto">
                {toArray(customer360Data?.notes_list).map(n => (
                  <div key={n.id} className="p-2 bg-white dark:bg-slate-800 rounded-xl text-[11px] shadow-xs">
                    <p className="font-medium text-slate-800 dark:text-slate-200">{n.note_text}</p>
                    <p className="text-[9px] text-slate-400 mt-0.5">{n.author_name} • {new Date(n.created_at).toLocaleDateString('ar-EG')}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Activity Timeline */}
            <div className="bg-slate-50 dark:bg-slate-800/50 p-3.5 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-2.5">
              <h4 className="font-bold text-xs text-slate-900 dark:text-white flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-blue-500" /> سجل التفاعل
              </h4>

              <div className="space-y-2 text-[11px] max-h-40 overflow-y-auto pr-1">
                {toArray(customer360Data?.activities).map(act => (
                  <div key={act.id} className="p-2 bg-white dark:bg-slate-800 rounded-xl space-y-0.5 shadow-xs">
                    <p className="font-semibold text-slate-800 dark:text-slate-200">{act.description}</p>
                    <p className="text-[9px] text-slate-400">{new Date(act.created_at).toLocaleString('ar-EG')}</p>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </>
      )}

      {/* Full-Screen Image Preview Modal */}
      {previewModalUrl && (
        <div
          className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4 animate-in fade-in duration-200"
          onClick={() => setPreviewModalUrl(null)}
        >
          <div
            className="relative max-w-4xl max-h-[90vh] flex flex-col items-center"
            onClick={e => e.stopPropagation()}
          >
            <div className="w-full flex items-center justify-between pb-3 text-white text-xs">
              <span className="font-bold truncate max-w-md">{previewModalName || 'معاينة المرفق'}</span>
              <div className="flex items-center gap-2">
                <a
                  href={resolveMediaUrl(previewModalUrl)}
                  download={previewModalName || 'attachment'}
                  target="_blank"
                  rel="noreferrer"
                  className="p-2 bg-white/20 hover:bg-white/30 rounded-xl text-white transition flex items-center gap-1.5"
                  title="تحميل"
                >
                  <Download className="w-4 h-4" />
                  <span className="hidden sm:inline">تحميل</span>
                </a>
                <button
                  onClick={() => setPreviewModalUrl(null)}
                  className="p-2 bg-white/20 hover:bg-white/30 rounded-xl text-white transition"
                  title="إغلاق"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
            <img
              src={resolveMediaUrl(previewModalUrl)}
              alt={previewModalName}
              className="max-w-full max-h-[80vh] object-contain rounded-2xl shadow-2xl border border-white/10"
            />
          </div>
        </div>
      )}

    </div>
  );
}