import os
import json
from typing import List, Dict

TXT_DIR = "txtfiles"
PATH_TO_MEMORY = os.path.join(TXT_DIR, "memory.json")
PATH_TO_PERSONALITY = os.path.join(TXT_DIR, "personality.txt")
PATH_TO_API_KEY = os.path.join(TXT_DIR, "api_key.txt")
PATH_TO_LLM_MODEL = os.path.join(TXT_DIR, "LLM_Model.txt")

DEFAULT_LLM_MODEL = "deepseek/deepseek-v3.2-exp"

def _ensure_file(path: str, default_text: str = "") -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(default_text)

# ---------- API KEY ----------
def load_api_key() -> str:
    _ensure_file(PATH_TO_API_KEY, default_text="")
    with open(PATH_TO_API_KEY, "r", encoding="utf-8") as f:
        return f.read().strip()

def save_api_key(key: str) -> None:
    with open(PATH_TO_API_KEY, "w", encoding="utf-8") as f:
        f.write((key or "").strip())



# ---------- MODEL ----------
def load_llm_model(default_model: str = DEFAULT_LLM_MODEL) -> str:
    _ensure_file(PATH_TO_LLM_MODEL, default_text="")
    with open(PATH_TO_LLM_MODEL, "r", encoding="utf-8") as f:
        model = f.read().strip()
    return model or default_model


def save_llm_model(model: str) -> None:
    with open(PATH_TO_LLM_MODEL, "w", encoding="utf-8") as f:
        f.write((model or "").strip())



# ---------- PERSONALITY ----------
def load_personality() -> str:
    _ensure_file(PATH_TO_PERSONALITY, default_text="")
    with open(PATH_TO_PERSONALITY, "r", encoding="utf-8") as f:
        return f.read()


def load_default_personality_messages() -> List[Dict[str, str]]:
    personality = load_personality().strip()
    if not personality:
        return []
    return [{"role": "system", "content": personality}]




# ---------- MEMORY (JSON list of messages) ----------
def load_memory() -> List[Dict[str, str]]:
    _ensure_file(PATH_TO_MEMORY, default_text="[]")
    with open(PATH_TO_MEMORY, "r", encoding="utf-8") as f:
        raw = f.read().strip()
        if not raw:
            return []
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                return data
            return []
        except json.JSONDecodeError:
            # If the file got corrupted, fail safe instead of crashing
            return []

def save_memory(messages: List[Dict[str, str]]) -> None:
    with open(PATH_TO_MEMORY, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False)


def append_message(role: str, content: str) -> None:
    messages = load_memory()
    messages.append({"role": role, "content": content})
    save_memory(messages)


def reset_memory() -> None:
    save_memory([])


