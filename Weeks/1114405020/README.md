# 物聯網期末專題 - 大城北游泳池空汙偵測系統

## 📋 學生資訊

| 項目 | 內容 |
|------|------|
| **學號** | 1114405020 |
| **姓名** | 范芯瑜 |
| **座號** | 20 |
| **郵件** | d14405020@ems.npu.edu.tw |

---

## 📊 學號客製化參數對照表

學號 **1114405020** 的末兩碼解讀：
- **十位數：2** → MQ2 氣體感測器使用 **GPIO 36**
- **個位數：0** → DHT22 溫濕度計使用 **GPIO 4**、彩屏標題色 **黃色**、告警門檻 **50 ppm**

| 參數 | 值 | 說明 |
|------|-----|------|
| DHT22 數據腳 | GPIO 4 | 溫濕度計讀取 |
| MQ2 類比輸出 | GPIO 36 | ADC 類比讀取氣體濃度 |
| 彩屏標題色 | 黃色 (0xFFE0) | RGB565: (255, 255, 0) |
| 告警門檻 | 50 ppm | 超過此值觸發告警 |
| I2C SCL | GPIO 22 | OLED 固定引腳 |
| I2C SDA | GPIO 21 | OLED 固定引腳 |

---

## 🎯 三題實作概述

### 第一題：彩屏中文標題
**檔案路徑**：`1/main.py`

**功能**：
- 使用 ILI9341 彩屏 (240×320 像素)
- 顯示中文標題「大城北游泳池空汙偵測」（5字×2列）
- 標題色：**黃色** (個位數=0)
- 水平置中於 X=40、垂直置中於 Y=122

**依賴**：
- `ili9341.py` - 彩屏驅動庫
- `fonts.py` - 中文字型與繪製函數

**SPI 接線配置**：
```
ILI9341 -> ESP32:
  CS  (Chip Select) -> GPIO 5
  D/C (Data/Command) -> GPIO 17
  MOSI (Data In) -> GPIO 23
  SCK (Clock) -> GPIO 18
  GND -> GND
  VCC -> 3V3
```

---

### 第二題：感測與 OLED 顯示
**檔案路徑**：`2/main.py`、`2/diagram.json`

**功能**：
- DHT22 溫濕度計：讀取當前溫度、濕度
- MQ2 氣體感測器：讀取空氣品質（PPM值）
- SSD1306 OLED：實時顯示所有數據

**硬體接線**：
```
DHT22 (溫濕度計):
  VCC -> ESP32 3V3
  GND -> ESP32 GND
  Data -> ESP32 GPIO 4 ✅ （個位=0）

MQ2 (氣體感測器):
  VCC -> ESP32 5V
  GND -> ESP32 GND
  AO (類比輸出) -> ESP32 GPIO 36 ✅ （十位=2）

SSD1306 OLED (128×64):
  VCC -> ESP32 3V3
  GND -> ESP32 GND
  SCL (時鐘) -> ESP32 GPIO 22
  SDA (數據) -> ESP32 GPIO 21
```

**顯示內容**：
```
Dacheng AirMon
Temp: XX.X C
Humi: XX.X %
Gas : XXX ppm
```

**MQ2 非線性校正公式**：
```
PPM = K × (V/(1-V))^P
  其中 K=2.60, P=2.467
  V = ADC讀值 / 4095.0
```

**OLED I2C 位址**：`0x3C`

---

### 第三題：雲端 PPM 告警
**檔案路徑**：`3/main.py`、`3/diagram.json`

**功能**：
- 實時監測 MQ2 氣體濃度
- 本地告警：當 PPM > 50 時，終端機輸出告警訊息
- 雲端上傳：每 5 秒發送數據到 ThingsBoard Cloud

**硬體接線**：
```
MQ2 (氣體感測器):
  VCC -> ESP32 5V
  GND -> ESP32 GND
  AO (類比輸出) -> ESP32 GPIO 36 ✅ （十位=2）
```

**告警門檻**：**50 ppm** ✅ （個位=0）

**告警訊息格式**：
```
[ALARM]!!! MQ2 偵測到有害氣體濃度超標！目前: XXX ppm, 門檻: 50 ppm
```

**雲端配置（ThingsBoard）**：
```
WiFi SSID：Wokwi-GUEST
WiFi 密碼：（空白）
MQTT 伺服器：thingsboard.cloud:1883
Access Token：nqbxwsrrugs3a77bj4i4
MQTT 密碼：pzcgbajjh274h8jtri07
發送間隔：5 秒
```

---

## 🚀 Wokwi 部署步驟

### 快速開始

1. **打開 Wokwi 模擬器**
   - 訪問 https://wokwi.com/
   - 若有帳戶登入，若無則建立新帳戶

