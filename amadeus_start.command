#!/bin/bash
set -e

# ====== EDIT IF NEEDED ======
PROJECT_ROOT="$HOME/Desktop/Amadeus Project"
AMADEUS_DIR="$PROJECT_ROOT/Amadeus"
SOVITS_DIR="$PROJECT_ROOT/GPT-SoVITS"

UNITY_APP="$PROJECT_ROOT/Builds/Amadeus_UI.app"   # change if different
SOVITS_URL="http://127.0.0.1:9872/"            # change if your gradio port differs
# ============================

echo "Project root: $PROJECT_ROOT"

# --- Load conda so `conda activate` works in scripts ---
CONDA_SH="/opt/anaconda3/etc/profile.d/conda.sh"
if [ ! -f "$CONDA_SH" ]; then
  echo "ERROR: conda.sh not found at: $CONDA_SH"
  echo "If your Anaconda path differs, update CONDA_SH in the script."
  exit 1
fi
source "$CONDA_SH"


# --- Free the Gradio port if a previous instance is still running ---
if lsof -nP -iTCP:9872 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port 9872 is in use. Killing the process using it..."
  kill -9 $(lsof -t -iTCP:9872 -sTCP:LISTEN)
fi


# --- Start GPT-SoVITS (Conda env: GPTSoVits) ---
echo "Starting GPT-SoVITS WebUI..."
conda activate GPTSoVits
cd "$SOVITS_DIR"                       # ✅ repo root
nohup python GPT_SoVITS/inference_webui.py > "$PROJECT_ROOT/log_sovits.txt" 2>&1 &
SOVITS_PID=$!
conda deactivate


# --- Wait for Gradio to respond ---
echo "Waiting for GPT-SoVITS to become ready at $SOVITS_URL ..."
python3 - <<PY
import time, urllib.request
url = "${SOVITS_URL}"
for i in range(180):
    try:
        urllib.request.urlopen(url, timeout=1)
        print("GPT-SoVITS is ready.")
        raise SystemExit(0)
    except Exception:
        time.sleep(1)
raise SystemExit("Timed out waiting for GPT-SoVITS.")
PY

# --- Start Amadeus backend (Conda env: amadeus) ---
echo "Starting Amadeus backend..."
conda activate amadeus
cd "$AMADEUS_DIR"
nohup python main.py > "$PROJECT_ROOT/log_amadeus.txt" 2>&1 &
AMADEUS_PID=$!
conda deactivate

# --- Launch Unity frontend ---
echo "Launching Unity app..."
if [ -d "$UNITY_APP" ]; then
  open "$UNITY_APP"
else
  echo "WARNING: Unity app not found at: $UNITY_APP"
  echo "Edit UNITY_APP in the script to the correct .app path."
fi

echo ""
echo "✅ Started everything"
echo "Logs:"
echo "  GPT-SoVITS → $PROJECT_ROOT/log_sovits.txt"
echo "  Amadeus   → $PROJECT_ROOT/log_amadeus.txt"
echo ""
echo "PIDs:"
echo "  GPT-SoVITS: $SOVITS_PID"
echo "  Amadeus:    $AMADEUS_PID"
echo ""
read -n 1 -s -r -p "Press any key to close this window..."
