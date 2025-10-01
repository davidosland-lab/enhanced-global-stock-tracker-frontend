// Service Worker for GSMT Mobile PWA
const CACHE_NAME = 'gsmt-mobile-v1.0.0';
const urlsToCache = [
  '/mobile_unified.html',
  'https://cdn.tailwindcss.com',
  'https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // Return cached version or fetch from network
        return response || fetch(event.request);
      }
    )
  );
});