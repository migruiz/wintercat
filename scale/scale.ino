#if defined(ESP32)
#include <analogWrite.h>
#endif
#include <ArduinoJson.h>
#if defined(ESP8266)
#include <ESP8266WiFi.h>
#else
#include <WiFi.h>
#endif
#include <PubSubClient.h>

const char *ssid = "PIAP";
const char *password = "hackol37";
const char *mqttServer = "192.168.0.11";
const int mqttPort = 1883;
const char *mqttUser = "";
const char *mqttPassword = "";

WiFiClient wifiClient;
PubSubClient client(wifiClient); // lib required for mqtt

int connectionTries = 0;

#include <HX711_ADC.h>

#if defined(ESP8266) || defined(ESP32) || defined(AVR)
#include <EEPROM.h>
#endif

// pins:
const int HX711_dout = 4; // mcu > HX711 dout pin
const int HX711_sck = 5;  // mcu > HX711 sck pin

// HX711 constructor:
HX711_ADC LoadCell(HX711_dout, HX711_sck);

const int calVal_eepromAdress = 0;
const int tareOffsetVal_eepromAdress = 4;
unsigned long t = 0;

void WIFI_Connect()
{
  WiFi.disconnect();
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    connectionTries = connectionTries + 1;
    if (connectionTries > 20)
    {
      connectionTries = 0;
      return;
    }
  }

  client.setServer(mqttServer, mqttPort);
  while (!client.connected())
  {
    if (client.connect("WINTERCATSCALE", mqttUser, mqttPassword))
    {
    }
    else
    {
      delay(2000);
    }
  }
  client.publish("WINTERCAT", "Hello from WINTERCATSCALE");
}

bool checkWifi()
{
  if (WiFi.status() != WL_CONNECTED)
  {
    WIFI_Connect();
    return false;
  }
  if (!client.connected())
  {
    WIFI_Connect();
    return false;
  }
  return true;
}

void setup()
{
  Serial.begin(57600);
  delay(10);
  WIFI_Connect();
  Serial.println();
  Serial.println("Starting...");

  LoadCell.begin();
  float calibrationValue = 18.05;

  LoadCell.setTareOffset(8888954);
  boolean _tare = false; // set this to false as the value has been resored from eeprom

  unsigned long stabilizingtime = 2000; // preciscion right after power-up can be improved by adding a few seconds of stabilizing time
  LoadCell.start(stabilizingtime, _tare);
  if (LoadCell.getTareTimeoutFlag())
  {
    Serial.println("Timeout, check MCU>HX711 wiring and pin designations");
    while (1)
      ;
  }
  else
  {
    LoadCell.setCalFactor(calibrationValue); // set calibration value (float)
    Serial.println("Startup is complete");
  }
}

void loop()
{
  static boolean newDataReady = 0;
  const int serialPrintInterval = 3000; // increase value to slow down serial print activity

  // check for new data/start next conversion:
  if (LoadCell.update())
    newDataReady = true;

  // get smoothed value from the dataset:
  if (newDataReady)
  {
    if (millis() > t + serialPrintInterval)
    {
      float i = LoadCell.getData();
      Serial.print("Load_cell output val: ");
      Serial.println(i);

      if (!checkWifi())
      {
        return;
      }

      JsonDocument doc;
      doc["messageType"] = "scale";
      doc["value"] = i

      char buffer[256];
      size_t n = serializeJson(doc, buffer);
      client.publish("WINTERCAT/readings", buffer, n);

      newDataReady = 0;
      t = millis();
    }
  }
  client.loop();
}
