import json
import requests
import config
from app.runtime_config import api_key, api_url


class LLMClient:
    def __init__(self):
        self._reload()

    def _reload(self):
        self._api_key = api_key()
        self._api_url = api_url()

    def chat(self, messages, model=None, temperature=None, max_tokens=None, json_mode=False):
        from app.runtime_config import model_chat, temp_dialogue, tokens_dialogue

        model = model or model_chat()
        temperature = temperature if temperature is not None else temp_dialogue()
        max_tokens = max_tokens or tokens_dialogue()

        self._reload()

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            resp = requests.post(self._api_url, headers=headers, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return content
        except Exception as e:
            print(f"[LLM Error] {e}")
            return None

    def chat_json(self, messages, model=None, temperature=None, max_tokens=None):
        raw = self.chat(messages, model=model, temperature=temperature,
                        max_tokens=max_tokens, json_mode=True)
        if raw is None:
            return None
        try:
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()
            return json.loads(raw)
        except json.JSONDecodeError:
            print(f"[LLM JSON Parse Error] raw: {raw[:500]}")
            return None


llm = LLMClient()
