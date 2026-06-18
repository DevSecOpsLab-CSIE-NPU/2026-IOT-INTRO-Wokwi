# Task 1: ESP32 MicroPython OLED Hello

## 目標
在 Wokwi 中使用 ESP32 + SSD1306 OLED，顯示文字 `Hello, August!`。

## 專案位置
請使用本題資料夾：

`Weeks/Week-13/in-class/task1/`

目前主要檔案：
- `main.py`
- `diagram.json`
- `wokwi.toml`
- `Makefile`
- `make.bat`（Windows 用）

## 任務要求
1. 開啟本題 Wokwi 專案。
2. 了解 `main.py` 中 I2C 與 OLED 初始化流程。
3. 執行程式並確認 OLED 顯示 `Hello, August!`。

## 執行方式
在 `task1` 目錄內執行：

macOS / Linux:
```bash
make run
```

Windows:
```bat
make.bat run
```

可選擇指定 RFC2217 Port（預設 `4000`）：

```bash
make run 4001
```

```bat
make.bat run 4001
```

## 程式重點
- I2C 腳位：`scl=22`、`sda=21`
- OLED 尺寸：`128x64`
- 使用 `ssd1306.SSD1306_I2C(...)` 建立顯示物件
- `oled.text(...)` 寫字後呼叫 `oled.show()` 更新畫面

## 驗收標準
- 程式可透過 `make` 或 `make.bat` 正常執行。
- Wokwi 模擬中 OLED 成功顯示 `Hello, August!`。
- `main.py` 內容與接線設定一致。
