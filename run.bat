@echo off
echo === PRD to Code Generator ===
echo     Gemini 2.5 Pro - 900k Token Limit
echo =====================================
echo.
echo Choose an option:
echo 1. Start Web Server (RECOMMENDED)
echo 2. Open Web Interface
echo 3. Generate from command line (single file)
echo 4. Generate from command line (multiple files)
echo 5. Install requirements
echo 6. Set API key
echo 7. Test API connection
echo 8. View configuration
echo.
set /p choice="Enter your choice (1-8): "

if "%choice%"=="1" (
    start cmd /k python app.py
    timeout /t 3
    start http://localhost:5000
) else if "%choice%"=="2" (
    start http://localhost:5000
) else if "%choice%"=="3" (
    python generate_from_file.py
) else if "%choice%"=="4" (
    python generate_multi_files.py
) else if "%choice%"=="5" (
    pip install -r requirements.txt
    echo.
    echo Requirements installed!
    pause
) else if "%choice%"=="6" (
    set /p apikey="Enter your OpenRouter API key: "
    setx OPENROUTER_API_KEY "%apikey%"
    echo API key saved!
    pause
) else if "%choice%"=="7" (
    python test_api.py
    pause
) else if "%choice%"=="8" (
    python start.py
) else (
    echo Invalid choice!
    pause
)
