self.addEventListener('push', function(event) {
    const data = event.data.json();
    const options = {
        body: data.body,
        data: {
            url: data.url
        }
    };
    event.waitUntil(
        self.registration.showNotification(data.head, options)
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data.url)
    );
});