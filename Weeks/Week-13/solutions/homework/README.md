# Week 13 Homework - SH1107 + DHT22 Chinese Animated Temperature Board

## File Location
- `Weeks/Week-13/solutions/homework/main.py`

## Design Summary
This homework combines the layout style from task3a with DHT22 integration from task4. The screen keeps the same visual hierarchy: information header at the top-left, a one-star dragon ball as the main graphic, and a vertical Chinese animation area on the right side. A new sensor block is added in the lower-left to show temperature and humidity values.

The board keeps running in a loop and updates one frame every 250 ms. Chinese characters `花火節` are animated with two effects: active-character zoom and wave-like vertical offset. The star inside the dragon ball also changes size over frames, making the whole screen feel alive.

## DHT22 Integration
- Sensor pin: `GPIO23`
- Read interval: every 2 seconds
- Display format: `xx.x C`
- Additional value: humidity is also shown as `xx.x %`

After each sensor read, Serial prints debug logs:
- `[DEBUG] temperature = ...C, humidity = ...%`
- `[ERROR] DHT22 read failed: ...`

If a read fails, the program does not crash:
- Uses `try/except`
- Keeps last valid temperature/humidity
- OLED shows `Sensor Error` blinking status

## Requirements Mapping
- Reference-like layout with clear sections: completed
- Continuous animation (250 ms/frame): completed
- Chinese text (`花火節`): completed
- Real-time DHT22 temperature (`xx.x C`): completed
- Student ID shown on OLED (`ID:1114405011`): completed

## One Problem and Fix
Problem: Wokwi SH1107 coordinate center is not visually centered when using naive `(64, 64)` placement.
Fix: Keep tunable constants (`center_x`, `center_y`, `status_x`, `status_y`, `chinese_base_x`, `chinese_base_y`) so the layout can be calibrated quickly without touching drawing logic.

## Proof Files To Add Before PR
Please add these files in this folder:
- `hw13-oled-screenshot.png` (OLED screenshot with Chinese + temperature)
- `hw13-running.gif` (at least 5 seconds)
- `hw13-serial-debug.png` (Serial log screenshot)

You can reference them in the PR description together with:
- main code path
- design summary
- sensor/debug behavior
