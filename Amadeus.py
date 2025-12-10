import requests

PATH_TO_MEMORY = "txtfiles/memory.txt"
PATH_TO_PERSONALITY = "txtfiles/personality.txt"
PATH_TO_API_KEY = "txtfiles/api_key.txt"

API_KEY = ""
personality = ""
memories = []

with open(PATH_TO_PERSONALITY, "r") as personalityFile:
    personality = personalityFile.read()
default_personality = [{"role" : "system", "content": personality}]

def setKey(key_string):
    global API_KEY 
    API_KEY = key_string
    updateAPIKEY(key_string)        
    print(f"[Amadeus] API key set: {API_KEY[:5]}...")

#Pre: Post: Gives JSON of memory
def getMemory():
    with open(PATH_TO_MEMORY, "r") as memoryFile:
        data = memoryFile.read().strip()
        if not data:
            return []
        else:
            return eval(data)

def updateMemory(context):
    with open(PATH_TO_MEMORY, "w") as file:
        file.write(str(context))

def updateAPIKEY(key_string):
    with open(PATH_TO_API_KEY, "w") as apikeyFile:
        apikeyFile.write(key_string)

with open(PATH_TO_API_KEY, "r") as apikeyFile:
     trial_api_key = apikeyFile.read()
     if trial_api_key:
        setKey(trial_api_key)

def getResponse(message_context):
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer " + API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "model": "deepseek/deepseek-chat-v3.1",
            "messages": default_personality + message_context,
        },
    )
    data = resp.json()
    return data["choices"][0]["message"]["content"]


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


def getOutput(user_message):
	context = getMemory()
	context.append({"role": "user", "content": user_message})
	assistant_reply = getResponse(context)
	context.append({"role": "assistant", "content": assistant_reply})
	updateMemory(context)
	return assistant_reply
