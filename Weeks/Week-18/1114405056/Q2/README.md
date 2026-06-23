# Q2 — 感測讀取與 OLED 顯示

示範使用 `ESP32 + DHT22 + MQ2 + SSD1306`：每 2 秒讀取 DHT22 溫濕度與 MQ2 氣體電壓，換算並顯示於 128x64 OLED。

設定（必要）
- 若你的學號決定 DHT / MQ2 腳位，請編輯 `main.py` 的 `DHT_PIN` 與 `MQ2_ADC_PIN`，並確保 `diagram.json` 的連線一致。

執行
1. 在 Wokwi 開啟 `diagram.json` 並按 Run。
2. 上傳並執行 `main.py`（或使用本 repo 的 `tools/wokwi_run.py` 上傳执行）。

範例截圖
- 已在此資料夾新增 `screenshot.svg`，示範 OLED 顯示畫面（包含標題與三項數值）。

注意
- `read_mq2_ppm()` 使用示範性的換算公式，非實驗室精確校正；若要精確 PPM，需先量測 R0 並套用 MQ2 的曲線參數。
