# California Ecosystem Resilience Simulator

An interactive environmental simulation platform that uses machine learning and natural language processing to model and visualize ecosystem changes in California.

## 🌟 Features

- **Natural Language Interface**: Interpret environmental change requests using LLM
- **Real-time Simulation**: Model environmental impacts across multiple factors
- **Interactive Visualization**: Dynamic charts and metrics for impact analysis
- **Geographical Integration**: County-level environmental data analysis
- **Confidence Scoring**: Reliability metrics for predictions

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+
- MongoDB Atlas account
- Google Cloud (Vertex AI) account

### Backend Setup

1. Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your credentials:
# - MONGO_URI
# - AZURE_STORAGE_CONNECTION_STRING
# - GOOGLE_CLOUD_PROJECT
```

4. Run the backend:

```bash
cd backend
python app.py
```

### Frontend Setup

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Run the development server:

```bash
npm run dev
```

## 📁 Project Structure

```
backend/
├── ml/
│   ├── models/           # ML models and inference
│   ├── analyze_merged_data.py
│   └── convertpis.py    # Data preprocessing
├── api/
│   └── environment_routes.py
└── app.py               # Main Flask application

frontend/
├── src/
│   ├── pages/          # React components
│   └── components/
└── app/
    └── layout.tsx      # Root layout
```

## 🔧 Key Components

### Machine Learning Pipeline

- Bayesian Network for environmental modeling
- LLM for natural language understanding
- Geographical data integration
- Confidence scoring system

### Visualization System

- Environmental changes tracking
- Impact analysis
- Confidence metrics
- Distribution analysis

### API Endpoints

- `/api/simulate`: Run environmental simulations
- `/api/messages`: Process natural language inputs
- `/api/variables`: Get available environmental variables

## 📊 Data Sources

The simulator uses various California environmental datasets:

- CalEnviroScreen 3.0
- Species Biodiversity Data
- Geographical/County-level Data
- Climate Vulnerability Metrics

## 🧪 Testing

Run the test suite:

```bash
cd backend/ml/models
python test_llm_pipeline.py
```

View test results and visualizations in:

- `llm_pipeline_results.png`
- `llm_pipeline_results.pdf`
- `llm_pipeline_test_results.json`

## 🌿 Environmental Variables

Key environmental factors modeled:

- Air Quality (PM2.5, Ozone)
- Traffic Patterns
- Biodiversity Metrics
- Species Vulnerability
- Pollution Burden
- Habitat Quality

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Open a Pull Request

## 📝 Notes

- Visualizations are saved in the `backend/ml/models` directory
- Geographical data integration requires proper GeoJSON files
- Some features require specific API access (Vertex AI, MongoDB)

## ⚠️ Known Issues

1. Frontend 3D models need separate installation
2. Some biodiversity metrics need fine-tuning
3. Geographical data sources need to be configured

## 📜 License

MIT License - see LICENSE file for details
