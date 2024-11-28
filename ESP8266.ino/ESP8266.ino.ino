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
    if (client.connect("WINTERCAT", mqttUser, mqttPassword)) {
      Serial1.println("connected");
    } else {
      Serial1.print("failed with state ");
      Serial1.print(client.state());
      delay(2000);
    }
  }
  client.publish("WINTERCAT", "Hello from WINTERCAT");
  client.subscribe("WINTERCAT/operate");
}


void setup() {
  Serial.begin(9600);
  Serial1.begin(115200);
  clearSerialBuffer();
  WIFI_Connect();
}

void clearSerialBuffer() {
  Serial.end();
  Serial.begin(9600);
}

void callback(char* topic, byte* payload, unsigned int length) {





  Serial1.print("Message arrived in topic: ");
  Serial1.println(topic);

  Serial1.print("Message:");
  for (int i = 0; i < length; i++) {
    Serial1.print((char)payload[i]);
  }

  payload[length] = 0;
  String recv_payload = String((char*)payload);
  Serial.println(recv_payload.c_str());
  Serial1.println(recv_payload.c_str());
  client.publish("WINTERCAT/Callback", topic);

  client.publish("WINTERCAT/Callback", recv_payload.c_str());
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
    Serial1.println(str);
    client.publish("WINTERCAT/readings", str.c_str());
  }
  client.loop();
}
