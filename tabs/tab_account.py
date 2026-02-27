"""
Tab 9 — Account
Optional Firebase login for cloud data sync across devices.
"""
import streamlit as st
from datetime import datetime


def _do_login(app, user_data):
    """Pull all cloud data into local files after a successful sign-in."""
    import firebase_sync
    st.session_state["firebase_user"] = user_data
    st.session_state["firebase_last_sync"] = None

    with st.spinner("☁️ Loading your cloud data…"):
        cloud_data, error = firebase_sync.load_all_user_data(
            app.FIREBASE_PROJECT_ID,
            user_data["idToken"],
            user_data["localId"],
        )

    if error:
        st.warning(f"⚠️ Could not load cloud data: {error}. Your local data is intact.")
        st.session_state["firebase_data_loaded"] = True
        return

    # Write cloud data to local JSON files so the rest of the app just works
    any_loaded = False
    if cloud_data.get("meals"):
        app.save_json(app.MEALS_FILE, cloud_data["meals"])
        any_loaded = True
    if cloud_data.get("goals"):
        app.save_json(app.GOALS_FILE, cloud_data["goals"])
        any_loaded = True
    if cloud_data.get("weight"):
        app.save_json(app.WEIGHT_FILE, cloud_data["weight"])
        any_loaded = True
    if cloud_data.get("water"):
        app.save_json(app.WATER_FILE, cloud_data["water"])
        any_loaded = True
    if cloud_data.get("exercises"):
        app.save_json(app.DATA_DIR / "exercises.json", cloud_data["exercises"])
        any_loaded = True
    if cloud_data.get("notifications"):
        st.session_state["notif_prefs"] = cloud_data["notifications"]

    st.session_state["firebase_data_loaded"] = True
    st.session_state["firebase_last_sync"] = datetime.now().strftime("%b %d %Y %H:%M")

    if any_loaded:
        st.success("✅ Cloud data loaded! Your meals, goals, and progress are synced.")
    else:
        st.info("☁️ No cloud data yet — your new entries will be saved to the cloud automatically.")


def _parse_time(val, default_h, default_m):
    """Parse HH:MM string to datetime.time, with fallback."""
    import datetime as _dt
    try:
        if val:
            parts = val.split(":")
            return _dt.time(int(parts[0]), int(parts[1]))
    except Exception:
        pass
    return _dt.time(default_h, default_m)


