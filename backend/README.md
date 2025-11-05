# Dispatcher Agents Backend

Backend service for the Voice Agent Conversation System.

## Setup

### Prerequisites
- Python 3.10+
- UV package manager

### Installation

1. Install UV (if not already installed):
```bash
pip install uv
```

2. Create virtual environment and install dependencies:
```bash
cd backend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

3. Create `.env` file:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### Running the Server

```bash
# Development mode with auto-reload
uvicorn src.api.main:app --reload --port 8000

# Or using Python directly
python -m src.api.main
```

The API will be available at `http://localhost:8000`

- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Project Structure

```
backend/
├── src/
│   ├── api/
│   │   ├── routes/          # API route handlers
│   │   └── main.py          # FastAPI application
│   ├── services/            # Business logic services
│   ├── models/              # Pydantic models
│   └── __init__.py
├── tests/                   # Milestone test scripts
│   ├── test_milestone1.py
│   ├── test_milestone2.py
│   └── ...
├── pyproject.toml           # Project dependencies
├── .env.example             # Environment variables template
└── README.md
```

## Environment Variables

See `.env.example` for required configuration.

## Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Run milestone tests
python tests/test_milestone1.py
python tests/test_milestone2.py
# ... etc
```

