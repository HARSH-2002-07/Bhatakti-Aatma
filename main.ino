#include <Servo.h>

Servo servo;
#define LF 4
#define LB 5

#define RF 6
#define RB 7

int serPin = 2;
int sp1 = 3, sp2 = 11;
void setup()
{
  Serial.begin(9600);

  pinMode(RF, OUTPUT);
  pinMode(LF, OUTPUT);
  pinMode(LB, OUTPUT);
  pinMode(RB, OUTPUT);
  pinMode(sp1, OUTPUT);
  pinMode(sp2, OUTPUT);
  servo.attach(serPin);
  delay(500);
  analogWrite(sp1, 100);
  analogWrite(sp2, 100);
}

void changeSpeed(int spd)
{
  analogWrite(sp1, spd);
  analogWrite(sp2, spd);
}

void backward()
{
  digitalWrite(LF, LOW);
  digitalWrite(LB, HIGH);
  digitalWrite(RF, LOW);
  digitalWrite(RB, HIGH);
}

void stopIt()
{
  digitalWrite(LF, LOW);
  digitalWrite(LB, LOW);
  digitalWrite(RF, LOW);
  digitalWrite(RB, LOW);
}

void forward()
{
  digitalWrite(LF, HIGH);
  digitalWrite(LB, LOW);
  digitalWrite(RF, HIGH);
  digitalWrite(RB, LOW);
}

void right()
{
  digitalWrite(LF, HIGH);
  digitalWrite(LB, LOW);
  digitalWrite(RF, LOW);
  digitalWrite(RB, HIGH);
}

void left()
{
  digitalWrite(LF, LOW);
  digitalWrite(LB, HIGH);
  digitalWrite(RF, HIGH);
  digitalWrite(RB, LOW);
}

void doBullshit(int incoming)
{
  if (incoming == 0)
  {
    Serial.println("Stopping");
    stopIt();
  }
  else if (incoming == 1)
  {
    Serial.println("Going Forward");
    forward();
  }
  else if (incoming == 2)
  {
    Serial.println("Going Backward");
    backward();
  }
  else if (incoming == 3)
  {
    Serial.println("Going Left");
    left();
  }
  else if (incoming == 4)
  {
    Serial.println("Going Right");
    right();
  }
  else if (incoming == 5)
  {
    Serial.println("Enter speed value (0 - 255)");
    while (Serial.available() <= 0) {}
    int val = Serial.readStringUntil('\n').toInt();
    changeSpeed(val);
    Serial.println("Speed successfully changed.");
    for (int i = 90; i < 180; i++) {
      servo.write(i);
      delay(10);
    }
    for (int i = 180; i >= 0; i--) {
      servo.write(i);
      delay(10);
    }
    for (int i = 0; i <= 90; i++) {
      servo.write(i);
      delay(10);
    }
  }
}

void loop()
{
  if (Serial.available() > 0)
  {
    int incoming = Serial.readStringUntil('\n').toInt();
    Serial.print("Received: ");
    Serial.println(incoming);

    doBullshit(incoming);

  }
  delay(20);
}