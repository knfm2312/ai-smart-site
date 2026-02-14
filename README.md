# 🤖 AI-Smart-Site — RAG-Powered Assistant

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-brightgreen.svg)
![Gemini](https://img.shields.io/badge/AI-Gemini%202.0%20Flash-orange.svg)

A **modern AI-powered website** featuring a Retrieval-Augmented Generation (RAG) chatbot.  
Admins can upload PDFs to build a dynamic knowledge base, while users interact with a **smart chatbot** that provides **context-aware answers** in real time.

---

## 📚 Table of Contents
- [✨ Features](#-features)
- [🛠️ Tech Stack](#%EF%B8%8F-tech-stack)
- [🚀 Getting Started](#-getting-started)
  - [1️⃣ Installation](#1%EF%B8%8F-installation)
  - [2️⃣ Environment Setup](#2%EF%B8%8F-environment-setup)
  - [3️⃣ Configure MongoDB Vector Index](#3%EF%B8%8F-configure-mongodb-vector-index)
- [📂 Project Structure](#-project-structure)
- [🧩 Summary](#-summary)

---

## ✨ Features

- 🧠 **Context-Aware AI:** Uses **Google Gemini 2.0 Flash** for intelligent, fast responses.  
- 📄 **Dynamic Knowledge Base:** Admins upload PDFs → automatically chunked & embedded.  
- 🔐 **Secure Authentication:** Includes local login/signup + **Google OAuth**.  
- 💬 **Real-time Chat Widget:** Sleek floating UI with typing indicators & message history.  
- 📱 **Fully Responsive:** Works smoothly on both desktop and mobile.

---

## 🛠️ Tech Stack

| Category | Technology |
|-----------|-------------|
| **Backend** | Flask (Python 3.9+) |
| **Database** | MongoDB Atlas (Vector Search) |
| **AI/LLM** | Google Gemini 2.5 Flash |
| **Embeddings** | text-embedding-004 |
| **Frontend** | Jinja2, Vanilla JS, CSS3 |
| **Auth** | Flask-Login & Google OAuth 2.0 |

---

## 🚀 Getting Started

### 1️⃣ Installation
```bash
git clone https://github.com/yourusername/ai-smart-site.git
cd ai-smart-site
pip install -r requirements.txt
2️⃣ Environment Setup
Create a .env file in the project root and add your credentials:

SECRET_KEY=your_flask_secret_key
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/ai_website
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_CLIENT_ID=your_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
3️⃣ Configure MongoDB Vector Index
In MongoDB Atlas, create a vector index with this configuration:

{
  "fields": [
    {
      "numDimensions": 3072,
      "path": "embedding",
      "similarity": "cosine",
      "type": "vector"
    }
  ]
}
📂 Project Structure
.
├── app.py              # Main Flask server & RAG logic
├── requirements.txt    # Dependencies
├── .env                # Environment variables
├── static/
│   ├── css/style.css   # Styling
│   └── js/chat.js      # Frontend chat logic
└── templates/
    ├── index.html      # Landing page
    ├── admin.html      # Document upload
    ├── login.html      # User login
    └── signup.html     # Registration
