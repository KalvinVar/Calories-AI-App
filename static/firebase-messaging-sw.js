// Firebase Cloud Messaging Service Worker
// Committed to repo so Streamlit Cloud serves it with correct MIME type.
importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: "AIzaSyA-placeholder-replaced-at-runtime",
  projectId: "calorie-app-auth-a0cbc",
  messagingSenderId: "164721147778",
  appId: "1:164721147778:web:289daa6366f4e7ffb6d99b"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
  console.log('[FCM SW] Background message received:', payload);
  const title   = (payload.notification && payload.notification.title) || 'Food Calorie Analyzer';
  const options = {
    body:  (payload.notification && payload.notification.body) || '',
    icon:  'https://raw.githubusercontent.com/googlefonts/noto-emoji/main/png/128/emoji_u1f37d.png',
    badge: 'https://raw.githubusercontent.com/googlefonts/noto-emoji/main/png/128/emoji_u1f37d.png',
    data:  payload.data || {}
  };
  return self.registration.showNotification(title, options);
});
