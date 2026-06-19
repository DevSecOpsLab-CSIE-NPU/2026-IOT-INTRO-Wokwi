# Week 13 Homework：SH1107 + DHT22 中文動畫溫度看板

學號：`1114405055`

## 版面配置
畫面延續 `task3a` 的龍珠版型邏輯，分成四個區塊：
- 左上：英文資訊區塊（`Penghu Univ` / `Dept of CSIE`）與右上角 `2026`。
- 第三行：學號 `1114405055`，確保學號直接顯示在 OLED 上而非只在 README。
- 畫面中央偏左：龍珠主視覺（雙圓 + 一星），中心座標使用可調校常數 `dragon_center_x` / `dragon_center_y`（由 `center_x`、`center_y`、`offset` 推導），方便依實機顯示效果微調。
- 右側直排：「花火節」中文動態區塊。
- 底部：以一條水平線隔出的溫度區塊，內含 `TEMP` 標籤、`xx.x C` 溫度值與濕度百分比，避免畫面只有單行溫度文字。

## 動畫設計
延續 `task3a` 的「花火節」波浪舞邏輯：
- `frame % 3` 決定目前哪個字放大（`shrink=1`，32x32），其餘字縮小為 16x16（`shrink=2`）。
- 每個字依 `wave = (-3, 0, 3, 0)` 產生上下波浪位移，搭配 `wrap_y=True` 讓超出畫面底部的像素接回頂部，避免破圖。
- 中文點陣資料直接用 32x32 bytearray，以 `glyph_pixel()` 搭配 `7 - (x % 8)` 的 bit order 解出像素，再用 `draw_char_pixels()` 依 `shrink` 做最近鄰縮放繪製。
- 主迴圈每 `250ms` 重畫一次整個畫面（背景 + 中文動畫 + 溫度），確保動畫連續可觀察，並可連續執行超過 30 秒不卡死。

## DHT22 整合
- `read_sensor_safe()` 每 2 秒呼叫一次（使用 `time.ticks_ms()` / `time.ticks_diff()` 控制節流，與畫面更新頻率分離，互不阻塞）。
- 讀值成功會印出 `[DEBUG] temperature = xx.xC, humidity = xx.x%`，並更新 `last_temp` / `last_humidity` 供 OLED 顯示。
- 讀值失敗時印出 `[ERROR] DHT22 read failed: ...`，並回傳前次有效值，OLED 在尚未取得任何有效值前顯示 `Sensor Error`；取得過有效值後即使單次失敗也會保留前次溫度並標示 `ERR`，避免畫面閃爍消失。

## 遇到的問題與解法
最初將動畫更新頻率與 DHT22 讀取頻率寫在同一個 `time.sleep()` 區塊，導致畫面每 2 秒才更新一幀，動畫看起來幾乎是靜態的。後改用 `time.ticks_ms()` 紀錄上次讀取時間，畫面每 250ms 重畫一次，DHT22 則獨立用時間差判斷是否該讀值，兩者解耦後動畫變得流暢，溫度仍每 2 秒更新一次。

## 待補充的繳交證明
- [ ] OLED 畫面截圖（中文 + 溫度 + 學號）
- [ ] 運行中 GIF（至少 5 秒）
- [ ] Serial debug 截圖
