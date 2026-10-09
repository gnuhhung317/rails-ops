@echo off
setlocal
title CompressorGuard - Lisbon Metro APU-COMP-01 Command Console

echo ================================================================================
echo   Launching CompressorGuard - Industrial Operations Command Platform
echo   MUGVN Hackathon 2026: MongoDB + Datadog Unified Observability
echo ================================================================================

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH. Please install Python 3.10+ and try again.
    pause
    exit /b 1
)

python run_demo.py

if %errorlevel% neq 0 (
    echo.
    echo Server exited with an error code.
    pause
)
