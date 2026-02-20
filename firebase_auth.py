"""
Firebase Authentication via REST API
No Firebase SDK required — uses only the standard 'requests' library.
"""
import requests

FIREBASE_AUTH_URL = "https://identitytoolkit.googleapis.com/v1/accounts"
FIREBASE_REFRESH_URL = "https://securetoken.googleapis.com/v1/token"

# Maps Firebase error codes to user-friendly messages
_ERROR_MAP = {
    "EMAIL_EXISTS": "An account with this email already exists.",
    "EMAIL_NOT_FOUND": "No account found with this email.",
    "INVALID_PASSWORD": "Incorrect password.",
    "INVALID_EMAIL": "Please enter a valid email address.",
    "WEAK_PASSWORD": "Password must be at least 6 characters.",
    "USER_DISABLED": "This account has been disabled.",
    "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many failed attempts. Please try again later.",
    "INVALID_LOGIN_CREDENTIALS": "Incorrect email or password.",
    "INVALID_ID_TOKEN": "Session expired. Please sign in again.",
    "USER_NOT_FOUND": "User not found.",
    "CREDENTIAL_TOO_OLD_LOGIN_AGAIN": "Please sign in again to perform this action.",
}


def _friendly_error(code: str) -> str:
    """Convert a Firebase error code to a human-readable message."""
    # Firebase sometimes appends extra info after a colon
    base = code.split(" : ")[0].strip()
    return _ERROR_MAP.get(base, code.replace("_", " ").title())


def sign_up(api_key: str, email: str, password: str, display_name: str = ""):
    """
    Register a new user with email + password.
    Returns (user_dict, error_str). On success error_str is None.
    user_dict contains: localId, idToken, refreshToken, email, displayName
    """
    url = f"{FIREBASE_AUTH_URL}:signUp?key={api_key}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        data = resp.json()
        if "error" in data:
            return None, _friendly_error(data["error"].get("message", "Sign up failed"))
        # Optionally set display name
        if display_name:
            _update_profile(api_key, data["idToken"], display_name)
            data["displayName"] = display_name
        print(f"[Firebase Auth] Sign-up success: {email}")
        return data, None
    except Exception as e:
        return None, f"Network error: {str(e)}"


def sign_in(api_key: str, email: str, password: str):
    """
    Sign in with email + password.
    Returns (user_dict, error_str). user_dict keys: localId, idToken, refreshToken,
    email, displayName, registered.
    """
    url = f"{FIREBASE_AUTH_URL}:signInWithPassword?key={api_key}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        data = resp.json()
        if "error" in data:
            return None, _friendly_error(data["error"].get("message", "Sign in failed"))
        print(f"[Firebase Auth] Sign-in success: {email}")
        return data, None
    except Exception as e:
        return None, f"Network error: {str(e)}"


def send_password_reset(api_key: str, email: str):
    """
    Send a password reset email.
    Returns (success_bool, error_str).
    """
    url = f"{FIREBASE_AUTH_URL}:sendOobCode?key={api_key}"
    payload = {"requestType": "PASSWORD_RESET", "email": email}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        data = resp.json()
        if "error" in data:
            return False, _friendly_error(data["error"].get("message", "Failed to send email"))
        print(f"[Firebase Auth] Password reset email sent to {email}")
        return True, None
    except Exception as e:
        return False, f"Network error: {str(e)}"


def refresh_id_token(api_key: str, refresh_token: str):
    """
    Exchange a refresh token for a new ID token.
    Returns (new_id_token, new_refresh_token, error_str).
    """
    url = f"{FIREBASE_REFRESH_URL}?key={api_key}"
    payload = {"grant_type": "refresh_token", "refresh_token": refresh_token}
    try:
        resp = requests.post(url, data=payload, timeout=10)
        data = resp.json()
        if "error" in data:
            return None, None, "Session expired, please sign in again."
        return data.get("id_token"), data.get("refresh_token"), None
    except Exception as e:
        return None, None, f"Network error: {str(e)}"


def _update_profile(api_key: str, id_token: str, display_name: str):
    """Internal: set display name on a newly created account."""
    url = f"{FIREBASE_AUTH_URL}:update?key={api_key}"
    payload = {"idToken": id_token, "displayName": display_name, "returnSecureToken": False}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception:
        pass  # Non-critical
