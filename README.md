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
- Data Pipeline: Python-based Serial-to-JSON bridge.
- Database: MongoDB for persistent storage of scan sessions (Temporal Data).
- Visualization: Streamlit Dashboard with Plotly interactive point-cloud rendering.


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

## Technical Note: Dependency Resolution

During environment setup, a versioning conflict may occur between Streamlit and Wheel regarding the `packaging` utility.
- Conflict: Streamlit (v1.31.0) requires `packaging < 24.0`, while modern Wheel versions require `packaging >= 24.0`.
- Resolution: Use the **Conda-First** installation strategy to allow the Conda SAT solver to stabilize the environment foundation before installing UI components.

#### Recommended Setup Sequence

```
# Bash Command

# 1. Create environment with core math foundations
conda create --name sentinel-v python=3.10 numpy pandas packaging -c conda-forge -y
conda activate sentinel-v

# 2. Install UI and Database bridges
pip install streamlit==1.31.0 plotly pymongo pyserial python-dotenv
```
