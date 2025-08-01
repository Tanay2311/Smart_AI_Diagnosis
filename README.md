 Smart AI Diagnosis 🏥

An intelligent medical diagnosis assistant that leverages AI to help analyze symptoms and provide preliminary medical insights. This application combines natural language processing with medical knowledge to assist in symptom analysis and diagnosis suggestions.

 Features

- Symptom Analysis: Input symptoms in natural language and get AI-powered analysis
- Interactive Diagnosis: Step-by-step diagnostic process with follow-up questions
- Medical Knowledge Base: RAG (Retrieval-Augmented Generation) system with comprehensive medical data
- Demographics Integration: Personalized analysis based on patient demographics
- Progress Tracking: Visual tracking of the diagnosis process
- Post-Diagnosis Chat: Follow-up conversations and additional medical guidance
- Condition Information: Detailed information about diagnosed conditions

 Architecture

The application follows a modern full-stack architecture:

- Frontend: React.js with Tailwind CSS for responsive UI
- Backend: Python FastAPI for robust API endpoints
- AI Engine: RAG-based system using ChromaDB for medical knowledge retrieval
- Data Processing: Advanced symptom extraction and medical data cleaning

 Project Structure

```
Smart_AI_Diagnosis/
├── front/                     React Frontend
│   ├── src/
│   │   ├── components/        Reusable UI components
│   │   ├── pages/            Main application pages
│   │   └── assets/           Static assets and data
│   └── public/               Public assets
│
└── back/                     Python Backend
    ├── data/                 Medical data and RAG index
    │   ├── rag_index/        ChromaDB vector store
    │   └── .csv             Medical datasets
    ├── main.py               FastAPI application
    ├── models.py             Data models
    └── chatbot.py            AI chatbot logic
```

 Quick Start

 Prerequisites

- Node.js (v14 or higher)
- Python 3.9+
- pip (Python package manager)

 Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd back
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the backend server:
   ```bash
   python main.py
    or use the provided script
   ./start.sh
   ```

The backend will run on `http://localhost:8000`

 Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd front
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The frontend will run on `http://localhost:3000`

 🔧 API Endpoints

- `POST /extract-symptoms` - Analyze user-provided symptoms
- `POST /followup-questions` - Generate follow-up questions
- `POST /diagnosis` - Provide diagnosis based on collected data
- `GET /condition-info/{condition}` - Get detailed condition information
- `POST /chat` - Post-diagnosis chat functionality

 Data & Evaluation

The system includes comprehensive evaluation metrics:

- Symptom Extraction Accuracy: Detailed performance metrics for symptom identification
- Follow-up Question Relevance: Evaluation of generated follow-up questions
- Diagnosis Accuracy: Performance metrics for diagnostic suggestions
- Latency Analysis: Response time optimization data

Evaluation results are stored in various CSV files and visualized through generated charts.

 Technology Stack

 Frontend
- React.js
- Tailwind CSS
- Modern JavaScript (ES6+)

 Backend
- FastAPI (Python)
- ChromaDB (Vector Database)
- RAG (Retrieval-Augmented Generation)
- Natural Language Processing

 Data Management
- CSV data processing
- Vector embeddings for medical knowledge
- SQLite for metadata storage

 Performance Metrics

The system tracks several key performance indicators:
- Symptom extraction accuracy
- False positive/negative rates
- Response latency per case
- Follow-up question match ratios

 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

 Disclaimer

This application is for educational and research purposes only. It should not be used as a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of qualified healthcare providers with any questions regarding medical conditions.

 
---

Note: Make sure to configure your environment variables and API keys before running the application in production.
