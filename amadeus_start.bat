@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ============================================================
REM Amadeus Launcher (Windows .bat)
REM - Starts GPT-SoVITS (Conda env: GPTSoVits)
REM - Waits for it to be ready
REM - Starts Amadeus backend (Conda env: amadeus)
REM - Launches Unity frontend and waits until it closes
REM - Then shuts everything down + writes logs
REM ============================================================

REM =======================
REM EDIT THESE PATHS
REM =======================
set "PROJECT_ROOT=%USERPROFILE%\Desktop\Amadeus Project"
set "AMADEUS_DIR=%PROJECT_ROOT%\Amadeus"
set "SOVITS_DIR=%PROJECT_ROOT%\GPT-SoVITS"

REM Unity Windows build usually looks like: <folder>\YourApp.exe
set "UNITY_EXE=%PROJECT_ROOT%\Builds\Amadeus_UI.exe"

REM Gradio/SoVITS URL + port
set "SOVITS_URL=http://127.0.0.1:9872/"
set "SOVITS_PORT=9872"

REM Path to conda activate.bat (Anaconda/Miniconda)
REM Common defaults:
REM   %USERPROFILE%\anaconda3\Scripts\activate.bat
REM   %USERPROFILE%\miniconda3\Scripts\activate.bat
set "CONDA_ACTIVATE=%USERPROFILE%\anaconda3\Scripts\activate.bat"
REM =======================

echo Project root: "%PROJECT_ROOT%"

if not exist "%PROJECT_ROOT%" (
  echo ERROR: PROJECT_ROOT not found: "%PROJECT_ROOT%"
  exit /b 1
)

if not exist "%CONDA_ACTIVATE%" (
  echo ERROR: conda activate not found at: "%CONDA_ACTIVATE%"
  echo Fix CONDA_ACTIVATE in this .bat to your Anaconda/Miniconda activate.bat
  exit /b 1
)

REM Create/clear log files (like your mac script)
echo Creating log files...
break> "%PROJECT_ROOT%\log_sovits.txt"
break> "%PROJECT_ROOT%\log_amadeus.txt"

