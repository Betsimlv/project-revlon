import os

# --- Use Postgres metadata DB (honor env) ---
SQLALCHEMY_DATABASE_URI = os.environ.get("SUPERSET_DATABASE_URI")

# --- Security headers / embedding ---
# Disable Talisman so we can set our own headers (e.g., allow iframe embedding)
TALISMAN_ENABLED = False

# Allow iframe embedding (you’re reverse-proxying at /dash)
HTTP_HEADERS = {
    "X-Frame-Options": "ALLOWALL",
}

# Do NOT enable ENABLE_CORS here unless you install flask_cors in the image.
# If you truly need API CORS, we can add it later the right way.
# ENABLE_CORS = True  # <-- leave this OFF to avoid flask_cors import errors

# --- Feature flags ---
FEATURE_FLAGS = {
    "EMBEDDED_SUPERSET": True,
}
EXTRA_TEMPLATE_PATHS = ["/app/pythonpath/templates"]
TEMPLATE_AUTO_RELOAD = True

# --- Branding (in-app header and browser tab) ---
APP_NAME = "Revlon"
APP_ICON = "/static/assets/branding/logo-white.png"     # put file in ./branding/
APP_ICON_WIDTH = 40
LOGO_TARGET_PATH = "/"

# if you embed at another origin later, adjust cookies; for normal use these are fine:
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE   = "Lax"

FAVICONS = [
    {
        "rel": "icon",
        "type": "image/png",
        "sizes": "32x32",
        "href": "/static/assets/branding/favicon-32.png",
    },
    {
        "rel": "icon",
        "type": "image/png",
        "sizes": "16x16",
        "href": "/static/assets/branding/favicon-16.png",
    },
]

EXTRA_CATEGORICAL_COLOR_SCHEMES = [
    {
        "id": "custom_revlon",
        "label": "Revlon Colors",
        "description": "Paleta de colores personalizada",
        "isDefault": False,
        "colors": [
           '#E9979C',
        '#F4D0D4',
        '#FEF9D5',
        '#E690B4',
        '#D4851A',
        '#5B6E2F',
        '#899E4C',
        '#A65D67',
        '#F5A9BC',
        '#a52755',
        '#C17A84',
        ],
    },
]