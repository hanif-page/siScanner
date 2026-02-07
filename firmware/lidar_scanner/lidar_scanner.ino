#include <Wire.h>
#include <VL53L1X.h>
#include <Servo.h>

// Haven't tested with the sensors

VL53L1X sensor;
Servo yawServo;

// Configuration
const int SERVO_PIN = 9;
const int START_ANGLE = 0;
const int END_ANGLE = 180;
const int NUM_SLICES = 13;

void setup() {
  Serial.begin(115200); // High-speed link for volumetric data
  Wire.begin();
  Wire.setClock(400000); // 400kHz I2C for fast ROI switching

  yawServo.attach(SERVO_PIN);
  yawServo.write(START_ANGLE);
  delay(500);

  if (!sensor.init()) {
    Serial.println("Failed to detect sensor!");
    while (1);
  }

  sensor.setDistanceMode(VL53L1X::Long);
  sensor.setMeasurementTimingBudget(20000); // 20ms per slice
  sensor.startContinuous(20);
}

void loop() {
  // Forward Sweep: 0 to 180
  for (int angle = START_ANGLE; angle <= END_ANGLE; angle++) {
    scanVerticalSlice(angle);
  }
  
  // Return Sweep: 180 to 0 (Optional: scan on return or just move back)
  yawServo.write(START_ANGLE);
  delay(1000); 
}

void scanVerticalSlice(int angle) {
  yawServo.write(angle);
  delay(15); // Wait for servo to stabilize

  for (int i = 0; i < NUM_SLICES; i++) {
    // Shifting a 4x4 ROI down the 16-pixel SPAD array
    // Center 199 is Top, Center 151 is Bottom.
    // Each step is a 1-pixel vertical shift (approx 4 units in center-code)
    int roi_center = 199 - (i * 4); 
    
    sensor.setROICenter(roi_center);
    int distance = sensor.read();

    // Protocol: angle,distance,roi_index
    Serial.print(angle);
    Serial.print(",");
    Serial.print(distance);
    Serial.print(",");
    Serial.println(i);
  }
}