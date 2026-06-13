import json
import urllib.request
import urllib.error
import ssl
from config import GEMINI_API_KEY

def call_gemini(prompt: str, response_json: bool = False, use_search: bool = False, model: str = "gemini-2.5-flash") -> str:
    """
    Calls the Gemini API using urllib.request.
    response_json: If True, forces the response to be in JSON format.
    use_search: If True, enables Google Search grounding tool.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set. Please set it in your environment or .env file.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
    
    # Constructing contents and parts
    contents = [
        {
            "parts": [
                {
                    "text": prompt
                }
            ]
        }
    ]
    
    # Base payload structure
    payload = {
        "contents": contents
    }

    # Configuration options
    generation_config = {}
    # Gemini API does not allow combining Google Search grounding with JSON mime type enforcement
    if response_json and not use_search:
        generation_config["responseMimeType"] = "application/json"
    
    if generation_config:
        payload["generationConfig"] = generation_config

    # Adding Google Search grounding tool
    if use_search:
        payload["tools"] = [
            {
                "googleSearch": {}
            }
        ]

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    # Allow bypassing SSL certificate verification issues if running in some restricted local environments
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            res_data = response.read().decode("utf-8")
            res_json = json.loads(res_data)
            
            # Extract text from the standard Gemini structure
            candidates = res_json.get("candidates", [])
            if not candidates:
                raise ValueError(f"No candidates returned by Gemini: {res_json}")
            
            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                raise ValueError(f"No content parts returned by Gemini: {res_json}")
            
            text_content = parts[0].get("text", "")
            return text_content
            
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        try:
            err_json = json.loads(err_msg)
            error_details = err_json.get("error", {}).get("message", err_msg)
        except Exception:
            error_details = err_msg
        raise RuntimeError(f"Gemini API HTTP Error {e.code}: {error_details}")
    except Exception as e:
        raise RuntimeError(f"Failed to communicate with Gemini API: {str(e)}")
