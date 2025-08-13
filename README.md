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
│   │   ├── database_models.py # Database model CRUD operations
│   │   └── chat.py       # Chat agent API endpoints
│   ├── agents/           # LangGraph agents
│   │   ├── __init__.py
│   │   └── chat_agent.py # Ollama chat agent implementation
│   ├── tests/            # Test suite
│   │   ├── conftest.py   # Pytest configuration and fixtures
│   │   ├── test_smoke.py
│   │   └── test_db.py
│   └── .dockerignore     # Docker build optimization
├── docker-compose.yml     # Multi-service orchestration
├── docker-compose-test.yml # Test environment configuration
├── .github/workflows/     # CI/CD workflows
├── entrypoint.sh          # Ollama startup script
└── README.md              # Documentation
```

## Services

- **postgres**: PostgreSQL database server for persistent data storage
- **ollama**: AI model server with GPU support and VRAM management
- **n8n**: Workflow automation platform
- **fastapi**: Python FastAPI application with clean, separated modules (runs `uvicorn app.main:app`)

## Database

The project uses **PostgreSQL** as the primary database:
- **Host**: `postgres` (container name)
- **Port**: `5432`
- **Database**: `ollama_fastapi`
- **User**: `ollama_user`
- **Password**: `ollama_password`

### Database Features
- **Connection Pooling**: Automatic connection management
- **Health Checks**: Database readiness verification
- **Persistent Storage**: Data survives container restarts
- **ACID Compliance**: Reliable transaction handling

## Testing Framework

Tests use FastAPI TestClient and SQLModel (no direct SQLAlchemy calls, no network mocks by default).

### Local Testing
```bash
# Run all tests
docker exec fastapi pytest -q -s

# Run with verbose output
docker exec fastapi pytest -v
```

### Test Database Lifecycle
- Tests do not use special TEST_* env vars.
- The test DB URL is derived from `DATABASE_URL` by appending `_test` to the database name (e.g., `/ollama_fastapi_test`).
- On test session start, the `_test` database is created if missing; on session end it is dropped.

### Optional: Testcontainers for PostgreSQL
If you prefer an ephemeral Postgres started by tests, enable testcontainers:
- Mount Docker socket to the `fastapi` container and add dependencies.
- docker-compose `fastapi` service additions:
```yaml
services:
  fastapi:
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - DOCKER_HOST=unix:///var/run/docker.sock
```
- Add to `app/requirements.txt`:
```
docker
testcontainers
```
When the Docker socket is available, tests will use a `postgres:16` container automatically. Otherwise, they fall back to the derived `_test` database.

### Test Files
- `tests/test_smoke.py`: basic smoke assertion
- `tests/test_db.py`: validates SQLModel connectivity and simple CRUD against the test DB

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
   - PostgreSQL: localhost:5432
   - Ollama Models: http://localhost:8000/api/v1/ollama/models
   - Chat API: http://localhost:8000/api/v1/ollama/chat
   - Database Models: http://localhost:8000/api/v1/models

3. **Run tests:**
   ```bash
   docker exec fastapi pytest -q -s
   ```

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

- `DATABASE_URL`: PostgreSQL connection string (tests derive the `_test` DB from this)
- `OLLAMA_BASE_URL`: Ollama service URL (default: http://ollama:11434)
- `OLLAMA_NUM_PARALLEL`: Number of parallel model operations
- `OLLAMA_MAX_LOADED_MODELS`: Maximum models to keep in memory
- `OLLAMA_KEEP_ALIVE`: How long to keep models loaded

## Code Organization Benefits

- **Separation of Concerns**: Model management, chat, and database operations are separate
- **Maintainability**: Each module has a single responsibility
- **Scalability**: Easy to add new features without affecting existing code
- **Testing**: Each module can be tested independently with minimal, fast tests
- **Documentation**: Clear API structure with logical grouping
- **CI/CD**: Automated testing and deployment pipeline
- **Database**: Robust PostgreSQL backend with connection pooling and health checks