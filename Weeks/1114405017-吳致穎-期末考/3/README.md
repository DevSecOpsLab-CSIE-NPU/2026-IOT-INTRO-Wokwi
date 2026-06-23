# 題目三 — 雲端 PPM 告警 (MQTT → ThingsBoard)

功能：讀取 MQ2 的 ADC 值，換算為 ppm，並每 5 秒透過 MQTT 上傳至 ThingsBoard 的 `v1/devices/me/telemetry`。

使用前請修改 `main.py` 中的：
- `WIFI_SSID`, `WIFI_PASS`：你的 WiFi 資訊
- `TB_TOKEN`：你在 ThingsBoard 建立裝置後得到的 Access Token
- `THRESHOLD`：ppm 的警示門檻

執行（先在 Wokwi 啟動模擬）：

Windows (PowerShell)：
```
cd D:\2026-IOT-INTRO-Wokwi\Weeks\1114405017-吳致穎-期末考\3
.\make.bat
```

或直接：
```
C:/Users/User/AppData/Local/Programs/Python/Python39/python.exe D:\2026-IOT-INTRO-Wokwi\tools\wokwi_run.py --port 4000 main.py
```

說明：程式會在 Serial 印出 debug 資訊，並上傳 JSON telemetry 例如 `{"gas_ppm": 132}`。在 ThingsBoard 的 Device → Latest telemetry 可看到資料流入，並可在 Device profile 建立 Alarm rule。
