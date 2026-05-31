// static/js/sw.js - Enhanced PWA Service Worker
const CACHE_VERSION = 'v3';
const CACHE_NAME = `metisma-${CACHE_VERSION}`;
const OFFLINE_URL = '/offline.html';

// ✅ Enhanced cache list - now caches more essential resources
const urlsToCache = [
    '/',
    '/static/css/output.css',
    '/static/js/three.min.js',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png',
    '/static/manifest.json',
    OFFLINE_URL,
    // Cache common fonts (local fallback)
    '/static/fonts/Vazirmatn-Regular.woff2',
    '/static/fonts/Vazirmatn-Bold.woff2'
];

// Install event - cache essential assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('✅ Cached essential assets');
                return cache.addAll(urlsToCache);
            })
            .catch(err => console.error('❌ Cache failed:', err))
    );
    self.skipWaiting(); // Activate immediately
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('🗑️ Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim(); // Take control immediately
});

// Fetch event - Network First with Cache fallback, Stale-While-Revalidate for static assets
self.addEventListener('fetch', (event) => {
    // Skip non-GET requests
    if (event.request.method !== 'GET') return;

    // Skip cross-origin requests
    if (!event.request.url.startsWith(self.location.origin)) return;

    const requestUrl = new URL(event.request.url);
    
    // ✅ Stale-While-Revalidate for static assets (CSS, JS, images, fonts)
    if (requestUrl.pathname.match(/\.(css|js|png|jpg|jpeg|svg|ico|woff2|woff|ttf)$/)) {
        event.respondWith(
            caches.match(event.request).then((cachedResponse) => {
                const fetchPromise = fetch(event.request).then((networkResponse) => {
                    // Update cache in background
                    if (networkResponse.status === 200) {
                        caches.open(CACHE_NAME).then((cache) => {
                            cache.put(event.request, networkResponse.clone());
                        });
                    }
                    return networkResponse;
                }).catch(() => cachedResponse);
                
                return cachedResponse || fetchPromise;
            })
        );
        return;
    }
    
    // ✅ Network First for HTML pages and API calls
    event.respondWith(
        fetch(event.request)
            .then((response) => {
                // Clone the response for caching
                const responseClone = response.clone();
                
                // Cache successful responses
                if (response.status === 200) {
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, responseClone);
                    });
                }
                
                return response;
            })
            .catch(() => {
                // Network failed, try cache
                return caches.match(event.request)
                    .then((cachedResponse) => {
                        if (cachedResponse) {
                            return cachedResponse;
                        }
                        
                        // Show offline page for navigation requests
                        if (event.request.mode === 'navigate') {
                            return caches.match(OFFLINE_URL);
                        }
                        
                        // Return empty response for other failures
                        return new Response('Offline', { status: 503 });
                    });
            })
    );
});
