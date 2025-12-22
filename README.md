# Amadeus
## Setup (Conda Recommended)

This project uses a Conda environment.

### 1. Install Conda
Install Miniconda or Anaconda:
https://docs.conda.io/en/latest/miniconda.html

### 2. Clone the repository
```
bash
git clone https://github.com/reflectors02/Amadeus.git
cd Amadeus
```

### 3. Create Virtual Enviroment
```
conda env create -f environment.yml
```

### 4. Activate the Environment

```
conda activate amadeus
```

### 5. From within the Amadeus folder
```
MACOS: python3 main.py
WINDOWS: python main.py
```

### 6. Run the .zip Amadeus APP when flask operations are complete



## Changelogs

### Amadeus – Release Notes (Model Control + Backend Stability) — 12/20/25

**New Features**

1. Runtime LLM Model Switching
   Added support for changing the active LLM model directly from the Unity UI.
   Users can now enter a model name (e.g. deepseek/deepseek-chat-v3-0324) and apply it without restarting the backend.

2. Current Model Display
   The active LLM model is now displayed in the settings panel.
   Unity queries the backend and reflects the currently selected model in real time.

3. Unity ↔ Flask Model API
   Implemented /setLLMModel and /getCurrLLMModel endpoints.
   Enables clean, stateless communication between the Unity frontend and Python backend.

![Amadeus UI](Images/1220.png)


### Amadeus – Release Notes (Animations + QOL) — 12/12/25

**New Features**

1. Memory Reset Button
   Added a memory reset option to clear conversation context when token usage becomes too large.
   (Chat summarization support planned next.)

2. Return to Home Screen
   Users can now return to the home screen to:
   switch API keys
   reset memory
   restart sessions cleanly

3. Special Touch Interaction (Live2D)
   Added a special touch interaction on the Kurisu Live2D model.
   Triggers a unique animation and an annoyed voice line.

4. Conda Environment Support
   Added environment.yml to allow easy installation of the required Conda environment.

**Improvements**

1. UI Improvements

2. Improved Amadeus panel visuals

3. Better background assets

4. Larger, more readable fonts

5. Improved Thinking Animations
   Refined thinking animations for smoother and more expressive behavior.

![Amadeus UI](Images/1212.png)






### **Amadeus – Release Notes (OpenRouter Upgrade) --- 12/9/25**

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
