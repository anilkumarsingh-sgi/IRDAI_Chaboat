@echo off
REM ========== WORKSPACE CLEANUP SCRIPT ==========
REM Run this AFTER closing all terminal windows
REM This removes unnecessary files keeping only source code and documentation

echo Cleaning up workspace...
echo.

REM Remove Python cache
if exist __pycache__ (
    echo Removing __pycache__...
    rmdir /s /q __pycache__
)

REM Remove virtual environment
if exist IRDAI_GPT (
    echo Removing IRDAI_GPT (use pip install -r requirements.txt instead)...
    rmdir /s /q IRDAI_GPT
)

REM Remove data folder (PDFs, vectorstore)
if exist data (
    echo Removing data folder (PDFs and vectorstore will be regenerated)...
    rmdir /s /q data
)

REM Remove logs
if exist logs (
    echo Removing logs...
    rmdir /s /q logs
)

REM Remove any .pyc files
echo Removing .pyc files...
for /r . %%f in (*.pyc) do del /q "%%f" 2>nul

REM Remove .pyo files
echo Removing .pyo files...
for /r . %%f in (*.pyo) do del /q "%%f" 2>nul

echo.
echo ========== CLEANUP COMPLETE ==========
echo.
echo REMOVED:
echo   - __pycache__ (Python cache files)
echo   - IRDAI_GPT (virtual environment)
echo   - data/ (crawled PDFs, vectorstore, etc.)
echo   - logs/ (log files)
echo   - *.pyc, *.pyo (Python compiled files)
echo.
echo KEPT:
echo   - All source code (*.py files)
echo   - All documentation (*.md files)
echo   - Configuration files (.env, .streamlit/)
echo   - requirements.txt (for pip install)
echo   - Dockerfile and docker-compose.yml
echo.
echo Workspace is now lean and ready for deployment!
echo.
pause
