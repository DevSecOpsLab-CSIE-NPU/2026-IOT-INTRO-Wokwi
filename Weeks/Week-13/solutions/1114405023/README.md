# Week 13 Homework：SH1107 + DHT22 中文動畫溫度看板

## 基本資料

- 學號：`1114405023`
- 主程式：`main.py`
- 顯示器：`board-grove-oled-sh1107`，解析度 `128x128`
- 感測器：`DHT22`
- Driver：使用 `sh1107`，未改用 `ssd1306`

## 版面配置說明

本作品以課堂 `task4` 的 SH1107 + DHT22 架構為基礎，再加入作業指定的中文動畫看板元素。畫面上方顯示 `DRAGON TEMP` 標題，右側顯示 `SH1107`、`DHT22`、`LIVE` 等英文資訊，中間以龍珠造型作為主視覺，包含圓形外框與多顆星星。右下角顯示即時溫度與濕度，底部顯示學號後五碼作為 OLED 畫面識別。整體版面不是單行溫度文字，而是保留標題、資訊區、圖形主視覺、中文動畫與感測資料等多層次結構。

## 動畫設計

程式每 `250 ms` 更新一幀，符合每 200～300ms 持續更新的要求。動畫包含龍珠外圈放大縮小、星星微幅位移、中文字「花火節」波浪移動，以及小煙火點閃爍。這些元素會在 `while True` 迴圈中持續重畫，因此執行時可以明顯觀察到畫面正在更新。

## DHT22 整合方式

本版本完全對齊課堂 `task4` 的硬體設定：OLED 使用 `SCL=GPIO21`、`SDA=GPIO22`，DHT22 使用 `GPIO23`。程式每 `2 秒` 呼叫一次 `sensor.measure()` 讀取 DHT22，成功後 OLED 會顯示 `xx.x C`，Serial Console 會輸出 `[DEBUG] temperature = ... humidity = ...`。感測讀取函式 `read_sensor_safe()` 使用 `try/except` 包住讀值流程；若 DHT22 暫時失敗，程式不會停止，而是印出錯誤訊息並在 OLED 顯示 `Sensor Error`。

## 遇到的問題與解法

主要問題是課堂 `task4` 的 SH1107 接線與一般 ESP32 I2C 習慣不同。課堂範例使用 `scl=Pin(21)`、`sda=Pin(22)`，而不是常見的 `SCL=22`、`SDA=21`。若照一般接法寫，OLED 可能會黑畫面。因此本版本改成完全對齊課堂 `task4`，並保留 `address=0x3C`、`rotate=90` 與 `dragon_center_x = center_x - 32` 的校正方式。另外，中文字不直接使用 `oled.text()`，而是用 16x16 bitmap 畫出「花火節」，避免中文字型缺失或破圖。

## Wokwi 接線設定

| 元件 | 腳位 | 連接 |
|---|---:|---|
| SH1107 OLED | SCL | GPIO 21 |
| SH1107 OLED | SDA | GPIO 22 |
| SH1107 OLED | VCC | 3V3 |
| SH1107 OLED | GND | GND |
| DHT22 | SDA / DATA | GPIO 23 |
| DHT22 | VCC | 3V3 |
| DHT22 | GND | GND |

## 執行方式

在 `Weeks/Week-13/solutions/1114405023/` 目錄打開 `diagram.json`，按 VS Code Wokwi Simulator 的綠色播放鍵即可執行。若使用課堂工具，也可在同資料夾執行：

```bash
make run
```

Windows 可使用：

```bat
make.bat run
```

## 驗收 Checklist

- [x] 有 `task3a` 風格版型
- [x] 有明顯動畫
- [x] 有可辨識中文字「花火節」
- [x] 有即時溫度 `xx.x C`
- [x] OLED 畫面有學號識別
- [x] Serial 有 `temperature` / `humidity` debug
- [x] 感測異常時程式不崩潰
