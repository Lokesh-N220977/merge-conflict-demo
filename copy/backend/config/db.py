import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables from .env
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

# Create a global MongoClient instance using pymongo
client = MongoClient(MONGO_URL, tlsAllowInvalidCertificates=True)

# Export a global db object for the project
db = client.health_appointment
