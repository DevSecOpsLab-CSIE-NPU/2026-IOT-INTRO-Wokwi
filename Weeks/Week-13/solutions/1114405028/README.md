# Week-13 Homework — SH1107 中文動畫溫度看板（1114405028）

簡述

本作品整合 `SH1107` OLED 與 `DHT22` 感測器，呈現類似課堂 `task3a` 的版型與動畫，同時每 2 秒讀取一次 DHT22 並在畫面上以 `xx.x C` 顯示。

版面配置

- 主視覺（左中）：一個圓與中心星形，類似龍珠主視覺。
- 英文標題與學號（左上）：`SH1107 Temp` 與 `1114405028`，確保學號可見以便驗收。
- 中文動畫（右側直排）：`花火節` 三字直排，使用縮放與上下波動的動畫效果。
- 溫度區塊（左中偏下）：顯示 `xx.x C`，每 2 秒更新一次感測值。

動畫設計

- 動畫主要以每 200 ms 更新一幀（`FRAME_DELAY_MS = 200`），在幀中切換字的縮放（`shrink` 值在 1 與 2 間切換）並配合簡單的上下位移，達成放大/縮小與波浪舞效果。

感測整合

- 使用 MicroPython 內建 `dht` 模組讀取 DHT22。
- 讀值以 `read_sensor_safe()` 包裝，包含 `try/except`，若失敗會在序列印出錯誤並於 OLED 顯示 `Sensor Error`，不會讓程式當掉。

實作重點與調校

- 顯示驅動為 `sh1107`，螢幕尺寸 128x128，`rotate=90`。
- 可調常數：`center_x/center_y`、`FRAME_DELAY_MS`、`SENSOR_INTERVAL_MS`。
- 程式採非阻塞設計，使用 `ticks_ms` 控制動畫與讀值頻率，避免長時間阻塞導致畫面停頓。

已附檔案

- `main.py`：主程式。可直接上傳至開發板或在 Wokwi 執行（注意 I2C 與 DHT 接腳需與 `diagram.json` 一致）。
- `pr.md`：PR 說明模板。

遇到問題與解法

- 問題：中文點陣繪製可能跨越畫面邊界導致破圖。
- 解法：採逐像素繪製（從 bytearray 轉 FrameBuffer 再用 `blit` 或 pixel sampling），並在直排文字採用 `wrap_y=True` 處理跨底部回卷。

執行方式（Wokwi / 實體板）

1. 確認 `I2C` 與 `DHT` 接腳符合 `diagram.json`。
2. 確保 `lib/sh1107.py` 與 `dht` 可用。
3. 上傳 `main.py` 到板子並執行，或在模擬器中執行 `make run`。

驗收重點

- 畫面能看到中文 `花火節`、即時溫度 `xx.x C`、以及學號 `1114405028`。
- Serial Monitor 有 `temperature` 與 `humidity` 的 debug 輸出。
- 感測失敗時顯示 `Sensor Error` 而非程式當掉。