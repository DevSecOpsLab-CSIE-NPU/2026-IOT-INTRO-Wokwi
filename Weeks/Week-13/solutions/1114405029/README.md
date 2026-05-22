# Week 13 Homework：SH1107 + DHT22 中文動畫溫度看板

## 基本資料

- 學號：1114405029
- 主題：SH1107 OLED 中文動畫溫度看板
- 開發板：ESP32 DevKit V4
- 顯示器：Grove SH1107 OLED 128x128
- 感測器：DHT22
- 程式語言：MicroPython

---

## 一、作業目標

本作業整合 Week 13 課堂中的 `task3a` OLED 動畫設計與 `task4` DHT22 溫溼度感測功能，完成一個可以在 Wokwi 上持續運作的中文動畫溫度看板。

本作品不是單純顯示溫度，而是將 OLED 畫面設計成具有主題性的動畫資訊看板。畫面中包含英文資訊、年份 `2026`、學號、中文「花火節」、龍珠主視覺、悟空 bitmap 圖像、煙火特效、即時溫度與濕度資料，並且透過動畫讓畫面持續更新。

---

## 二、繳交檔案說明

本作業資料夾內容如下：

```text
1114405029/
├── main.py
├── goku_bitmap.py
├── convert_bitmap.py
├── goku.png
├── diagram.json
├── wokwi.toml
├── make.bat
├── Makefile
├── README.md
├── AI_USAGE.md
├── oled.png
├── demo.gif
└── serial_debug.png
```

各檔案用途如下：

| 檔案 | 說明 |
|---|---|
| `main.py` | 主程式，負責 OLED 顯示、DHT22 感測、動畫、輪播與錯誤處理 |
| `goku_bitmap.py` | 悟空頭像 bitmap 資料，由圖片轉換而來 |
| `convert_bitmap.py` | 將 `goku.png` 轉成 1-bit OLED bitmap 的工具 |
| `goku.png` | 用來轉換成 bitmap 的悟空圖片素材 |
| `diagram.json` | Wokwi 硬體接線圖 |
| `wokwi.toml` | Wokwi 韌體與模擬器設定 |
| `make.bat` | Windows 執行腳本，可透過 `.\make.bat run` 上傳並執行 |
| `Makefile` | make 指令版本的執行設定 |
| `README.md` | 作業說明文件 |
| `AI_USAGE.md` | AI 使用紀錄 |
| `oled.png` | OLED 執行畫面截圖 |
| `demo.gif` | OLED 動畫運行 GIF |
| `serial_debug.png` | Serial Monitor debug 輸出截圖 |

---

## 三、硬體接線說明

本作業使用 ESP32、Grove SH1107 OLED 與 DHT22。

### OLED SH1107 接線

| ESP32 | OLED SH1107 |
|---|---|
| GPIO22 | SDA |
| GPIO21 | SCL |
| 3V3 | VCC |
| GND | GND |

### DHT22 接線

| ESP32 | DHT22 |
|---|---|
| GPIO23 | DATA |
| 3V3 | VCC |
| GND | GND |

程式中的設定如下：

```python
i2c = I2C(0, scl=Pin(21), sda=Pin(22))
dht_sensor = dht.DHT22(Pin(23))
```

---

## 四、主要功能

本作品完成以下功能：

- 使用 ESP32 讀取 DHT22 溫度與濕度
- 使用 SH1107 OLED 顯示 128x128 畫面
- 顯示英文資訊：`PENGHU`、`SCI TECH`、`CSIE`
- 顯示年份：`2026`
- OLED 畫面中顯示學號：`ID:1114405029`
- 顯示中文「花火節」
- 顯示即時溫度：`xx.x C`
- 顯示即時濕度：`H:xx%`
- Serial Monitor 輸出 temperature / humidity debug 訊息
- 使用 `try/except` 避免 DHT22 讀取失敗造成程式中斷
- 使用 bitmap 顯示悟空頭像
- 使用龍珠圓形與星星作為主視覺
- 使用煙火與閃爍粒子強化「花火節」氣氛
- 花火節三個中文字會依序放大，形成明顯動畫
- 保留參數化設定，方便調整動畫速度、感測更新時間與輪播時間

---

## 五、畫面設計說明

OLED 畫面採用「參考圖風格的黑底白字像素看板」設計。

### 1. 上方資訊區

畫面上方顯示：

```text
PENGHU 2026
SCI TECH
CSIE
ID:1114405029
```

