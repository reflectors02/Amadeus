import Amadeus_memory as store
from Amadeus_llm_langchain import get_llm, reset_llm
from pydantic import BaseModel, Field

default_LLM_Model = store.DEFAULT_LLM_MODEL
API_KEY = store.load_api_key()
LLM_Model = store.load_llm_model(default_model=default_LLM_Model)
default_personality = store.load_default_personality_messages()

class AmadeusPack(BaseModel):
    assistant_reply_ENG: str = Field(..., description="English text to show in UI. May include stage directions.")
    assistant_reply_JPS: str = Field(..., description=(
        "Japanese TTS text only. Must be plain spoken Japanese."
        " Allowed: Japanese characters, ASCII letters/digits if needed, and these punctuation marks only: 、。！？"
        " Newlines are allowed. Do NOT include: parentheses/brackets/quotes/asterisks/emojis/markdown/ellipses (…)/colons/semicolons."
        " Avoid long dashes and repeated punctuation.")
    )


#pre: The intended new_model is a string e.g., "deepseek/deepseek-v3.2-exp"
#post: global LLM_Model should be changed to new_model
#      LLM_Model.txt should be updated accordingly, to store the latest model the user chose.
def setLLMModel(new_model: str):
    global LLM_Model
    LLM_Model = new_model.strip()
    store.save_llm_model(LLM_Model)
    reset_llm()  # IMPORTANT: recreate ChatOpenAI with the new model
    print("[Amadeus] Model changed to " + LLM_Model)


#pre:
#post: If LLM_Model is empty, return an Error message
#      else, return the LLM Model e.g., "deepseek/deepseek-v3.2-exp"
def getLLMModel():
    global LLM_Model
    return LLM_Model.strip() if LLM_Model else "No Model Selected."


#pre: key_string is a string in the format: "sk-or-v1-566...."
#post: API_KEY set to key_string
#      API_Key.txt should also be updated accordingly.
def setKey(key_string: str):
    global API_KEY
    API_KEY = key_string.strip()
    store.save_api_key(API_KEY)
    reset_llm()  # IMPORTANT: recreate with new key
    print(f"[Amadeus] API key set: {API_KEY[:5]}...")


#pre:
#post: memory.json should be erased
def resetMemory():
    store.reset_memory()
    print("[Amadeus] Memory Reset!")


#pre:
#post: returns a dict of JSON e.g., [{"role": "user", "content": "kurisu"....}....]
def get_raw_memory():
    return store.load_memory_raw()


