#include <LiquidCrystal.h>
LiquidCrystal lcd(8,7,5,4,3,2);
void setup() {
    Serial.begin(9600);
}

void loop() {
    if (Serial.available()) {
        String mensaje = Serial.readStringUntil('\n');
        if (mensaje == "Comprobar") {
            Serial.println("CONECTADO");
            lcd.print("Conectado");
        }
    }
}
