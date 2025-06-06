const CACHE_NAME = 'sitcom-addiction-cache-v2';
const STATIC_ASSETS = [
    '/static/manifest.json',
    'https://e7.pngegg.com/pngimages/741/810/png-clipart-limb-finger-arm-thumb-joint-family-guy-child-hand-thumbnail.png',
    '/static/images/thumbnail.jpg',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.12.0-2/css/all.min.css',
];

// Dynamic URLs that should always fetch from network first
const DYNAMIC_URLS = [
    '/',
    '/post-comment/',
    '/?searchtext=',
    '/terms/',
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

    // Check if the request is for a dynamic URL
    if (DYNAMIC_URLS.some(url => requestUrl.pathname.startsWith(url) || event.request.url.includes(url))) {
        // Network-first strategy for dynamic content
        event.respondWith(
            fetch(event.request)
                .then((networkResponse) => {
                    // Cache the response for future offline use
                    return caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, networkResponse.clone());
                        return networkResponse;
                    });
                })
                .catch(() => {
                    // Fallback to cache if offline
                    return caches.match(event.request);
                })
        );
    } else {
        // Cache-first strategy for static assets
        event.respondWith(
            caches.match(event.request)
                .then((response) => {
                    return response || fetch(event.request).then((networkResponse) => {
                        // Cache new static assets
                        return caches.open(CACHE_NAME).then((cache) => {
                            cache.put(event.request, networkResponse.clone());
                            return networkResponse;
                        });
                    });
                })
                .catch(() => {
                    console.error('Fetch failed for:', event.request.url);
                })
        );
    }
});