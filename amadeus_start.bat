@echo off
setlocal enabledelayedexpansion

REM ==================================================
REM Amadeus Project Launcher (Windows)
REM ==================================================

set "PROJECT_ROOT=%USERPROFILE%\Desktop\Amadeus Project"

set "SOVITS_ROOT=%PROJECT_ROOT%\GPT-SoVITS"
set "AMADEUS_DIR=%PROJECT_ROOT%\Amadeus"
set "UNITY_EXE=%PROJECT_ROOT%\Builds\Amadeus_UI.exe\Amadeus.exe"

set "PY_GPTSOVITS=C:\ProgramData\anaconda3\envs\GPTSoVits\python.exe"
set "PY_AMADEUS=C:\ProgramData\anaconda3\envs\amadeus\python.exe"

REM --- Where GPT-SoVITS should become reachable ---
set "SOVITS_URL=http://127.0.0.1:9872/"
set "WAIT_SECONDS=180"

REM --- GPT-SoVITS (MATCHES POWERSHELL BEHAVIOR) ---
start "GPT-SoVITS" /min cmd /c ^
  "cd /d "%SOVITS_ROOT%" && set PYTHONPATH=. && "%PY_GPTSOVITS%" GPT_SoVITS\inference_webui.py"

REM --- Amadeus backend ---
start "Amadeus Backend" /min cmd /c ^
  "cd /d "%AMADEUS_DIR%" && "%PY_AMADEUS%" main.py"

REM --- Wait for GPT-SoVITS to become ready ---
echo Waiting for GPT-SoVITS at %SOVITS_URL% (up to %WAIT_SECONDS%s) ...
set "ELAPSED=0"

:wait_loop
powershell -NoProfile -Command ^
  "try { $r = Invoke-WebRequest -UseBasicParsing -TimeoutSec 1 '%SOVITS_URL%'; exit 0 } catch { exit 1 }"
if %ERRORLEVEL%==0 goto ready

timeout /t 1 /nobreak >nul
set /a ELAPSED+=1
if %ELAPSED% GEQ %WAIT_SECONDS% goto timeout

goto wait_loop

:ready
echo GPT-SoVITS is ready. Launching Unity...
start "" "%UNITY_EXE%"
goto end

:timeout
echo ERROR: Timed out waiting for GPT-SoVITS after %WAIT_SECONDS% seconds.
echo Unity will NOT be started.
exit /b 1

:end
endlocal