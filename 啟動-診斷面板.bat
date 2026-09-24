@echo off
REM 系統診斷面板啟動腳本
REM 支持Windows中文環境

chcp 65001 > nul

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  🔍 Ian's Tool - 系統診斷面板
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM 檢查Python是否已安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤: Python未安裝或未在PATH中
    echo.
    echo 請先安裝Python 3.10+: https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo ✅ Python環境檢測成功
python --version
echo.

REM 檢查並進入工作目錄
cd /d "%~dp0"
if errorlevel 1 (
    echo ❌ 錯誤: 無法進入工作目錄
    pause
    exit /b 1
)

REM 檢查並激活虛擬環境
if exist ".venv\Scripts\activate.bat" (
    echo ✅ 檢測到虛擬環境，正在激活...
    call .venv\Scripts\activate.bat
) else (
    echo ⚠️  未檢測到虛擬環境
    echo 建議執行: python -m venv .venv
    echo.
)

REM 檢查必要的依賴包
echo 🔍 檢查必要的依賴包...
python -c "import flask; import flask_cors; import psutil" 2>nul
if errorlevel 1 (
    echo ⚠️  缺少依賴包，正在安裝...
    pip install flask flask-cors psutil
    if errorlevel 1 (
        echo ❌ 安裝失敗，請檢查網路連接
        pause
        exit /b 1
    )
)
echo ✅ 依賴包檢查完成
echo.

REM 啟動診斷服務
echo 🚀 正在啟動診斷服務...
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  診斷服務運行中...
echo  📍 訪問: http://localhost:5555/diagnosis_dashboard.html
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 按 Ctrl+C 停止服務
echo.

python diagnosis_service.py

pause
