import math
import random 
from app.database import SiScannerDatabase

def run_high_res_simulator():
    db = SiScannerDatabase()
    simulated_points = []

    # Constants based on hardware physics
    NUM_SLICES = 13
    VERTICAL_FOV = 27.0
    DEG_PER_PIXEL = VERTICAL_FOV / 16.0 # 1.6875 degrees
    
    print(f"🚀 Generating 13-Slice Volumetric Sweep ({NUM_SLICES} points per horizontal angle)...")

    # Step through 180 degrees horizontally
    for angle in range(0, 181, 2):
        theta = math.radians(angle)
        
        # Simulate a wall at 2m with a decorative pillar in the center
        base_dist = 2000 if not (85 < angle < 95) else 1400
        
        for i in range(NUM_SLICES):
            # Calculate vertical angle (phi)
            # Center of the 27° FoV is 0°. Top is +13.5°, Bottom is -13.5°.
            # Each ROI shift (i) moves the 4x4 window down the 16-pixel array.
            phi_deg = 13.5 - (i * DEG_PER_PIXEL)
            phi = math.radians(phi_deg)
            
            # Add micro-texture noise
            distance = base_dist + random.uniform(-15, 15)
            
            # Spherical to Cartesian Coordinate Conversion
            # Corrected for 3D projection
            x = round(distance * math.cos(phi) * math.cos(theta), 2)
            y = round(distance * math.cos(phi) * math.sin(theta), 2)
            z = round(distance * math.sin(phi), 2)

            simulated_points.append({
                "angle": angle,
                "roi_index": i,      # Vertical slice ID (0 to 12)
                "dist": distance,
                "x": x,
                "y": y,
                "z": z,              # Real vertical height in mm
                "phi": phi_deg       # Store for verification
            })

    # Save with the new Ultra-Res mode
    session_id = db.save_scan_session(simulated_points, scan_mode="13D_ULTRA")
    if session_id:
        print(f"✅ Simulation Complete. Total Nodes: {len(simulated_points)}")

if __name__ == "__main__":
    run_high_res_simulator()