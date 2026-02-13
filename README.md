# RAG Agent Backend

A customer support agent powered by Retrieval-Augmented Generation (RAG) with Human-in-the-Loop capabilities, built with LangGraph and FastAPI.

## 🏗️ Architecture

This backend implements an intelligent agent that combines document retrieval, classification, and response generation with the ability to escalate to human support when needed.

### Core Components

- **LangGraph Agent**: State-based conversation flow with checkpointing for multi-turn conversations
- **RAG Pipeline**: ChromaDB vector store + FastEmbed embeddings + retrieval-augmented generation
- **FastAPI Server**: REST API with custom endpoints for documents, users, and authentication
- **PostgreSQL**: User data storage and LangGraph state persistence
- **Redis**: Caching layer required by LangGraph Agent Server

### Agent Workflow

```
START → Classification Query → Retrieve (if needed) → Generate Response → END
                ↓
        Human Handoff (HITL) -> END
```

The agent classifies incoming queries, retrieves relevant documents, generates responses, and can interrupt for human intervention when confidence is low or specialized support is needed.

### Project Structure

```
rag-agent-backend/
├── config/              # Application configuration
├── src/
│   ├── agent.py         # LangGraph workflow definition
│   ├── server.py        # FastAPI application
│   ├── controllers/     # API endpoints
│   ├── dtos/            # Data transfer objects
│   ├── models/          # Database entities
│   ├── rag/             # RAG components (embeddings, retriever, store)
│   ├── security/        # Authentication & authorization
│   ├── services/        # Business logic
│   └── utils/           # Utils for Agent workflow
├── main.py              # CLI and setup utilities
├── docker-compose.yml   # Container orchestration
└── langgraph.json       # LangGraph configuration
```

## 🚀 Technologies

- **Python 3.11+**
- **FastAPI** - Modern web framework
- **LangGraph** - Agent orchestration and state management
- **LangChain** - RAG components and LLM integration
- **ChromaDB** - Vector database for document embeddings
- **PostgreSQL 15** - Relational database
- **Redis 7** - In-memory cache
- **SQLModel** - SQL database ORM
- **Google Generative AI** - LLM provider
- **FastEmbed** - Fast embedding generation
- **JWT** - Token-based authentication
- **BCrypt** - Password hashing
- **Docker** - Containerization

## 📋 Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
-  Google API key
- LangGraph CLI (`pip install langgraph-cli[inmem]`)

## ⚙️ Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Environment
ENVIRONMENT=development  # Options: development and production

# Google AI
GOOGLE_API_KEY=your_google_api_key_here

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=langgraph-postgres
POSTGRES_DB=langgraph
POSTGRES_PORT=5432

# Redis
REDIS_URI=redis://langgraph-redis:6379

# JWT Authentication
JWT_SECRET_KEY=your_secret_key_here  # Generate with: openssl rand -hex 32
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=180

# Vector Store (optional, defaults to Docker volume path)
# VECTOR_STORE_PATH=/app/data/vectorstore
```


## 🚀 Getting Started

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -e .

# Or using uv (recommended)
uv pip install -e .
```

### 2. Build Docker Image

```bash
# Build LangGraph image
langgraph build -t rag-agent:latest
```

This command creates a Docker image with your agent and all dependencies.

### 3. Start Services

```bash
# Start all services (PostgreSQL, Redis, API)
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- Redis cache on port 6379
- LangGraph API server on port 8000

### 4. Initialize Database

```bash
# Setup database tables and create default roles
python main.py setup-db 
```

## 🔧 Development



### CLI Commands

```bash
# Database setup
python main.py setup-db

```

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

- `POST /api/auth/login` - User authentication
- `POST /api/auth/register` - User registration
- `GET /api/users/me` - Get current user
- `POST /api/documents` - Upload documents
- `GET /api/documents` - List documents
- `DELETE /api/documents/{id}` - Delete document

LangGraph streaming endpoints are automatically available at `/agent/*`.


### Roles

The system includes predefined roles:
- `ADMIN` - Full system access
- `USER` - Standard user access (only chat)

Roles are automatically created during database setup.

## 🔒 Security

- **Password Hashing**: BCrypt with salt
- **JWT Tokens**: Secure token-based authentication
- **CORS**: Configured for frontend (http://localhost:3000)
- **SQL Injection**: Protected via SQLModel ORM
- **Environment Variables**: Sensitive data stored in `.env`

## 🐳 Docker Services

### Services Overview

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| langgraph-api | rag-agent:latest | 8000 | Main API server |
| langgraph-postgres | postgres:15-alpine | 5432 | Database |
| langgraph-redis | redis:7-alpine | 6379 | Cache |

### Volume Mounts

- `postgres_data`: PostgreSQL data persistence
- `./data/vectorstore`: ChromaDB vector store
