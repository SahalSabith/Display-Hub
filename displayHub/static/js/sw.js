self.addEventListener('push', function(event) {
    const data = event.data.json();
    const options = {
        body: data.body,
        badge: data.badge
    };
    event.waitUntil(
        self.registration.showNotification(data.head, options)
    );
});