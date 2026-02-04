# siScanner: Real-Time LiDAR Spatial Mapping System

siScanner is a 2D LiDAR scanning system designed for industrial spatial auditing and digital twinning. By leveraging Time-of-Flight (ToF) laser technology and a NoSQL data pipeline, the system generates real-time, persistent spatial maps used for logistics optimization, safety boundary monitoring, and historical structural analysis.

## Business Value & Further Application
- Industrial Logistics: Automates warehouse floor-plan auditing to optimize robot navigation and storage density.
- O&G Safety: Monitors "Red Zones" in hazardous areas, providing non-contact obstacle detection for offshore rigs.
- Predictive Analysis: Uses historical scan playback to detect structural shifts or unauthorized modifications over time.

## Technical Architecture
#### Hardware Layer
- Microcontroller: Arduino Nano (ATmega328P).
- Primary Sensor: TOF400C-VL53L1X (4-meter range, 1mm resolution).
- Actuator: TowerPro SG90 180° Servo for precise angular sweeping.
- Protocol: High-speed I2C communication at 400kHz.

#### Software Layer
- Firmware: C++ (Arduino IDE) with optimized Region of Interest (ROI) beam-narrowing.
- Desktop Engine (Python 3.10+): 
    - PyQt6 Framework: Native macOS/Windows/Linux UI for zero-latency interaction.
    - PyQtGraph: High-performance, GPU-accelerated graphics engine for real-time 2D point-cloud rendering.
- Data Pipeline: Multithreaded `SerialWorker` that decouples hardware I/O from UI rendering to prevent frame-drops.
- Database: MongoDB for persistent storage of scan sessions (Temporal Data).


## Project Structure
```
siScanner/
├── firmware/
│   └── lidar_scanner/
│       └── lidar_scanner.ino      # Arduino C++: Servo control & Sensor reading
├── app/
│   ├── __init__.py                # Package marker (empty)
│   ├── database.py                # MongoDB: Save/Load scan sessions
│   ├── processor.py               # Math: Polar-to-Cartesian logic
│   ├── serial_worker.py           # Threading: Async Serial listener for Nano
│   └── styles.qss                 # UI Styling: Modern "Dark Mode" stylesheet
├── main.py                        # Entry Point: PyQt6 App & Main Window
├── simulate_data.py               # Testing: Virtual sweep generator
├── .env                           # Config: SERIAL_PORT=/dev/cu.usbserial...
├── .gitignore                     # Git rules: ignore __pycache__, .env, etc.
├── requirements.txt               # Updated PyQt6 dependencies
└── README.md                      # Documentation: Setup & Usage
```

## Technical Note:

(none)
