# Simple Auth API (Django + DRF + JWT)

A minimal Django REST Framework project providing **JWT authentication** with a **React-friendly flow**:

- **Access token**: short-lived (15 min), returned in JSON, stored in memory (Redux).
- **Refresh token**: long-lived (7 days), stored in an **HttpOnly Secure cookie**, used to silently refresh access tokens.
- **Logout**: blacklists refresh token + clears cookie.

---

## 🚀 Features

- `POST /api/login/` → Login, get access token (in JSON) + refresh token (in HttpOnly cookie).
- `POST /api/refresh/` → Refresh access token using cookie.
- `POST /api/logout/` → Logout, blacklist refresh + clear cookie.

---

## 🛠️ Project Setup

### 1. Clone & Install
```bash
git clone <repo-url> simple_auth
cd simple_auth
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
