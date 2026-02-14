import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def test_cloud_db():
    try:
        # 1. Connect
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client.ai_website
        collection = db.knowledge_base
        
        # 2. Check Connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")

        # 3. Check for Data
        doc_count = collection.count_documents({})
        print(f"📊 Total documents in 'knowledge_base': {doc_count}")

        if doc_count > 0:
            sample = collection.find_one()
            print(f"🔎 Sample Document Found: {sample.get('filename')}")
            if "embedding" in sample:
                print(f"🧠 Vector detected! (Size: {len(sample['embedding'])})")
            else:
                print("❌ Document found, but it's missing the 'embedding' field.")
        else:
            print("⚪ Collection is empty. Try uploading a PDF via your web app first!")

    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    test_cloud_db()