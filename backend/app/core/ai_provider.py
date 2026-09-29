import os
import requests
import json
from .config import settings

class AIProvider:
    def __init__(self):
        self.mode = "demo" if settings.AI_PROVIDER.lower() == "demo" or not settings.API_KEY else "api"
        self.api_key = settings.API_KEY
        self.base_url = settings.API_BASE_URL
        self.model = settings.MODEL

    def generate_response(self, prompt: str, system_prompt: str = "") -> dict:
        if self.mode == "demo":
            return self._demo_response(prompt)
        
        return self._api_response(prompt, system_prompt)

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
            "text": f"[DEMO MODE] This is a mock AI response for: '{prompt}'. Configure API key in settings to enable real AI.",
            "actions": []
        }

    def _api_response(self, prompt: str, system_prompt: str) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        try:
            response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            text = data["choices"][0]["message"]["content"]
            return {"text": text, "actions": []} # In a full implementation, we'd parse actions from structured output.
        except Exception as e:
            return {"text": f"Error communicating with AI Provider: {str(e)}", "actions": []}
