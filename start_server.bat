@echo off
echo === PRD to Code Generator - Backend Server ===
echo.
echo Installing requirements...
pip install -r requirements.txt
echo.
echo Starting Flask server...
echo.
echo Server will run at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py