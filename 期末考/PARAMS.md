# 你的參數

學號末兩碼：23

```text
DHT22 = GPIO19
MQ2   = GPIO36
標題顏色 = 青色 Cyan = color565(0, 255, 255)
THRESHOLD = 80 ppm
```

ThingsBoard Alarm Rule 建議：

- Create Alarm：`gas_ppm > 80`
- Clear Alarm：`gas_ppm <= 80`
