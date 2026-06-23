# Test 1：彩屏中文標題顯示與排版

## 目標
用 ESP32 + ILI9341（SPI, 240×320）顯示中文標題「大城北游泳池空汙偵測」（10 字），並依規則自動換行、置中排版。

## 硬體
| 元件 | Wokwi 類型 |
|------|-----------|
| ESP32 | `board-esp32-devkit-c-v4` |
| TFT LCD | `wokwi-ili9341`（240×320, SPI） |

## 接線
| ILI9341 腳位 | 連到 ESP32 |
|-------------|-----------|
| VCC | 3V3 |
| GND | GND |
| CS | GPIO5 |
| D/C | GPIO17 |
| MOSI | GPIO23 |
| SCK | GPIO18 |

## 排版邏輯
- 每字 32px，10 字若一列排不下（10×32=320px > 240px 螢幕寬），故每列最多 `240 // 32 = 7` 字，取每列 5 字（5×32=160px ≤ 240px）：
  - 第一列：大城北游泳
  - 第二列：池空汙偵測
- 水平置中：`x = (240 − 5×32) ÷ 2 = 40`
- 垂直不重疊：第一列 `y = 122`，第二列 `y = 122 + 32 + 12(行距) = 166`，畫面底部落在 198px（< 320px）
- 顏色：白色 `ili9341.color565(255, 255, 255)`，背景黑底

## 檔案
| 檔案 | 說明 |
|------|------|
| `main.py` | 主程式：初始化 SPI/ILI9341、清螢幕、呼叫 `draw_title()` 畫標題 |
| `diagram.json` | Wokwi 接線圖（ESP32 + ILI9341） |
| `wokwi.toml` | 指向 repo 共用 firmware |
| `ili9341.py` | ILI9341 SPI 驅動（複製自 `lib/`） |
| `fonts.py` | 中文點陣字型 + `draw_char`/`draw_title`（複製自 `lib/`） |
| `Makefile` / `make.bat` | 透過 RFC2217 連到已開啟的 Wokwi 模擬器執行 `main.py` |

> `ili9341.py`、`fonts.py` 直接複製自 repo 根目錄的 `lib/`，因為 Wokwi 模擬器把專案資料夾當作裝置檔案系統，`import` 的模組必須跟 `main.py` 同層才能載入。

## 執行方式

### 方式一：直接在 Wokwi 開啟資料夾
在 VS Code 安裝 Wokwi 擴充套件後，開啟本資料夾的 `diagram.json`，直接按下 ▶️ 模擬即可（`main.py`/`ili9341.py`/`fonts.py` 都在同層，不需額外步驟）。

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
   此方式會先把 `lib/` 下的 `.py` 上傳到裝置，再執行 `main.py`。

若缺少 `pyserial`：
```bash
python3 -m pip install pyserial
```

## 驗收標準
- [ ] 畫面黑底白字，完整顯示「大城北游泳池空汙偵測」
- [ ] 兩列各 5 字，水平置中，垂直不重疊、不超出 320px 高
- [ ] 不含本題不需要的感測器初始化
