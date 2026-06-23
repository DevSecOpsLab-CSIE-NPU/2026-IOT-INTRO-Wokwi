# 大城北空氣品質監測試題檔案（學號末兩碼 23）

共用參數：

| 項目 | 值 |
|---|---|
| DHT22 | GPIO19 |
| MQ2 AO | GPIO36 |
| 第一題標題顏色 | 青色 / Cyan |
| 第三題 THRESHOLD | 80 ppm |

## 資料夾

1. `01_ili9341_chinese_title/`：第一題，ILI9341 彩屏中文標題。
2. `02_oled_sensor_display/`：第二題，DHT22 + MQ2 顯示在 SSD1306 OLED。
3. `03_thingsboard_mqtt_alarm/`：第三題，MQ2 gas_ppm 透過 MQTT 上傳 ThingsBoard。

## 使用方式

在 Wokwi 專案中放入該題資料夾內的：

- `main.py`
- `diagram.json`
- `lib/` 內的必要模組

第三題請先到 ThingsBoard Device 複製 MQTT 認證，填到：

```python
TB_USERNAME = "PUT_YOUR_ACCESS_TOKEN_HERE"
TB_PASSWORD = ""
```

如果你的 ThingsBoard 是 username/password 模式，就把兩個欄位都填上。
