# 系統診斷面板 - 使用說明

## 概述
這是一個完整的系統診斷工具，可以檢查你的所有工具（翻譯、DevOps、Outlook等）的健康狀態。

## 功能特性
✅ **Python環境檢查**
- Python版本、執行路徑
- Pip版本
- 虛擬環境狀態

✅ **依賴包檢查**
- faster-whisper、soundcard、deep-translator等
- 自動檢測缺失包並提示安裝命令

✅ **系統資源監控**
- CPU使用率
- 記憶體使用率和詳情
- 磁碟空間使用情況

✅ **音訊設備檢查**
- 列出所有可用的麥克風
- 檢測Loopback/Stereo Mix設備

✅ **網路服務檢查**
- Google翻譯API連接性
- Microsoft Graph API（Outlook）連接性
- 互聯網連接狀態
- 本地診斷服務狀態

✅ **實時告警**
- 自動檢測問題並顯示友好的告警
- 提示修復建議

## 快速開始

### 方法1：使用批處理文件（推薦）
```batch
# 雙擊運行
啟動-診斷面板.bat
```

### 方法2：手動啟動

#### 1. 打開PowerShell或命令提示字符
```powershell
cd c:\Users\panian\Ian-sTool
```

#### 2. 激活虛擬環境（如果有的話）
```powershell
.\.venv\Scripts\Activate.ps1
```

#### 3. 安裝診斷服務依賴（首次使用）
```powershell
pip install flask flask-cors psutil
```

#### 4. 啟動診斷服務
```powershell
python diagnosis_service.py
```

#### 5. 打開瀏覽器訪問
在瀏覽器中打開：
```
http://localhost:5555/diagnosis_dashboard.html
```

或者直接用File Explorer打開：
```
c:\Users\panian\Ian-sTool\diagnosis_dashboard.html
```

## 頁面說明

### 📊 摘要區域
- **總檢查項**：執行的檢查總數
- **正常**：通過的檢查數（綠色）
- **警告**：需要注意的項目（橙色）
- **錯誤**：需要修復的項目（紅色）

### 🔍 狀態卡片
快速概覽各工具狀態：
- 🗣️ 桌面即時翻譯
- 📊 DevOps儀表板
- 📧 Outlook工具
- 📈 台灣股票

### 🐍 Python環境
- Python版本和路徑
- Pip版本
- 虛擬環境狀態

### 📦 依賴包檢查
所有必要套件的安裝狀態和版本

### 💻 系統資源
- CPU使用率（實時）
- 記憶體使用率和詳細信息
- 磁碟空間使用情況

### 🎙️ 音訊設備
列出所有可用的音訊輸入設備

### 🌐 網路與服務
檢查各項服務的連接狀態和延遲

## 常見問題

### ❌ "無法連接診斷服務"
**解決方案：**
1. 確保 `diagnosis_service.py` 已啟動
2. 檢查5555端口是否被占用
3. 嘗試重新啟動診斷服務

### ⚠️ "缺少依賴: faster-whisper"
**解決方案：**
```powershell
pip install faster-whisper
```

### ⚠️ "未檢測到Loopback設備"
**解決方案：**
1. 安裝VB-CABLE虛擬音訊線（推薦）
   - 訪問: https://vb-audio.com/Cable/
2. 或啟用Stereo Mix（Windows）
   - 右鍵音量圖標 → 音效設定 → 錄音 → 啟用"立體聲混音"

### ❌ "網路連接失敗"
**解決方案：**
1. 檢查互聯網連接
2. 檢查防火牆設置
3. 嘗試重啟路由器

## 按鈕功能

### 🔄 重新診斷
重新執行所有檢查。適合在修復問題後用來驗證

### 📥 匯出報告
將診斷結果導出為JSON或PDF文件（開發中）

## 故障排除

### 服務無法啟動
```powershell
# 檢查是否有其他進程占用5555端口
netstat -ano | findstr :5555

# 查看進程詳情
Get-Process -Id <PID>

# 終止占用端口的進程
Stop-Process -Id <PID> -Force
```

### 某個檢查項失敗
1. 查看頁面上的告警信息（通常有修復建議）
2. 按照建議執行命令
3. 點擊「重新診斷」按鈕驗證修復

## API端點

### GET /api/diagnose
執行完整診斷並返回JSON結果

**示例：**
```powershell
Invoke-WebRequest -Uri http://localhost:5555/api/diagnose | ConvertFrom-Json
```

**響應格式：**
```json
{
    "timestamp": "2026-09-09T10:30:00",
    "summary": {
        "total_checks": 20,
        "passed": 18,
        "warnings": 1,
        "errors": 1
    },
    "alerts": [...],
    "tools": {...},
    "python": {...},
    "dependencies": [...],
    "resources": {...},
    "audio_devices": [...],
    "services": [...]
}
```

## 技術架構

- **前端**: HTML5 + CSS3 + Vanilla JavaScript
- **後端**: Python Flask + CORS
- **監控**: psutil（系統資源）、soundcard（音訊設備）

## 許可證
MIT License
