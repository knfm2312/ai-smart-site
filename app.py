import os
import re
import gc  # Added for memory management
from datetime import datetime
from functools import wraps

# Flask and Security
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Third-party Integrations
from authlib.integrations.flask_client import OAuth
from google import genai
from pypdf import PdfReader
from pymongo import MongoClient
from bson.objectid import ObjectId

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "pro-dev-2026")

# --- MEMORY SAFETY CONFIGURATION ---
# Prevent OOM (Out of Memory) by limiting PDF size to 5MB
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 

# --- DATABASE & CLIENT CONFIGURATION ---
client = MongoClient(os.getenv("MONGO_URI"))
db = client.ai_website
users_col = db.users
kb_col = db.knowledge_base  
chat_col = db.chat_history

ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# OAuth Setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# --- USER MANAGEMENT ---
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.is_admin = user_data.get('is_admin', False)

@login_manager.user_loader
def load_user(user_id):
    try:
        u = users_col.find_one({"_id": ObjectId(user_id)})
        return User(u) if u else None
    except:
        return None

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin access required.")
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# --- AUTHENTICATION ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_data = users_col.find_one({"email": email})
        
        if user_data and user_data.get('password'):
            if check_password_hash(user_data['password'], password):
                login_user(User(user_data))
                return redirect(url_for('home'))
        
        flash("Invalid credentials or account uses social login.")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        if password != confirm:
            flash("Passwords do not match.")
            return redirect(url_for('signup'))

        if len(password) < 8 or not re.search(r"[0-9!@#$%^&*()]", password):
            flash("Password must be 8+ chars and include a number or symbol.")
            return redirect(url_for('signup'))

        if users_col.find_one({"email": email}):
            flash("User already exists.")
            return redirect(url_for('signup'))

        users_col.insert_one({
            "username": username,
            "email": email,
            "password": generate_password_hash(password),
            "is_admin": False,
            "auth_provider": "local"
        })
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login/google')
def google_login():
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/callback')
def google_callback():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')
    
    user_data = users_col.find_one({"email": user_info['email']})
    
    if not user_data:
        new_user = {
            "username": user_info['name'],
            "email": user_info['email'],
            "password": None,
            "is_admin": False,
            "auth_provider": "google"
        }
        res = users_col.insert_one(new_user)
        user_data = users_col.find_one({"_id": res.inserted_id})

    login_user(User(user_data))
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

# --- CORE CHAT LOGIC ---

@app.route('/')
@login_required
def home():
    return render_template('index.html', user=current_user)

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    try:
        user_query = request.json.get('message')
        if not user_query: return jsonify({"response": "Empty message."})

        prev_chats = list(chat_col.find({"user_id": current_user.id}).sort("timestamp", -1).limit(3))
        chat_context = "\n".join([f"{c['role']}: {c['content']}" for c in reversed(prev_chats)])

        query_res = ai_client.models.embed_content(model="models/gemini-embedding-001", contents=user_query)
        query_embedding = query_res.embeddings[0].values

        pipeline = [{
            "$vectorSearch": {
                "index": "vector_index", 
                "path": "embedding", 
                "queryVector": query_embedding, 
                "numCandidates": 100, 
                "limit": 4
            }
        }]
        search_results = list(kb_col.aggregate(pipeline))
        kb_context = " ".join([r.get('text', '') for r in search_results])
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Context: {kb_context}\n\nHistory: {chat_context}\n\nUser: {user_query}"
        )

        chat_col.insert_many([
            {"user_id": current_user.id, "role": "User", "content": user_query, "timestamp": datetime.now()},
            {"user_id": current_user.id, "role": "AI", "content": response.text, "timestamp": datetime.now()}
        ])

        return jsonify({"response": response.text})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"response": "Internal processing error."}), 500

# --- UTILITY & ADMIN ---

@app.route('/get_history')
@login_required
def get_history():
    history = list(chat_col.find({"user_id": current_user.id}).sort("timestamp", 1).limit(50))
    for m in history: m['_id'] = str(m['_id'])
    return jsonify(history)

@app.route('/delete_history', methods=['POST'])
@login_required
def delete_history():
    chat_col.delete_many({"user_id": current_user.id})
    return jsonify({"message": "History cleared."})

@app.route('/admin')
@login_required
@admin_required
def admin_page():
    files = kb_col.distinct("filename")
    return render_template('admin.html', files=files)

@app.route('/upload', methods=['POST'])
@login_required
@admin_required
def upload():
    file = request.files.get('file')
    if file and file.filename.endswith('.pdf'):
        try:
            filename = secure_filename(file.filename)
            reader = PdfReader(file)
            text = " ".join([p.extract_text() or "" for p in reader.pages])
            
            # Chunking and embedding
            chunks = [text[i:i+1000] for i in range(0, len(text), 800)]
            for chunk in chunks:
                res = ai_client.models.embed_content(model="models/gemini-embedding-001", contents=chunk)
                kb_col.insert_one({
                    "filename": filename, 
                    "text": chunk, 
                    "embedding": res.embeddings[0].values
                })
            
            # CRITICAL: Clean up memory after upload
            del reader
            gc.collect() 
            
            return jsonify({"message": "Knowledge updated successfully."})
        except Exception as e:
            print(f"Upload Error: {e}")
            return jsonify({"message": "Processing error."}), 500
            
    return jsonify({"message": "Upload failed."}), 400

@app.route('/delete_file/<filename>', methods=['POST'])
@login_required
@admin_required
def delete_file(filename):
    kb_col.delete_many({"filename": filename})
    return jsonify({"message": f"Document '{filename}' removed."})

if __name__ == '__main__':
    app.run(debug=True)
