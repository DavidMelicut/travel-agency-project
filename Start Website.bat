@echo off
REM Porneste serverul si deschide site-ul in browser
cd /d "%~dp0backend"
call .venv\Scripts\activate.bat
start "" cmd /c "timeout /t 3 >nul & start http://127.0.0.1:8000/"
python main.py
pause
