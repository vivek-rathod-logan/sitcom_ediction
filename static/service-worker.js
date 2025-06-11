const CACHE_NAME = 'sitcom-addiction-cache-v3';
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/offline.html',
    '/static/manifest.json',
    '/static/images/icon-192x192.png',
    '/static/images/icon-512x512.png',
    '/static/images/thumbnail.jpg',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.12.0-2/css/all.min.css'
];

const DYNAMIC_URLS = [
    '/post-comment/',
    '/?searchtext=',
    '/terms/'
];

// Install event: Cache static assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => self.skipWaiting())
            .catch((error) => {
                console.error('Caching failed:', error);
            })
    );
});

// Activate event: Clean up old caches
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

// Fetch event: Network-first for dynamic URLs, cache-first for static assets
self.addEventListener('fetch', (event) => {
    const requestUrl = new URL(event.request.url);

    // Handle dynamic URLs with network-first strategy
    if (DYNAMIC_URLS.some(url => requestUrl.pathname.startsWith(url) || event.request.url.includes(url))) {
        event.respondWith(
            fetch(event.request)
                .then((networkResponse) => {
                    if (!networkResponse || networkResponse.status !== 200) {
                        throw new Error('Network response was not ok');
                    }
                    return caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, networkResponse.clone());
                        return networkResponse;
                    });
                })
                .catch(() => {
                    return caches.match(event.request)
                        .then((response) => response || caches.match('/offline.html'));
                })
        );
    } else {
        // Cache-first strategy for static assets
        event.respondWith(
            caches.match(event.request)
                .then((response) => {
                    return response || fetch(event.request).then((networkResponse) => {
                        if (!networkResponse || networkResponse.status !== 200) {
                            throw new Error('Network response was not ok');
                        }
                        return caches.open(CACHE_NAME).then((cache) => {
                            cache.put(event.request, networkResponse.clone());
                            return networkResponse;
                        });
                    });
                })
                .catch(() => {
                    if (event.request.mode === 'navigate') {
                        return caches.match('/offline.html');
                    }
                    return null;
                })
        );
    }
});