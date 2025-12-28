from flask import Flask, request, jsonify
from Amadeus import getOutput, getTranslation, setKey, resetMemory, setLLMModel, getLLMModel, get_raw_memory
from AmadeusSpeak import generateVoice, play_sound
from flask_cors import CORS
import threading

application = Flask(__name__)
CORS(application)

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
    
@application.route("/", methods=["POST"])
def request_message():
    content = request.get_json()
    user_input = content.get("user_input", "")
    assistant_reply_ENG = getOutput(user_input)
    assistant_reply_JPS = getTranslation(assistant_reply_ENG)
    generateVoice(assistant_reply_JPS)
    threading.Thread(target=play_sound).start()
    return jsonify({"response": assistant_reply_ENG})

@application.route("/memory_reset", methods=["POST"])
def memory_reset():
    resetMemory()
    return jsonify({"status": "ok", "message": "Memory reset"})

@application.route("/setLLMModel", methods=["POST"])
def settingLLMModel():
    data = request.get_json() or {}
    new_model = data.get("model", "").strip()
    if new_model:
        setLLMModel(new_model)
        return jsonify({"status": "ok", "message": "new model recieved!"})
    else:
        return jsonify({"status": "error", "message": "No model recieved"}), 400

@application.route("/getCurrLLMModel", methods=["GET"])
def getCurrLLMModel():
    LLM_Model = getLLMModel()
    if LLM_Model:
        return jsonify({"status": "ok", "message": LLM_Model})
    else:
        return jsonify({"status": "error", "message": "No Model Selected"}), 400


@application.route("/getMemory", methods=["POST"])
def getMemory():
    msgs = get_raw_memory()
    return jsonify({"status":"ok","messages": msgs})