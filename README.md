# 🌊 ClutterFlow

> AI-powered document processing and organization system for students and professionals

[![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.4-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.39.0-red.svg)](https://streamlit.io/)

## 🚀 Features

### Core Functionality
- **📝 OCR Text Extraction** - Extract text from PDFs and images using Tesseract
- **🤖 AI Summarization** - Generate summaries using Mistral 7B via Ollama
- **🏷️ Topic Classification** - Automatically categorize documents by subject
- **🔍 Semantic Search** - Find documents using natural language queries
- **⚙️ Background Processing** - Non-blocking AI tasks with queue management

### Technical Highlights
- **RESTful API** with FastAPI and comprehensive OpenAPI documentation
- **Real-time Processing** with background task queue system
- **Database Integration** with Supabase (PostgreSQL)
- **Modern Frontend** with Streamlit for beautiful web interface
- **Local AI** using Ollama and Mistral 7B (no API costs!)

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │───▶│     FastAPI      │───▶│     Supabase    │
│   Frontend      │    │     Backend      │    │    Database     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │      Ollama      │
                       │    Mistral 7B    │
                       └──────────────────┘
```

## 📋 Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai) installed and running
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed
- Supabase account and project

## 🛠️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/clutterflow.git
cd clutterflow
```

### 2. Set up virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies
cd ../frontend
pip install -r requirements.txt
```

### 4. Set up Ollama and Mistral
```bash
# Install Ollama (visit https://ollama.ai for instructions)

# Start Ollama server
ollama serve

# Download Mistral 7B model
ollama pull mistral:7b
```

### 5. Configure environment variables
```bash
# Create backend/.env file
cp backend/.env.example backend/.env

# Edit with your Supabase credentials
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
DATABASE_URL=postgresql://postgres:password@db.project.supabase.co:5432/postgres
```

### 6. Set up database schema
Run the SQL schema in your Supabase SQL Editor (see `docs/schema.sql`)

## 🚀 Usage

### Start the Backend
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Start the Frontend
```bash
cd frontend
streamlit run streamlit_app.py
```

### Access the Application
- **Frontend**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **API**: http://localhost:8000

## 📚 API Endpoints

### Document Processing
- `POST /extract` - Upload and process documents
- `GET /documents` - List all documents
- `GET /documents/{id}` - Get document details
- `DELETE /documents/{id}` - Delete document

### AI Features
- `POST /documents/{id}/summarize` - Generate summary
- `POST /documents/{id}/classify` - Classify document
- `GET /documents/{id}/summary` - Get existing summary
- `GET /documents/{id}/classification` - Get classification

### Processing Management
- `GET /tasks` - View processing queue
- `GET /analytics/overview` - Processing statistics

## 🧪 Testing

### Test OCR and AI Integration
```bash
cd backend
python test_llm.py
```

### Test API Endpoints
```bash
curl -X POST "http://localhost:8000/extract" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample.pdf"
```

## 📁 Project Structure

```
clutterflow/
├── backend/                 # FastAPI backend
│   ├── main.py             # API server
│   ├── services/           # Business logic
│   │   ├── text_extractor.py
│   │   ├── llm_service.py
│   │   ├── database.py
│   │   └── background_processor.py
│   ├── models/             # Data models
│   │   ├── database_models.py
│   │   └── schemas.py
│   └── config/             # Configuration
│       └── settings.py
├── frontend/               # Streamlit frontend
│   └── streamlit_app.py
├── docs/                   # Documentation
└── README.md
```

## 🎯 Use Cases

### For Students
- **Lecture Notes**: Upload handwritten or typed notes for automatic organization
- **Research Papers**: Extract key insights and classify by subject
- **Assignment Materials**: Keep track of all course documents

### For Professionals
- **Contract Analysis**: Extract and summarize legal documents
- **Report Processing**: Organize business reports by department/topic
- **Knowledge Management**: Build searchable company knowledge base

## 🔧 Configuration

### Environment Variables
```bash
# Supabase
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
DATABASE_URL=your-database-url

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral:7b

# Processing
MAX_FILE_SIZE=52428800
BACKGROUND_PROCESSING_ENABLED=true
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) for local AI model serving
- [Mistral AI](https://mistral.ai) for the 7B language model
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for text extraction
- [Supabase](https://supabase.com) for database and backend services
- [FastAPI](https://fastapi.tiangolo.com/) for the modern API framework
- [Streamlit](https://streamlit.io/) for the beautiful frontend

## 📧 Contact

Your Name - your.email@example.com

Project Link: [https://github.com/yourusername/clutterflow](https://github.com/yourusername/clutterflow)