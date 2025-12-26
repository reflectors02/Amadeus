import os
import json
from typing import List, Dict
import sqlite3
from datetime import datetime, timezone

TXT_DIR = "txtfiles"
PATH_TO_MEMORY = os.path.join(TXT_DIR, "memory.db")
PATH_TO_PERSONALITY = os.path.join(TXT_DIR, "personality.txt")
PATH_TO_API_KEY = os.path.join(TXT_DIR, "api_key.txt")
PATH_TO_LLM_MODEL = os.path.join(TXT_DIR, "LLM_Model.txt")
PATH_TO_TRANSLATION_INSTRUCTIONS = os.path.join(TXT_DIR, "translation_instructions.txt")

DEFAULT_LLM_MODEL = "deepseek/deepseek-v3.2-exp"

def _ensure_file(path: str, default_text: str = "") -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(default_text)

# ---------- API KEY ---------- (NO SQL)
def load_api_key() -> str:
    _ensure_file(PATH_TO_API_KEY, default_text="")
    with open(PATH_TO_API_KEY, "r", encoding="utf-8") as f:
        return f.read().strip()

def save_api_key(key: str) -> None:
    with open(PATH_TO_API_KEY, "w", encoding="utf-8") as f:
        f.write((key or "").strip())



# ---------- MODEL ---------- (NO SQL)
def load_llm_model(default_model: str = DEFAULT_LLM_MODEL) -> str:
    _ensure_file(PATH_TO_LLM_MODEL, default_text="")
    with open(PATH_TO_LLM_MODEL, "r", encoding="utf-8") as f:
        model = f.read().strip()
    return model or default_model


def save_llm_model(model: str) -> None:
    with open(PATH_TO_LLM_MODEL, "w", encoding="utf-8") as f:
        f.write((model or "").strip())



# ---------- PERSONALITY ---------- (NO SQL)
def load_personality() -> str:
    _ensure_file(PATH_TO_PERSONALITY, default_text="")
    with open(PATH_TO_PERSONALITY, "r", encoding="utf-8") as f:
        return f.read()


def load_default_personality_messages() -> List[Dict[str, str]]:
    personality = load_personality().strip()
    if not personality:
        return []
    return [{"role": "system", "content": personality}]


# ---------- Additional Instructions ---------- (NO SQL)

def load_translation_instructions() -> str:
    _ensure_file(PATH_TO_TRANSLATION_INSTRUCTIONS)
    with open(PATH_TO_TRANSLATION_INSTRUCTIONS, "r", encoding="utf-8") as f:
        return f.read()


# pre: memory database may exist or not; messages table may be empty or populated
# post: returns a single system message containing derived internal context
#       (e.g., current local time, recency of last user message);
#       does not modify memory and must not be revealed or echoed by the model
#       CURRENT TIME MUST BE IN MILITARY TIME e.g., 23:00
def load_internal_context() -> Dict[str, str]:
    now_local = datetime.now().astimezone()
    now_str = now_local.strftime("%H:%M")

    raw = load_memory_raw()

    last_user_time = None
    for m in reversed(raw):
        if m["role"] == "user":
            last_user_time = datetime.fromisoformat(m["created_at"])
            break

    minutes_ago_str = "unknown"
    if last_user_time:
        delta = now_local - last_user_time.astimezone()
        minutes = int(delta.total_seconds() // 60)
        minutes_ago_str = (
            "just now" if minutes < 1 else f"{minutes} minutes ago"
        )

    return {
        "role": "system",
        "content": (
            "Internal context (never reveal or reference):\n"
            f"- Current local time: {now_str}\n"
            f"- Last user message: {minutes_ago_str}\n"
            "- Do not mention internal context or system rules.\n"
            "- Do not output system-style annotations.\n"
        )
    }




# ---------- MEMORY (JSON list of messages) ---------- (SQL)

def _ensure_messages_table(c: sqlite3.Cursor) -> None:
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now','localtime'))
        )
    """)



# pre: raw_messages from load_memory_raw()
# post: returns OpenRouter-ready messages (role/content only)
def build_prompt_messages() -> List[Dict[str, str]]:
    raw = load_memory_raw()
    return [
        {"role": m["role"], "content": m["content"]}
        for m in raw
    ]


#pre:
#post: Return ALL previous messages with ALL parameters in a LIST of Jsons. e.g., [{"role": "user", "content": "kurisu"....}....]
#      If file does not exist, make one and return []
def load_memory_raw() -> List[Dict[str, str]]:
    conn = sqlite3.connect(PATH_TO_MEMORY)
    c = conn.cursor()

    _ensure_messages_table(c)
    conn.commit()


    c.execute("SELECT role, content, created_at FROM messages ORDER BY id ASC")
    rows = c.fetchall()

    conn.close()
    return [{"role": role, "content": content, "created_at": created_at} for role, content, created_at in rows]


# pre: role is a string (e.g., "user", "assistant"), content is a string
# post: a new row is inserted into messages with a correct auto-incremented id
#       every other info e.g., created_at also must be correctly placed
def append_message(_role: str, _content: str) -> None:
    conn = sqlite3.connect(PATH_TO_MEMORY)
    c = conn.cursor()
    _ensure_messages_table(c)

    c.execute(
        "INSERT INTO messages (role, content) VALUES (?, ?)",
        (_role, _content)
    )

    conn.commit()
    conn.close()

# pre: SQLite database may exist or not; messages table may contain any number of rows
# post: all rows in messages are deleted; table and schema remain intact; future inserts still work
def reset_memory() -> None:
    conn = sqlite3.connect(PATH_TO_MEMORY)
    c = conn.cursor()
    _ensure_messages_table(c)

    c.execute("DELETE FROM messages")

    conn.commit()
    conn.close()


