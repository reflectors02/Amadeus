import requests
import os

PATH_TO_MEMORY = "txtfiles/memory.txt"
PATH_TO_PERSONALITY = "txtfiles/personality.txt"
PATH_TO_API_KEY = "txtfiles/api_key.txt"

API_KEY = ""
personality = ""
memories = []

with open(PATH_TO_PERSONALITY, "r") as personalityFile:
    personality = personalityFile.read()
default_personality = [{"role" : "system", "content": personality}]

#pre: apikey is passed in as a string key_string. 
#post: API_KEY set to key_string
def setKey(key_string):
    global API_KEY 
    API_KEY = key_string
    updateAPIKEY(key_string)        
    print(f"[Amadeus] API key set: {API_KEY[:5]}...")

#Pre: 
#Post: returns JSON of memory.txt
def getMemory():
    with open(PATH_TO_MEMORY, "r") as memoryFile:
        data = memoryFile.read().strip()
        if not data:
            return []
        else:
            return eval(data)

#pre: newMemories is passed in as string context. 
#post: Overwrite memory.txt with context
def updateMemory(context):
    with open(PATH_TO_MEMORY, "w") as file:
        file.write(str(context))

#pre: new apikey is passed in as key_string. 
#post: update apikey by overwrite api_key.txt with key_string
def updateAPIKEY(key_string):
    with open(PATH_TO_API_KEY, "w") as apikeyFile:
        apikeyFile.write(key_string)

#pre:
#post: set key to whatever the file has, if files doesn't exist, then make one as empty
if not os.path.exists(PATH_TO_API_KEY):
    with open(PATH_TO_API_KEY, 'w') as f:
        pass

with open(PATH_TO_API_KEY, "r") as apikeyFile:
     trial_api_key = apikeyFile.read()
     if trial_api_key:
        setKey(trial_api_key)

#pre: A Json of message is passed in. 
#post: returns string of ONLY the response from openrouter e.g., "Hello from deepseek!"
def getResponse(message_context):
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer " + API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "model": "deepseek/deepseek-v3.2-exp",
            "messages": default_personality + message_context,
        },
    )
    data = resp.json()
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
            "model": "deepseek/deepseek-chat-v3.1",
            "messages": [{"role" : "system", "content": "translate following into japanese to be used in voice generation. Ignore the expressions i.e. whats inside * *. Only do the spoken dialogue"}] + [{"role": "user", "content" : assistant_reply}],
        },
    )
    data = resp.json()
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
