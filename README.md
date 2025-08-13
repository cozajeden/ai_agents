# Ollama FastAPI Service

A FastAPI application that integrates with Ollama for AI model management and inference, built with SQLModel for robust database operations and LangGraph for intelligent chat agents.

## Project Structure

```
├── app/                    # FastAPI service (self-contained)
│   ├── Dockerfile         # Container definition
│   ├── requirements.txt   # Python dependencies
│   ├── main.py           # FastAPI entrypoint and router configuration
│   ├── database.py       # Database configuration and session management
│   ├── models/           # Data models
│   │   ├── __init__.py
│   │   └── base.py       # Base models and mixins
│   ├── routers/          # API route modules
│   │   ├── __init__.py
│   │   ├── models/       # Model management routes
│   │   │   ├── __init__.py
│   │   │   └── ollama.py # Ollama model management API
│   │   ├── models.py     # Database model CRUD operations
│   │   └── chat.py       # Chat agent API endpoints
│   ├── agents/           # LangGraph agents
│   │   ├── __init__.py
│   │   └── chat_agent.py # Ollama chat agent implementation
│   └── .dockerignore     # Docker build optimization
├── docker-compose.yml     # Multi-service orchestration
├── entrypoint.sh          # Ollama startup script
└── README.md              # Documentation
```

## Services

- **ollama**: AI model server with GPU support and VRAM management
- **n8n**: Workflow automation platform
- **fastapi**: Python FastAPI application with clean, separated modules

## API Structure

### Ollama Model Management (`/api/v1/ollama/models`)
- `GET /` - List available Ollama models
- `POST /{model_name}/load` - Load model into VRAM
- `DELETE /{model_name}/unload` - Unload model from VRAM
- `GET /status` - Get models status and VRAM usage
- `GET /health` - Ollama service health check

### Chat API (`/api/v1/ollama/chat`)
- `POST /` - Chat with an Ollama model using LangGraph
- `GET /health` - Chat service health check

### Database Models (`/api/v1/models`)
- `GET /` - List all model requests
- `GET /{request_id}` - Get specific model request
- `POST /` - Create new model request
- `PUT /{request_id}` - Update model request
- `DELETE /{request_id}` - Delete model request

## Quick Start

1. **Build and start all services:**
   ```bash
   docker compose up -d --build
   ```

2. **Access services:**
   - FastAPI: http://localhost:8000
   - FastAPI docs: http://localhost:8000/docs
   - Ollama Models: http://localhost:8000/api/v1/ollama/models
   - Chat API: http://localhost:8000/api/v1/ollama/chat
   - Database Models: http://localhost:8000/api/v1/models

## VRAM Management

The service automatically manages GPU VRAM:
- **`OLLAMA_MAX_LOADED_MODELS: "1"`** - Only 1 model in VRAM at a time
- **`OLLAMA_KEEP_ALIVE: "5m"`** - Unload models after 5 minutes of inactivity
- **Automatic switching** - Models load/unload based on usage

## Chat Usage

### Simple Chat (auto-generates session)
```bash
curl -X POST "http://localhost:8000/api/v1/ollama/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "model_name": "llama3.1:8b"
  }'
```

### Continue Conversation (uses existing session)
```bash
curl -X POST "http://localhost:8000/api/v1/ollama/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What did I just ask you?",
    "model_name": "llama3.1:8b",
    "session_id": "uuid-from-previous-response"
  }'
```

## Environment Variables

- `OLLAMA_BASE_URL`: Ollama service URL (default: http://ollama:11434)
- `OLLAMA_NUM_PARALLEL`: Number of parallel model operations
- `OLLAMA_MAX_LOADED_MODELS`: Maximum models to keep in memory
- `OLLAMA_KEEP_ALIVE`: How long to keep models loaded

## Code Organization Benefits

- **Separation of Concerns**: Model management, chat, and database operations are separate
- **Maintainability**: Each module has a single responsibility
- **Scalability**: Easy to add new features without affecting existing code
- **Testing**: Each module can be tested independently
- **Documentation**: Clear API structure with logical grouping