2. **匯入第一題（彩屏中文標題）**
   - 複製 `1/diagram.json` 內容到新專案
   - 複製 `1/main.py` 代碼到編輯器
   - 在 Wokwi 文件系統中上傳：
     - `ili9341.py`（彩屏驅動）
     - `fonts.py`（中文字型）
   - 點擊 ▶ 執行按鈕

3. **匯入第二題（感測與 OLED）**
   - 複製 `2/diagram.json` 內容到新專案
   - 複製 `2/main.py` 代碼到編輯器
   - 在 Wokwi 文件系統中上傳：
     - `ssd1306.py`（OLED 驅動）
     - `dht.py`（DHT22 驅動）
   - 點擊 ▶ 執行按鈕
   - 觀察終端機輸出和 OLED 顯示

4. **匯入第三題（雲端 PPM 告警）**
   - 複製 `3/diagram.json` 內容到新專案
   - 複製 `3/main.py` 代碼到編輯器
   - 在 Wokwi 文件系統中上傳：
     - `umqtt/simple.py`（MQTT 客戶端）
   - 點擊 ▶ 執行按鈕
   - 確認終端機顯示 WiFi 連接狀態
   - 確認 MQTT 連接成功，數據上傳到 ThingsBoard

---

## 📱 ThingsBoard 雲端告警規則設定

### 登入 ThingsBoard
1. 訪問 https://thingsboard.cloud/
2. 使用提供的認證資訊登入

### 創建告警規則
1. **進入 Rule Chains**
   - 側邊菜單 → Dashboards → Rule Chains → Create new

2. **設定觸發條件**
   - 條件：`gas_ppm > 50`
   - 當 PPM 超過 50 ppm 時觸發告警

3. **設定告警動作**
   - 發送郵件通知（至 d14405020@ems.npu.edu.tw）
   - 郵件內容包含時間戳記和氣體濃度值

4. **測試告警**
   - 在 Wokwi 中修改 MQ2 模擬值超過 50 ppm
   - 檢查是否收到郵件通知

---

## 📂 檔案結構

```
1114405020/
├── 1/
│   ├── main.py              # 彩屏中文標題程式
│   ├── diagram.json         # 彩屏電路接線圖
│   ├── README.md            # 第一題說明
│   ├── wokwi.toml           # Wokwi 配置
│   ├── Makefile             # 建置腳本
│   └── make.bat             # Windows 建置腳本
│
├── 2/
│   ├── main.py              # 感測與OLED程式
│   ├── diagram.json         # 感測電路接線圖
│   ├── README.md            # 第二題說明
│   ├── wokwi.toml           # Wokwi 配置
│   ├── Makefile             # 建置腳本
│   └── make.bat             # Windows 建置腳本
│
├── 3/
│   ├── main.py              # 雲端告警程式
│   ├── diagram.json         # 雲端電路接線圖
│   ├── README.md            # 第三題說明
│   ├── wokwi.toml           # Wokwi 配置
│   ├── Makefile             # 建置腳本
│   └── make.bat             # Windows 建置腳本
│
└── README.md                # 本檔案（總說明）
```

---

## 🛠️ 本地建置與測試

### 使用 Make 命令
```bash
# 進入題目目錄
cd 1/   # 或 2 或 3

# 清理舊建置
make clean

# 執行建置
make

# Windows 系統
make.bat
```

### 驅動庫下載
如果缺少驅動庫，請從以下來源下載：

**ILI9341 彩屏驅動**：
- 檔案：`ili9341.py`
- 來源：https://github.com/rdagger/micropython-ili9341

**SSD1306 OLED 驅動**：
- 檔案：`ssd1306.py`
- 來源：https://github.com/micropython/micropython-lib

**DHT22 感測器驅動**：
- 檔案：`dht.py`（MicroPython 內置）
- 無需額外下載

**MQTT 客戶端**：
- 檔案：`umqtt/simple.py`
- 來源：https://github.com/micropython/micropython-lib

---

## 📝 常見問題

### Q1：彩屏顯示不出來？
**A**：確認 `ili9341.py` 和 `fonts.py` 已上傳到 Wokwi 文件系統。

### Q2：OLED 顯示亂碼？
**A**：確認 `ssd1306.py` 已上傳，且 I2C 位址設定正確（0x3C）。

### Q3：MQ2 讀取一直是 0？
**A**：檢查 GPIO 36 接線，確認 ADC 衰減設定為 `ATTN_11DB`。

### Q4：無法連接到 ThingsBoard？
**A**：確認 WiFi 連接成功，檢查 Access Token 和 MQTT 密碼。

---

## ✅ 期末反思與學習成果

詳見 [学習反思.md](学習反思.md)

---

## 📧 聯絡方式

- **姓名**：范芯瑜
- **學號**：1114405020
- **郵件**：d14405020@ems.npu.edu.tw
- **課程**：物聯網技術概論期末專題

---

**最後更新日期**：2026年6月23日

