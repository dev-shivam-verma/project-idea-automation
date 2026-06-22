import json
import urllib.request
import urllib.error
import ssl
from pathlib import Path
import config

# Global cache for the Gist ID to avoid redundant listings
_GIST_ID = None

def _get_headers() -> dict:
    return {
        "Authorization": f"Bearer {config.GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "curl/8.0"
    }

def _get_ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def _discover_or_create_gist() -> str:
    """Discovers the state Gist on GitHub, or creates it if not found."""
    global _GIST_ID
    if _GIST_ID:
        return _GIST_ID

    if not config.GITHUB_TOKEN:
        return ""

    headers = _get_headers()
    ctx = _get_ssl_context()

    # 1. List Gists to find existing state
    try:
        url = "https://api.github.com/gists"
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, context=ctx, timeout=10) as res:
            gists = json.loads(res.read().decode("utf-8"))
            for g in gists:
                if g.get("description") == "Project Idea Automation State":
                    _GIST_ID = g.get("id")
                    print(f"Discovered existing state Gist ID: {_GIST_ID}")
                    return _GIST_ID
    except Exception as e:
        print(f"Error listing Gists: {e}")

    # 2. Not found, create a new private Gist
    try:
        print("State Gist not found. Creating a new private Gist on GitHub...")
        url = "https://api.github.com/gists"
        payload = {
            "description": "Project Idea Automation State",
            "public": False,
            "files": {
                "sources.json": {"content": "[]"},
                "seen_ideas.json": {"content": "[]"},
                "scheduler_state.json": {"content": "{}"}
            }
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, context=ctx, timeout=10) as res:
            res_data = json.loads(res.read().decode("utf-8"))
            _GIST_ID = res_data.get("id")
            print(f"Successfully created state Gist. ID: {_GIST_ID}")
            return _GIST_ID
    except Exception as e:
        print(f"Failed to create private Gist on GitHub: {e}")
        return ""

def _read_file_from_gist(filename: str) -> str:
    """Reads a file's content from the GitHub Gist."""
    gist_id = _discover_or_create_gist()
    if not gist_id:
        return ""

    headers = _get_headers()
    ctx = _get_ssl_context()
    try:
        url = f"https://api.github.com/gists/{gist_id}"
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, context=ctx, timeout=10) as res:
            gist_data = json.loads(res.read().decode("utf-8"))
            file_data = gist_data.get("files", {}).get(filename, {})
            content = file_data.get("content", "")
            # If the file is truncated, fetch raw content
            if file_data.get("truncated", False) and file_data.get("raw_url"):
                raw_req = urllib.request.Request(file_data["raw_url"], headers=headers, method="GET")
                with urllib.request.urlopen(raw_req, context=ctx, timeout=10) as raw_res:
                    content = raw_res.read().decode("utf-8")
            return content
    except Exception as e:
        print(f"Error reading {filename} from Gist: {e}")
        return ""

def _write_file_to_gist(filename: str, content: str) -> bool:
    """Writes a file's content to the GitHub Gist."""
    gist_id = _discover_or_create_gist()
    if not gist_id:
        return False

    headers = _get_headers()
    ctx = _get_ssl_context()
    try:
        url = f"https://api.github.com/gists/{gist_id}"
        payload = {
            "files": {
                filename: {
                    "content": content
                }
            }
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="PATCH"
        )
        with urllib.request.urlopen(req, context=ctx, timeout=10) as res:
            return res.status == 200
    except Exception as e:
        print(f"Error patching Gist for {filename}: {e}")
        return False

# --- Public API for Storage Handling ---

def load_sources() -> list:
    """Loads sources list from Gist or local file."""
    if config.GITHUB_TOKEN:
        content = _read_file_from_gist("sources.json")
        if content:
            try:
                return json.loads(content)
            except Exception:
                pass
    
    # Fallback to local
    if config.SOURCES_FILE.exists():
        try:
            with open(config.SOURCES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_sources(sources: list):
    """Saves sources list to local file and syncs with Gist if enabled."""
    content = json.dumps(sources, indent=2)
    # Save local first
    try:
        with open(config.SOURCES_FILE, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        print(f"Error saving local sources: {e}")

    # Sync Gist
    if config.GITHUB_TOKEN:
        _write_file_to_gist("sources.json", content)

def load_seen_ideas() -> list:
    """Loads seen ideas from Gist or local file."""
    if config.GITHUB_TOKEN:
        content = _read_file_from_gist("seen_ideas.json")
        if content:
            try:
                return json.loads(content)
            except Exception:
                pass

    # Fallback to local
    if config.SEEN_IDEAS_FILE.exists():
        try:
            with open(config.SEEN_IDEAS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_seen_ideas(ideas: list):
    """Saves seen ideas list to local file and syncs with Gist if enabled."""
    content = json.dumps(ideas, indent=2)
    # Save local first
    try:
        with open(config.SEEN_IDEAS_FILE, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        print(f"Error saving local seen ideas: {e}")

    # Sync Gist
    if config.GITHUB_TOKEN:
        _write_file_to_gist("seen_ideas.json", content)

def load_scheduler_state() -> dict:
    """Loads scheduler state from Gist or local file."""
    default_state = {
        "last_sources_research": "1970-01-01T00:00:00",
        "last_ideas_generation": "1970-01-01T00:00:00"
    }
    if config.GITHUB_TOKEN:
        content = _read_file_from_gist("scheduler_state.json")
        if content:
            try:
                return json.loads(content)
            except Exception:
                pass

    # Fallback to local
    if config.SCHEDULER_STATE_FILE.exists():
        try:
            with open(config.SCHEDULER_STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default_state

def save_scheduler_state(state: dict):
    """Saves scheduler state to local file and syncs with Gist if enabled."""
    content = json.dumps(state, indent=2)
    # Save local first
    try:
        with open(config.SCHEDULER_STATE_FILE, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        print(f"Error saving local scheduler state: {e}")

    # Sync Gist
    if config.GITHUB_TOKEN:
        _write_file_to_gist("scheduler_state.json", content)
