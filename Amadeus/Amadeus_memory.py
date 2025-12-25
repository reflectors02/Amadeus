import os
import json
from typing import List, Dict
import sqlite3

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


# ---------- MEMORY (JSON list of messages) ---------- (SQL)

def _ensure_messages_table(c: sqlite3.Cursor) -> None:
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT
        )
    """)

#pre:
#post: Return ALL previous messages in a LIST of Jsons. e.g., [{"role": "user", "content": "kurisu"}....]
#      If file does not exist, make one and return []
def load_memory() -> List[Dict[str, str]]:
    conn = sqlite3.connect(PATH_TO_MEMORY)
    c = conn.cursor()

    _ensure_messages_table(c)
    conn.commit()


    c.execute("SELECT role, content FROM messages ORDER BY id ASC")
    rows = c.fetchall()

    conn.close()
    return [{"role": role, "content": content} for role, content in rows]

# pre: role is a string (e.g., "user", "assistant"), content is a string
# post: a new row is inserted into messages with a correct auto-incremented id
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


