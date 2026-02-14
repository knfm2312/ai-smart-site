from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# 1. Get your URI from the .env file
# It should look like: mongodb+srv://user:pass@cluster.mongodb.net/
uri = os.getenv("MONGO_URI")

try:
    # 2. Initialize the client
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    
    # 3. Send a 'ping' to the server
    client.admin.command('ping')
    print("✅ Success! You have bypassed the firewall and logged in.")
    
    # 4. Try creating a tiny test record
    db = client.test_database
    db.test_collection.insert_one({"status": "Success", "message": "I am alive!"})
    print("📝 Test record written to MongoDB Atlas successfully.")

except Exception as e:
    print(f"❌ Connection Error: {e}")
    print("\n💡 Check if: \n1. Your IP is whitelisted (0.0.0.0/0)\n2. Your password in the URI is correct\n3. You replaced <password> (including the brackets!)")