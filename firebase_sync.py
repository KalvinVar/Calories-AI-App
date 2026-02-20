"""
Firestore Cloud Sync via REST API
No Firebase SDK required — uses only 'requests' and 'json'.

Data structure in Firestore:
  Collection: users
  Document:   {uid}
  Fields:     meals, goals, weight, water, exercises  (each is a JSON string)

Using a single document per user with JSON-serialized values keeps the
REST API calls simple and avoids Firestore's complex nested value format.
"""
import requests
import json


def _url(project_id: str, uid: str) -> str:
    return (
        f"https://firestore.googleapis.com/v1/projects/{project_id}"
        f"/databases/(default)/documents/users/{uid}"
    )


def _headers(id_token: str) -> dict:
    return {"Authorization": f"Bearer {id_token}", "Content-Type": "application/json"}


def save_user_data(project_id: str, id_token: str, uid: str, data_type: str, data):
    """
    Save one data type to Firestore for a user (partial update via PATCH).
    data_type: 'meals' | 'goals' | 'weight' | 'water' | 'exercises'
    data: any JSON-serialisable Python object
    Returns (success_bool, error_str).
    """
    url = _url(project_id, uid)
    params = {"updateMask.fieldPaths": data_type}
    payload = {
        "fields": {
            data_type: {"stringValue": json.dumps(data, default=str)}
        }
    }
    try:
        resp = requests.patch(url, headers=_headers(id_token), params=params,
                              json=payload, timeout=15)
        if resp.status_code in (200, 201):
            print(f"[Firebase Sync] Saved '{data_type}' for uid {uid[:8]}…")
            return True, None
        error = resp.json().get("error", {}).get("message", "Unknown Firestore error")
        print(f"[Firebase Sync] Save error ({data_type}): {error}")
        return False, error
    except Exception as e:
        print(f"[Firebase Sync] Save exception ({data_type}): {e}")
        return False, str(e)


def load_user_data(project_id: str, id_token: str, uid: str, data_type: str, default=None):
    """
    Load one data type from Firestore for a user.
    Returns (data, error_str). data is None if field absent.
    """
    url = _url(project_id, uid)
    try:
        resp = requests.get(url, headers=_headers(id_token), timeout=15)
        if resp.status_code == 200:
            fields = resp.json().get("fields", {})
            if data_type in fields:
                raw = fields[data_type].get("stringValue", "")
                try:
                    return json.loads(raw) if raw else default, None
                except json.JSONDecodeError:
                    return default, "Could not parse cloud data"
            return default, None
        if resp.status_code == 404:
            return default, None  # New user — document doesn't exist yet
        error = resp.json().get("error", {}).get("message", "Unknown error")
        print(f"[Firebase Sync] Load error ({data_type}): {error}")
        return default, error
    except Exception as e:
        print(f"[Firebase Sync] Load exception ({data_type}): {e}")
        return default, str(e)


def load_all_user_data(project_id: str, id_token: str, uid: str):
    """
    Fetch the entire user document in a single request.
    Returns (data_dict, error_str).
    data_dict keys: meals, goals, weight, water, exercises — values are
    already-parsed Python objects (or None if the field is absent).
    """
    url = _url(project_id, uid)
    try:
        resp = requests.get(url, headers=_headers(id_token), timeout=15)
        if resp.status_code == 200:
            fields = resp.json().get("fields", {})
            result = {}
            for key in ("meals", "goals", "weight", "water", "exercises"):
                if key in fields:
                    raw = fields[key].get("stringValue", "")
                    try:
                        result[key] = json.loads(raw) if raw else None
                    except json.JSONDecodeError:
                        result[key] = None
                else:
                    result[key] = None
            print(f"[Firebase Sync] Loaded all data for uid {uid[:8]}…")
            return result, None
        if resp.status_code == 404:
            print(f"[Firebase Sync] New user — no data yet (uid {uid[:8]}…)")
            return {}, None
        error = resp.json().get("error", {}).get("message", "Unknown error")
        print(f"[Firebase Sync] Load-all error: {error}")
        return {}, error
    except Exception as e:
        print(f"[Firebase Sync] Load-all exception: {e}")
        return {}, str(e)


def delete_user_data(project_id: str, id_token: str, uid: str):
    """
    Delete the entire user document from Firestore.
    Used when user requests account data deletion.
    Returns (success_bool, error_str).
    """
    url = _url(project_id, uid)
    try:
        resp = requests.delete(url, headers=_headers(id_token), timeout=15)
        if resp.status_code in (200, 204):
            print(f"[Firebase Sync] Deleted all data for uid {uid[:8]}…")
            return True, None
        if resp.status_code == 404:
            return True, None  # Already gone
        error = resp.json().get("error", {}).get("message", "Unknown error")
        return False, error
    except Exception as e:
        return False, str(e)
