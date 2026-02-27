/**
 * Cloud Functions for Food Calorie Analyzer
 * Handles scheduled push notifications for meal & workout reminders.
 */

const { setGlobalOptions } = require("firebase-functions");
const { onSchedule } = require("firebase-functions/v2/scheduler");
const { onRequest } = require("firebase-functions/v2/https");
const logger = require("firebase-functions/logger");
const admin = require("firebase-admin");

admin.initializeApp();
setGlobalOptions({ maxInstances: 10 });

// ─── Helpers ──────────────────────────────────────────────────────────────────

/**
 * Returns true if storedUTCTime (HH:MM) is within `windowMins` minutes of
 * currentUTCTime (HH:MM), wrapping midnight correctly.
 */
function timeMatches(storedUTCTime, currentUTCTime, windowMins = 5) {
  const toMins = (t) => {
    const [h, m] = t.split(":").map(Number);
    return h * 60 + m;
  };
  const a = toMins(storedUTCTime);
  const b = toMins(currentUTCTime);
  const diff = Math.abs(a - b);
  return diff <= windowMins || diff >= 24 * 60 - windowMins;
}

/**
 * Convert a local HH:MM time + JS timezone offset (minutes) to UTC HH:MM.
 * JS getTimezoneOffset() returns (UTC - local) in minutes.
 */
function localToUTC(timeStr, tzOffsetMinutes) {
  const [h, m] = timeStr.split(":").map(Number);
  const localMins = h * 60 + m;
  const utcMins = ((localMins + tzOffsetMinutes) % (24 * 60) + 24 * 60) % (24 * 60);
  return `${String(Math.floor(utcMins / 60)).padStart(2, "0")}:${String(utcMins % 60).padStart(2, "0")}`;
}

/**
 * Send an FCM push notification to a single device token.
 */
async function sendNotification(token, title, body) {
  try {
    await admin.messaging().send({
      token,
      notification: { title, body },
      webpush: {
        notification: {
          title,
          body,
          icon: "https://raw.githubusercontent.com/googlefonts/noto-emoji/main/png/128/emoji_u1f37d.png",
          requireInteraction: false,
        },
        fcmOptions: { link: "/" },
      },
    });
    return true;
  } catch (err) {
    if (
      err.code === "messaging/registration-token-not-registered" ||
      err.code === "messaging/invalid-registration-token"
    ) {
      logger.warn("Invalid/expired FCM token — skipping.");
      return false;
    }
    logger.error("FCM send error:", err);
    return false;
  }
}

// ─── Scheduled Reminders (runs every 5 minutes) ───────────────────────────────

exports.scheduledReminders = onSchedule("every 5 minutes", async () => {
  const db = admin.firestore();
  const now = new Date();
  const currentUTC = `${String(now.getUTCHours()).padStart(2, "0")}:${String(now.getUTCMinutes()).padStart(2, "0")}`;
  const todayName = now.toLocaleDateString("en-US", { weekday: "long", timeZone: "UTC" }).toLowerCase();

  logger.info(`Reminder check at UTC ${currentUTC}, day=${todayName}`);

  const snapshot = await db.collection("users").get();
  if (snapshot.empty) return;

  const sends = [];

  for (const doc of snapshot.docs) {
    const data = doc.data();
    if (!data.notifications) continue;

    let prefs;
    try {
      prefs = typeof data.notifications === "string"
        ? JSON.parse(data.notifications)
        : data.notifications;
    } catch {
      continue;
    }

    const token = prefs.fcm_token;
    if (!token) continue;

    const tzOffset = typeof prefs.timezone_offset_minutes === "number"
      ? prefs.timezone_offset_minutes : 0;

    // Breakfast
    if (prefs.breakfast_enabled && prefs.breakfast_time) {
      if (timeMatches(localToUTC(prefs.breakfast_time, tzOffset), currentUTC)) {
        sends.push(sendNotification(token, "🍳 Breakfast Time!", "Don't forget to log your breakfast."));
      }
    }

    // Lunch
    if (prefs.lunch_enabled && prefs.lunch_time) {
      if (timeMatches(localToUTC(prefs.lunch_time, tzOffset), currentUTC)) {
        sends.push(sendNotification(token, "🥗 Lunch Time!", "Time to log your lunch."));
      }
    }

    // Dinner
    if (prefs.dinner_enabled && prefs.dinner_time) {
      if (timeMatches(localToUTC(prefs.dinner_time, tzOffset), currentUTC)) {
        sends.push(sendNotification(token, "🍽️ Dinner Time!", "Don't forget to log your dinner."));
      }
    }

    // Workout
    if (prefs.workout_enabled && prefs.workout_time) {
      const workoutDays = prefs.workout_days || [];
      if (
        timeMatches(localToUTC(prefs.workout_time, tzOffset), currentUTC) &&
        workoutDays.includes(todayName)
      ) {
        sends.push(sendNotification(token, "💪 Workout Time!", "Your workout reminder is here. Let's go!"));
      }
    }
  }

  await Promise.allSettled(sends);
  logger.info(`Dispatched ${sends.length} notification(s).`);
});

// ─── Test HTTP endpoint (for debugging) ──────────────────────────────────────

exports.sendTestNotification = onRequest(async (req, res) => {
  const token = req.query.token || (req.body && req.body.token);
  if (!token) {
    res.status(400).json({ error: "Missing token parameter" });
    return;
  }
  const ok = await sendNotification(
    token,
    "🎉 Test Notification",
    "Your push notifications are working correctly!"
  );
  res.json({ success: ok });
});
