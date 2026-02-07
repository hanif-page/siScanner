# haven't tested with the sensors

import math

class ScanProcessor:
    # Hardware Constants
    VERTICAL_FOV = 27.0
    NUM_SLICES = 13
    # Angular shift per pixel in the 16-pixel array
    DEG_PER_STEP = VERTICAL_FOV / 16.0 # 1.6875 degrees

    @staticmethod
    def to_3d_coordinates(angle_deg, distance_mm, roi_index):
        """
        Transforms polar hardware readings into a 3D Cartesian point cloud.
        """
        # 1. Horizontal Angle (Theta)
        theta = math.radians(angle_deg)
        
        # 2. Vertical Angle (Phi)
        # 0 is center, Top is +13.5 deg, Bottom is -13.5 deg
        phi_deg = 13.5 - (roi_index * ScanProcessor.DEG_PER_STEP)
        phi = math.radians(phi_deg)

        # 3. Spherical to Cartesian Projection
        # Distance (d) is the slant range from the sensor
        x = round(distance_mm * math.cos(phi) * math.cos(theta), 2)
        y = round(distance_mm * math.cos(phi) * math.sin(theta), 2)
        z = round(distance_mm * math.sin(phi), 2)

        return {
            "x": x, 
            "y": y, 
            "z": z, 
            "dist": distance_mm, 
            "angle": angle_deg, 
            "roi_index": roi_index
        }