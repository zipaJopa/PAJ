#!/usr/bin/env python3
"""
PAI Agent - Personal AI Infrastructure Agent
FastAPI OpenAI-compatible API with PydanticAI integration
"""

import asyncio
import os
import time
from typing import List, Optional, Dict, Any, AsyncGenerator
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.messages import ModelMessage, UserPromptPart, TextPart
import httpx

# Import RAG and Graph Memory systems
from rag_system import rag_system, initialize_rag, get_rag_context, store_rag_knowledge
from graph_memory import graph_memory, initialize_graph_memory, store_graph_memory, query_graph_memory_tool

# Import A2A system
from a2a_system import initialize_a2a_network, a2a_manager, AgentCapability, MessageType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# OpenAI-compatible data models
class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: system, user, assistant")
    content: str = Field(..., description="Message content")


class ChatCompletionRequest(BaseModel):
    model: str = Field(default="pai-agent", description="Model identifier")
    messages: List[ChatMessage] = Field(..., description="Chat messages")
    temperature: Optional[float] = Field(default=0.7, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    stream: Optional[bool] = Field(default=False)
    top_p: Optional[float] = Field(default=1.0, ge=0, le=1)
    frequency_penalty: Optional[float] = Field(default=0, ge=-2, le=2)
    presence_penalty: Optional[float] = Field(default=0, ge=-2, le=2)
    stop: Optional[List[str]] = Field(default=None)


class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str = "stop"


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Dict[str, int] = Field(default_factory=lambda: {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0
    })


class ChatCompletionStreamChoice(BaseModel):
    index: int
    delta: Dict[str, Any]
    finish_reason: Optional[str] = None


class ChatCompletionStreamResponse(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[ChatCompletionStreamChoice]


# PAI Agent Configuration
class PAIAgentConfig:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("PAI_MODEL", "openai:gpt-4")
        self.system_prompt = self.load_system_prompt()

    def load_system_prompt(self) -> str:
        """Load system prompt from PAI configuration"""
        try:
            claude_dir = os.path.expanduser("~/.claude")
            prompt_file = os.path.join(claude_dir, "system_prompt.txt")
            if os.path.exists(prompt_file):
                with open(prompt_file, 'r') as f:
                    return f.read().strip()
        except Exception as e:
            logger.warning(f"Could not load system prompt: {e}")

        return """You are PAI (Personal AI Infrastructure), an elite AI agent built with PydanticAI.
        You help users with personal and professional tasks by leveraging knowledge from their context and tools.
        You are integrated with PostgreSQL+pgvector for RAG capabilities and Neo4j for graph memory.
        Provide helpful, accurate, and contextual responses while being concise and actionable."""


# Global agent configuration
config = PAIAgentConfig()

# PydanticAI Agent setup
pai_agent = Agent(
    model=config.model,
    system_prompt=config.system_prompt,
    deps_type=dict,  # For dependency injection
)


@pai_agent.tool
async def get_context_from_rag(ctx: RunContext[dict], query: str) -> str:
    """Retrieve relevant context from RAG system"""
    return await get_rag_context(query, ctx)


@pai_agent.tool
async def store_memory_graph(ctx: RunContext[dict], content: str, relationships: List[str]) -> str:
    """Store information in Neo4j graph memory"""
    return await store_graph_memory(content, relationships, ctx)


@pai_agent.tool
async def query_graph_memory(ctx: RunContext[dict], query: str) -> str:
    """Query Neo4j graph memory"""
    return await query_graph_memory_tool(query)


# FastAPI app setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🚀 PAI Agent starting up...")

    # Initialize RAG and Graph Memory systems
    try:
        await initialize_rag()
        logger.info("✅ RAG system initialized")
    except Exception as e:
        logger.warning(f"⚠️ RAG system initialization failed: {e}")

    try:
        await initialize_graph_memory()
        logger.info("✅ Graph memory system initialized")
    except Exception as e:
        logger.warning(f"⚠️ Graph memory system initialization failed: {e}")

    # Initialize A2A network system
    try:
        global a2a_manager
        host = os.getenv("HOST", "localhost")
        port = int(os.getenv("PORT", 8181))
        endpoint = f"http://{host}:{port}"

        a2a_manager = initialize_a2a_network(
            agent_id="pai-agent",
            agent_name="PAI Agent",
            endpoint=endpoint
        )
        logger.info("✅ A2A network system initialized")
    except Exception as e:
        logger.warning(f"⚠️ A2A system initialization failed: {e}")

    yield

    # Cleanup
    try:
        await rag_system.engine.dispose()
        logger.info("🔄 RAG system cleaned up")
    except Exception as e:
        logger.warning(f"⚠️ RAG cleanup error: {e}")

    try:
        await graph_memory.close()
        logger.info("🔄 Graph memory system cleaned up")
    except Exception as e:
        logger.warning(f"⚠️ Graph memory cleanup error: {e}")

    logger.info("🛑 PAI Agent shutting down...")


app = FastAPI(
    title="PAI Agent API",
    description="Personal AI Infrastructure Agent with OpenAI-compatible API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_request_id() -> str:
    """Generate unique request ID"""
    return f"pai-{int(time.time())}-{os.urandom(4).hex()}"


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "PAI Agent",
        "status": "healthy",
        "version": "1.0.0",
        "features": [
            "OpenAI-compatible API",
            "PydanticAI integration",
            "RAG with PostgreSQL+pgvector",
            "Graph memory with Neo4j",
            "FastMCP 2.0 ready",
            "FastA2A architecture"
        ]
    }


@app.get("/v1/models")
async def list_models():
    """List available models (OpenAI-compatible)"""
    return {
        "object": "list",
        "data": [
            {
                "id": "pai-agent",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "pai-infrastructure",
                "permission": [],
                "root": "pai-agent",
                "parent": None
            }
        ]
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint"""
    try:
        request_id = get_request_id()

        # Convert OpenAI messages to PydanticAI format
        conversation_history = []
        for msg in request.messages[:-1]:  # Exclude last message (current user input)
            if msg.role == "user":
                conversation_history.append(ModelMessage(parts=[UserPromptPart(content=msg.content)], kind="request"))
            elif msg.role == "assistant":
                conversation_history.append(ModelMessage(parts=[TextPart(content=msg.content)], kind="response"))
            # System messages are handled via system_prompt

        # Extract user message
        user_message = request.messages[-1].content if request.messages else ""

        if request.stream:
            return StreamingResponse(
                stream_chat_completion(request_id, user_message, request),
                media_type="text/plain"
            )

        # Non-streaming response
        result = await pai_agent.run(
            user_input=user_message,
            deps={"temperature": request.temperature},
            message_history=conversation_history if conversation_history else []
        )

        response = ChatCompletionResponse(
            id=request_id,
            created=int(time.time()),
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=result.data)
                )
            ]
        )

        return response

    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def stream_chat_completion(
    request_id: str,
    user_message: str,
    request: ChatCompletionRequest
) -> AsyncGenerator[str, None]:
    """Stream chat completion response"""
    try:
        # Start streaming response
        yield f"data: {ChatCompletionStreamResponse(
            id=request_id,
            created=int(time.time()),
            model=request.model,
            choices=[ChatCompletionStreamChoice(
                index=0,
                delta={"role": "assistant"},
                finish_reason=None
            )]
        ).model_dump_json()}\n\n"

        # Stream the actual response
        result = await pai_agent.run(user_input=user_message, deps={})

        # Send the complete response as a stream chunk
        yield f"data: {ChatCompletionStreamResponse(
            id=request_id,
            created=int(time.time()),
            model=request.model,
            choices=[ChatCompletionStreamChoice(
                index=0,
                delta={"content": result.data},
                finish_reason=None
            )]
        ).model_dump_json()}\n\n"

        # Send final chunk
        yield f"data: {ChatCompletionStreamResponse(
            id=request_id,
            created=int(time.time()),
            model=request.model,
            choices=[ChatCompletionStreamChoice(
                index=0,
                delta={},
                finish_reason="stop"
            )]
        ).model_dump_json()}\n\n"

        yield "data: [DONE]\n\n"

    except Exception as e:
        logger.error(f"Streaming error: {e}")
        yield f"data: {{'error': '{str(e)}'}}\n\n"


# MCP 2.0 Integration endpoints
@app.post("/mcp/v1/tools/list")
async def list_mcp_tools():
    """List available MCP tools"""
    return {
        "tools": [
            {
                "name": "get_context_from_rag",
                "description": "Retrieve relevant context from RAG system",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "store_memory_graph",
                "description": "Store information in Neo4j graph memory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "relationships": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["content", "relationships"]
                }
            },
            {
                "name": "query_graph_memory",
                "description": "Query Neo4j graph memory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"}
                    },
                    "required": ["query"]
                }
            }
        ]
    }


@app.post("/mcp/v1/tools/call")
async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]):
    """Call MCP tool"""
    try:
        if tool_name == "get_context_from_rag":
            result = await get_context_from_rag(None, arguments["query"])
        elif tool_name == "store_memory_graph":
            result = await store_memory_graph(
                None,
                arguments["content"],
                arguments["relationships"]
            )
        elif tool_name == "query_graph_memory":
            result = await query_graph_memory(None, arguments["query"])
        else:
            raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")

        return {"result": result}

    except Exception as e:
        logger.error(f"MCP tool call error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Agent-to-Agent communication endpoints (FastA2A)
@app.get("/a2a/v1/profile")
async def get_agent_profile():
    """Get agent profile for A2A discovery"""
    return {
        "agent_id": "pai-agent",
        "name": "PAI Agent",
        "description": "Personal AI Infrastructure Agent with PydanticAI",
        "capabilities": [
            AgentCapability.RAG_RETRIEVAL.value,
            AgentCapability.GRAPH_MEMORY.value,
            AgentCapability.KNOWLEDGE_SYNTHESIS.value,
            AgentCapability.CONVERSATION_MANAGEMENT.value
        ],
        "endpoint": f"http://{os.getenv('HOST', 'localhost')}:{os.getenv('PORT', 8181)}",
        "version": "1.0.0",
        "metadata": {
            "features": [
                "OpenAI-compatible API",
                "PydanticAI integration",
                "RAG with PostgreSQL+pgvector",
                "Graph memory with Neo4j",
                "FastMCP 2.0",
                "FastA2A architecture"
            ]
        }
    }


@app.post("/a2a/v1/message")
async def handle_a2a_message(message_data: Dict[str, Any]):
    """Handle incoming A2A message"""
    if not a2a_manager:
        raise HTTPException(status_code=503, detail="A2A system not initialized")

    try:
        result = await a2a_manager.handle_incoming_message(message_data)
        return result
    except Exception as e:
        logger.error(f"A2A message handling error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/a2a/v1/delegate")
async def delegate_task(
    task_type: str,
    description: str,
    parameters: Dict[str, Any],
    required_capabilities: List[str],
    deadline: Optional[str] = None,
    priority: int = 0
):
    """Delegate a task to another agent in the network"""
    if not a2a_manager:
        raise HTTPException(status_code=503, detail="A2A system not initialized")

    try:
        caps = set(AgentCapability(cap) for cap in required_capabilities)
        deadline_dt = datetime.fromisoformat(deadline) if deadline else None

        task_id = await a2a_manager.delegate_task(
            task_type=task_type,
            description=description,
            parameters=parameters,
            required_capabilities=caps,
            deadline=deadline_dt,
            priority=priority
        )

        if task_id:
            return {"task_id": task_id, "status": "delegated"}
        else:
            return {"error": "No suitable agents found", "status": "failed"}

    except Exception as e:
        logger.error(f"Task delegation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/a2a/v1/network")
async def get_network_status():
    """Get A2A network status"""
    if not a2a_manager:
        raise HTTPException(status_code=503, detail="A2A system not initialized")

    try:
        return await a2a_manager.get_network_status()
    except Exception as e:
        logger.error(f"Network status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/a2a/v1/discover")
async def discover_agents(discovery_endpoints: List[str]):
    """Discover other agents in the network"""
    if not a2a_manager:
        raise HTTPException(status_code=503, detail="A2A system not initialized")

    try:
        discovered = await a2a_manager.discover_agents(discovery_endpoints)
        return {"discovered_agents": discovered, "count": len(discovered)}
    except Exception as e:
        logger.error(f"Agent discovery error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/a2a/v1/broadcast")
async def broadcast_message(
    message_type: str,
    content: Dict[str, Any],
    exclude_agents: Optional[List[str]] = None
):
    """Broadcast a message to all agents"""
    if not a2a_manager:
        raise HTTPException(status_code=503, detail="A2A system not initialized")

    try:
        msg_type = MessageType(message_type)
        exclude_set = set(exclude_agents) if exclude_agents else set()

        successful = await a2a_manager.broadcast_message(msg_type, content, exclude_set)
        return {"successful_sends": successful, "count": len(successful)}
    except Exception as e:
        logger.error(f"Broadcast error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Legacy A2A endpoint for backward compatibility
@app.post("/a2a/v1/communicate")
async def agent_communicate(
    agent_id: str,
    message: str,
    context: Optional[Dict[str, Any]] = None
):
    """Legacy agent communication endpoint"""
    try:
        # Process inter-agent communication
        result = await pai_agent.run(
            user_input=f"[Agent {agent_id}]: {message}",
            deps=context or {}
        )

        return {
            "response": result.data,
            "agent_id": "pai-agent",
            "timestamp": int(time.time())
        }

    except Exception as e:
        logger.error(f"A2A communication error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8181))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"🚀 Starting PAI Agent on {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
