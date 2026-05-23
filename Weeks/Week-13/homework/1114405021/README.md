# Week 13 Homework — SH1107 中文動畫溫度看板 (1114405021)

概述
本作業整合 `in-class/task3a` 的中文動畫顯示與 `in-class/task4` 的 DHT22 感測，目標在 128x128 的 SH1107 OLED 上持續顯示動態的中文字（「花火節」）、主視覺（龍珠圓與星）、英文資訊，以及即時溫度 `xx.x C`，並在畫面上顯示學號 `1114405021`。

版面配置
- 左/中央：龍珠主視覺（兩個圓 + 星形）為主要視覺元素。
- 上方右側：英文資訊文字（Penghu University / Dept of CSIE / 2026）。
- 右側：中文動畫區塊（「花火節」），採放大/縮小與垂直擺動的動畫效果。
- 底部或右上：即時溫度顯示（`xx.x C`）與學號小字（`1114405021`）。

動畫設計
- 採用每 250 ms 更新一幀（約 4 FPS），中文動畫使用循環放大（active frame 放大）與波浪偏移來達到動感。
- 主畫面每幀以 `draw_static_scene()` 與 `draw_chinese_animation()` 重畫，確保動畫與主視覺同步。

感測整合
- 使用 `dht.DHT22(Pin(23))` 串接 DHT22。
- 每 2 秒讀取一次感測器（在幀數控制中以每 8 幀觸發一次讀值）。
- 讀值包在 `try/except` 中：成功時更新 `last_temp`、`last_hum` 並在 Serial 印出 debug 訊息；失敗時在 Serial 印出錯誤並保留上次有效值，OLED 顯示 `--.- C` 或前一次數值。

旋轉/顯示處理
- 因 SH1107 driver 原生只支援 0/90/180/270 整數角度，若要自訂非 90 度倍數的旋轉（本次為左旋 23°，即逆時針 23°），採用離屏 `FrameBuffer`（`src_fb`）先繪製完整畫面，再以逐像素座標旋轉（以畫面中心為旋轉中心）將像素寫回 `oled`。
- 在 `main.py` 中，驅動 `rotate` 設為 `0`（不由驅動做旋轉），並提供 `blit_rotate(src, dst, angle_deg)` 可接受任意角度（度數為逆時針方向）進行映射。

錯誤與解法（遇到的一個問題）
- 問題：在直接讀取 `framebuf.FrameBuffer.pixel(x,y)` 時，某些 framebuf 變體或讀取超出範圍會丟出例外，或是直接在 OLED 上逐像素寫回導致效能瓶頸。若未妥善處理，程式會在模擬器上產生例外並中斷。
- 解法：
  1. 使用 `try/except` 包住 pixel 讀寫，若讀取失敗就忽略該像素，確保不會中斷主迴圈。
  2. 使用離屏 `src_fb` 將所有繪製先完成，再一次性以我們的 `blit_rotate()` 演算法將非 90 度角旋轉後的像素寫回 OLED，並在必要時以 `dst.fill(0)` 清畫面，減少逐像素更新時的頁面碎片問題。

如何執行（Wokwi）
1. 啟動 Wokwi 的 RFC2217 server（通常在 Wokwi web 專案上啟動模擬後會監聽 `localhost:4000`）。
2. 在專案根目錄執行：

```powershell
python tools\wokwi_run.py --port 4000 Weeks/Week-13/homework/1114405021/main.py
```

3. 觀察 Serial 與 Wokwi 預覽視窗，Serial 會輸出類似：
```
[DEBUG] temperature = 24.0C, humidity = 40.0%
```

交付檔案
- `main.py`：已實作（路徑：Weeks/Week-13/homework/1114405021/main.py）
- `README.md`（此檔）
- 證明檔（請使用 Wokwi UI 擷取 OLED 截圖與製作 GIF）

後續建議
- 若要更順暢的非整數角度旋轉，可考慮在 PC 端預先運算位圖或以更高效的旋轉演算法（例如掃描線映射或使用 lookup 表）來減少 MCU 運算負擔。
# Week13 作業 — SH1107 中文動畫溫度看板

作者：1114405021

概要
- 本作業整合 `in-class/task3a` 的中文動畫與 `in-class/task4` 的 DHT22 感測，使用 SH1107 128x128 OLED 顯示動畫與即時溫度。
- 顯示元素：龍珠主視覺（圓 + 星）、左側英文字區塊、右側溫度區塊、右側直排中文動畫（花火節）、OLED 顯示學號。

版面配置
- 左上：校名與系名（小字）
- 左中：學號（`1114405021`）
- 中下：龍珠（偏左校正，使用 `CENTER_X/CENTER_Y` 可調）
- 右上：溫度資訊（`xx.x C`）與濕度
- 右中：直排中文動畫（花火節），會輪流放大與上下波動

動畫設計
- 動畫採每 250 ms 更新一幀，中文採放大（縮放 2x / 1x）與波浪位移組合。
- 龍珠為靜態主視覺（如需可加入旋轉星或呼吸效果作為加分）。

感測整合
- DHT22 接到 `GPIO23`（`DHT_PIN` 可調）
- 每 2000 ms 讀一次感測值，若成功會將 `temperature` 與 `humidity` 更新並在 Serial 列印：
  - 範例：`[DEBUG] temperature = 24.0C, humidity = 40.0%`
- 若讀取失敗，程式不會崩潰，會在 Serial 印出錯誤訊息並保留最後一次有效值。

程式結構
- `main.py` 主要函式：
  - `draw_static_scene(oled, temp_text, humidity_text)`
  - `draw_chinese_animation(oled, frame)`
  - `read_sensor_safe(sensor, last_temp, last_hum)`
  - `main()` 主迴圈：負責定時讀感測、更新動畫幀、重畫並 `oled.show()`。

遇到的問題與解法
- 問題：Wokwi 上 SH1107 的可視中心與座標對齊與預期不同，導致主視覺看起來偏移。
- 解法：提供 `CENTER_X`、`CENTER_Y` 常數作為校正點，並把龍珠 `dragon_cx = CENTER_X - 16` 作微幅偏移以貼齊視覺中心。

如何執行（在 `Weeks/Week-13/homework/1114405021` 下）
1. 啟動 Wokwi 模擬器並確認 RFC2217 連線（localhost:4000）。
2. 執行：
```powershell
& 'd:\11\2026-IOT-INTRO-Wokwi\tools\wokwi_run.py' run --target .
```
或使用各 task 的 `make.bat run`（若你在該資料夾）：
```powershell
& 'd:\11\2026-IOT-INTRO-Wokwi\Weeks\Week-13\homework\1114405021\make.bat' run
```

繳交檔案
- `main.py`（已包含）
- `README.md`（本檔）
- 建議附：OLED 截圖、運行 GIF、Serial 截圖
