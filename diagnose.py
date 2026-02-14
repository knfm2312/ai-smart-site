import os
from dotenv import load_dotenv
from google import genai
from pymongo import MongoClient

# Load environment variables
load_dotenv()

print("1. Checking Environment Variables...")
api_key = os.getenv("GEMINI_API_KEY")
mongo_uri = os.getenv("MONGO_URI")

if not api_key or api_key == "--":
    print("❌ ERROR: Gemini API Key is missing or invalid in .env file!")
else:
    print("✅ Gemini API Key found.")

if not mongo_uri:
    print("❌ ERROR: MongoDB URI is missing in .env file!")
else:
    print("✅ MongoDB URI found.")

print("\n2. Testing Gemini Embedding Connection...")
try:
    client = genai.Client(api_key=api_key)
    response = client.models.embed_content(
        model="models/gemini-embedding-001",
        contents="This is a test to see if the AI can do math."
    )
    vector = response.embeddings[0].values
    print(f"✅ Gemini is working! Generated vector with {len(vector)} dimensions.")
except Exception as e:
    print(f"❌ GEMINI ERROR: {str(e)}")

print("\n3. Testing MongoDB Connection & Collection...")
try:
    db_client = MongoClient(mongo_uri)
    db = db_client.ai_website
    kb_col = db.knowledge_base
    
    doc_count = kb_col.count_documents({})
    print(f"✅ Connected to MongoDB! Found {doc_count} documents in 'knowledge_base'.")
    
    # Check if any documents actually have embeddings
    valid_docs = kb_col.count_documents({"embedding": {"$exists": True}})
    if valid_docs == 0:
        print("❌ ERROR: There are NO documents in your database with an 'embedding' field. You must delete the hollow document and re-upload.")
    else:
        print(f"✅ Found {valid_docs} document(s) with proper embeddings.")
        
except Exception as e:
    print(f"❌ MONGODB ERROR: {str(e)}")