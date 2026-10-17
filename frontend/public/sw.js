/**
 * NEXORA Software Solutions — Service Worker & Web Push Handler
 * Version: 1.0.0
 */

const CACHE_NAME = 'nexora-cache-v1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.webmanifest',
  '/favicon.svg',
  '/icon-192.png',
  '/icon-512.png',
  '/apple-touch-icon.png'
];

// Install: Cache core static assets and skip waiting immediately
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.warn('[SW] Cache addAll warning:', err);
      });
    })
  );
});

// Activate: Claim clients and purge outdated caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch: Network-first for API/Socket.io (NEVER cache private API data), cache-first for static assets
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Strictly skip caching for any API, webhook, socket, or dynamic requests
  if (
    url.pathname.startsWith('/api') ||
    url.pathname.startsWith('/socket.io') ||
    event.request.method !== 'GET'
  ) {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      })
      .catch(() => caches.match(event.request))
  );
});

// Push: Handle incoming Web Push notifications (iOS 16.4+ standalone & Desktop)
self.addEventListener('push', (event) => {
  let payload = {
    title: 'NEXORA — رسالة جديدة',
    body: 'لديك رسالة واردة جديدة من أحد العملاء.',
    icon: '/icon-192.png',
    badge: '/favicon.svg',
    tag: 'nexora-incoming-message',
    data: { url: '/inbox' }
  };

  if (event.data) {
    try {
      const data = event.data.json();
      payload = {
        title: data.title || payload.title,
        body: data.body || payload.body,
        icon: data.icon || payload.icon,
        badge: data.badge || payload.badge,
        tag: data.tag || payload.tag,
        data: data.data || payload.data,
        renotify: true,
        vibrate: [200, 100, 200]
      };
    } catch (e) {
      payload.body = event.data.text() || payload.body;
    }
  }

  const notificationOptions = {
    body: payload.body,
    icon: payload.icon,
    badge: payload.badge,
    tag: payload.tag,
    renotify: true,
    vibrate: [200, 100, 200],
    data: payload.data
  };

  event.waitUntil(
    self.registration.showNotification(payload.title, notificationOptions)
  );
});

// Notification Click: Focus existing client or open new window to conversation
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  const targetUrl = (event.notification.data && event.notification.data.url) || '/inbox';
  const conversationId = event.notification.data && event.notification.data.conversationId;

  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      // If a NEXORA window is already open, focus it and tell it to select conversation
      for (const client of clientList) {
        if ('focus' in client) {
          if (conversationId) {
            client.postMessage({
              type: 'SELECT_CONVERSATION',
              conversationId: conversationId
            });
          }
          return client.focus();
        }
      }
      // If no window is open, open a new window to the target URL
      if (self.clients.openWindow) {
        return self.clients.openWindow(targetUrl);
      }
    })
  );
});
