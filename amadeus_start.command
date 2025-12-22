#!/bin/bash
set -e

# ====== EDIT IF NEEDED ======
PROJECT_ROOT="$HOME/Desktop/Amadeus Project"
AMADEUS_DIR="$PROJECT_ROOT/Amadeus"
SOVITS_DIR="$PROJECT_ROOT/GPT-SoVITS"

UNITY_APP="$PROJECT_ROOT/Builds/Amadeus_UI.app"   # change if different
SOVITS_URL="http://127.0.0.1:9872/"              # change if your gradio port differs
SOVITS_PORT=9872
# ============================

# Initialize (so cleanup is safe even if something fails early)
AMADEUS_PID=""
SOVITS_PID=""

cleanup() {
  echo ""
  echo "Shutting down services..."

  if [[ -n "$AMADEUS_PID" ]] && ps -p "$AMADEUS_PID" >/dev/null 2>&1; then
    echo "Stopping Amadeus backend (PID $AMADEUS_PID)..."
    kill "$AMADEUS_PID" 2>/dev/null || true
    wait "$AMADEUS_PID" 2>/dev/null || true
  fi

  if [[ -n "$SOVITS_PID" ]] && ps -p "$SOVITS_PID" >/dev/null 2>&1; then
    echo "Stopping GPT-SoVITS (PID $SOVITS_PID)..."
    kill "$SOVITS_PID" 2>/dev/null || true
    wait "$SOVITS_PID" 2>/dev/null || true
  fi

  echo "✅ Clean shutdown complete."
}
trap cleanup EXIT INT TERM

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
if lsof -nP -iTCP:${SOVITS_PORT} -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port ${SOVITS_PORT} is in use. Killing the process using it..."
  kill -9 $(lsof -t -iTCP:${SOVITS_PORT} -sTCP:LISTEN) 2>/dev/null || true
fi

# --- Start GPT-SoVITS (Conda env: GPTSoVits) ---
echo "Starting GPT-SoVITS..."
conda activate GPTSoVits
cd "$SOVITS_DIR"                       # repo root
nohup python GPT_SoVITS/inference_webui.py > "$PROJECT_ROOT/log_sovits.txt" 2>&1 &
SOVITS_PID=$!
conda deactivate

# --- Wait for Gradio to respond ---
echo "Waiting for GPT-SoVITS to become ready at $SOVITS_URL ..."
python3 - <<PY
import time, urllib.request
url = "${SOVITS_URL}"
for _ in range(180):
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

# --- Launch Unity frontend and wait until it closes ---
echo "Launching Unity app..."
if [ -d "$UNITY_APP" ]; then
  open -W "$UNITY_APP"
  echo "Unity app closed."
else
  echo "ERROR: Unity app not found at: $UNITY_APP"
  echo "Edit UNITY_APP in the script to the correct .app path."
  exit 1
fi

# Optional: keep the terminal window open after Unity closes
read -n 1 -s -r -p "Press any key to close this window..."
echo ""
