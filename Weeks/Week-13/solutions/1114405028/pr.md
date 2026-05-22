# PR 說明 — 1114405028 Week-13 Homework

## 標題建議
[Week13][1114405028] SH1107 中文動畫溫度看板

## 摘要
本 PR 新增 Week-13 作業實作，包含 `main.py`（SH1107 + DHT22 整合）與 `README.md`、`pr.md`。

## 變更項目
- 新增 `Weeks/Week-13/solutions/1114405028/main.py`
- 新增 `Weeks/Week-13/solutions/1114405028/README.md`
- 新增 `Weeks/Week-13/solutions/1114405028/pr.md`

## 變更內容說明
- `main.py`：
  - 每 200ms 更新動畫幀，右側直排中文字 `花火節` 做放大/縮小與上下波動。
  - 每 2 秒讀取 DHT22，序列印出 `temperature` 與 `humidity`。
  - 顯示學號 `1114405028` 在 OLED 畫面。
  - 使用 `try/except` 處理讀感測器錯誤，並在 OLED 顯示 `Sensor Error`。

## 測試步驟
1. 切換分支或將檔案加入專案。
2. 在板上或 Wokwi 執行 `Weeks/Week-13/solutions/1114405028/main.py`。
3. 觀察 OLED 是否有動畫、中文顯示與即時溫度。並檢查序列輸出。

## 檢查清單
- [ ] 有中文動畫 `花火節`
- [ ] 顯示即時溫度 `xx.x C`
- [ ] OLED 畫面有學號 `1114405028`
- [ ] Serial 有 `temperature`/`humidity` debug

---

（依照課程 HOMEWORK.md 規定製作）