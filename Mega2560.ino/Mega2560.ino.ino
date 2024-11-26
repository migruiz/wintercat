/**
 *******************************
 *
 * Version 1.0 - Hubert Mickael <mickael@winlux.fr> (https://github.com/Mickaelh51)
 *  - Clean ino code
 *  - Add MY_DEBUG mode in library
 * Version 0.2 (Beta 2) - Hubert Mickael <mickael@winlux.fr> (https://github.com/Mickaelh51)
 *  - Auto detect Oregon 433Mhz
 *  - Add battery level
 *  - etc ...
 * Version 0.1 (Beta 1) - Hubert Mickael <mickael@winlux.fr> (https://github.com/Mickaelh51)
 *
 *******************************
 * DESCRIPTION
 * This sketch provides an example how to implement a humidity/temperature from Oregon sensor.
 * - Oregon sensor's battery level
 * - Oregon sensor's id
 * - Oregon sensor's type
 * - Oregon sensor's channel
 * - Oregon sensor's temperature
 * - Oregon sensor's humidity
 *
 * Arduino UNO <-- (PIN 2) --> 433Mhz receiver <=============> Oregon sensors
 */


#include <ArduinoJson.h>
#include <SPI.h>
#include <EEPROM.h>
#include <Oregon.h>

//Define pin where is 433Mhz receiver (here, pin 2)
#define MHZ_RECEIVER_PIN 2
#define RELAY_PIN 50

void setup() {
  Serial.begin(9600);

  JsonDocument setupDoc;
  setupDoc["messageType"] = "debug";
  setupDoc["value"] = "Setup started";
  serializeJson(setupDoc, Serial);
  Serial.println();

  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
  //Setup received data
  attachInterrupt(digitalPinToInterrupt(MHZ_RECEIVER_PIN), ext_int_1, CHANGE);

  JsonDocument setupCompletedDoc;
  setupCompletedDoc["messageType"] = "debug";
  setupCompletedDoc["value"] = "Setup Completed";
  serializeJson(setupCompletedDoc, Serial);
  Serial.println();
}


void loop() {
  //------------------------------------------
  //Start process new data from Oregon sensors
  //------------------------------------------
  cli();
  word p = pulse;
  pulse = 0;
  sei();
  if (p != 0) {
    if (orscV2.nextPulse(p)) {
      //Decode Hex Data once
      const byte* DataDecoded = DataToDecoder(orscV2);

      JsonDocument doc;
      doc["messageType"] = "oregonReading";
      doc["id"] = String(id(DataDecoded));
      doc["channel"] = String(channel(DataDecoded));
      doc["model"] = String(OregonType(DataDecoded));
      doc["temperature"] = String(temperature(DataDecoded));
      doc["humidity"] = String(humidity(DataDecoded));
      doc["battery"] = String(battery(DataDecoded));
      serializeJson(doc, Serial);
      Serial.println();
    }
  }
  if (Serial.available() > 0) {
    String str = Serial.readString();
    str.trim();
    JsonDocument docReading;
    DeserializationError error = deserializeJson(docReading, str);
    if (error) {
      Serial.print(F("deserializeJson() failed: "));
      Serial.println(error.c_str());
      return;
    }
    const char* messageType = docReading["messageType"];
    Serial.println(messageType);
    if (String(messageType) == "heatRelay") {
      const bool value = docReading["value"];
      Serial.println(String(value));
      if (value) {
        digitalWrite(RELAY_PIN, HIGH);
      } else {
        digitalWrite(RELAY_PIN, LOW);
      }
    }
  }
}