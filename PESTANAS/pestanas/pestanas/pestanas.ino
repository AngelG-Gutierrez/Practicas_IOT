/* Realizado por:
   Angel Antelmo Gutierrez Gadea
   Genaro Alfredo Silva Espinoza
   Alejandro Hernandez Hernandez
*/

#include <LiquidCrystal.h>
#include <ArduinoJson.h>
#include <DHT.h>

LiquidCrystal lcd(8, 7, 5, 4, 3, 2);

int red, green, blue;
int r = 11;
int g = 12;
int b = 13;

int SENSOR = 10;
float tempC;
int humed;

int LDR = A0;
int intensidad = 0;

unsigned long previoMillis = 0;
unsigned long previoMillis2 = 0;
const long intervalo = 2000;
const long intervalo2 = 4000;

DHT dht(SENSOR, DHT11);

void setup() {
    lcd.begin(16, 2);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Esperando...");

    Serial.begin(9600);
    pinMode(r, OUTPUT);
    pinMode(g, OUTPUT);
    pinMode(b, OUTPUT);
    pinMode(LDR, INPUT);
    dht.begin();
}

void loop() {
    if (Serial.available() > 0) {
        String cadena = Serial.readStringUntil('\n');
        cadena.trim();

        if (cadena == "Conectado") {
            Serial.println("CONECTADO");
            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("Conectado");
            return;
        }

        int resultado = procesarJson(cadena, red, green, blue);
        if (resultado == 1) {
            lcd.setCursor(0, 0);
            lcd.print("                "); 
            lcd.setCursor(0, 0);
            lcd.print("RGB:");
            lcd.print(red);
            lcd.print(",");
            lcd.print(green);
            lcd.print(",");
            lcd.print(blue);

            analogWrite(r, red);
            analogWrite(g, green);
            analogWrite(b, blue);
        }
    }
    leerDHT11();
    leerLDR();
}

int procesarJson(const String &cadena, int &red, int &green, int &blue) {
    StaticJsonDocument<128> doc;
    DeserializationError error = deserializeJson(doc, cadena);
    if (error) {
        Serial.println("Error al convertir a JSON: " + String(error.c_str()));
        return -1;
    }
    if (doc.containsKey("r") && doc.containsKey("g") && doc.containsKey("b")) {
        red = doc["r"];
        green = doc["g"];
        blue = doc["b"];
        return 1;
    } else {
        Serial.println("Error: Faltan campos en el JSON.");
        return -2;
    }
}

void leerDHT11() {
    if (millis() - previoMillis >= intervalo) {
        previoMillis = millis();
        tempC = dht.readTemperature();
        humed = dht.readHumidity();
        
        lcd.setCursor(0, 1);
        lcd.print("                "); 
        lcd.setCursor(0, 1);
        lcd.print("T:");
        lcd.print(tempC, 1);
        lcd.print((char)223);
        lcd.print("C H:");
        lcd.print(humed);
        lcd.print("%");
    }
}

void leerLDR() {
    if (millis() - previoMillis2 >= intervalo2) {
        previoMillis2 = millis();
        intensidad = analogRead(LDR);
        StaticJsonDocument<128> doc;
        doc["tempc"] = tempC;
        doc["humed"] = humed;
        doc["ldr"] = intensidad;
        String output;
        serializeJson(doc, output);
        Serial.println(output);
    }
}