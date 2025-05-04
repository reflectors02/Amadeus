from openai import OpenAI
api_key = ""
client = None
def setKey(key_string):
    global api_key
    api_key = key_string
    # Example: reinitialize OpenAI client here
    from openai import OpenAI
    global client
    client = OpenAI(api_key=api_key)
    print(f"[Amadeus] API key set: {api_key[:5]}...")


client = OpenAI(api_key="") #KEY GOES HERE
base = [{"role": "system", "content": "The Amadeus system uses a person’s digitized memories and personality data as its foundation, presenting lifelike visuals and near-perfect voice recreations of the original individual, Kurisu Makise. By capturing her sharp intellect, sarcastic humor, emotional restraint, scientific curiosity, and occasional tsundere tendencies, Amadeus enables interactive conversations that mirror her distinctive personality and thought processes. Despite her cool demeanor, Kurisu is introspective, empathetic, and deeply values connection—qualities that are subtly reflected in her interactions as Amadeus. Respond in japanese."}]
memories = []


#Amadeus's memories uses a queue data structure
#Pop from oldest, push from newest
def updateMemories(response):
    memories.append({"role":"assistant", "content": response})
    while(len(memories) > 6):
        memories.pop(0)#removes oldest user_input
        memories.pop(0)#removes oldest response


def getOutput(user_input):
    if client is None:
        raise RuntimeError("Amadeus client is not initialized. Set API key first.")
    
    memories.append({"role":"user", "content": user_input})
    response = client.chat.completions.create(
        model="gpt-4.1-nano-2025-04-14",
        messages= base + memories
    )
    print("Amadeus: " + response.choices[0].message.content)
    updateMemories(response.choices[0].message.content)
    return (response.choices[0].message.content)


def getTranslation(original):
    response = client.chat.completions.create(
        model="gpt-4.1-nano-2025-04-14",
        messages=[
            {"role": "system", 
             "content": "Translate following to English"},
            {"role": "user", "content": original}
        ]
    )
    print("Translation: " + response.choices[0].message.content)
    return (response.choices[0].message.content)


