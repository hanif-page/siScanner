from pymongo import MongoClient, errors
from datetime import datetime

class SiScannerDatabase:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="siScanner_DB"):
        # initialized the MongoDB connection
        # use a 2-second timeout to ensure UI stability (so that it does not freeze when the DB is not responsing)

        try:
            self.client = MongoClient(uri, serverSelectionTimeoutMS=2000)
            self.db = self.client[db_name]
            self.collection = self.db["Scans"]

            # Server status check
            self.client.server_info()
            print(f"Successfully connected to MongoDB: {db_name}")
        except errors.ServerSelectionTimeoutError:
            print("MongoDB Connection Error: Server not found. Run 'brew services start mongodb-community@7.0'")
            self.client = None

    def save_scan_session(self, points):
        # saves 180degree sweep to the siScanner database.
        if self.client:
            scanned_document = {
                "project": "siScanner",
                "timestamp": datetime.now(),
                "total_points": len(points),
                "data": points
            }
            try:
                result = self.collection.insert_one(scanned_document)
                print(f"Saved scan session with ID: {result.inserted_id}")
                return result.inserted_id
            except Exception as e:
                print(f"Failed to save siScanner data: {e}")

    def get_all_sessions(self):
        # retrieves list of siScanner sessions for historical replay
        if self.client:
            return list(self.collection.find({}, {"_id": 1, "timestamp": 1}))
        return []
    
    def get_session_by_id(self, session_id):
        # load specific siScanner data based on its id
        if self.client:
            return self.collection.find_one({"_id": session_id})
        return None