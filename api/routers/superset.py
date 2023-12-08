from fastapi import APIRouter
import requests
from settings import SUPERSET_PASS, SUPRESET_ADMIN

router = APIRouter(prefix="/api/superset", tags=["superset"])

SUPRESET_BASE = "https://superset.protobox.xyz"


def login():
    LOGIN_URL = f"{SUPRESET_BASE}/api/v1/security/login"
    session = requests.Session()
    payload = {"password": SUPERSET_PASS, "provider": "db", "refresh": True, "username": SUPRESET_ADMIN}
    response = session.post(LOGIN_URL, json=payload)
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        refresh_token = response.json().get("refresh_token")
    else:
        raise Exception("Login failed")
    return (access_token, refresh_token)


def get_csrf_token():
    access_token, _ = login()
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{SUPRESET_BASE}/api/v1/security/csrf_token/", headers=headers)
    csrf_token = response.json().get("result")
    return csrf_token


def create_guest_token(dashboard_id):
    access_token, _ = login()
    session = requests.Session()
    session.headers["Authorization"] = f"Bearer {access_token}"
    session.headers["Content-Type"] = "application/json"
    csrf_url = f"{SUPRESET_BASE}/api/v1/security/csrf_token/"
    csrf_res = session.get(csrf_url)
    csrf_token = csrf_res.json()["result"]
    session.headers["Referer"] = csrf_url
    session.headers["X-CSRFToken"] = csrf_token
    guest_token_endpoint = f"{SUPRESET_BASE}/api/v1/security/guest_token/"
    payload = {
        "user": {"username": "ebr1", "first_name": "embedded", "last_name": "reader"},
        "resources": [{"type": "dashboard", "id": dashboard_id}],
        "rls": [],
    }
    response = session.post(guest_token_endpoint, json=payload)
    return response.json()


@router.get("/{dashboard_id}", status_code=200)
async def handle_generate_guest_token(dashboard_id: str):
    return create_guest_token(dashboard_id)
