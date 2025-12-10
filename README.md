# Amadeus

12/9/2025
✨ Major Backend Architecture Overhaul

Replaced legacy OpenAI client with a fully vendor-agnostic OpenRouter HTTP API integration.

Implemented new request flow using:

requests.post

explicit model selection (deepseek/deepseek-chat-v3.1)

custom personality + memory context system

Improved backend modularity and future-proofed all model calls.

🧠 Memory System Upgrade

Replaced volatile in-RAM memory with persistent file-based memory:

Memory is now stored in txtfiles/memory.txt.

Memory loads automatically on startup.

Memory updates after every user message.

Eliminated previous queue-based memory; now uses a persistent conversation history.

Improved reliability and enabled Amadeus to “remember” across restarts.

📝 Personality System Externalization

Personality prompt moved from hardcoded Python into txtfiles/personality.txt.

Backend now loads personality dynamically at startup.

Allows persona changes without modifying backend code.

🔑 Automatic API Key Persistence

Added txtfiles/api_key.txt to store the user’s OpenRouter key.

Implemented:

setKey()

updateAPIKEY()

auto-load key on startup

Eliminated need for user to re-enter API key every session.

Fixed bug where file was being read twice (causing empty key overwrite).

🌐 Flask Server Integration Update

Updated Flask app (appOpenRouter.py) to use new OpenRouter-based backend.

Cleaned / route logic:

Generate English assistant reply

Translate to Japanese for TTS

Trigger voice generation & playback

Ensured compatibility with Unity frontend.

🔊 TTS Pipeline Preparation

Prepared backend for migration from gpt_sovits_python wrapper to true GPT-SoVITS.

Established integration boundaries:

generateVoice(text)

play_sound()

Ensured future TTS engine swaps will not break existing backend/UI.

🗂️ Project Path Fixes & Reliability Improvements

Fixed absolute path issues (/txtfiles/...) → corrected to project-relative paths.

Ensured personality, memory, and key files load correctly regardless of working directory.

Improved file-not-found handling for clean startup on first install.

🚀 Project Stability & Maintainability Enhancements

Code reorganized for clarity and easier debugging.

Standardized message structure (role: system/user/assistant).

Improved modularity across:

AmadeusOpenRouter.py

appOpenRouter.py

Unity API key sender

Cleaned up indentation, casing errors, and import consistency.