REM Everything below is done in PowerShell so we can:
REM - reliably get PIDs
REM - wait for URL
REM - try/finally cleanup
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference='Stop';" ^
  "$PROJECT_ROOT=$env:PROJECT_ROOT;" ^
  "$AMADEUS_DIR=$env:AMADEUS_DIR;" ^
  "$SOVITS_DIR=$env:SOVITS_DIR;" ^
  "$UNITY_EXE=$env:UNITY_EXE;" ^
  "$SOVITS_URL=$env:SOVITS_URL;" ^
  "$SOVITS_PORT=[int]$env:SOVITS_PORT;" ^
  "$CONDA_ACTIVATE=$env:CONDA_ACTIVATE;" ^
  "" ^
  "function Kill-Port($port) {" ^
  "  $pids = @();" ^
  "  try {" ^
  "    $lines = netstat -aon | Select-String (':'+$port+'\s+.*LISTENING');" ^
  "    foreach($l in $lines) {" ^
  "      $parts = ($l.Line -split '\s+') | Where-Object { $_ -ne '' };" ^
  "      if($parts.Count -ge 5) { $pids += [int]$parts[-1] }" ^
  "    }" ^
  "  } catch {}" ^
  "  $pids = $pids | Sort-Object -Unique;" ^
  "  foreach($pid in $pids) {" ^
  "    if($pid -and $pid -ne 0) {" ^
  "      Write-Host ('Port {0} in use. Killing PID {1}...' -f $port,$pid);" ^
  "      try { Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue } catch {}" ^
  "    }" ^
  "  }" ^
  "}" ^
  "" ^
  "function Wait-Url($url, $seconds) {" ^
  "  Write-Host ('Waiting for GPT-SoVITS to become ready at {0} ...' -f $url);" ^
  "  $deadline = (Get-Date).AddSeconds($seconds);" ^
  "  while((Get-Date) -lt $deadline) {" ^
  "    try {" ^
  "      $req = [System.Net.WebRequest]::Create($url);" ^
  "      $req.Timeout = 1000;" ^
  "      $resp = $req.GetResponse();" ^
  "      $resp.Close();" ^
  "      Write-Host 'GPT-SoVITS is ready.';" ^
  "      return;" ^
  "    } catch {" ^
  "      Start-Sleep -Seconds 1;" ^
  "    }" ^
  "  }" ^
  "  throw ('Timed out waiting for GPT-SoVITS at ' + $url);" ^
  "}" ^
  "" ^
  "$sovitsProc=$null; $amadeusProc=$null;" ^
  "try {" ^
  "  Kill-Port $SOVITS_PORT;" ^
  "" ^
  "  Write-Host 'Starting GPT-SoVITS...';" ^
  "  $sovitsLog = Join-Path $PROJECT_ROOT 'log_sovits.txt';" ^
  "  $sovitsCmd = 'call \"' + $CONDA_ACTIVATE + '\" GPTSoVits ^&^& cd /d \"' + $SOVITS_DIR + '\" ^&^& python GPT_SoVITS\\inference_webui.py';" ^
  "  $sovitsProc = Start-Process -FilePath 'cmd.exe' -ArgumentList @('/c', $sovitsCmd) -WindowStyle Hidden -PassThru -RedirectStandardOutput $sovitsLog -RedirectStandardError $sovitsLog;" ^
  "" ^
  "  Wait-Url $SOVITS_URL 180;" ^
  "" ^
  "  Write-Host 'Starting Amadeus backend...';" ^
  "  $amadeusLog = Join-Path $PROJECT_ROOT 'log_amadeus.txt';" ^
  "  $amadeusCmd = 'call \"' + $CONDA_ACTIVATE + '\" amadeus ^&^& cd /d \"' + $AMADEUS_DIR + '\" ^&^& python main.py';" ^
  "  $amadeusProc = Start-Process -FilePath 'cmd.exe' -ArgumentList @('/c', $amadeusCmd) -WindowStyle Hidden -PassThru -RedirectStandardOutput $amadeusLog -RedirectStandardError $amadeusLog;" ^
  "" ^
  "  Write-Host '';" ^
  "  Write-Host '✅ Started everything';" ^
  "  Write-Host ('Logs:' );" ^
  "  Write-Host ('  GPT-SoVITS -> ' + $sovitsLog);" ^
  "  Write-Host ('  Amadeus    -> ' + $amadeusLog);" ^
  "  Write-Host '';" ^
  "  Write-Host 'PIDs:';" ^
  "  if($sovitsProc){ Write-Host ('  GPT-SoVITS: ' + $sovitsProc.Id) }" ^
  "  if($amadeusProc){ Write-Host ('  Amadeus:    ' + $amadeusProc.Id) }" ^
  "  Write-Host '';" ^
  "" ^
  "  Write-Host 'Launching Unity app...';" ^
  "  if(!(Test-Path $UNITY_EXE)) { throw ('Unity exe not found at: ' + $UNITY_EXE + '  (Fix UNITY_EXE in the .bat)') }" ^
  "  Start-Process -FilePath $UNITY_EXE -Wait;" ^
  "  Write-Host 'Unity app closed.';" ^
  "} finally {" ^
  "  Write-Host '';" ^
  "  Write-Host 'Shutting down services...';" ^
  "  if($amadeusProc -and -not $amadeusProc.HasExited) {" ^
  "    Write-Host ('Stopping Amadeus backend (PID ' + $amadeusProc.Id + ')...');" ^
  "    try { Stop-Process -Id $amadeusProc.Id -Force -ErrorAction SilentlyContinue } catch {}" ^
  "  }" ^
  "  if($sovitsProc -and -not $sovitsProc.HasExited) {" ^
  "    Write-Host ('Stopping GPT-SoVITS (PID ' + $sovitsProc.Id + ')...');" ^
  "    try { Stop-Process -Id $sovitsProc.Id -Force -ErrorAction SilentlyContinue } catch {}" ^
  "  }" ^
  "  Write-Host '✅ Clean shutdown complete.';" ^
  "}"

if errorlevel 1 (
  echo.
  echo ERROR: Something failed to start. Check logs:
  echo   "%PROJECT_ROOT%\log_sovits.txt"
  echo   "%PROJECT_ROOT%\log_amadeus.txt"
)

echo.
pause
endlocal
