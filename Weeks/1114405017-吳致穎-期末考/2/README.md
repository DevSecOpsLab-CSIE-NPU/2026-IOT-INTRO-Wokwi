# 題目二 — 感測讀取與 OLED 顯示

內容：使用 DHT22 讀溫溼度，MQ2（ADC）讀氣體偵測值，並用 SSD1306 OLED (I2C, 128x64) 每 2 秒顯示一次。

執行：

1. 在 Wokwi 開啟並啟動本資料夾內的 `diagram.json`（確認 I2C 接腳為 SCL=GPIO22, SDA=GPIO21）。
2. 在此資料夾執行：

Windows (PowerShell)：
```
.\make.bat
```

或直接用 Python 執行 runner：
```
C:/Users/User/AppData/Local/Programs/Python/Python39/python.exe D:\2026-IOT-INTRO-Wokwi\tools\wokwi_run.py --port 4000 main.py
```

3. 若需修改 DHT 或 MQ2 腳位，編輯 `main.py` 上方的 `DHT_PIN` 與 `MQ2_ADC_PIN` 設定。