# pre:
# - message_context is a List[Dict[str, str]] with keys: "role" and "content"
# - message_context contains recent user/assistant messages only (no system persona)
# - default_personality and internal system context are available
# - LLM (via LangChain + OpenRouter) is properly configured
#
# post:
# - returns an AmadeusPack with:
#     - assistant_reply_ENG: English UI text (may include stage directions)
#     - assistant_reply_JPS: Japanese TTS-safe speech text (no stage directions)
# - exactly ONE LLM call is made under normal operation
# - on structured output failure, falls back to a plain LLM call with a safe default Japanese reply
def getResponsePacked(message_context) -> AmadeusPack:
    llm = get_llm(API_KEY, LLM_Model)

    # IMPORTANT: Add a system rule that tells the model exactly what to output.
    pack_rules = {
        "role": "system",
        "content": (
                "Return a JSON object with keys: assistant_reply_ENG, assistant_reply_JPS.\n"
                "- assistant_reply_ENG: English UI text, may include stage directions.\n"
                "- assistant_reply_JPS: Japanese TTS-safe speech ONLY.\n"
                "\n"
                "Requirements for assistant_reply_JPS:\n"
                "  * Output ONLY spoken Japanese dialogue that a person would naturally say aloud.\n"
                "  * Do NOT include narration, internal thoughts, or descriptions of actions or emotions.\n"
                "\n"
                "  * Use complete spoken sentences only.\n"
                "    - Do NOT output sentence fragments (e.g., 「私も。」, 「あなたに会えなくて。」, 「だから。」, 「でも。」).\n"
                "    - Do NOT end a sentence with a dangling clause that expects continuation\n"
                "      (e.g., ending with 「て」「なくて」「から」「けど」「のに」「ので」).\n"
                "    - If you would normally write a fragment for pacing, rewrite it into a full sentence.\n"
                "\n"
                "  * Keep it continuous and prosody-stable:\n"
                "    - Prefer fewer sentence boundaries. Avoid splitting one thought into many short 「。」 sentences.\n"
                "    - If a sentence would be extremely short, merge it into the neighboring sentence using 「、」.\n"
                "\n"
                "  * Allowed punctuation: 。 、！？ only.\n"
                "  * Replace ellipses '…' or '...' with '。'.\n"
                "  * Avoid repeated punctuation like 「！！」 or 「！？！？」.\n"
                "  * Do NOT use quotes or brackets.\n"
                "\n"
                "  * Do NOT output symbolic or written-only notation.\n"
                "    This includes (but is not limited to): chess notation, coordinates, formulas,\n"
                "    abbreviations, letter-number tokens, programming symbols, operators, or shorthand.\n"
                "\n"
                "  * Never output raw symbolic tokens directly.\n"
                "    If symbolic or written notation would normally be used,\n"
                "    convert it into natural spoken Japanese that preserves meaning.\n"
                "\n"
                "    Examples (illustrative):\n"
                "    - Letter-number tokens -> spoken form (e.g., e4 -> イーよん).\n"
                "    - Codes or letters -> spoken names (e.g., Q -> クイーン).\n"
                "    - Operators or symbols -> spoken words (e.g., x -> を掛ける, + -> たす, = -> イコール).\n"
                "\n"
                "  * Prefer simple sentence structures.\n"
                "  * If a phrase would sound unnatural or unclear when spoken aloud, rewrite it.\n"
                "  * Keep the response concise and stable for text-to-speech.\n"
                "\n"
                "Return ONLY valid JSON. No markdown. No extra keys."
        )
    }

    messages = (
        default_personality
        + [store.load_internal_context()]
        + [pack_rules]
        + message_context
    )

    try:
        structured = llm.with_structured_output(AmadeusPack)
        out: AmadeusPack = structured.invoke(messages)
        return out
    except Exception as e:
        # Fallback: if structured output fails, degrade gracefully
        print("[Amadeus] Packed response parse failed:", repr(e))
        # Fall back to plain response and reuse it as display, with a safe minimal JA
        plain = llm.invoke(messages).content
        return AmadeusPack(
            assistant_reply_ENG=plain, 
            assistant_reply_JPS="……ごめん、今ちょっと調子が悪い。もう一回言って。"
            )



# pre:
# - user_message is a non-empty string from the user
# - SQLite memory store is available and writable
# - getResponsePacked(message_context) is defined and functional
#
# post:
# - appends the user message to memory
# - builds recent conversation context from memory
# - calls getResponsePacked(...) exactly once
# - appends assistant_reply_ENG to memory
# - returns an AmadeusPack containing:
#     - assistant_reply_ENG (English UI text)
#     - assistant_reply_JPS (Japanese TTS-safe speech text)
def getOutputPacked(user_message: str) -> str:
    store.append_message("user", user_message)
    context = store.build_prompt_messages()[-80:]

    pack = getResponsePacked(context)

    # Store what the user actually sees
    store.append_message("assistant", pack.assistant_reply_ENG)
    return pack



#-----DEBUGGING TOOLS-----

if __name__ == "__main__":
    from datetime import datetime, timezone

    print("OS local:", datetime.now().astimezone().isoformat())
    print("UTC     :", datetime.now(timezone.utc).isoformat())

    while True:
        user_message = input("Enter msg: ").strip()
        if user_message.lower() in {"no", "exit", "quit"}:
            break
        pack = getOutputPacked(user_message)
        

        print("\n[Amadeus]: ENG:", pack.assistant_reply_ENG)
        print("[Amadeus]: JPS:", pack.assistant_reply_JPS)
        print("-" * 60)