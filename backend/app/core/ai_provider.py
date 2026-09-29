import os
import requests
import json
from .config import settings

class AIProvider:
    def get_mode(self):
        settings.reload()
        return settings.AI_PROVIDER.lower()

    def generate_response(self, prompt: str, system_context: str = "") -> dict:
        mode = self.get_mode()
        if mode == "demo":
            return self._demo_response(prompt)
        
        return self._gemini_response(prompt, system_context)

    def test_connection(self) -> dict:
        settings.reload()
        if self.get_mode() == "demo":
            return {
                "success": True, 
                "message": "Demo mode is active. No external connection needed.", 
                "model": "demo"
            }
        
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            return {"success": False, "message": "Gemini API key is missing."}
        
        url = f"{settings.GEMINI_API_BASE_URL}/models/{settings.GEMINI_MODEL}:generateContent"
        headers = {
            "x-goog-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [
                {
                    "parts": [{"text": "Reply with exactly: AIS Gemini connection successful"}]
                }
            ]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            
            if "AIS Gemini connection successful" in text:
                return {"success": True, "message": "Connection successful", "model": settings.GEMINI_MODEL}
            
            return {"success": False, "message": f"Unexpected response from Gemini: {text}"}
        
        except requests.exceptions.HTTPError as e:
            code = e.response.status_code
            msg = "HTTP Error."
            if code == 401: msg = "Invalid API Key or unauthorized (401)."
            elif code == 403: msg = "Permission denied (403)."
            elif code == 429: msg = "Rate limit exceeded (429)."
            elif code >= 500: msg = f"Gemini server error ({code})."
            return {"success": False, "message": f"{msg} Details: {e.response.text}"}
        except requests.exceptions.Timeout:
            return {"success": False, "message": "Connection timed out."}
        except Exception as e:
            return {"success": False, "message": f"Connection failed: {str(e)}"}

    def _demo_response(self, prompt: str) -> dict:
        p = prompt.lower()
        if "lead" in p and "score" in p:
            return {"text": "AI Priority Score: 85/100. High potential.", "actions": []}
        if "pitch" in p:
            return {"text": "Hello, we specialize in high-quality solutions tailored for your business. We would love to discuss how AIS can help you.", "actions": []}
        if "task" in p and "breakdown" in p:
            return {"text": "1. Review requirements\n2. Draft proposal\n3. Schedule meeting", "actions": [{"type": "CREATE_TASK", "title": "Review requirements"}]}
        if "आज क्या करना चाहिए" in p or "today" in p:
            return {
                "text": "Situation: You have 3 overdue tasks and 2 high priority leads.\n\nRecommendation: Focus on contacting the new leads first, then clear the overdue tasks.\n\nNext Action: Call ABC Restaurant.",
                "actions": [{"type": "CONTACT_LEAD", "title": "Call ABC Restaurant"}]
            }
        
        return {
            "text": f"[DEMO MODE] This is a mock AI response for: '{prompt}'. Switch AI Provider to Gemini in settings for real intelligence.",
            "actions": []
        }

    def _gemini_response(self, prompt: str, system_context: str) -> dict:
        settings.reload()
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            return {"text": "Error: Gemini API key is missing. Please configure it in settings.", "actions": []}

        url = f"{settings.GEMINI_API_BASE_URL}/models/{settings.GEMINI_MODEL}:generateContent"
        headers = {
            "x-goog-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        full_prompt = f"SYSTEM CONTEXT:\n{system_context}\n\nUSER REQUEST:\n{prompt}"
        
        payload = {
            "contents": [
                {
                    "parts": [{"text": full_prompt}]
                }
            ]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return {"text": text, "actions": []}
            
        except requests.exceptions.HTTPError as e:
            code = e.response.status_code
            error_msg = f"API Error ({code})."
            if code == 401: error_msg = "Gemini API key is invalid or expired."
            elif code == 403: error_msg = "Permission denied to access Gemini API."
            elif code == 429: error_msg = "Rate limit exceeded. Please try again later."
            elif code >= 500: error_msg = "Gemini API server error. Please try again later."
            return {"text": f"Error: {error_msg}", "actions": []}
            
        except requests.exceptions.Timeout:
            return {"text": "Error: Gemini API request timed out.", "actions": []}
        except Exception as e:
            return {"text": f"Error communicating with Gemini Provider: {str(e)}", "actions": []}
