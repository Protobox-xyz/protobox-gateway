SECRET_KEY = "M33X5m&1A[n9ilf]gvgz9,R*.a~&$&.}FJ(Y"
PUBLIC_ROLE_LIKE_GAMMA = True
AUTH_ROLE_PUBLIC = "Public"
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
