// Description: This code was provided from: 
// https://github.com/curiores/ArduinoTutorials/blob/main/SpeedControl/SpeedControl_NoAtomic/SpeedControl_NoAtomic.ino
// and serves as an example on how PID works with a brushed DC motor using an encoder on Arduino

// This alternate version of the code does not require
// atomic.h. Instead, interrupts() and noInterrupts() 
// are used. Please use this code if your 
// platform does not support ATOMIC_BLOCK.

// Encoder pins
#define ENCA 15
#define ENCB 19

// Motor driver pins
#define PWM1 2
#define PWM2 3
#define EN 4
#define ENB 5

// globals
long prevT = 0;
int posPrev = 0;
float v1 = 0;
float v2 = 0;

// Use the "volatile" directive for variables
// used in an interrupt
volatile int pos_i = 0;
volatile float velocity_i = 0;
volatile long prevT_i = 0;

float v1Filt = 0;
float v1Prev = 0;
float v2Filt = 0;
float v2Prev = 0;
float uPrev = 0;

float eintegral = 0;

void setup() {
  Serial.begin(115200);

  // label the pin modes
  pinMode(ENCA,INPUT);
  pinMode(ENCB,INPUT);
  pinMode(PWM1,OUTPUT);
  pinMode(PWM2,OUTPUT);
  pinMode(EN,OUTPUT);
  pinMode(ENB,OUTPUT);

  // enable the motor driver by default
  digitalWrite(EN, 1);
  digitalWrite(ENB, 0);

  attachInterrupt(digitalPinToInterrupt(ENCA),
                  readEncoder,RISING);
}

void loop() {

  // read the position and velocity
  int pos = 0;
  float velocity2 = 0;
  noInterrupts(); // disable interrupts temporarily while reading
  pos = pos_i;
  velocity2 = velocity_i;
  interrupts(); // turn interrupts back on

  // Compute velocity with method 1
  long currT = micros();
  float deltaT = ((float) (currT-prevT))/1.0e6;
  float velocity1 = (pos - posPrev)/deltaT;
  posPrev = pos;
  prevT = currT;

  // Convert count/s to RPM
  float temp_v1 = velocity1/116.16*60.0;
  float temp_v2 = velocity2/116.16*60.0;

  // Perform checks to ensure velocities are correct in magnitude
  if (temp_v1 < 1100) {
    v1 = temp_v1;
  }

  if (temp_v2 < 1100) {
    v2 = temp_v2;
  }

  // Low-pass filter (25 Hz cutoff)
  v1Filt = 0.854*v1Filt + 0.0728*v1 + 0.0728*v1Prev;
  v1Prev = v1;
  v2Filt = 0.854*v2Filt + 0.0728*v2 + 0.0728*v2Prev;
  v2Prev = v2;

  // Set a target
  float vt = 1000*(sin(currT/5e6));
//  float vt = 500;

  // Compute the control signal u
  float kp = 0.01;
  float ki = 0.0001;
  float e = vt-v1Filt;
  eintegral = eintegral + e*deltaT;
  
  float u = kp*e + ki*eintegral + uPrev;
  uPrev = u;

  // Set the motor speed and direction
  int dir = 1;
  if (u<0){
    dir = -1;
  }
  int pwr = (int) fabs(u);
  if(pwr > 255){
    pwr = 255;
  }
  setMotor(dir, pwr, PWM1, PWM2);

//  Serial.println(dir);
  Serial.print(pwr);
  Serial.print(" ");
  Serial.print(vt);
  Serial.print(" ");
  Serial.print(v1Filt);
  Serial.println();
  delay(50);

//    // Code to test the motor function
//    int pwr = 10/3.0*micros()/1.0e6;
//    int dir = 1;
//    setMotor(dir, pwr, PWM1, PWM2);
//    Serial.println(pos);
//    Serial.print(v1);
//    Serial.print(" ");
//    Serial.print(v2);
//    Serial.println();
}

void setMotor(int dir, int pwmVal, int pwmPin1, int pwmPin2){
  if(dir == 1){ 
    // Turn one way
    analogWrite(pwmPin1, pwmVal);
    digitalWrite(pwmPin2, 0);
  }
  else if(dir == -1){
    // Turn the other way
    digitalWrite(pwmPin1, 0);
    analogWrite(pwmPin2, pwmVal);
  }
  else{
    // Or dont turn
    digitalWrite(pwmPin1, 0);
    digitalWrite(pwmPin2, 0);    
  }
}

void readEncoder(){
  // Read encoder B when ENCA rises
  int b = digitalRead(ENCB);
  int increment = 0;
  if(b>0){
    // If B is HIGH, increment backward
    increment = -1;
  }
  else{
    // Otherwise, increment forward
    increment = 1;
  }
  pos_i = pos_i + increment;
//  Serial.println(pos_i);
  
  // Compute velocity with method 2
  long currT = micros();
  float deltaT = ((float) (currT - prevT_i))/1.0e6;
  velocity_i = increment/deltaT;
  prevT_i = currT;
}
