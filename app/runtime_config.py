import json
import os
import threading

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_FILE = os.path.join(PROJECT_ROOT, "user_settings.json")

DEFAULTS = {
    "api_key": "",
    "api_url": "https://api.deepseek.com/v1/chat/completions",
    "model_reasoner": "deepseek-v4-pro",
    "model_chat": "deepseek-v4-flash",
    "temperature_creative": 0.95,
    "temperature_narrative": 0.85,
    "temperature_dialogue": 0.8,
    "temperature_director": 0.3,
    "temperature_novel": 0.9,
    "max_tokens_world": 4096,
    "max_tokens_plot": 4096,
    "max_tokens_dialogue": 2048,
    "max_tokens_narrator": 2048,
    "max_tokens_director": 1024,
    "max_tokens_novel": 4096,
}

_lock = threading.Lock()
_cache = None


def _load():
    global _cache
    if not os.path.exists(SETTINGS_FILE):
        _cache = dict(DEFAULTS)
        _save()
        return _cache
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}
    _cache = dict(DEFAULTS)
    _cache.update({k: v for k, v in data.items() if k in DEFAULTS})
    _save()
    return _cache


def _save():
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(_cache, f, ensure_ascii=False, indent=2)


def get(key, default=None):
    with _lock:
        if _cache is None:
            _load()
        return _cache.get(key, default)


def get_all():
    with _lock:
        if _cache is None:
            _load()
        return dict(_cache)


def update(settings_dict):
    with _lock:
        global _cache
        if _cache is None:
            _load()
        for k, v in settings_dict.items():
            if k in DEFAULTS:
                if isinstance(DEFAULTS[k], (int, float)) and v is not None:
                    try:
                        v = type(DEFAULTS[k])(v)
                    except (ValueError, TypeError):
                        continue
                _cache[k] = v
        _save()
    return dict(_cache)


def api_key():
    key = get("api_key")
    if key:
        return key
    import config
    return config.DEEPSEEK_API_KEY


def api_url():
    url = get("api_url")
    if url:
        return url
    import config
    return config.DEEPSEEK_API_URL


def model_reasoner():
    return get("model_reasoner") or DEFAULTS["model_reasoner"]


def model_chat():
    return get("model_chat") or DEFAULTS["model_chat"]


def temp_creative():
    return get("temperature_creative")


def temp_narrative():
    return get("temperature_narrative")


def temp_dialogue():
    return get("temperature_dialogue")


def temp_director():
    return get("temperature_director")


def temp_novel():
    return get("temperature_novel")


def tokens_world():
    return get("max_tokens_world")


def tokens_plot():
    return get("max_tokens_plot")


def tokens_dialogue():
    return get("max_tokens_dialogue")


def tokens_narrator():
    return get("max_tokens_narrator")


def tokens_director():
    return get("max_tokens_director")


def tokens_novel():
    return get("max_tokens_novel")
