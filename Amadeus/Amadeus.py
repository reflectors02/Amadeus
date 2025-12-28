import requests
import os
import Amadeus_memory as store

default_LLM_Model = store.DEFAULT_LLM_MODEL
API_KEY = store.load_api_key()
LLM_Model = store.load_llm_model(default_model=default_LLM_Model)
default_personality = store.load_default_personality_messages()
translation_instructions = store.load_translation_instructions()

#pre: The intended new_model is a string e.g., "deepseek/deepseek-v3.2-exp"
#post: global LLM_Model should be changed to new_model
#      LLM_Model.txt should be updated accordingly, to store the latest model the user chose.
def setLLMModel(new_model: str):
    global LLM_Model
    LLM_Model = new_model.strip()
    store.save_llm_model(LLM_Model)
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


#pre: message_context is a List[Dict[str, str]] where each dict has keys role and content.
#post: returns string of ONLY the response from openrouter e.g., "Hello from deepseek!"
def getResponse(message_context):
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer " + API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "model": LLM_Model,
            "messages": default_personality + [store.load_internal_context()] + message_context,
        },
    )
    data = resp.json()
    print("[Amadeus]: ENG:" + data["choices"][0]["message"]["content"])
    return data["choices"][0]["message"]["content"]

#pre: English text is passed in as assistant_reply e.g., "Hello from deepseek! *happyface*"
#post: Assistant_reply should be translated into Japanese, only the word parts of it. e.g., "JPS(Hello from deepseeK!)" 
#      Without the *happyface*
def getTranslation(assistant_reply: str):
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer " + API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "model": LLM_Model,
            "messages": [{"role" : "system", "content": translation_instructions}] + [{"role": "user", "content" : assistant_reply}],
        },
    )
    data = resp.json()
    print("[Amadeus]: JPS: " + data["choices"][0]["message"]["content"])
    return data["choices"][0]["message"]["content"]

#pre: user_input e.g., "Testing!"
#post: returns a english response from openrouter e.g., "Hello from deepseek!", updates memory.txt.
def getOutput(user_message: str):
    store.append_message("user", user_message)
    context = store.build_prompt_messages()[-80:]
    assistant_reply = getResponse(context)
    store.append_message("assistant", assistant_reply)
    return assistant_reply



#-----DEBUGGING TOOLS-----

# from datetime import datetime, timezone
# print("OS local:", datetime.now().astimezone().isoformat())
# print("UTC     :", datetime.now(timezone.utc).isoformat())
# exit = False
# while(exit != True):
#     user_message = input("Enter msg")
#     if(user_message == "No"):
#         exit = True
#         break

#     getOutput(user_message)
