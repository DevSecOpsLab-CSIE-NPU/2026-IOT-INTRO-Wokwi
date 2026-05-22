# Week 13 Homework: SH1107 中文動畫溫度看板

## 版面配置

使用 task3a 的座標系統 (`rotate=0`, `center_y=90`)，畫面配置如下：

- **左上**：英文資訊（Penghu University / of Science and Technology / Dept of CSIE）+ 年份 2026
- **左中**：溫度顯示（Temp + xx.x C）
- **中央**：一星龍珠（雙層圓 + 五角星）
- **右側**：直排「花火節」動畫（波浪舞 + 依序放大）
- **左下**：學號識別

## 動畫設計

- 三字「花火節」每 250ms 更新一幀
- 每幀有一個字放大為 2 倍（32x32），其餘維持 16x16
- 波浪偏移 `(-5, 0, 5, 0)` 產生上下浮動
- 使用 `wrap_y=True` 處理 SH1107 Wokwi Y 軸環狀映射

## DHT22 整合

- DHT22 接在 GPIO23，每 2 秒讀取一次
- Serial 輸出 `[DEBUG] temperature / humidity`
- 錯誤時 `try/except` 捕捉，OLED 顯示 `Sensor Error`
- 溫度格式：`xx.x C`

## 遇到的問題與解法

**問題**：SH1107 在 Wokwi 的 framebuffer 超出 y=127 時會環狀映射，導致「節」字下半部消失。
**解法**：在 `draw_char_pixels()` 加入 `wrap_y=True`，以 `py %= 128` 將超出 pixel 接回上方，確保三字完整。

## 接線

| 元件 | ESP32 | 裝置 |
|------|-------|------|
| OLED | GPIO22 (SDA) | SDA |
| OLED | GPIO21 (SCL) | SCL |
| OLED | 3V3 | VCC |
| OLED | GND | GND |
| DHT22 | GPIO23 | SDA |
| DHT22 | 3V3 | VCC |
| DHT22 | GND | GND |
