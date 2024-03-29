SECRET_KEY = "M33X5m&1A[n9ilf]gvgz9,R*.a~&$&.}FJ(Y"
PUBLIC_ROLE_LIKE_GAMMA = True
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://superset:superset@postgres:5432/superset"
FEATURE_FLAGS = {"EMBEDDED_SUPERSET": True}
SESSION_COOKIE_SAMESITE = None
ENABLE_PROXY_FIX = True
CORS_OPTIONS = {
    "supports_credentials": True,
    "allow_headers": ["*"],
    "resources": ["*"],
    "origins": ["http://localhost:8088", "http://localhost:8888"],
}
ENABLE_JAVASCRIPT_CONTROLS = True
HTTP_HEADERS = {"X-Frame-Options": "Allow"}
ENABLE_CORS = True
CORS_ALLOW_HEADERS = "*"
OVERRIDE_HTTP_HEADERS = {"X-Frame-Options": "ALLOWALL"}
GUEST_TOKEN_JWT_EXP_SECONDS = 2592000
GUEST_ROLE_NAME = "Gamma"
GUEST_TOKEN_JWT_SECRET = "test-guest-secret-change-me"
GUEST_TOKEN_JWT_ALGO = "HS256"
GUEST_TOKEN_HEADER_NAME = "X-GuestToken"
