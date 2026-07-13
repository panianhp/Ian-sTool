# Desktop 即時英翻中 (Windows)

這個工具可直接擷取 Windows 播放中的音訊來源（loopback），將英文語音即時轉文字並翻成繁中。

## 1) 建立虛擬環境（建議）

```powershell
cd c:\Users\panian\Ian-sTool
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 2) 安裝套件

```powershell
pip install -r requirements-desktop-translator.txt
```

## 3) 啟動

```powershell
python desktop_realtime_translator.py
```

## 4) 使用方式

1. 在 Audio Source 選擇名稱帶有 `Loopback` 或 `Stereo Mix` 的來源。
2. 按 Start。
3. 播放 YouTube 英文影片。
4. 上方會出現英文逐句辨識，下方會出現繁中翻譯。

## 常見問題

- 看不到 loopback 裝置:
  - 先確認音效輸出裝置正常，重新按 Refresh Sources。
  - 有些裝置驅動不提供 loopback，可安裝 VB-CABLE 後改選其輸入。

- 延遲太高:
  - 將 Chunk Seconds 調到 2.0 或 2.5。
  - 將 Whisper Model 改為 `base`。

- 辨識品質不佳:
  - 將 Whisper Model 改為 `medium`（CPU 會更慢）。
  - 提升影片音量，降低背景噪音。