def _render_notifications(app, user):
    """Push notification settings panel — logged-in users only."""
    import firebase_sync

    notif_prefs = st.session_state.get("notif_prefs") or {}
    notif_enabled = bool(notif_prefs.get("fcm_token"))

    # Colourful header banner
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                border-radius: 16px; padding: 1.5rem 2rem; margin-bottom: 1rem;">
        <h3 style="color:white; margin:0 0 0.3rem 0;">🔔 Smart Meal & Workout Reminders</h3>
        <p style="color:rgba(255,255,255,0.9); margin:0; font-size:0.95rem;">
            Real push notifications — alerts you even when the app is closed.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Status row
    if notif_enabled:
        col_s1, col_s2 = st.columns([4, 1])
        with col_s1:
            st.success("✅ Push notifications enabled on this device")
        with col_s2:
            if st.button("🔄 Re-register", key="notif_rereg", use_container_width=True):
                notif_prefs.pop("fcm_token", None)
                st.session_state["notif_prefs"] = notif_prefs
                st.rerun()
    else:
        st.warning("🔔 Push notifications not yet enabled on this device")
        st.info(
            "**Step 1:** Click **Enable Notifications** and allow when your browser asks.  \n"
            "**Step 2:** Set your reminder times below and click Save.  \n"
            "**Note:** Repeat on every device you want to receive alerts on."
        )

        import streamlit.components.v1 as _components
        api_key   = app.FIREBASE_API_KEY or ""
        vapid_key = getattr(app, "FIREBASE_VAPID_KEY", "")
        sender_id = getattr(app, "FIREBASE_MESSAGING_SENDER_ID", "")
        app_id    = getattr(app, "FIREBASE_APP_ID", "")
        project   = "calorie-app-auth-a0cbc"

        _components.html(f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ margin:0; padding:0; font-family: sans-serif; background: transparent; }}
  #btn {{
    width: 100%;
    padding: 0.75rem 1.5rem;
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: opacity 0.2s;
  }}
  #btn:disabled {{ opacity: 0.6; cursor: not-allowed; }}
  #status {{ margin-top: 8px; font-size: 0.9rem; color: #555; text-align: center; }}
  .err {{ color: #d32f2f !important; }}
  .ok  {{ color: #2e7d32 !important; }}
</style>
</head>
<body>
<button id="btn" onclick="enableNotifications()">🔔 Enable Notifications on This Device</button>
<p id="status"></p>

<script>
async function loadScript(parent, src) {{
  return new Promise((resolve, reject) => {{
    const s = parent.document.createElement('script');
    s.src = src;
    s.onload = resolve;
    s.onerror = reject;
    parent.document.head.appendChild(s);
  }});
}}

async function enableNotifications() {{
  const btn    = document.getElementById('btn');
  const status = document.getElementById('status');
  btn.disabled = true;

  try {{
    // 1 ─ Request browser permission (must come from user gesture)
    status.textContent = 'Requesting notification permission…';
    const perm = await Notification.requestPermission();
    if (perm !== 'granted') {{
      status.textContent = '❌ Permission denied. Please allow notifications in browser settings.';
      status.className = 'err';
      btn.disabled = false;
      return;
    }}

    // 2 ─ Load Firebase SDK into the PARENT window so SW registers at correct scope
    status.textContent = 'Loading Firebase…';
    const par = window.parent;
    if (!par.firebase) {{
      await loadScript(par, 'https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js');
      await loadScript(par, 'https://www.gstatic.com/firebasejs/10.12.0/firebase-messaging-compat.js');
    }}

    // 3 ─ Init Firebase in parent (once)
    if (!par.firebase.apps.length) {{
      par.firebase.initializeApp({{
        apiKey: "{api_key}",
        projectId: "{project}",
        messagingSenderId: "{sender_id}",
        appId: "{app_id}"
      }});
    }}

    // 4 ─ Register service worker with correct scope
    status.textContent = 'Registering service worker…';
    const swUrl = '/app/static/firebase-messaging-sw.js';
    const reg   = await par.navigator.serviceWorker.register(swUrl, {{ scope: '/app/static/' }});
    await par.navigator.serviceWorker.ready;

    // 5 ─ Get FCM token
    status.textContent = 'Getting notification token…';
    const messaging = par.firebase.messaging();
    const token = await messaging.getToken({{ vapidKey: "{vapid_key}", serviceWorkerRegistration: reg }});
    if (!token) {{
      status.textContent = '❌ Could not get token. Make sure you are on HTTPS and try again.';
      status.className = 'err';
      btn.disabled = false;
      return;
    }}

    // 6 ─ Pass token back to Streamlit via URL query param
    status.textContent = '✅ Done! Saving token…';
    status.className = 'ok';
    const tz  = new Date().getTimezoneOffset();
    const url = new URL(par.location.href);
    url.searchParams.set('fcm_token', token);
    url.searchParams.set('tz_offset', tz);
    par.location.href = url.toString();

  }} catch(e) {{
    console.error('Notification setup error:', e);
    status.textContent = '❌ ' + e.message;
    status.className = 'err';
    btn.disabled = false;
  }}
}}
</script>
</body>
</html>
""", height=90, scrolling=False)

    st.divider()

    # Settings form
    st.markdown("#### ⚙️ Reminder Schedule")
    with st.form("notif_settings_form"):
        st.markdown("**🍽️ Meal Reminders**")
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            breakfast_on   = st.toggle("🍳 Breakfast",  value=notif_prefs.get("breakfast_enabled", False), key="nf_bf_on")
            breakfast_time = st.time_input("Time", value=_parse_time(notif_prefs.get("breakfast_time"), 8, 0),  key="nf_bf_t")
        with mc2:
            lunch_on   = st.toggle("🥗 Lunch",  value=notif_prefs.get("lunch_enabled", False), key="nf_lu_on")
            lunch_time = st.time_input("Time", value=_parse_time(notif_prefs.get("lunch_time"),  12, 30), key="nf_lu_t")
        with mc3:
            dinner_on   = st.toggle("🍽️ Dinner", value=notif_prefs.get("dinner_enabled", False), key="nf_di_on")
            dinner_time = st.time_input("Time", value=_parse_time(notif_prefs.get("dinner_time"), 18, 30), key="nf_di_t")

        st.markdown("**💪 Workout Reminder**")
        wc1, wc2 = st.columns([1, 2])
        with wc1:
            workout_on   = st.toggle("💪 Workout", value=notif_prefs.get("workout_enabled", False), key="nf_wo_on")
            workout_time = st.time_input("Time", value=_parse_time(notif_prefs.get("workout_time"), 7, 0), key="nf_wo_t")
        with wc2:
            _all_days     = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
            _saved_days   = [d.capitalize() for d in notif_prefs.get("workout_days", ["monday","wednesday","friday"])]
            workout_days  = st.multiselect("Days of the week", _all_days, default=_saved_days, key="nf_wo_days")

        st.markdown("**🔥 Calorie Budget Alert**")
        cal_c1, cal_c2 = st.columns(2)
        with cal_c1:
            calorie_alert_on = st.toggle(
                "Alert when nearly at calorie limit",
                value=notif_prefs.get("calorie_alert_enabled", False),
                key="nf_cal_on"
            )
        with cal_c2:
            calorie_remain = st.number_input(
                "Notify when remaining calories ≤",
                min_value=50, max_value=1000,
                value=int(notif_prefs.get("calorie_alert_remaining", 300)),
                step=50, key="nf_cal_thresh"
            )

        save_notif = st.form_submit_button(
            "💾 Save Reminder Settings", type="primary", use_container_width=True
        )

        if save_notif:
            new_prefs = {
                "fcm_token":                notif_prefs.get("fcm_token", ""),
                "timezone_offset_minutes":  notif_prefs.get("timezone_offset_minutes", 0),
                "breakfast_enabled":        breakfast_on,
                "breakfast_time":           breakfast_time.strftime("%H:%M"),
                "lunch_enabled":            lunch_on,
                "lunch_time":               lunch_time.strftime("%H:%M"),
                "dinner_enabled":           dinner_on,
                "dinner_time":              dinner_time.strftime("%H:%M"),
                "workout_enabled":          workout_on,
                "workout_time":             workout_time.strftime("%H:%M"),
                "workout_days":             [d.lower() for d in workout_days],
                "calorie_alert_enabled":    calorie_alert_on,
                "calorie_alert_remaining":  int(calorie_remain),
            }
            ok, err = firebase_sync.save_user_data(
                app.FIREBASE_PROJECT_ID, user["idToken"], user["localId"],
                "notifications", new_prefs
            )
            if ok:
                st.session_state["notif_prefs"] = new_prefs
                st.success("✅ Reminder settings saved!")
                if not notif_enabled:
                    st.info("💡 Don't forget to click **Enable Notifications** above to activate alerts on this device.")
            else:
                st.error(f"Failed to save: {err}")


def _show_benefits():
    """Display a benefit banner encouraging sign-up."""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 16px; padding: 1.8rem 2rem; margin-bottom: 1.5rem;">
        <h2 style="color:white; margin:0 0 0.4rem 0; text-align:center;">☁️ Save Your Data Across All Devices</h2>
        <p style="color:rgba(255,255,255,0.85); text-align:center; margin:0;">
            Create a free account and your nutrition & fitness data follows you everywhere.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div style="background:#f0f4ff; border-radius:12px; padding:1.2rem; text-align:center;">
            <div style="font-size:2.2rem;">📱</div>
            <strong>Any Device</strong>
            <p style="color:#555; font-size:0.9rem; margin:0.4rem 0 0 0;">
                Access your meals, goals, and progress from your phone, tablet, or computer.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div style="background:#f0fff4; border-radius:12px; padding:1.2rem; text-align:center;">
            <div style="font-size:2.2rem;">🔒</div>
            <strong>Secure & Private</strong>
            <p style="color:#555; font-size:0.9rem; margin:0.4rem 0 0 0;">
                Your data is protected by Google Firebase. Only you can access it.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div style="background:#fff8f0; border-radius:12px; padding:1.2rem; text-align:center;">
            <div style="font-size:2.2rem;">♾️</div>
            <strong>Never Lose Data</strong>
            <p style="color:#555; font-size:0.9rem; margin:0.4rem 0 0 0;">
                Browser refreshes and new sessions won't erase your history anymore.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.info(
        "🙌 **Completely optional** — you can keep using the app without an account. "
        "Guest mode stores data locally in your current session only.",
        icon=None
    )


def render(app):
    # ── Firebase not configured ────────────────────────────────────────────
    if not app.FIREBASE_ENABLED:
        st.markdown("### ⚙️ Firebase Not Configured")
        st.warning(
            "**Firebase credentials are not set up yet.**  "
            "Follow the steps below to enable cloud accounts."
        )
        with st.expander("📋 Setup Instructions", expanded=True):
            st.markdown("""
**Step 1 — Create a Firebase project**
1. Go to [console.firebase.google.com](https://console.firebase.google.com/)
2. Click **Add project** → give it a name → Continue

**Step 2 — Enable Email/Password Authentication**
1. Sidebar → **Build → Authentication** → Get Started
2. Sign-in method tab → **Email/Password** → Enable → Save

**Step 3 — Create a Firestore Database**
1. Sidebar → **Build → Firestore Database** → Create database
2. Choose **Production mode** → select a region → Done
3. Go to **Rules** tab and replace with:
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```
4. Click **Publish**

**Step 4 — Get your API credentials**
1. Project Settings (gear icon) → **General** tab
2. Scroll to **Your apps** → copy the **Web API Key** and **Project ID**

**Step 5 — Add secrets to Streamlit**

*Local development* — add to your `.env` file:
```
FIREBASE_API_KEY=your-web-api-key
FIREBASE_PROJECT_ID=your-project-id
```

*Streamlit Cloud* — go to **App settings → Secrets** and add:
```toml
FIREBASE_API_KEY = "your-web-api-key"
FIREBASE_PROJECT_ID = "your-project-id"
```

**Step 6 — Restart the app**
The Account tab will become fully functional after restart.
""")
        return

    # ── Already logged in ─────────────────────────────────────────────────
    user = st.session_state.get("firebase_user")

    if user:
        # ── Handle FCM token returned via URL query param after JS registration ─
        _fcm_token = st.query_params.get("fcm_token", "")
        if _fcm_token:
            import firebase_sync as _fs
            _tz = int(st.query_params.get("tz_offset", "0"))
            _np = st.session_state.get("notif_prefs") or {}
            _np["fcm_token"] = _fcm_token
            _np["timezone_offset_minutes"] = _tz
            _fs.save_user_data(app.FIREBASE_PROJECT_ID, user["idToken"],
                               user["localId"], "notifications", _np)
            st.session_state["notif_prefs"] = _np
            st.query_params.clear()
            st.rerun()

        display_name = user.get("displayName") or user.get("email", "User")
        email = user.get("email", "")
        last_sync = st.session_state.get("firebase_last_sync", "Unknown")

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                    border-radius: 16px; padding: 1.5rem 2rem; margin-bottom: 1.5rem; text-align:center;">
            <div style="font-size:3rem;">👤</div>
            <h2 style="color:white; margin:0.3rem 0 0.2rem 0;">Welcome back, {display_name}!</h2>
            <p style="color:rgba(255,255,255,0.85); margin:0;">{email}</p>
        </div>
        """, unsafe_allow_html=True)

        # Sync status
        col1, col2 = st.columns([3, 1])
        with col1:
            if last_sync:
                st.success(f"✅ Cloud sync active — last synced: **{last_sync}**")
            else:
                st.info("☁️ Cloud sync active — data is saved automatically.")
        with col2:
            if st.button("🔄 Sync Now", use_container_width=True, key="acc_sync_now"):
                import firebase_sync
                with st.spinner("Syncing…"):
                    cloud_data, error = firebase_sync.load_all_user_data(
                        app.FIREBASE_PROJECT_ID, user["idToken"], user["localId"]
                    )
                if error:
                    st.error(f"Sync failed: {error}")
                else:
                    if cloud_data.get("meals"):
                        app.save_json(app.MEALS_FILE, cloud_data["meals"])
                    if cloud_data.get("goals"):
                        app.save_json(app.GOALS_FILE, cloud_data["goals"])
                    if cloud_data.get("weight"):
                        app.save_json(app.WEIGHT_FILE, cloud_data["weight"])
                    if cloud_data.get("water"):
                        app.save_json(app.WATER_FILE, cloud_data["water"])
                    if cloud_data.get("exercises"):
                        app.save_json(app.DATA_DIR / "exercises.json", cloud_data["exercises"])
                    st.session_state["firebase_last_sync"] = datetime.now().strftime("%b %d %Y %H:%M")
                    st.success("✅ Synced successfully!")
                    st.rerun()

        st.divider()

        # 🔔 Notification Reminders (prominent — logged-in only)
        _render_notifications(app, user)

        st.divider()

        # Account actions
        st.markdown("### ⚙️ Account Actions")
        acc1, acc2 = st.columns(2)

        with acc1:
            with st.expander("🔑 Change Password"):
                with st.form("change_pass_form"):
                    new_pass = st.text_input("New Password", type="password",
                                             placeholder="At least 6 characters")
                    confirm_pass = st.text_input("Confirm Password", type="password")
                    submitted = st.form_submit_button("Update Password", type="primary")
                    if submitted:
                        if len(new_pass) < 6:
                            st.error("Password must be at least 6 characters.")
                        elif new_pass != confirm_pass:
                            st.error("Passwords don't match.")
                        else:
                            import firebase_auth
                            import requests as _req
                            url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={app.FIREBASE_API_KEY}"
                            resp = _req.post(url, json={"idToken": user["idToken"],
                                                        "password": new_pass,
                                                        "returnSecureToken": True}, timeout=10)
                            data = resp.json()
                            if "error" in data:
                                st.error(firebase_auth._friendly_error(data["error"].get("message", "")))
                            else:
                                # Update stored token
                                st.session_state["firebase_user"]["idToken"] = data.get("idToken", user["idToken"])
                                st.success("✅ Password updated!")

        with acc2:
            with st.expander("📧 Forgot / Reset Password"):
                reset_email = st.text_input("Email address", value=email,
                                            key="acc_reset_email")
                if st.button("Send Reset Email", key="acc_send_reset"):
                    import firebase_auth
                    ok, err = firebase_auth.send_password_reset(app.FIREBASE_API_KEY, reset_email)
                    if ok:
                        st.success("✅ Reset email sent! Check your inbox.")
                    else:
                        st.error(err)

        st.divider()

        # Danger zone
        with st.expander("🗑️ Danger Zone"):
            st.warning("⚠️ This will permanently delete your cloud data. Your current local session data is unaffected.")
            if "acc_confirm_delete" not in st.session_state:
                st.session_state["acc_confirm_delete"] = False

            if not st.session_state["acc_confirm_delete"]:
                if st.button("🗑️ Delete My Cloud Data", key="acc_delete_btn"):
                    st.session_state["acc_confirm_delete"] = True
                    st.rerun()
            else:
                st.error("Are you sure? This cannot be undone.")
                dcol1, dcol2 = st.columns(2)
                with dcol1:
                    if st.button("✅ Yes, delete it", type="primary", key="acc_delete_confirm"):
                        import firebase_sync
                        ok, err = firebase_sync.delete_user_data(
                            app.FIREBASE_PROJECT_ID, user["idToken"], user["localId"]
                        )
                        if ok:
                            st.success("✅ Cloud data deleted.")
                        else:
                            st.error(f"Error: {err}")
                        st.session_state["acc_confirm_delete"] = False
                with dcol2:
                    if st.button("❌ Cancel", key="acc_delete_cancel"):
                        st.session_state["acc_confirm_delete"] = False
                        st.rerun()

        st.divider()

        # Sign Out
        if st.button("🚪 Sign Out", type="secondary", use_container_width=False, key="acc_signout"):
            st.session_state["firebase_user"] = None
            st.session_state["firebase_data_loaded"] = False
            st.session_state["firebase_last_sync"] = None
            st.success("👋 Signed out. You're now in guest mode.")
            st.rerun()

        return

    # ── Not logged in ─────────────────────────────────────────────────────
    _show_benefits()

    # Sign-in / Sign-up forms
    tab_signin, tab_signup = st.tabs(["🔐 Sign In", "✨ Create Account"])

    # ── SIGN IN ──────────────────────────────────────────────────────────
    with tab_signin:
        with st.form("signin_form"):
            st.markdown("#### Sign In to Your Account")
            si_email = st.text_input("Email", placeholder="you@example.com", key="si_email")
            si_pass = st.text_input("Password", type="password", placeholder="Your password", key="si_pass")
            si_submit = st.form_submit_button("🔐 Sign In", type="primary", use_container_width=True)

        if si_submit:
            if not si_email or not si_pass:
                st.error("Please fill in both email and password.")
            else:
                import firebase_auth
                with st.spinner("Signing in…"):
                    user_data, error = firebase_auth.sign_in(app.FIREBASE_API_KEY, si_email, si_pass)
                if error:
                    st.error(f"❌ {error}")
                else:
                    _do_login(app, user_data)
                    st.rerun()

        # Forgot password (outside form)
        st.markdown("")
        with st.expander("🔑 Forgot your password?"):
            fp_email = st.text_input("Enter your email", key="fp_email",
                                     placeholder="you@example.com")
            if st.button("Send Reset Email", key="fp_send"):
                if not fp_email:
                    st.error("Please enter your email.")
                else:
                    import firebase_auth
                    ok, err = firebase_auth.send_password_reset(app.FIREBASE_API_KEY, fp_email)
                    if ok:
                        st.success("✅ Reset email sent! Check your inbox.")
                    else:
                        st.error(f"❌ {err}")

    # ── SIGN UP ──────────────────────────────────────────────────────────
    with tab_signup:
        with st.form("signup_form"):
            st.markdown("#### Create Your Free Account")
            su_name = st.text_input("Display Name", placeholder="Your name (optional)", key="su_name")
            su_email = st.text_input("Email", placeholder="you@example.com", key="su_email")
            su_pass = st.text_input("Password", type="password",
                                     placeholder="At least 6 characters", key="su_pass")
            su_pass2 = st.text_input("Confirm Password", type="password",
                                      placeholder="Repeat your password", key="su_pass2")
            su_agree = st.checkbox("I understand this is a free service and my data may be deleted if I violate terms.",
                                    key="su_agree")
            su_submit = st.form_submit_button("✨ Create Account", type="primary", use_container_width=True)

        if su_submit:
            if not su_email or not su_pass:
                st.error("Email and password are required.")
            elif len(su_pass) < 6:
                st.error("Password must be at least 6 characters.")
            elif su_pass != su_pass2:
                st.error("Passwords don't match.")
            elif not su_agree:
                st.error("Please accept the terms to continue.")
            else:
                import firebase_auth
                with st.spinner("Creating your account…"):
                    user_data, error = firebase_auth.sign_up(
                        app.FIREBASE_API_KEY, su_email, su_pass, su_name
                    )
                if error:
                    st.error(f"❌ {error}")
                else:
                    st.balloons()
                    _do_login(app, user_data)
                    st.success(f"🎉 Welcome, {su_name or su_email}! Your account is ready.")
                    st.rerun()
