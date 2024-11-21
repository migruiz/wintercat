#if defined(ESP32)
#include <analogWrite.h>
#endif

#if defined(ESP8266)
#include <ESP8266WiFi.h>
#else
#include <WiFi.h>
#endif
#include <PubSubClient.h>

const char* ssid = "VM712429A";
const char* password = "tBhj6Hxe7abj";
const char* mqttServer = "192.168.0.11";
const int mqttPort = 1883;
const char* mqttUser = "";
const char* mqttPassword = "";

WiFiClient wifiClient;
PubSubClient client(wifiClient);  //lib required for mqtt

int pin = 14;
int connectionTries = 0;


void WIFI_Connect() {
  WiFi.disconnect();
  WiFi.begin(ssid, password);
  Serial1.print("Wifi Status:");
  Serial1.println(WiFi.status());
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial1.println("Connecting to WiFi..");
    connectionTries = connectionTries + 1;
    if (connectionTries > 20) {
      connectionTries = 0;
      Serial1.println("aborting connection...");
      return;
    }
  }
  Serial1.println("Connected to the WiFi network");

  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);
  while (!client.connected()) {
    Serial1.println("Connecting to MQTT...");
    if (client.connect("OREGON", mqttUser, mqttPassword)) {
      Serial1.println("connected");
    } else {
      Serial1.print("failed with state ");
      Serial1.print(client.state());
      delay(2000);
    }
  }
  client.publish("OREGON/esp", "Hello from OREGON");
  client.subscribe("OREGON/relay");
}


void setup() {
  Serial.begin(9600);
  Serial1.begin(115200);
  WIFI_Connect();
}

void callback(char* topic, byte* payload, unsigned int length) {

  Serial1.print("Message arrived in topic: ");
  Serial1.println(topic);

  Serial1.print("Message:");
  for (int i = 0; i < length; i++) {
    Serial1.print((char)payload[i]);
  }


  if (!strncmp((char*)payload, "on", length)) {
    Serial.println("on");
    Serial1.println("on");
  } else if (!strncmp((char*)payload, "off", length)) {
    Serial.println("off");
    Serial1.println("off");
  }
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    WIFI_Connect();
    return;
  }
  if (!client.connected()) {
    WIFI_Connect();
    return;
  }
  if (Serial.available() > 0) {
    String str = Serial.readString();
    str.trim();
    Serial1.println(str);
    client.publish("OREGON/esp", str.c_str());
  }
  client.loop();
}
