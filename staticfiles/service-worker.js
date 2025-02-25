const CACHE_NAME = 'my-app-cache';
const urlsToCache = [
    '/',
    '/index.html',
    '/static/manifest.json',
    'https://e7.pngegg.com/pngimages/741/810/png-clipart-limb-finger-arm-thumb-joint-family-guy-child-hand-thumbnail.png',
    'https://e7.pngegg.com/pngimages/741/810/png-clipart-limb-finger-arm-thumb-joint-family-guy-child-hand-thumbnail.png',
    // Add other assets you want to cache
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                return response || fetch(event.request);
            })
    );
});