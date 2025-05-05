from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGODB_URL"))
        self.db = self.client["sound_monitoring"]
        self.alerts = self.db["alerts"]
        self.sensors = self.db["sensors"]
        self.trackings = self.db["trackings"]

    def close(self):
        self.client.close()

db = Database()
