import os
from pathlib import Path

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Check for persistent data directory (useful for container volumes)
DATA_DIR_PATH = os.getenv("DATA_DIR", "")
if DATA_DIR_PATH:
    DATA_DIR = Path(DATA_DIR_PATH)
else:
    DATA_DIR = BASE_DIR

# Data Files
SOURCES_FILE = DATA_DIR / "sources.json"
SEEN_IDEAS_FILE = DATA_DIR / "seen_ideas.json"
SCHEDULER_STATE_FILE = DATA_DIR / "scheduler_state.json"
EMAILS_DIR = DATA_DIR / "emails_sent"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True, parents=True)
EMAILS_DIR.mkdir(exist_ok=True, parents=True)

# Try to load environment variables from .env file manually to keep it zero-dependency
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

# Configuration Variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", SMTP_USER)
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "")

# Print configuration status (excluding secrets)
def print_config_status():
    print("=== Configuration Status ===")
    print(f"Base Directory: {BASE_DIR}")
    print(f"Gemini API Key Configured: {'YES' if GEMINI_API_KEY else 'NO'}")
    print(f"SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
    print(f"SMTP User Configured: {'YES' if SMTP_USER else 'NO'}")
    print(f"Recipient Email: {RECIPIENT_EMAIL if RECIPIENT_EMAIL else 'NOT CONFIGURED'}")
    print("============================")
