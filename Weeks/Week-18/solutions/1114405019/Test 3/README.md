# Test 3：雲端 PPM 告警（MQTT → ThingsBoard）

## 目標
用 ESP32 + MQ2（氣體感測器）讀取 ADC 值換算成 `gas_ppm`，每 5 秒透過 MQTT 上傳到 ThingsBoard Cloud 的 telemetry，同時在本地判斷是否超過門檻值並印出告警訊息。雲端的 Alarm Rule（`gas_ppm > 140` 觸發）在 ThingsBoard 後台設定，不由本程式處理。

## 硬體
| 元件 | Wokwi 類型 |
|------|-----------|
| ESP32 | `board-esp32-devkit-c-v4` |
| 氣體感測器 | `wokwi-gas-sensor`（MQ2） |

## 接線
| 元件腳位 | 連到 ESP32 |
|---------|-----------|
| MQ2 AOUT | GPIO35 |
| MQ2 VCC | 5V（VIN） |
| MQ2 GND | GND |

> 本題不使用 OLED / DHT22，僅專注 MQ2 → MQTT → ThingsBoard。

## 網路與雲端設定
| 項目 | 值 |
|------|-----|
| WiFi SSID | `Wokwi-GUEST`（無密碼） |
| MQTT Broker | `mqtt.thingsboard.cloud` |
| MQTT Port | `1883` |
| 認證方式 | Access Token 當 username，password 留空 |
| Telemetry Topic | `v1/devices/me/telemetry` |
| 門檻值 | `THRESHOLD = 140`（學號換算固定值） |

執行前請先把 [main.py](main.py) 裡的：
```python
ACCESS_TOKEN = "PASTE_YOUR_TOKEN_HERE"
```
換成你在 ThingsBoard Cloud 建立的裝置 Access Token。

## 邏輯說明
1. `network.WLAN(STA_IF)` 連線 WiFi，成功後印出取得的 IP。
2. `umqtt.simple.MQTTClient` 連線 ThingsBoard，`user=ACCESS_TOKEN`、`password=""`。
3. `ADC(Pin(35)) + .atten(ADC.ATTN_11DB)` 初始化 MQ2。
4. 每 5 秒一次迴圈：
   - 讀取 ADC 原始值，用 MQ2 非線性公式換算 `gas_ppm`：
     ```python
     v = raw / 4095.0
     ratio = v / (1.0 - v)
     ppm = K * (ratio ** P)   # K=2.60, P=2.467
     ```
     （非精確校正公式，僅供模擬展示用，沿用本 repo 既有慣例）
   - `client.publish("v1/devices/me/telemetry", ujson.dumps({"gas_ppm": ppm}), qos=1)`
   - `ppm > THRESHOLD` 印出 `[ALARM] gas_ppm=...`，否則印出 `[DEBUG] gas_ppm=...`
5. 錯誤處理：WiFi 斷線會自動重連；MQTT publish 失敗會印出錯誤訊息並嘗試重新連線，不會讓程式直接掛掉。

## 檔案
| 檔案 | 說明 |
|------|------|
| `main.py` | 主程式：WiFi → MQTT → 每 5 秒讀 MQ2 換算 ppm → publish telemetry → 本地告警判斷 |
| `diagram.json` | Wokwi 接線圖（ESP32 + MQ2） |
| `wokwi.toml` | 指向 repo 共用 firmware |
| `umqtt/simple.py` | 向量化（vendored）的 `umqtt.simple` 函式庫，供 `from umqtt.simple import MQTTClient` 使用（本課程 firmware 未內建此模組，需隨專案一起上傳到模擬板） |
| `Makefile` / `make.bat` | 透過 RFC2217 連到已開啟的 Wokwi 模擬器執行 `main.py` |

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

## ThingsBoard 後台設定（雲端 Alarm Rule，不在程式內處理）
1. ThingsBoard Cloud → Devices → 建立裝置，取得 Access Token，貼到 `main.py` 的 `ACCESS_TOKEN`。
2. Device profile → Alarm rules → 新增規則：`gas_ppm > 140` 觸發告警、`gas_ppm <= 140` 清除告警。

## 驗收標準
- [ ] Wokwi 執行後 Serial 能看到 WiFi 取得 IP、MQTT 連線成功訊息
- [ ] 每 5 秒印出一次 `[DEBUG] gas_ppm=...`（或 `[ALARM]`）並同步 publish 到 ThingsBoard
- [ ] 拖動 MQ2 滑桿讓 ppm > 140 時，本地印出 `[ALARM] gas_ppm=...`
- [ ] 程式碼只專注 WiFi + MQTT + MQ2，不含第一、二題的 TFT/OLED/DHT22 邏輯
