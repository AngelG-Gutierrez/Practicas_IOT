/*Realizado por 
Angel Antelmo Gutierrez Gadea
Genaro Alfredo Silva Espinoza
Alejandro Hernandez Hernandez
*/

#include <LiquidCrystal.h>
#include <ArduinoJson.h>
#include <ArduinoJson.hpp>
#include <DHT.h>
#include <DHT_U.h>
LiquidCrystal lcd(8,7,5,4,3,2);

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
unsigned long actualMillis = 0;

unsigned long previoMillis2 = 0;
unsigned long actualMillis2 = 0;

const long intervalo = 2000;
const long intervalo2 =4000;

DHT dht (SENSOR, DHT11);

void setup() {
  // put your setup code here, to run once:
  lcd.begin(16,2);
  Serial.begin(9600);
  pinMode(r,OUTPUT);
  pinMode(g,OUTPUT);
  pinMode(b,OUTPUT);
  pinMode(LDR, INPUT);
  dht.begin();
  Serial.println("");
  Serial.println("Escribe la cadena rgb (ejemplo: {\"r\":21,\"g\":51,\"b\":100}):");
  Serial.println("");

}

void loop() {
  // put your main code here, to run repeatedly:
  lcd.setCursor(2,0);
  if(Serial.available() > 0){
    String cadena1 = Serial.readStringUntil('\n');
    cadena1.trim();

    //Serial.println("\nCadena RGB ingresada: " + cadena1);

    int resultado = procesarJson(cadena1, red, green, blue);

    if (resultado == 1) {
      Serial.println("");
      Serial.println("Valores extraídos:");
      Serial.print("Rojo: ");
      Serial.println(red);
      Serial.print("Verde: ");
      Serial.println(green);
      Serial.print("Azul: ");
      Serial.println(blue);

      lcd.clear();
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
    Serial.println("Error al convertir a JSON:");
    Serial.println(error.c_str());
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

int leerDHT11(){

  actualMillis = millis();
  if(actualMillis - previoMillis >= intervalo){
    previoMillis = actualMillis;
      tempC = dht.readTemperature();
      humed = dht.readHumidity();
      //Serial.println("tempC: " + String(tempC,1));
      //Serial.println("humed: " + String(humed));
  }

  lcd.setCursor(0,1);
  lcd.print("T:");
  lcd.print(tempC,1);
  lcd.print((char)223);
  lcd.print(" ");
  lcd.print("H:");
  lcd.print(humed);
  lcd.print("%");
}

int leerLDR(){
  actualMillis2 = millis();
  if(actualMillis2 - previoMillis2 >= intervalo2){
    previoMillis2 = actualMillis2;
    intensidad = analogRead(LDR);
    //Serial.println("LDR: " + String(intensidad));
      String cadena = "{\"tempC\": " + String(tempC) + ", \"humed\": " + String(humed) + ", \"LDR\": " + String(intensidad) + "\}";
      Serial.println(cadena);
  }
}

