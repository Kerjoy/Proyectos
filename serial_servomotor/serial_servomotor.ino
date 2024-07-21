#include <Servo.h>
#include <pwmWrite.h>

/*
  Controls servo position from 0-180 degrees and back
  https://wokwi.com/projects/350037178957431378
  by dlloydev, December 2022.
*/

#include <Servo.h>

Servo myservo = Servo();
int pos;
const int servoPin = 2;

void setup() {
  Serial.begin(9600);
}

void loop() {

  while(Serial.available() > 0){
    pos = Serial.parseInt();
    myservo.write(servoPin, pos);
    delay(500);

 }

}
