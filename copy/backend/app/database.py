import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    raise ValueError("MONGO_URL environment variable is not set")

# Connect to MongoDB Atlas using PyMongo
client = MongoClient(MONGO_URL, tlsAllowInvalidCertificates=True)

# Expose the global database object
database = client.health_appointment
