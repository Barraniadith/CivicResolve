@echo off
title CivicResolve - AI-Powered Citizen Grievance Platform
echo ========================================================
echo  CivicResolve: AI Citizen Grievance Management
echo  PromptWars x GDG on-Campus PSG iTech Hackathon
echo ========================================================
echo Starting FastAPI Backend + Web Application...
cd /d "%~dp0"
py -3 run.py
if errorlevel 1 (
    echo.
    echo Trying direct python path...
    "C:\Users\Admin\AppData\Local\Programs\Python\Python313\python.exe" run.py
)
pause
