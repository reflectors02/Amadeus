**Amadeus – Release Notes (OpenRouter Upgrade) --- 12/9/25**

**New Features**

1. OpenRouter Integration
   Replaced the old OpenAI client with a fully vendor-agnostic OpenRouter HTTP API.
   Model selection is now flexible and easily swappable (e.g., DeepSeek, Qwen, Llama).

2. Persistent Memory System
   Conversation context is now stored in:
   txtfiles/memory.txt
   Amadeus now remembers previous interactions across restarts.

3. Externalized Personality
   Personality prompt moved out of code and into:
   txtfiles/personality.txt
   Can now update Kurisu’s persona without modifying Python.

4. Automatic API Key Persistence
   API key is saved to and loaded from:
   txtfiles/api_key.txt
   No need for the user to re-enter the key every session.


**Improvements**

1. Updated Flask backend to use new OpenRouter-based response pipeline.

2. Clean separation between:
   -English chat output
   -Japanese TTS output (for GPT-SoVITS)

3. Fixed path issues by switching to project-relative paths.

4. Better error handling for memory/key loading.

5. Backend architecture simplified and made more maintainable.

6. UI-Improvements:
<img width="1924" height="1154" alt="image" src="https://github.com/user-attachments/assets/0d3a27e6-9b96-4d31-9b0a-bc321193bd92" />
