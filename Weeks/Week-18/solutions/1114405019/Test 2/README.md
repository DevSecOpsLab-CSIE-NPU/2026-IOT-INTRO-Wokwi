# Test 2：感測讀取與 OLED 顯示

## 目標
用 ESP32 + DHT22（溫濕度）+ MQ2（氣體）讀取感測數值，每 2 秒在 SSD1306 OLED（128×64, I2C）上刷新顯示，並同步在 Serial Monitor 印出 debug 訊息。

## 硬體
| 元件 | Wokwi 類型 |
|------|-----------|
| ESP32 | `board-esp32-devkit-c-v4` |
| OLED | `board-ssd1306`（128×64, I2C） |
| 溫濕度感測器 | `wokwi-dht22` |
| 氣體感測器 | `wokwi-gas-sensor`（MQ2） |

## 接線
| 元件腳位 | 連到 ESP32 |
|---------|-----------|
| OLED SCL | GPIO22 |
| OLED SDA | GPIO21 |
| OLED VCC | 3V3 |
| OLED GND | GND |
| DHT22 DATA | GPIO33 |
| DHT22 VCC | 3V3 |
| DHT22 GND | GND |
| MQ2 AOUT | GPIO35 |
| MQ2 VCC | 5V（VIN） |
| MQ2 GND | GND |

> I2C（GPIO21/22）已被 OLED 佔用，DHT22/MQ2 改接 GPIO33/35，不衝突。

## 邏輯說明
- 每 2 秒一次迴圈：`dht22.measure()` 取得 `.temperature()` / `.humidity()`；`mq2.read()` 取得 ADC 原始值。
- MQ2 ppm 換算公式（沿用本 repo Week-15 既有慣例）：
  ```python
  v = raw / 4095.0
  ratio = v / (1.0 - v)
  ppm = K * (ratio ** P)   # K=2.60, P=2.467
  ```
  非精確校正公式，僅供模擬展示用。
- OLED 每輪都 `fill(0)` → `text(...)` → `show()` 全部重畫，確保拖動 Wokwi 滑桿後數值會即時跟著變動（不快取）。

## 檔案
| 檔案 | 說明 |
|------|------|
| `main.py` | 主程式：初始化 I2C/SSD1306/DHT22/MQ2，每 2 秒讀取、更新 OLED 並印出 Serial debug |
| `diagram.json` | Wokwi 接線圖（ESP32 + SSD1306 + DHT22 + MQ2） |
| `wokwi.toml` | 指向 repo 共用 firmware |
| `Makefile` / `make.bat` | 透過 RFC2217 連到已開啟的 Wokwi 模擬器執行 `main.py` |

> `ssd1306`、`dht` 模組已內建於本課程使用的 ESP32 MicroPython firmware，不需要額外複製驅動檔到本資料夾。

## 執行方式

### 方式一：直接在 Wokwi 開啟資料夾
在 VS Code 安裝 Wokwi 擴充套件後，開啟本資料夾的 `diagram.json`，直接按下 ▶️ 模擬即可。

### 方式二：透過 make 上傳執行（與其他週次一致的工作流程）
1. VS Code `Command Palette` → `Wokwi: Start Simulator`
2. 在新的 Terminal 執行：
   ```bash
   make run
   ```
   Windows 也可用：
   ```bat
   make.bat run
   ```

若缺少 `pyserial`：
```bash
python3 -m pip install pyserial
```

## 驗收標準
- [ ] OLED 每 2 秒刷新顯示標題「Dacheng AirMon」+ Temp/Humi/Gas 三項數值
- [ ] Serial Monitor 同步每 2 秒印出 `[DEBUG] temp=... humi=... gas_ppm=...`
- [ ] 拖動 Wokwi 介面 DHT22/MQ2 滑桿，下一輪刷新數值會跟著變動
- [ ] 接腳與學號對照表一致：DHT22=GPIO33, MQ2=GPIO35, OLED SCL=22/SDA=21
- [ ] 不含第一題（ILI9341 中文標題）或第三題的程式邏輯
