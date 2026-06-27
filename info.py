import re
from os import environ

# -------------------------
# Helper
# -------------------------
def str_to_bool(val, default=False):
    if val is None:
        return default
    return val.lower() in ("true", "1", "yes", "on")

# =========================================================
# 🤖 BOT BASIC INFORMATION
# =========================================================
API_ID = int(environ.get("API_ID", "33361737"))
API_HASH = environ.get("API_HASH", "7cd3bda26b08957a7205bbe8a51e6e90")
BOT_TOKEN = environ.get("BOT_TOKEN", "")
PORT = int(environ.get("PORT", "8080"))
TIMEZONE = environ.get("TIMEZONE", "Asia/Kolkata")
OWNER_USERNAME = environ.get("OWNER_USERNAME", "EvaRoseX")
POST_CHANNEL = int(environ.get('POST_CHANNEL', '-1002707776700'))#isha ko kuch mat karo chhod do isha hii

# =========================================================
# 💾 DATABASE CONFIGURATION
# =========================================================
DB_URL = environ.get("DATABASE_URI", "mongodb+srv://GodMongo:qwertyu@cluster0.irkwpaf.mongodb.net/?appName=Cluster0")
DB_NAME = environ.get("DATABASE_NAME", "testing")

# =========================================================
# 📢 CHANNELS & ADMINS
# =========================================================
ADMINS = int(environ.get("ADMINS", "8391386178"))

LOG_CHANNEL = int(environ.get("LOG_CHANNEL", "-1004214402860"))
PREMIUM_LOGS = int(environ.get("PREMIUM_LOGS", "-1004214402860"))
VERIFIED_LOG = int(environ.get("VERIFIED_LOG", "-1004214402860"))

POST_CHANNEL = int(environ.get("POST_CHANNEL", "-1002707776700"))
VIDEO_CHANNEL = int(environ.get("VIDEO_CHANNEL", "-1004408020486"))
BRAZZER_CHANNEL = int(environ.get("BRAZZER_CHANNEL", "-1004491495280"))
PHOTO_CHANNEL = int(get_env("PHOTO_CHANNEL", "-1004493848925")) 


# Auth channels list
auth_channel_str = environ.get("AUTH_CHANNEL", "-1003985895823")
AUTH_CHANNEL = [int(x) for x in auth_channel_str.split() if x.strip().lstrip("-").isdigit()]

# =========================================================
# ⚙️ FEATURES & TOGGLES  (FIXED)
# =========================================================
FSUB = str_to_bool(environ.get("FSUB"), True)
IS_VERIFY = str_to_bool(environ.get("IS_VERIFY"), True)
POST_SHORTLINK = str_to_bool(environ.get("POST_SHORTLINK"), False)
SEND_POST = str_to_bool(environ.get("SEND_POST"), True)
PROTECT_CONTENT = str_to_bool(environ.get("PROTECT_CONTENT"), True)

# =========================================================
# 🔢 LIMITS
# =========================================================
DAILY_LIMIT = int(environ.get("DAILY_LIMIT", "25"))
VERIFICATION_DAILY_LIMIT = int(environ.get("VERIFICATION_DAILY_LIMIT", "50"))
PREMIUM_DAILY_LIMIT = int(environ.get("PREMIUM_DAILY_LIMIT", "100"))

# =========================================================
# 🔗 SHORTLINK & VERIFICATION
# =========================================================
SHORTLINK_URL = environ.get("SHORTLINK_URL", "vplink.in")
SHORTLINK_API = environ.get("SHORTLINK_API", "643cf7208bfdc009d2e1f953905840a9619d48ca")
POST_SHORTLINK_URL = environ.get("POST_SHORTLINK_URL", "")
POST_SHORTLINK_API = environ.get("POST_SHORTLINK_API", "")
VERIFY_EXPIRE = int(environ.get("VERIFY_EXPIRE", "3600"))
TUTORIAL_LINK = environ.get("TUTORIAL_LINK", "none")

# =========================================================
# 💳 PAYMENT SETTINGS
# =========================================================
UPI_ID = environ.get("UPI_ID", "chauhanvikrambhai@fam")
QR_CODE_IMAGE = environ.get("QR_CODE_IMAGE", "https://i.ibb.co/vxrhGKVp/photo-2026-03-27-16-29-44-7621973470288543756.jpg")

# =========================================================
# 🖼️ IMAGES
# =========================================================
START_PIC = environ.get("START_PIC", "https://i.ibb.co/d4FNBQrc/photo-2026-02-06-17-34-07-7603806888202862604.jpg")
AUTH_PICS = environ.get("AUTH_PICS", "https://i.ibb.co/bVks1XM/photo-2026-03-22-04-38-09-7619934675082936336.jpg")
VERIFY_IMG = environ.get("VERIFY_IMG", "https://i.ibb.co/HLhnypGg/photo-2026-05-27-17-49-35-7644630238818730000.jpg")
NO_IMG = environ.get("NO_IMG", "")

# =========================================================
# 🌐 WEB APP
# =========================================================
WEB_APP_URL = environ.get("WEB_APP_URL", "")
