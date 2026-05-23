#include <Arduino.h>
#include "DHT.h"

#define DHTPIN 23        // matches diagram.json
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  delay(1000);
  dht.begin();
  Serial.println("DHT22 test start");
}

void loop() {
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature(); // Celsius

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("[ERROR] Failed to read from DHT sensor!");
  } else {
    Serial.printf("[DEBUG] temperature = %.1fC, humidity = %.1f%%\n", temperature, humidity);
  }

  delay(2000); // read every 2 seconds
}
