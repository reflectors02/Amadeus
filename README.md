# Amadeus
## Setup (Conda Recommended)

This project uses a Conda environment.

### 1. Install Conda
Install Anaconda:
https://www.anaconda.com/


### 2. Clone the repository(s)
```
#NOTES: ALWAYS USE ANACONDA PROMPT, NEVER USE POWERSHELL. POWERSHELL CAUSES MAJOR PROBLEMS WITH CONDA

git clone https://github.com/reflectors02/Amadeus-Project.git
cd Amadeus-Project

#INSTALLING GPTSOVITS (IMPORTANT!)

# Clone the required GPT-SoVITS dependency inside the Amadeus-folder
git clone https://github.com/RVC-Boss/GPT-SoVITS.git


#CHECK IF THIS IS TRUE
Your repository should look like this:
Amadeus-Project/
├── Amadeus/
│   └── environment.yml
├── GPT-SoVITS/
│   ├── requirements.txt
│   └── extra-req.txt
└── Builds/
...

```

### 3. Create Virtual Environment(s)
```
#CREATING AMADEUS ENVIRONMENT

(cd into Amadeus-Project/Amadeus)
cd Amadeus
conda env create -f environment.yml


#CREATING GPTSOVITS ENVIRONMENT
cd ..
(you should now be returned to Amadeus-Project/)

cd GPT-SoVITS
(you should now be in Amadeus-Project/GPT-SoVITS)

conda create -n GPTSoVits python=3.10
conda activate GPTSoVits

pip install -r extra-req.txt --no-deps
pip install -r requirements.txt
```

### 4. NVIDIA GPU ONLY:

```
#If you have an NVIDIA GPU, run these commands to enable CUDA support:

conda activate GPTSoVits

# remove CPU-only torch packages
pip uninstall -y torch torchvision torchaudio

# install CUDA-enabled torch (Windows)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121```
``` 


### 5. Download required pretrained_models from huggingface

```
# This step requires Git LFS. If you don't have it, run: 'git lfs install'

conda activate GPTSoVITS
cd Amadeus-Project/GPT-SoVITS/GPT_SoVITS

git lfs install
git clone https://huggingface.co/lj1995/GPT-SoVITS

(This is a 5gb download! It will take a while)


Repo Check: Make sure the pretrained_models looks like this

Amadeus-Project/
├── Amadeus/
│   ├── main.py
│   └── run_gptsovits.py
├── GPT-SoVITS/
│   ├── GPT_SoVITS/
│   │   └── pretrained_models/
│   │       ├── chinese-hubert-base/
│   │       ├── chinese-roberta-wwm-ext-large/
│   │       ├── fast_langdetect/
│   │       ├── gsv-v2final-pretrained/
│   │       ├── gsv-v4-pretrained/
│   │       ├── models--nvidia--bigvgan_v2_24khz_100band_256x/
│   │       ├── s1bert25hz-2kh-longer-epoch.ckpt
│   │       ├── s1v3.ckpt
│   │       ├── s2D488k.pth
│   │       ├── s2G488k.pth
│   │       └── s2Gv3.pth
└── Builds/
    ├── Amadeus_UI.exe (Windows)
    └── Amadeus_UI.app (Mac)


```

### 6. Launch Procedures
```
#Note: This procedure will require the use of two terminal windows (Anaconda Prompt), so open two

Step 1: Launch GPT-SoVITS from terminal 1

conda activate GPTSoVits
# Navigate to the root folder first if you just opened the prompt
cd Amadeus-Project/Amadeus
python run_gptsovits.py


Step 2: Launch Flask server from terminal 2

conda activate amadeus
cd Amadeus-Project/Amadeus
python main.py


Step 3: Ensure both terminals are up and running without issue before doing this step!

MACOS: Run Amadeus-Project/Builds/Amadeus_UI.app
WINDOWS: Run Amadeus-Project/Builds/Amadeus_UI.exe/Amadeus.exe



Rule of thumb: This is a general guide that should work for most systems. I cannot possibly take care of every possibe scenario. If you encounter any issues not listed here, just ask chatgpt. 
```

### 7. Commonly encountered issues
```
TO BE DONE, NO USERS CURRENTLY
```

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


