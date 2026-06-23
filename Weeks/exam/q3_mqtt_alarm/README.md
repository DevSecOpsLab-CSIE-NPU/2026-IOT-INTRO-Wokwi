# Q3: MQTT PPM Alarm to ThingsBoard

Student ID: 1114405029

Teacher correction: MQ2 AO/AOUT uses GPIO34, not GPIO36.

## Hardware

- ESP32 DevKit C V4
- MQ2 gas sensor

## Wiring

| MQ2 gas sensor | ESP32 |
| --- | --- |
| AO/AOUT | GPIO34 |
| VCC | VIN / 5V |
| GND | GND |

## Program Requirements

- WiFi SSID: `Wokwi-GUEST`
- WiFi password: empty string
- ThingsBoard MQTT host: `mqtt.thingsboard.cloud`
- ThingsBoard MQTT port: `1883`
- MQTT topic: `v1/devices/me/telemetry`
- Telemetry payload: `{"gas_ppm": ppm}`
- JSON key must be exactly `gas_ppm`
- `THRESHOLD = 140`
- MQ2 ADC uses `ADC(Pin(34))`
- ADC attenuation uses `ADC.ATTN_11DB`
- Upload interval: 5 seconds

## ThingsBoard Cloud Steps

1. Log in to ThingsBoard Cloud.
2. Go to Devices, then Add device.
3. Copy the device Access Token.
4. Paste the token into `main.py`:
   ```python
   ACCESS_TOKEN = "PUT_YOUR_THINGSBOARD_ACCESS_TOKEN_HERE"
   ```
5. Run Wokwi.
6. Open the device Latest telemetry tab and confirm that `gas_ppm` keeps updating.
7. Create an Alarm Rule:
   - If `gas_ppm > 140`, create an Alarm.
   - If `gas_ppm <= 140`, clear the Alarm.
8. Drag the MQ2 gas sensor value in Wokwi so `gas_ppm` is over 140, then confirm that one Alarm is created.

## Run

```bat
cd exam\q3_mqtt_alarm
make.bat run 4001
```

Expected serial output:

```text
[DEBUG] raw=... gas_ppm=... threshold=140
[ALARM] gas_ppm over threshold
```

or:

```text
[DEBUG] raw=... gas_ppm=... threshold=140
[NORMAL] gas_ppm <= threshold
```
