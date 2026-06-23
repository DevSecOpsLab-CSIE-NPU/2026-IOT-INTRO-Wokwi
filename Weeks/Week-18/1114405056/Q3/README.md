# Q3 — 雲端 PPM 告警 (MQTT → ThingsBoard)

說明
- 讀取 MQ2 的 gas_ppm，並每 5 秒透過 MQTT 上傳到 ThingsBoard Cloud（topic: `v1/devices/me/telemetry`）。
- 當 `gas_ppm` 超過 `THRESHOLD` 時，程式會在 Serial 印出 `[ALARM]`，並由你在 ThingsBoard 建立 Alarm 規則自動產生雲端 Alarm。

使用說明
1. 在 ThingsBoard Cloud 建立一個 Device，取得其 **Access Token**（Device Credentials）。
2. 編輯 `main.py`：把 `THINGSBOARD_TOKEN` 設為你的裝置 Token，並把 `THRESHOLD` 設為你的門檻值。
3. 在 Wokwi 開啟 `diagram.json` 並按 Run，或把程式上傳到實體 ESP32。
4. 執行 `main.py`，應可在 Serial 看到類似：
   ```
   [DEBUG] gas_ppm=123 raw=58062 V=2.92
   [ALARM] gas_ppm 350 > 300
   ```
5. 在 ThingsBoard 裡的 Device → Latest telemetry 檢視 `gas_ppm` 是否持續更新。
6. 建立 Alarm rule（在 Device profile → Alarm rules）：設定當 `gas_ppm > THRESHOLD` 時產生 Alarm，回到低於則清除。

提示
- Wokwi 使用網路模擬器，可選 WiFi SSID `Wokwi-GUEST`（無密碼）。
- MQTT 連線設定已預設為 `mqtt.thingsboard.cloud:1883`，Device Token 當作 username 使用。
