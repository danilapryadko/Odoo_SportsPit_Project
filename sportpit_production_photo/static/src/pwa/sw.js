// Service Worker для офлайн работы
const CACHE_NAME = 'sportpit-photo-v1';
const urlsToCache = [
    '/',
    '/index.html',
    '/manifest.json',
    '/offline.html'
];

// Установка Service Worker
self.addEventListener('install', event => {
    console.log('Service Worker установлен');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Кэширование файлов');
                return cache.addAll(urlsToCache);
            })
    );
});

// Активация Service Worker
self.addEventListener('activate', event => {
    console.log('Service Worker активирован');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Удаление старого кэша:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Обработка запросов
self.addEventListener('fetch', event => {
    // Пропускаем запросы к API
    if (event.request.url.includes('/web/dataset/') || 
        event.request.url.includes('/web/session/')) {
        return;
    }
    
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Возвращаем кэшированный ответ или делаем запрос
                if (response) {
                    return response;
                }
                
                return fetch(event.request)
                    .then(response => {
                        // Не кэшируем неуспешные ответы
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }
                        
                        // Клонируем ответ для кэширования
                        const responseToCache = response.clone();
                        
                        caches.open(CACHE_NAME)
                            .then(cache => {
                                cache.put(event.request, responseToCache);
                            });
                        
                        return response;
                    });
            })
            .catch(() => {
                // Если офлайн, показываем офлайн страницу
                if (event.request.destination === 'document') {
                    return caches.match('/offline.html');
                }
            })
    );
});

// Фоновая синхронизация
self.addEventListener('sync', event => {
    console.log('Фоновая синхронизация:', event.tag);
    
    if (event.tag === 'sync-photos') {
        event.waitUntil(syncPendingPhotos());
    }
});

// Синхронизация фото
async function syncPendingPhotos() {
    try {
        // Получаем офлайн фото из IndexedDB или localStorage
        const cache = await caches.open(CACHE_NAME);
        const requests = await cache.matchAll('/offline-photos');
        
        for (const request of requests) {
            const data = await request.json();
            
            // Отправляем на сервер
            const response = await fetch('/web/dataset/call_kw', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'call',
                    params: {
                        model: 'production.photo',
                        method: 'create_from_mobile',
                        args: [data],
                        kwargs: {}
                    }
                })
            });
            
            if (response.ok) {
                // Удаляем из кэша после успешной отправки
                await cache.delete(request.url);
            }
        }
    } catch (error) {
        console.error('Ошибка синхронизации:', error);
    }
}

// Push-уведомления
self.addEventListener('push', event => {
    const options = {
        body: event.data ? event.data.text() : 'Напоминание о фото-отчете',
        icon: '/icon-192.png',
        badge: '/icon-192.png',
        vibrate: [200, 100, 200],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'take-photo',
                title: 'Сделать фото',
                icon: '/camera-icon.png'
            },
            {
                action: 'dismiss',
                title: 'Позже',
                icon: '/close-icon.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('SportsPit Производство', options)
    );
});

// Обработка действий уведомления
self.addEventListener('notificationclick', event => {
    event.notification.close();
    
    if (event.action === 'take-photo') {
        // Открываем приложение с камерой
        event.waitUntil(
            clients.openWindow('/?action=camera')
        );
    } else {
        // Просто открываем приложение
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});
