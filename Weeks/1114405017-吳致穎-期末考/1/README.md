# 題目一 — 彩屏中文標題顯示

內容：使用 ESP32 + ILI9341 彩屏顯示中文標題「大城北游泳池空汙偵測」。

檔案：
- `main.py`：主程式，初始化 SPI 與 ILI9341，並在畫面置中顯示標題。
- `wokwi.toml`：Wokwi 模擬器設定。
- `Makefile` / `make.bat`：啟動模擬器的 helper 指令。

執行（Linux / macOS）：
```
make run
```

執行（Windows）：
```
make.bat
```
