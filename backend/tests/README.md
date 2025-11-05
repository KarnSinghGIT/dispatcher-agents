# Backend Tests

This directory contains milestone test scripts for the Dispatcher Agents backend.

## Test Files

- **test_milestone1.py** - Backend Foundation Setup
- **test_milestone2.py** - Pydantic Models & API Structure
- **test_milestone3.py** - LLM Service Integration
- **test_milestone4.py** - Langfuse Integration
- **test_milestone5.py** - Conversation Service - Single Turn
- **test_milestone6.py** - Conversation Service - Multi-Turn
- **test_payload.json** - Sample payload for API testing

## Running Tests

Make sure you're in the `backend/` directory with the virtual environment activated:

```bash
cd backend
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Set required environment variables
export OPENROUTER_API_KEY=your_key
export LANGFUSE_PUBLIC_KEY=your_key  # Optional for milestones 1-3
export LANGFUSE_SECRET_KEY=your_key  # Optional for milestones 1-3
```

### Run Individual Tests

```bash
# Test Backend Foundation (requires server running)
python tests/test_milestone1.py

# Test Pydantic Models (requires server running)
python tests/test_milestone2.py

# Test LLM Service (requires OPENROUTER_API_KEY)
python tests/test_milestone3.py

# Test Langfuse Integration (requires OPENROUTER_API_KEY + Langfuse keys)
python tests/test_milestone4.py

# Test Single Turn Conversation (requires OPENROUTER_API_KEY)
python tests/test_milestone5.py

# Test Multi-Turn Conversation (requires server running + OPENROUTER_API_KEY)
python tests/test_milestone6.py
```

### Run All Tests

```bash
# Start the server in one terminal
uvicorn src.api.main:app --reload

# In another terminal, run tests
for i in {1..6}; do python tests/test_milestone$i.py; done
```

## Prerequisites

### For All Tests
- Python 3.10+
- Virtual environment activated
- Dependencies installed (`uv pip install -e .`)

### For Milestones 1-2
- Backend server running (`uvicorn src.api.main:app --reload`)

### For Milestones 3-6
- `OPENROUTER_API_KEY` environment variable set
- OpenRouter account with credits

### For Milestones 4-6 (Optional)
- `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` for observability
- Langfuse account at https://cloud.langfuse.com

## Test Descriptions

### Milestone 1: Backend Foundation Setup
Tests basic FastAPI setup including:
- Health check endpoint
- Root endpoint
- Server availability

### Milestone 2: Pydantic Models & API Structure
Tests API structure and model validation:
- Conversation endpoint accepts valid payload
- Response has correct structure
- API documentation is available

### Milestone 3: LLM Service Integration
Tests OpenRouter API integration:
- Basic LLM calls work
- Conversation-style prompts work
- Different models can be selected

### Milestone 4: Langfuse Integration
Tests observability setup:
- Langfuse configuration
- Trace creation for LLM calls
- Multiple traces work correctly

### Milestone 5: Conversation Service - Single Turn
Tests basic conversation generation:
- Single turn generation works
- Scenario formatting is correct
- Custom prompts work

### Milestone 6: Conversation Service - Multi-Turn
Tests full conversation generation:
- Multi-turn conversations generate (10+ turns)
- Conversations end naturally
- Full API integration works

## Troubleshooting

**ModuleNotFoundError**
- Make sure you're running from the `backend/` directory
- Ensure virtual environment is activated

**Connection Refused (tests 1-2, 6)**
- Start the backend server: `uvicorn src.api.main:app --reload`

**API Key Errors (tests 3-6)**
- Set OPENROUTER_API_KEY: `export OPENROUTER_API_KEY=your_key`
- Verify key is valid at https://openrouter.ai

**Langfuse Warnings (tests 4-6)**
- Non-critical if you don't need observability
- Set Langfuse keys to enable tracing

