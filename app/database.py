from pymongo import MongoClient, errors
from datetime import datetime

class SiScannerDatabase:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="siScanner_DB"):
        try:
            self.client = MongoClient(uri, serverSelectionTimeoutMS=2000)
            self.db = self.client[db_name]
            self.collection = self.db["Scans"]
            self.client.server_info()
            print(f"Connected to MongoDB: {db_name}")
        except errors.ServerSelectionTimeoutError:
            print("Database Error: Check if MongoDB is running.")
            self.client = None

    def save_scan_session(self, points, scan_mode="13D_ULTRA"):
        """Saves high-density volumetric scan data."""
        if self.client:
            scanned_document = {
                "project": "siScanner",
                "timestamp": datetime.now(),
                "scan_mode": scan_mode,
                "v_resolution": 13, # Vertical slices
                "total_points": len(points),
                "data": points
            }
            try:
                result = self.collection.insert_one(scanned_document)
                print(f"✅ {scan_mode} Session Saved. ID: {result.inserted_id}")
                return result.inserted_id
            except Exception as e:
                print(f"Save Failed: {e}")

    def get_all_sessions(self):
        if self.client:
            return list(self.collection.find({}, {"_id": 1, "timestamp": 1, "scan_mode": 1}))
        return []
    
    def get_session_by_id(self, session_id):
        if self.client:
            return self.collection.find_one({"_id": session_id})
        return None