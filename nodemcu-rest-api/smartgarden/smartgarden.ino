#include <ESP8266WiFi.h>       
#include <DHT.h>      
#include <WiFiUdp.h>
#include <WiFiClient.h>
#include "Arduino.h"
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>
#include <ArduinoJson.h>
#include <ESP8266HTTPClient.h>


WiFiClient wifiClient;

#define dht_pin D2                                            // the dht air temperature and humidity sensor is conntected to NodeMCU ESP8266 at digital pin D2
#define dht_type DHT22                                        // initialize dht type as DHT22
DHT dht(dht_pin, dht_type); 

#define soil_moisture_pin A0  // the capacitive soil moisture sensor is conntected to NodeMCU ESP8266 at analog pin A0

#define relay_input D3 // the relay is conntected to NodeMCU ESP8266 at digital pin D4  -> the relay is controlling the pump
String pump_state = "off"; // variable that keeps whether the pump is on or off to be written on the web server 


//initialize the variables used for sensor readings as global variables
float air_humidity = 0.0;                                 // read air humidity from dht sensor
float air_temperature = 0.0;                              // read air temperature from dht sensor
float soil_moisture = 0.0;                                // read soil moisture from capacitive sensor
float calibrated_soil_moisture = 0.0;                     // used for mapping the raw soil moisture value in the interval 0-100%

// the values given by the soil humidity sensor in special cases (for calibrating the sensor)
const float saturated_soil = 286;
const float water = 305;
const float dry_soil = 560;
const float air = 740;


#define wifi_ssid "CremeneD2.4"                                  
#define wifi_password "deliadiana99" 

unsigned long previousMillis = 0;
unsigned long interval = 30000;


ESP8266WebServer server(80);


void getSensorReadings() {
  // read sensor data
  dht.begin();   //reads dht sensor data  
  air_humidity = dht.readHumidity();                                 // read air humidity
  air_temperature = dht.readTemperature();                           // read air temperature
  soil_moisture = analogRead(soil_moisture_pin);                     // read soil moisture
  // map(value, fromLow, fromHigh, toLow, toHigh)
  // re-maps a number from one range to another -> we want to go from 286-560 raw values to 0-100%
  calibrated_soil_moisture = map(soil_moisture, dry_soil, saturated_soil, 0, 100);      

  DynamicJsonBuffer jsonBuffer;
  JsonObject& root = jsonBuffer.createObject();
  root["moisture"] = calibrated_soil_moisture;
  root["humidity"] = air_humidity;
  root["temperature"] = air_temperature;
  root["board_id"] = 1;
  String json;
  root.prettyPrintTo(json);
  server.send(200, "text/json", json);
}

void turnPumpOn() {
   pump_state = "on";
   digitalWrite(relay_input, LOW); // turn relay on = turn the pump on in the normally open circuit
   getPumpState();
}

void turnPumpOff() {
   pump_state = "off";
   digitalWrite(relay_input, HIGH); // turn relay off = turn the pump off  
   getPumpState();
}

void getPumpState() {
  DynamicJsonBuffer jsonBuffer;
  JsonObject& root = jsonBuffer.createObject();
  root["pump_state"] = pump_state;
  root["board_id"] = 1;
  String json;
  root.prettyPrintTo(json);

  server.send(200, "text/json", json);
}

// define routing
void restServerRouting() {
  
    server.on("/", HTTP_GET, []() {
        server.send(200, F("text/html"),
            F("welcome to the REST web server"));
    });
    
    server.on("/getSensorReadings", HTTP_GET, getSensorReadings);

    server.on("/turnPumpOn", HTTP_GET, turnPumpOn);

    server.on("/turnPumpOff", HTTP_GET, turnPumpOff);

    server.on("/getPumpState", HTTP_GET, getPumpState);
}
 
// manage not found url
void handleNotFound() {
  String message = "File Not Found\n\n";
  message += "URI: ";
  message += server.uri();
  message += "\nMethod: ";
  message += (server.method() == HTTP_GET) ? "GET" : "POST";
  message += "\nArguments: ";
  message += server.args();
  message += "\n";
  for (uint8_t i = 0; i < server.args(); i++) {
    message += " " + server.argName(i) + ": " + server.arg(i) + "\n";
  }
  server.send(404, "text/plain", message);
}
 

void connectToWiFi()
{
  Serial.print("Connecting to ");
  Serial.print(wifi_ssid);
  WiFi.begin(wifi_ssid, wifi_password);  
  while (WiFi.status() != WL_CONNECTED) 
  {
    Serial.print(".");
    delay(500);
  } 

  Serial.println("\nConnected");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());   // prints local IP address
}


void connectToBackend()
{
  
  DynamicJsonBuffer jsonBuffer;
  JsonObject& root = jsonBuffer.createObject();
  root["message:"] = "connected a new board";
  root["ip"] = WiFi.localIP().toString();
  root["board_id"] = 1;
  String json;
  root.prettyPrintTo(json);
  Serial.println(json);

  HTTPClient http; //Object of class HTTPClient
  http.begin(wifiClient, "http://f193-46-97-176-161.ngrok.io/connectBoard");
  http.addHeader("Content-Type", "application/json");

  int httpCode = http.POST(json);
  Serial.println(httpCode);

  if (httpCode > 0) 
  {
    Serial.println("success");
  }
  http.end(); //close connection
}


void setupServer() {
  // Activate mDNS this is used to be able to connect to the server
  // with local DNS hostmane esp8266.local
  if (MDNS.begin("esp8266")) {
    Serial.println("MDNS responder started");
  }
 
  // Set server routing
  restServerRouting();
  // Set not found response
  server.onNotFound(handleNotFound);
  // Start server
  server.begin();
  Serial.println("HTTP server started");
}

void tryToReconnectToWiFiIfIssues() {
  unsigned long currentMillis = millis();
  // if WiFi is down, try reconnecting every CHECK_WIFI_TIME seconds
  if ((WiFi.status() != WL_CONNECTED) && (currentMillis - previousMillis >=interval)) {
    Serial.print(millis());
    Serial.println("Reconnecting to WiFi...");
    WiFi.disconnect();
    WiFi.begin(wifi_ssid, wifi_password);
    Serial.println(WiFi.localIP());
    //Alternatively, you can restart your board
    //ESP.restart();
    Serial.println(WiFi.RSSI());
    previousMillis = currentMillis;
  }
}


void setup() {
  Serial.begin(9600);

  pinMode(relay_input, OUTPUT); // set the digital pin of the relay as output
  pinMode(dht_pin, INPUT); // set the dht pin as input
  pinMode(soil_moisture_pin, INPUT); // set the analog pin of the soil moisture sensor as input

  connectToWiFi();                                 
  connectToBackend();
  setupServer();
  
}



// the loop function runs over and over again forever
void loop() {

      server.handleClient();

      tryToReconnectToWiFiIfIssues();
}
