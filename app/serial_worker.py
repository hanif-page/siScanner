# haven't tested with the sensors

import serial
import time
from PyQt6.QtCore import QThread, pyqtSignal

class SerialWorker(QThread):
    data_received = pyqtSignal(dict)
    status_changed = pyqtSignal(str)

    def __init__(self, port='/dev/cu.usbserial-10', baud=115200):
        super().__init__()
        self.port = port
        self.baud = baud
        self.running = True

    def run(self):
        try:
            # Connect to Arduino Nano
            ser = serial.Serial(self.port, self.baud, timeout=0.1)
            self.status_changed.emit(f"Connected: {self.port}")
            
            while self.running:
                if ser.in_waiting > 0:
                    try:
                        line = ser.readline().decode('utf-8').strip()
                        parts = line.split(',')
                        
                        if len(parts) == 3:
                            # Package the hardware signals for the UI
                            payload = {
                                "angle": int(parts[0]),
                                "dist": float(parts[1]),
                                "roi_index": int(parts[2])
                            }
                            self.data_received.emit(payload)
                    except ValueError:
                        continue # Skip corrupted serial packets
                time.sleep(0.001)
            ser.close()
        except Exception as e:
            self.status_changed.emit(f"Serial Error: {str(e)}")

    def stop(self):
        self.running = False
        self.wait()