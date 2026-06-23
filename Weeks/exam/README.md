# 物聯網概論期末上機考

學號：1114405029

本資料夾已拆成兩個獨立 Wokwi 專案，不共用 `main.py`，也不共用 `diagram.json`。

## Q1：ILI9341 彩屏中文標題

位置：`q1_ili9341_title/`

硬體只包含：
- ESP32 DevKit C V4
- ILI9341 TFT LCD

顯示：
- `大城北游泳`
- `池空汙偵測`

接腳：
- CS：GPIO5
- D/C：GPIO17
- MOSI：GPIO23
- SCK：GPIO18

執行：

```bat
cd q1_ili9341_title
make.bat send 4001
make.bat run 4001
```

## Q2：OLED + DHT22 + MQ2

位置：`q2_oled_sensor/`

硬體只包含：
- ESP32 DevKit C V4
- SSD1306 OLED
- DHT22
- MQ2 gas sensor

專屬接腳：
- DHT22 DATA：GPIO33
- MQ2 AO/AOUT：GPIO34
- OLED SCL：GPIO22
- OLED SDA：GPIO21
- THRESHOLD：140 ppm

執行：

```bat
cd q2_oled_sensor
make.bat send 4001
make.bat run 4001
```
