# Week-12 Knight Rider — 解答（1114405028）

本資料夾包含 Week-12 範例與作業解答，實作 Knight Rider（跑馬燈）效果：

- `main.py`：Knight Rider 主程式。4 顆 LED 由左向右掃描，抵達端點後反向，間隔 0.15 秒，且同一時刻僅有一顆 LED 亮。
- `task1_main.py`、`task2_main.py`、`task3_main.py`、`task4_main.py`：對應課堂練習題的註解版實作。
- `homework_knight_rider_main.py`：與 `main.py` 相同的作法，保留為實作備份。

執行方式：
1. 將 `main.py` 上傳到開發板或在模擬器中執行。
2. 觀察 4 顆 LED 是否依序從左至右再回到左側往返掃描。

注意：腳位可依實際電路圖調整 `PINS` 陣列內容（預設為 [5, 2, 15, 4]）。