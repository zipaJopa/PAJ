# PAI Agent - Elite PydanticAI Framework

=€ **Personal AI Infrastructure Agent** with full PydanticAI featureset, agentic RAG (PostgreSQL+pgvector), Neo4j graph memory, FastMCP 2.0, and FastA2A architecture.

## < Features

-  **PydanticAI Integration**: Elite community framework with full featureset
-  **OpenAI-Compatible API**: Drop-in replacement for OpenAI API
-  **Agentic RAG**: PostgreSQL + pgvector for intelligent retrieval
-  **Graph Memory**: Neo4j for relationship tracking and contextual memory
-  **FastMCP 2.0**: Model Context Protocol server integration
-  **FastA2A Architecture**: Agent-to-Agent communication by design
-  **Type-Safe**: Full Pydantic validation and type checking
-  **Production Ready**: Async/await, proper error handling, monitoring

## =€ Quick Start

### Prerequisites

```bash
# Install PostgreSQL with pgvector
sudo apt-get install postgresql postgresql-contrib
sudo -u postgres psql -c "CREATE EXTENSION vector;"

# Install Neo4j
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt-get update && sudo apt-get install neo4j
```

### Installation

```bash
# Clone and setup
cd PAI/pai-agent
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your API keys and database settings

# Run the agent
uv run python main.py
```

### Alternative: Docker Setup

```bash
# Start dependencies
docker run -d --name postgres-pgvector \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=pai_db \
  -p 5432:5432 \
  pgvector/pgvector:pg16

docker run -d --name neo4j \
  -e NEO4J_AUTH=neo4j/password \
  -p 7474:7474 -p 7687:7687 \
  neo4j:latest

# Run PAI Agent
uv run python main.py
```

## =Ú API Documentation

### OpenAI-Compatible Endpoints

```bash
# Chat completions (streaming and non-streaming)
POST /v1/chat/completions

# List models
GET /v1/models
```

### Example Usage

```python
import openai

# Use PAI Agent as OpenAI replacement
client = openai.OpenAI(
    api_key="any-key",  # Not required for local usage
    base_url="http://localhost:8181/v1"
)

response = client.chat.completions.create(
    model="pai-agent",
    messages=[
        {"role": "user", "content": "Tell me about quantum computing"}
    ],
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content, end="")
```

### FastMCP 2.0 Tools

```bash
# List available tools
POST /mcp/v1/tools/list

# Call a tool
POST /mcp/v1/tools/call
{
  "tool_name": "rag_query",
  "arguments": {
    "query": "What is machine learning?"
  }
}
```

### FastA2A Communication

```bash
# Get agent profile
GET /a2a/v1/profile

# Send message to agent
POST /a2a/v1/message

# Delegate task
POST /a2a/v1/delegate

# Get network status
GET /a2a/v1/network
```

## =à Architecture

### Core Components

1. **PydanticAI Agent**: Main conversation handler with tool integration
2. **RAG System**: PostgreSQL + pgvector for semantic search and storage
3. **Graph Memory**: Neo4j for relationship tracking and temporal memory
4. **MCP Server**: Model Context Protocol for external tool integration
5. **A2A Network**: Agent-to-Agent communication and task delegation

### Data Flow

```
User Request ’ FastAPI ’ PydanticAI Agent ’ Tools (RAG/Graph/MCP) ’ Response
                “
        A2A Network  ’ Other Agents
```

### Tools Available

- `get_context_from_rag`: Semantic retrieval from knowledge base
- `store_memory_graph`: Store information with relationships
- `query_graph_memory`: Query graph-based memory system

## =' Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_key_here
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
NEO4J_URI=bolt://localhost:7687

# Optional
PAI_MODEL=openai:gpt-4
HOST=0.0.0.0
PORT=8181
LOG_LEVEL=INFO
```

### Custom Tools

```python
@pai_agent.tool
async def your_custom_tool(ctx: RunContext[dict], param: str) -> str:
    """Your custom tool description"""
    # Implementation
    return "result"
```

### A2A Network Setup

```python
# Register capabilities
a2a_manager.register_capability_handler(
    AgentCapability.YOUR_CAPABILITY,
    your_handler_function
)

# Discover other agents
await a2a_manager.discover_agents([
    "http://agent1:8181",
    "http://agent2:8182"
])
```

## = Monitoring & Health

### Health Check

```bash
GET /
```

Returns system status and feature availability.

### System Status

```bash
GET /a2a/v1/network  # A2A network status
```

### Logs

The agent provides structured logging for:
- Request/response cycles
- Tool executions
- A2A communications
- System health events

## =€ Advanced Usage

### RAG Knowledge Management

```python
# Store knowledge
await rag_system.store_knowledge(
    content="Your knowledge content",
    source="document_name",
    metadata={"category": "technical"}
)

# Query with context
result = await rag_system.agentic_retrieve(
    query="machine learning concepts",
    context={"prefer_source_type": "technical"}
)
```

### Graph Memory Operations

```python
# Store conversation with entities
await graph_memory.store_conversation_memory(
    conversation_id="conv_123",
    user_message="Tell me about AI",
    assistant_response="AI is...",
    entities=[
        {"name": "AI", "type": "CONCEPT"},
        {"name": "Machine Learning", "type": "CONCEPT"}
    ]
)

# Find related memories
memories = await graph_memory.find_related_memories(
    query_entities=["AI", "Machine Learning"],
    max_depth=2
)
```

### Task Delegation

```python
# Delegate computation-heavy task
task_id = await a2a_manager.delegate_task(
    task_type="data_analysis",
    description="Analyze sales data for Q4",
    parameters={"dataset": "sales_q4.csv"},
    required_capabilities={
        AgentCapability.DATA_ANALYSIS,
        AgentCapability.DOCUMENT_PROCESSING
    }
)
```

## = Integration with PAI Framework

This agent is designed to integrate seamlessly with the broader PAI (Personal AI Infrastructure) ecosystem:

- Place in `~/.claude/agents/` for Claude Code integration
- Use as MCP server: `pai-agent-mcp`
- Connect to other PAI agents via A2A network
- Leverage existing PAI context and memory systems

## =æ Dependencies

- **pydantic-ai**: Core agent framework
- **fastapi**: Web API framework
- **asyncpg**: PostgreSQL async driver
- **pgvector**: Vector similarity search
- **neo4j**: Graph database driver
- **httpx**: HTTP client for A2A communication
- **mcp**: Model Context Protocol

## > Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure type checking passes: `mypy pai-agent/`
5. Submit pull request

## =Ä License

MIT License - see LICENSE file for details.

## =O Acknowledgments

- **PydanticAI Team**: For the excellent agent framework
- **PAI Project**: For the broader infrastructure vision
- **PostgreSQL + pgvector**: For vector search capabilities
- **Neo4j**: For graph database technology