其中 `2026` 放在右上角，模仿參考圖右上年份位置；`ID:1114405029` 直接顯示在 OLED 畫面內，符合題目要求的學號識別。

### 2. 中央主視覺區

中央區域會在兩種主視覺之間切換：

- 龍珠模式：顯示圓形龍珠與中間星星
- 悟空模式：顯示由圖片轉換而來的悟空 bitmap

這樣可以讓畫面不只是靜態圖案，而是有明顯的主題動畫變化。

### 3. 右側中文區

畫面右側顯示直排中文：

```text
花
火
節
```

三個中文字使用 32x32 中文點陣資料繪製，不是用普通英文字型模擬。為了增加動畫感，程式會讓「花」、「火」、「節」依序放大，每個字約維持 2 秒，再切換到下一個字。

### 4. 下方溫濕度區

畫面下方顯示：

```text
24.0 C
H:40%
```

其中溫度與濕度都來自 DHT22 感測器，不是寫死的文字。

---

## 六、動畫設計

本作業的動畫分成四種：

### 1. 龍珠動畫

龍珠由兩層圓形與空心五角星組成。圓形半徑會隨 `frame` 做輕微變化，形成脈衝效果。星星也會隨時間旋轉，讓龍珠看起來不是靜態圖案。

### 2. 悟空動畫

悟空圖像由 `goku.png` 轉換成 `goku_bitmap.py` 的 1-bit bitmap，再透過 `framebuf.FrameBuffer` 與 `oled.blit()` 顯示。

悟空模式中會有輕微上下浮動與周圍粒子，讓畫面保持動態感。

### 3. 花火節依序放大動畫

右側「花火節」三個字會依序放大：

```text
花 放大約 2 秒
火 放大約 2 秒
節 放大約 2 秒
然後循環
```

這讓中文字區塊不是單純靜態顯示，而是有清楚可觀察的中文動畫。

### 4. 煙火與粒子動畫

畫面中加入煙火特效，使用像素點與自製 `draw_pixel_line()` 繪製。煙火會有放射狀變化與閃爍星點，強化「花火節」的主題感。

後來也調整煙火尾巴位置，避免特效干擾下方的溫度數字。

---

## 七、感測器與錯誤處理

DHT22 每 2 秒讀取一次資料。每次成功讀值時，Serial Monitor 會輸出：

```text
[DEBUG] temperature = 24.0C, humidity = 40.0%
```

若 DHT22 暫時讀取失敗，程式不會直接停止，而是進入 `except` 區塊：

```python
except Exception as e:
    sensor_ok = False
    print("[ERROR] DHT22 read failed:", e)
```

OLED 也會顯示錯誤狀態：

```text
Sensor
Error
```

這樣可以避免感測器偶發錯誤導致整個作品崩潰。

---

## 八、參數化設定

程式保留多個可調整常數：

```python
ANIMATION_DELAY_MS = 120
SENSOR_INTERVAL_MS = 2000
SWITCH_INTERVAL_MS = 2000
```

| 參數 | 說明 |
|---|---|
| `ANIMATION_DELAY_MS` | 控制動畫更新速度 |
| `SENSOR_INTERVAL_MS` | 控制 DHT22 感測器讀取間隔 |
| `SWITCH_INTERVAL_MS` | 控制龍珠模式與悟空模式輪播時間 |

這樣之後如果想要調整動畫速度、感測頻率或畫面切換節奏，只需要修改這些常數，不需要重寫整個程式。

---

## 九、溫度區間視覺化

本作品加入溫度視覺化概念：龍珠中的星星大小會依照溫度區間做變化。

程式邏輯如下：

```python
if temperature >= 28:
    temp_level = 3
elif temperature >= 24:
    temp_level = 1
else:
    temp_level = -1
```

接著將 `temp_level` 加入星星大小：

```python
draw_star(display, center_x, center_y, 11 + max(0, pulse) + temp_level, frame * 16)
```

| 溫度區間 | 視覺效果 |
|---|---|
| 低於 24°C | 星星較小 |
| 24°C～27.9°C | 星星正常大小 |
| 28°C 以上 | 星星較大 |

這讓感測資料不只是用文字顯示，也能反映到畫面視覺效果中。

---

## 十、系統流程圖

