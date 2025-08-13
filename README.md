# Ollama FastAPI Service

A FastAPI application that integrates with Ollama for AI model management and inference, built with SQLModel for robust database operations and LangGraph for intelligent chat agents.

## Project Structure

```
├── app/                    # FastAPI service (self-contained)
│   ├── Dockerfile         # Container definition
│   ├── requirements.txt   # Python dependencies
│   ├── main.py           # FastAPI entrypoint
│   ├── database.py       # Database configuration
│   ├── models/           # Data models
│   │   ├── __init__.py
│   │   └── base.py       # Base models and mixins
│   ├── routers/          # API routes
│   │   ├── __init__.py
│   │   ├── models.py     # Model request CRUD operations
│   │   └── chat.py       # LangGraph chat agent endpoints
│   ├── agents/           # LangGraph agents
│   │   ├── __init__.py
│   │   └── chat_agent.py # Ollama chat agent implementation
│   └── .dockerignore     # Docker build optimization
├── docker-compose.yml     # Multi-service orchestration
├── entrypoint.sh          # Ollama startup script
└── README.md              # Documentation
```

## Services

- **ollama**: AI model server with GPU support
- **n8n**: Workflow automation platform
- **fastapi**: Python FastAPI application with SQLModel ORM and LangGraph

## Quick Start

1. **Build and start all services:**
   ```bash
   docker compose up -d --build
   ```

2. **Access services:**
   - FastAPI: http://localhost:8000
   - FastAPI docs: http://localhost:8000/docs
   - Models API: http://localhost:8000/api/v1/models
   - Chat API: http://localhost:8000/api/v1/ollama
   - n8n: http://localhost:5678
   - Ollama: http://localhost:11434

3. **View logs:**
   ```bash
   docker compose logs -f fastapi
   ```

## Development

- **Local development:**
  ```bash
  cd app
  pip install -r requirements.txt
  uvicorn main:app --reload --host 0.0.0.0 --port 8000
  ```

- **Add new routes:**
  - Create new files in `app/routers/`
  - Import and include in `app/main.py`

- **Add new models:**
  - Create models in `app/models/`
  - Import in `app/database.py` create_tables function

## API Endpoints

### Models API
- `GET /api/v1/models/` - List all model requests
- `GET /api/v1/models/{request_id}` - Get specific model request
- `POST /api/v1/models/` - Create new model request
- `PUT /api/v1/models/{request_id}` - Update model request
- `DELETE /api/v1/models/{request_id}` - Delete model request

### Ollama Chat API
- `GET /api/v1/ollama/models` - Get available Ollama models
- `POST /api/v1/ollama/chat` - Chat with an Ollama model using LangGraph
- `GET /api/v1/ollama/health` - Chat service health check

## Chat Usage

### Get Available Models
```bash
curl http://localhost:8000/api/v1/ollama/models
```

### Chat with a Model
```bash
curl -X POST "http://localhost:8000/api/v1/ollama/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "model_name": "llama3.1:8b"
  }'
```

### Chat with Conversation History
```bash
curl -X POST "http://localhost:8000/api/v1/ollama/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What did I just ask you?",
    "model_name": "llama3.1:8b",
    "conversation_history": [
      {"role": "user", "content": "Hello, how are you?"},
      {"role": "assistant", "content": "I am doing well, thank you for asking!"}
    ]
  }'
```

## Environment Variables

- `OLLAMA_BASE_URL`: Ollama service URL (default: http://ollama:11434)
- `OLLAMA_NUM_PARALLEL`: Number of parallel model operations
- `OLLAMA_MAX_LOADED_MODELS`: Maximum models to keep in memory
- `OLLAMA_KEEP_ALIVE`: How long to keep models loaded

## Database

- SQLite database with SQLModel ORM
- Automatic table creation and schema management
- Session dependency injection for database operations
- Lifespan management for connection lifecycle
- Built-in validation with Pydantic integration
- Chat interaction tracking and analytics

## LangGraph Features

- **State Management**: Typed state management for chat conversations
- **Workflow Orchestration**: Structured chat processing workflow
- **Model Integration**: Seamless Ollama model integration
- **Conversation History**: Maintains context across chat sessions
- **Error Handling**: Robust error handling and validation