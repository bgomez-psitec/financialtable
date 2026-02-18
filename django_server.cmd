@echo off
setlocal enabledelayedexpansion

set "PID_FILE=.django_runserver.pid"

if /I "%1"=="start" goto :start
if /I "%1"=="stop" goto :stop

echo Usage: %~nx0 start ^| stop
exit /b 1

:start
if exist "%PID_FILE%" (
  echo Server already running? PID file exists: %PID_FILE%
  exit /b 1
)
for /f "usebackq delims=" %%p in (`
  powershell -NoProfile -Command ^
    "$p = Start-Process -PassThru -WorkingDirectory (Get-Location) -FilePath python -ArgumentList 'manage.py','runserver'; $p.Id"
`) do set "PID=%%p"
if not defined PID (
  echo Failed to start server.
  exit /b 1
)
echo %PID%>"%PID_FILE%"
echo Server started. PID: %PID%
exit /b 0

:stop
if not exist "%PID_FILE%" (
  echo PID file not found: %PID_FILE%
  exit /b 1
)
set /p PID=<"%PID_FILE%"
taskkill /PID %PID% /T /F >nul 2>&1
del "%PID_FILE%" >nul 2>&1
echo Server stopped.
exit /b 0