```text
開始
  ↓
初始化 ESP32 GPIO
  ↓
初始化 I2C
  ↓
初始化 SH1107 OLED
  ↓
初始化 DHT22
  ↓
載入悟空 bitmap
  ↓
第一次讀取 DHT22 溫濕度
  ↓
進入 while True 主迴圈
  ↓
判斷是否超過 2 秒
  ├─ 是 → 重新讀取 DHT22，並輸出 Serial Debug
  └─ 否 → 使用目前資料
  ↓
清空 OLED 畫面
  ↓
顯示固定資訊
  - PENGHU
  - SCI TECH
  - CSIE
  - 2026
  - ID:1114405029
  ↓
顯示右側花火節中文字動畫
  ↓
判斷目前輪播模式
  ├─ 模式 A：龍珠模式
  │    ├─ 顯示龍珠圓形
  │    ├─ 顯示空心星星
  │    └─ 依溫度調整星星大小
  │
  └─ 模式 B：悟空模式
       ├─ 顯示悟空 bitmap
       └─ 顯示粒子動畫
  ↓
顯示溫度與濕度
  ↓
oled.show()
  ↓
frame += 1
  ↓
延遲 120 ms
  ↓
回到 while True
```

---

## 十一、狀態機說明

本作品可以視為兩個主要狀態：

```text
State 0：Dragon Ball Mode
State 1：Goku Mode
```

狀態切換條件：

```python
mode = (elapsed // SWITCH_INTERVAL_MS) % 2
```

### State 0：Dragon Ball Mode

此模式負責顯示：

- 龍珠主視覺
- 雙層圓形
- 空心星星
- 溫度影響星星大小
- 右側花火節動畫
- 溫濕度資料

### State 1：Goku Mode

此模式負責顯示：

- 悟空 bitmap
- 悟空上下浮動
- 周圍閃爍粒子
- 右側花火節動畫
- 溫濕度資料

使用狀態機設計可以避免畫面元素全部同時擠在一起，也讓動畫輪播更清楚。

---

## 十二、遇到的問題與解法

### 問題 1：悟空圖片轉成 OLED bitmap 後看不清楚

一開始使用彩色圖片或複雜漫畫截圖轉成 bitmap，OLED 上顯示後會變成雜訊，看不出悟空。後來改用黑白漫畫風、頭部較大的圖片，並調整 `convert_bitmap.py` 的尺寸與 threshold，讓五官與頭髮輪廓更明顯。

### 問題 2：bitmap 顯示方向錯誤

一開始使用 `framebuf.MONO_HMSB`，結果畫面出現橫條紋。後來發現轉換程式是用每 8 個垂直像素組成一個 byte，因此 FrameBuffer 格式應改為：

```python
framebuf.MONO_VLSB
```

改完後悟空圖像才正確顯示。

### 問題 3：龍珠與圖案超出畫面造成左右分裂

若圖形座標太靠右，例如 `x + width > 128`，OLED 上會出現左右分裂或邊界殘影。後來透過調整 `center_x`、`goku_x` 與中文座標，確保圖形不超出 128x128 顯示範圍。

### 問題 4：中文字與悟空互相遮擋

若「花火節」與悟空同時在相同區域顯示，畫面會變亂。因此後來把「花火節」移到右側，悟空與龍珠放在中央主視覺區，讓畫面分區更清楚。

### 問題 5：煙火特效干擾溫度顯示

一開始煙火尾巴太長，會碰到下方 `24.0 C` 的溫度區塊。後來縮短煙火尾巴，讓溫度與濕度保持清楚可讀。

### 問題 6：年份 2026 位置容易被切到

因為 SH1107 使用 `rotate=90`，座標方向與一般直覺不同。如果 `2026` 放太右，會被邊界裁切。後來多次調整座標，讓 `2026` 可以完整顯示在右上角。

---

## 十三、執行方式

確認 Wokwi 模擬器已在 VS Code 中開啟後，在本資料夾執行：

```powershell
.\make.bat run
```

如果使用 Makefile，可執行：

```bash
make run
```

---

## 十四、驗收 Checklist

- [x] 使用 `board-grove-oled-sh1107`
- [x] 使用 `sh1107` driver
- [x] 使用 ESP32
- [x] 使用 DHT22
- [x] 顯示即時溫度 `xx.x C`
- [x] 顯示即時濕度 `H:xx%`
- [x] OLED 畫面顯示學號 `1114405029`
- [x] 顯示中文「花火節」
- [x] 具有動畫
- [x] 具有龍珠主視覺
- [x] 具有悟空 bitmap 圖像
- [x] Serial Monitor 有 temperature / humidity debug
- [x] 感測器讀取失敗時不會讓程式崩潰
- [x] 保留參數化設定
- [x] 有溫度區間視覺化
- [x] README 有流程圖與狀態機說明