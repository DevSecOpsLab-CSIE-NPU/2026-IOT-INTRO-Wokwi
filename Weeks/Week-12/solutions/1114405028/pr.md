# PR 說明 — 1114405028 Week-12 Knight Rider

## 標題範例

完成 Week-12 Knight Rider 作業：1114405028

## 摘要

本次 PR 將 `Weeks/Week-12/solutions/1114405028/main.py` 完成 Knight Rider 跑馬燈題目的 TODO 部分。

## 變更項目

- 新增 `Weeks/Week-12/solutions/1114405028/README.md`
- 新增 `Weeks/Week-12/solutions/1114405028/pr.md`
- 完成 `Weeks/Week-12/solutions/1114405028/main.py`

## 變更內容說明

- `main.py` 實作 4 顆 LED 的 Knight Rider 來回掃描效果。
- 每步的間隔為 `0.15` 秒。
- 只有一顆 LED 會亮，抵達兩端時反轉移動方向。
- `all_off()` 用來熄滅所有 LED，避免同時有多顆 LED 亮。

## 測試步驟

1. 切換到此 PR 的分支。
2. 儲存並執行 `main.py`。
3. 觀察 LED 是否依序點亮，從左往右再往左來回掃描。
4. 確認每步間隔約 0.15 秒，目標僅有一顆 LED 亮著。

## 檢查清單

- [ ] 已完成 `main.py` 的 Knight Rider 掃描邏輯
- [ ] 已加入 `README.md` 與 `pr.md`
- [ ] 已確認執行結果符合題目描述
- [ ] 若有截圖，可補上於 PR 說明中

---

問題說明參考自 `Weeks/Week-12/homework/knight-rider/task.md`。