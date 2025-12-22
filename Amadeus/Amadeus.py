import requests
import os

PATH_TO_MEMORY = "txtfiles/memory.txt"
PATH_TO_PERSONALITY = "txtfiles/personality.txt"
PATH_TO_API_KEY = "txtfiles/api_key.txt"
PATH_TO_LLM_MODEL = "txtfiles/LLM_Model.txt"

API_KEY = ""
personality = ""
memories = []
LLM_Model = ""
default_LLM_Model = "deepseek/deepseek-v3.2-exp"

with open(PATH_TO_PERSONALITY, "r") as personalityFile:
    personality = personalityFile.read()
default_personality = [{"role" : "system", "content": personality}]

#pre: The intended new_model is a string e.g., "deepseek/deepseek-v3.2-exp"
#post: global LLM_Model should be changed to new_model
#      LLM_Model.txt should be updated accordingly, to store the latest model the user chose.
def setLLMModel(new_model):
    global LLM_Model
    LLM_Model = new_model.strip()
    print("[Amadeus] Model changed to " + new_model)

    with open(PATH_TO_LLM_MODEL, 'w') as LLMFile:
        LLMFile.write(LLM_Model)

#pre:
#post: If LLM_Model is empty, return an Error message
#      else, return the LLM Model e.g., "deepseek/deepseek-v3.2-exp"
def getLLMModel():
    global LLM_Model
    if LLM_Model:
        return LLM_Model.strip()
    return "No Model Selected."

#pre: key_string is a string in the format: "sk-or-v1-566...."
#post: API_KEY set to key_string
#      API_Key.txt should also be updated accordingly.
def setKey(key_string):
    global API_KEY 
    API_KEY = key_string.strip()

    with open(PATH_TO_API_KEY, "w") as f:
        f.write(API_KEY)   

    print(f"[Amadeus] API key set: {API_KEY[:5]}...")

# Pre:
#   PATH_TO_MEMORY is a valid filesystem path.
# Post:
#   - Ensures PATH_TO_MEMORY exists (creates empty file if missing).
#   - Returns a Python list representing the stored conversation memory.
#   - Returns [] if the memory file is empty.
def getMemory():
    if not os.path.exists(PATH_TO_MEMORY):
        with open(PATH_TO_MEMORY, 'w') as f:
            pass

    with open(PATH_TO_MEMORY, "r") as memoryFile:
        data = memoryFile.read().strip()
        if not data:
            return []
        else:
            return eval(data)

#pre: context represents the new memory, it is in a JSON format.
#post: Overwrite memory.txt with context.
def updateMemory(context):
    with open(PATH_TO_MEMORY, "w") as file:
        file.write(str(context))

#pre:
#post: memory.txt should be set to nothing.
def resetMemory():
    with open(PATH_TO_MEMORY, "w") as file:
        file.write("")
        print("[Amadeus] Memory Reset!")


### Initiating default Global variables:

#pre:
#post: set key to whatever the file has, if files doesn't exist, then make one as empty
if not os.path.exists(PATH_TO_API_KEY):
    with open(PATH_TO_API_KEY, 'w') as f:
        pass

with open(PATH_TO_API_KEY, "r") as apikeyFile:
     trial_api_key = apikeyFile.read().strip()
     if trial_api_key:
        setKey(trial_api_key)

#pre:  LLM_Model.txt MUST exist!
#post: Set global LLM_Model to whatever is in LLM_Model.txt
#      If is empty, then set to default model. It should also update the LLM_Model.txt
with open(PATH_TO_LLM_MODEL, 'r') as initModelFile:
    initModel = initModelFile.read().strip()
    if initModel:
        setLLMModel(initModel)
    else:
        setLLMModel(default_LLM_Model)


### Main logic

#pre: message_context is a JSON format
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
            "messages": default_personality + message_context,
        },
    )
    data = resp.json()
    print("[Amadeus]: " + data["choices"][0]["message"]["content"])
    return data["choices"][0]["message"]["content"]

#pre: English text is passed in as assistant_reply e.g., "Hello from deepseek! *happyface*"
#post: Assistant_reply should be translated into Japanese, only the word parts of it. e.g., "JPS(Hello from deepseeK!)" 
#      Without the *happyface*
def getTranslation(assistant_reply):
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer " + API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "model": default_LLM_Model,
            "messages": [{"role" : "system", "content": "Translate the user's text into natural Japanese for TTS. Output ONLY the spoken dialogue text. No actions, no narration, no brackets, no asterisks."}] + [{"role": "user", "content" : assistant_reply}],
        },
    )
    data = resp.json()
    print("[Amadeus]: " + data["choices"][0]["message"]["content"])
    return data["choices"][0]["message"]["content"]

#pre: user_input e.g., "Testing!"
#post: returns a english response from openrouter e.g., "Hello from deepseek!", updates memory.txt.
def getOutput(user_message):
    context = getMemory()
    context.append({"role": "user", "content": user_message})
    assistant_reply = getResponse(context)
    context.append({"role": "assistant", "content": assistant_reply})
    updateMemory(context)
    return assistant_reply


