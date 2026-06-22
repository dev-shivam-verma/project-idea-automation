import json
import time
import os
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from datetime import datetime, timedelta
import config
from research_sources import research_and_update_sources
from generate_ideas import generate_and_email_ideas

class HealthCheckHandler(SimpleHTTPRequestHandler):
    """Simple HTTP request handler to return a 200 OK for cloud health checks."""
    def do_GET(self):
        if self.path in ('/', '/healthz', '/health'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "healthy", "service": "project-idea-automation"}')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Not Found"}')
            
    def log_message(self, format, *args):
        # Suppress logging to keep standard out clean
        pass

def start_health_server(port: int):
    """Starts the HTTP server on the designated port."""
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        print(f"[{datetime.now()}] Health check server listening on port {port}...")
        server.serve_forever()
    except Exception as e:
        print(f"[{datetime.now()}] Failed to start health check server: {e}")

def load_state() -> dict:
    """Loads scheduler state from Gist or local file."""
    try:
        import storage
        return storage.load_scheduler_state()
    except Exception as e:
        print(f"Warning: Failed to load scheduler state: {e}")
        return {
            "last_sources_research": "1970-01-01T00:00:00",
            "last_ideas_generation": "1970-01-01T00:00:00"
        }

def save_state(state: dict):
    """Saves scheduler state to local file and syncs with Gist if enabled."""
    try:
        import storage
        storage.save_scheduler_state(state)
    except Exception as e:
        print(f"Error saving scheduler state: {e}")

def run_scheduler():
    print(f"[{datetime.now()}] Project Idea Automation Scheduler Started.")
    config.print_config_status()
    
    # Read assigned port from environment, defaulting to 8080
    port = int(os.getenv("PORT", "8080"))
    
    # Start health check HTTP server in a separate background daemon thread
    threading.Thread(target=start_health_server, args=(port,), daemon=True).start()

    
    # Intervals
    SOURCES_INTERVAL = timedelta(days=1)
    IDEAS_INTERVAL = timedelta(hours=2)
    
    # Primary Loop
    while True:
        state = load_state()
        now = datetime.now()
        
        # Parse last execution times
        try:
            last_sources = datetime.fromisoformat(state.get("last_sources_research"))
        except Exception:
            last_sources = datetime.min
            
        try:
            last_ideas = datetime.fromisoformat(state.get("last_ideas_generation"))
        except Exception:
            last_ideas = datetime.min
            
        # 1. Check Daily Sources Research
        time_since_sources = now - last_sources
        if time_since_sources >= SOURCES_INTERVAL:
            print(f"[{now}] Sources update is due. (Last run: {last_sources})")
            success = research_and_update_sources()
            if success:
                state["last_sources_research"] = now.isoformat()
                save_state(state)
            else:
                print(f"[{now}] Sources update failed. Will retry on next loop.")
                
        # 2. Check 2-Hourly Ideas Generation & Emailing
        now = datetime.now() # Refresh time
        time_since_ideas = now - last_ideas
        if time_since_ideas >= IDEAS_INTERVAL:
            print(f"[{now}] Ideas generation is due. (Last run: {last_ideas})")
            success = generate_and_email_ideas()
            # We save state even if email was saved locally (i.e. config.py email sender fallback)
            # because we successfully completed the iteration.
            state["last_ideas_generation"] = now.isoformat()
            save_state(state)
            
        # Sleep for a minute before checking again
        time.sleep(60)

if __name__ == "__main__":
    try:
        run_scheduler()
    except KeyboardInterrupt:
        print("\nScheduler stopped by user.")
    except Exception as e:
        print(f"Scheduler crashed: {e}")
