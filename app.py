from flask import Flask, request, jsonify
from Amadeus import getOutput, getTranslation
from AmadeusSpeak import generateVoice, play_sound
from flask_cors import CORS
import threading

application = Flask(__name__)
CORS(application)

@application.route("/", methods=["POST"])
def request_message():
    content = request.get_json()
    user_input = content.get("user_input", "")
    result = getOutput(user_input)
    generateVoice(result)
    result = getTranslation(result)
    threading.Thread(target=play_sound).start()
    return jsonify({"response": result})