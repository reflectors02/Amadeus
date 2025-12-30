from flask import Flask, request, jsonify
from Amadeus import getOutputPacked, setKey, resetMemory, setLLMModel, getLLMModel, get_raw_memory
from AmadeusSpeak import generateVoice, play_sound
from flask_cors import CORS
import threading

application = Flask(__name__)
CORS(application)

# pre:
# - JSON body contains an "key" field
#
# post:
# - updates the active API key if provided
# - returns status indicating success or error
@application.route("/set_key", methods=["POST"])
def set_api_key():
    print("[Flask] /set_key route triggered")  # ← add this
    data = request.get_json()
    key = data.get("key", "")
    if key:
        setKey(key)
        return jsonify({"status": "ok", "message": "API key received"})
    else:
        return jsonify({"status": "error", "message": "No key received"}), 400

# pre:
# - JSON body contains "user_input" as a string
#
# post:
# - generates an assistant response and voice output
# - returns English UI text to the client
@application.route("/", methods=["POST"])
def request_message():
    print("[Flask] / route triggered")  
    content = request.get_json()
    user_input = content.get("user_input", "")

    pack = getOutputPacked(user_input)
    print("\n[Flask]: ENG:", pack.assistant_reply_ENG)
    print("[Flask]: JPS:", pack.assistant_reply_JPS)
    
    generateVoice(pack.assistant_reply_JPS)
    threading.Thread(target=play_sound).start()

    return jsonify({"response": pack.assistant_reply_ENG})

# pre
# post:
# - clears all stored conversation memory
# - returns confirmation status
@application.route("/memory_reset", methods=["POST"])
def memory_reset():
    print("[Flask] /memory_reset triggered")  
    resetMemory()
    return jsonify({"status": "ok", "message": "Memory reset"})


# pre:
# - JSON body contains "model" option as string
#
# post:
# - updates the active LLM model if provided
# - returns success or error status
@application.route("/setLLMModel", methods=["POST"])
def settingLLMModel():
    print("[Flask] /setLLMModel triggered")  
    data = request.get_json() or {}
    new_model = data.get("model", "").strip()
    if new_model:
        setLLMModel(new_model)
        return jsonify({"status": "ok", "message": "new model recieved!"})
    else:
        return jsonify({"status": "error", "message": "No model recieved"}), 400

# pre
# post:
# - returns the currently active LLM model name as a string
@application.route("/getCurrLLMModel", methods=["GET"])
def getCurrLLMModel():
    print("[Flask] /getCurrLLMModel triggered")  
    LLM_Model = getLLMModel()
    if LLM_Model:
        return jsonify({"status": "ok", "message": LLM_Model})
    else:
        return jsonify({"status": "error", "message": "No Model Selected"}), 400

# pre
# post:
# - returns all stored conversation messages in list of Jsons
@application.route("/getMemory", methods=["POST"])
def getMemory():
    print("[Flask] /getMemory triggered")  
    msgs = get_raw_memory()
    return jsonify({"status":"ok","messages": msgs})