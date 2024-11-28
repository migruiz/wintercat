#if defined(ESP32)
#include <analogWrite.h>
#endif

#if defined(ESP8266)
#include <ESP8266WiFi.h>
#else
#include <WiFi.h>
#endif
#include <PubSubClient.h>

const char* ssid = "PIAP";
const char* password = "hackol37";
const char* mqttServer = "192.168.0.11";
const int mqttPort = 1883;
const char* mqttUser = "";
const char* mqttPassword = "";

WiFiClient wifiClient;
PubSubClient client(wifiClient);  //lib required for mqtt

int connectionTries = 0;


void WIFI_Connect() {
  WiFi.disconnect();
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    connectionTries = connectionTries + 1;
    if (connectionTries > 20) {
      connectionTries = 0;
      return;
    }
  }

  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);
  while (!client.connected()) {
    if (client.connect("WINTERCAT", mqttUser, mqttPassword)) {
    } else {
      delay(2000);
    }
  }
  client.publish("WINTERCAT", "Hello from WINTERCAT");
  client.subscribe("WINTERCAT/operate");
}


void setup() {
  clearSerialBuffer();
  WIFI_Connect();
}

void clearSerialBuffer() {
  Serial.end();
  Serial.begin(9600);
}

void callback(char* topic, byte* payload, unsigned int length) {



  payload[length] = 0;
  String recv_payload = String((char*)payload);
  Serial.println(recv_payload.c_str());
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    clearSerialBuffer();
    WIFI_Connect();
    return;
  }
  if (!client.connected()) {
    clearSerialBuffer();
    WIFI_Connect();
    return;
  }
  if (Serial.available() > 0) {
    String str = Serial.readString();
    str.trim();
    client.publish("WINTERCAT/readings", str.c_str());
  }
  client.loop();
}
