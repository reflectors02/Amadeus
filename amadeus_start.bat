@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM =======================
REM EDIT THESE PATHS
REM =======================
set "PROJECT_ROOT=%USERPROFILE%\Desktop\Amadeus Project"
set "SOVITS_DIR=%PROJECT_ROOT%\GPT-SoVITS"
set "AMADEUS_DIR=%PROJECT_ROOT%\Amadeus"
set "UNITY_EXE=%PROJECT_ROOT%\Builds\Amadeus.exe"
set "SOVITS_PORT=9872"
set "SOVITS_URL=http://127.0.0.1:9872/"
REM =======================

echo Project root: "%PROJECT_ROOT%"

REM --- Find conda.bat reliably (works even if conda isn't initialized in this shell) ---
set "CONDA_BAT="
for /f "delims=" %%I in ('where conda 2^>nul') do (
  set "CONDA_EXE=%%I"
  goto :got_conda
)
:got_conda
if not defined CONDA_EXE (
  echo ERROR: Could not find conda on PATH. Open "Anaconda Prompt" once or add conda to PATH.
  pause
  exit /b 1
)

REM conda.exe usually lives in ...\condabin\conda.bat or ...\Scripts\conda.exe; we want conda.bat if possible
REM If `where conda` returns conda.exe, we can still run `conda` commands via it.
REM We'll just call `conda` directly.

REM --- Kill anything already listening on port 9872 (prevents "address already in use") ---
echo Checking port %SOVITS_PORT%...
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%SOVITS_PORT% .*LISTENING"') do (
  echo Port %SOVITS_PORT% is in use. Killing PID %%P ...
  taskkill /F /PID %%P >nul 2>&1
)

REM --- Start GPT-SoVITS ---
echo Starting GPT-SoVITS WebUI...
cd /d "%SOVITS_DIR%"

REM Run in a separate minimized window; write logs to PROJECT_ROOT
start "GPT-SoVITS" /min cmd /c ^
  "cd /d ""%SOVITS_DIR%"" && set PYTHONPATH=%SOVITS_DIR% && conda activate GPTSoVits && python GPT_SoVits\inference_webui.py > ""%PROJECT_ROOT%\log_sovits.txt"" 2>&1"
  
REM --- Wait for GPT-SoVITS HTTP to respond ---
echo Waiting for GPT-SoVITS to become ready at %SOVITS_URL% ...
powershell -NoProfile -Command ^
  "$u='%SOVITS_URL%';" ^
  "$ok=$false;" ^
  "for($i=0;$i -lt 180;$i++){" ^
  "  try { Invoke-WebRequest -UseBasicParsing -TimeoutSec 1 $u | Out-Null; $ok=$true; break } catch { Start-Sleep -Seconds 1 }" ^
  "}" ^
  "if(-not $ok){ Write-Host 'Timed out waiting for GPT-SoVITS.'; exit 1 }"

if errorlevel 1 (
  echo GPT-SoVITS did not start. Check: "%PROJECT_ROOT%\log_sovits.txt"
  pause
  exit /b 1
)

REM --- Start Amadeus backend ---
echo Starting Amadeus backend...
cd /d "%AMADEUS_DIR%"

start "Amadeus Backend" /min cmd /c ^
  "conda activate amadeus && python main.py > ""%PROJECT_ROOT%\log_amadeus.txt"" 2>&1"

REM --- Launch Unity frontend ---
echo Launching Unity app...
if exist "%UNITY_EXE%" (
  start "" "%UNITY_EXE%"
) else (
  echo WARNING: Unity EXE not found at:
  echo   "%UNITY_EXE%"
  echo Edit UNITY_EXE in this script.
)

echo.
echo ✅ Started everything
echo Logs:
echo   GPT-SoVITS: "%PROJECT_ROOT%\log_sovits.txt"
echo   Amadeus:    "%PROJECT_ROOT%\log_amadeus.txt"
echo.
pause
