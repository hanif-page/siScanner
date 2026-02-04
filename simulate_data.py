import math
import random 
from database import SiScannerDatabase

def run_siScanner_simulator():
    db = SiScannerDatabase()
    simulated_points = []

    print("Generating Virtual 180-Degree siScanner Sweep...")

    # Simulate a 180-degree sweep with points every degree
    for angle in range(181):
        # Simulating a dynamic distance
        distance = 1800 + random.randint(-200, 200)
        theta = math.radians(angle)
        x = round(distance * math.cos(theta), 2)
        y = round(distance * math.sin(theta), 2)

        simulated_points.append({"angle": angle, "dist": distance, "x": x, "y": y})

    # Saving the scan session
    session_id = db.save_scan_session(simulated_points)
    if session_id:
        print(f"siScanner Data Saved!\nSession ID: {session_id}")

if __name__ == "__main__":
    run_siScanner_simulator()
