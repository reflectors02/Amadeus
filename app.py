from flask import Flask, request, jsonify
from Amadeus import getOutput, getTranslation, setKey
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

