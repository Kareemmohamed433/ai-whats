/**
 * NEXORA Software Solutions — Push & Notification Service
 * Handles Web Push API, Service Worker registration, iOS PWA detection, and audio alerts.
 */

import api from './api';

// api.js interceptor already returns response.body, so support both
// { data: {...} } and flat { ... } response shapes
const unwrap = (res) => (res && res.data !== undefined ? res.data : res);

// Reject if a promise takes too long (prevents buttons stuck on "loading" forever)
function withTimeout(promise, ms, message) {
  let timer;
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error(message)), ms);
  });
  return Promise.race([promise, timeout]).finally(() => clearTimeout(timer));
}

// Convert URL-safe base64 string to Uint8Array for PushManager
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

// Synthesize pleasant sound chime using Web Audio API
export function playNotificationChime() {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    const ctx = new AudioContext();

    const osc1 = ctx.createOscillator();
    const osc2 = ctx.createOscillator();
    const gain = ctx.createGain();

    osc1.type = 'sine';
    osc1.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
    osc1.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.15); // A5

    osc2.type = 'triangle';
    osc2.frequency.setValueAtTime(880, ctx.currentTime + 0.15);
    osc2.frequency.exponentialRampToValueAtTime(1174.66, ctx.currentTime + 0.35); // D6

    gain.gain.setValueAtTime(0.2, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.45);

    osc1.connect(gain);
    osc2.connect(gain);
    gain.connect(ctx.destination);

    osc1.start(ctx.currentTime);
    osc1.stop(ctx.currentTime + 0.2);
    osc2.start(ctx.currentTime + 0.15);
    osc2.stop(ctx.currentTime + 0.45);
  } catch (e) {
    console.warn('Audio chime could not play:', e);
  }
}

export const notificationService = {
  // Check if browser/device supports Web Push
  isPushSupported() {
    return (
      typeof window !== 'undefined' &&
      'serviceWorker' in navigator &&
      'PushManager' in window &&
      'Notification' in window
    );
  },

  // Detect iOS environment (iPhone / iPad / iPod)
  isIOS() {
    if (typeof window === 'undefined') return false;
    return /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  },

  // Detect whether running as installed standalone PWA on Home Screen
  isStandalone() {
    if (typeof window === 'undefined') return false;
    return (
      window.matchMedia('(display-mode: standalone)').matches ||
      window.navigator.standalone === true ||
      document.referrer.includes('homescreen')
    );
  },

  // Get current permission status: 'granted', 'denied', or 'default'
  getPermission() {
    if (typeof window === 'undefined' || !('Notification' in window)) {
      return 'unsupported';
    }
    return Notification.permission;
  },

  // Register service worker if supported
  async registerServiceWorker() {
    if (!('serviceWorker' in navigator)) return null;
    try {
      const reg = await navigator.serviceWorker.register('/sw.js', { scope: '/' });
      console.log('[PWA] Service Worker registered:', reg.scope);
      return reg;
    } catch (err) {
      console.error('[PWA] Service Worker registration failed:', err);
      return null;
    }
  },

  // Fetch Public VAPID Key from backend
  async getVapidPublicKey() {
    const res = await api.get('/notifications/vapid-public-key');
    const body = unwrap(res);
    return body?.public_key || res?.public_key || res?.publicKey || null;
  },

  // Get subscription status and user preferences
  async getStatus() {
    return unwrap(await api.get('/notifications/status'));
  },

  // Subscribe current device to Web Push
  async subscribe() {
    if (!this.isPushSupported()) {
      throw new Error('متصفحك لا يدعم تقنية Web Push. على أجهزة iPhone، يجب إضافة التطبيق للشاشة الرئيسية (Add to Home Screen) أولاً على iOS 16.4+');
    }

    // 1. Request explicit browser permission
    const permission = await Notification.requestPermission();
    if (permission !== 'granted') {
      throw new Error('تم رفض إذن الإشعارات من المتصفح أو إعدادات النظام.');
    }

    // 2. Ensure Service Worker is registered and active
    //    (navigator.serviceWorker.ready never resolves if nothing is registered)
    let registration = await navigator.serviceWorker.getRegistration('/');
    if (!registration) {
      registration = await this.registerServiceWorker();
    }
    if (!registration) {
      throw new Error('تعذر تسجيل Service Worker. تأكد من وجود الملف public/sw.js.');
    }
    registration = await withTimeout(
      navigator.serviceWorker.ready,
      8000,
      'انتهت مهلة تشغيل Service Worker. أعد تحميل الصفحة وحاول مرة أخرى.'
    );

    // 3. Fetch server VAPID key
    const vapidPublicKey = await this.getVapidPublicKey();
    if (!vapidPublicKey) {
      throw new Error('مفتاح VAPID العام غير مهيأ في الخادم.');
    }

    // 4. Create PushSubscription with PushManager
    const convertedKey = urlBase64ToUint8Array(vapidPublicKey);
    let subscription = await registration.pushManager.getSubscription();
    if (subscription) {
      // Unsubscribe existing stale registration if any
      await subscription.unsubscribe().catch(() => { });
    }

    try {
      subscription = await withTimeout(
        registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: convertedKey
        }),
        15000,
        'انتهت مهلة الاشتراك في خدمة Push. تحقق من الاتصال بالإنترنت وأعد المحاولة.'
      );
    } catch (e) {
      throw new Error(`فشل الاشتراك في Push: ${e.name ? e.name + ' - ' : ''}${e.message}`);
    }

    const subJson = subscription.toJSON();

    // 5. Detect device label
    let deviceName = 'متصفح سطح المكتب';
    if (/iPhone/.test(navigator.userAgent)) {
      deviceName = 'آيفون (iPhone Web App)';
    } else if (/iPad/.test(navigator.userAgent)) {
      deviceName = 'آيباد (iPad Web App)';
    } else if (/Android/.test(navigator.userAgent)) {
      deviceName = 'أندرويد (Android)';
    } else if (/Macintosh/.test(navigator.userAgent)) {
      deviceName = 'ماك (macOS Safari/Chrome)';
    } else if (/Windows/.test(navigator.userAgent)) {
      deviceName = 'ويندوز (Windows PC)';
    }

    // 6. Send subscription to Flask backend
    const res = await api.post('/notifications/subscribe', {
      endpoint: subJson.endpoint,
      keys: {
        p256dh: subJson.keys?.p256dh,
        auth: subJson.keys?.auth
      },
      device_name: deviceName
    });

    return unwrap(res);
  },

  // Unsubscribe current device
  async unsubscribe() {
    try {
      if ('serviceWorker' in navigator) {
        const registration = await navigator.serviceWorker.getRegistration('/');
        const subscription = registration ? await registration.pushManager.getSubscription() : null;
        if (subscription) {
          const endpoint = subscription.endpoint;
          await subscription.unsubscribe();
          await api.post('/notifications/unsubscribe', { endpoint }).catch(() => { });
        }
      }
      return true;
    } catch (e) {
      console.error('[PWA] Unsubscribe error:', e);
      return false;
    }
  },

  // Update notification preferences
  async updatePreferences(preferences) {
    return unwrap(await api.put('/notifications/preferences', preferences));
  },

  // Trigger test notification
  async sendTestPush() {
    return unwrap(await api.post('/notifications/test'));
  },

  // Delete registered device
  async deleteDevice(deviceId) {
    return unwrap(await api.delete(`/notifications/devices/${deviceId}`));
  }
};

export default notificationService;