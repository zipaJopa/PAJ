#!/usr/bin/env python3
"""
FastMCP 2.0 Server for PAI Agent
Model Context Protocol server with enhanced agent capabilities
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional, Sequence
from dataclasses import dataclass
from datetime import datetime
import logging

from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from pydantic import BaseModel

# Import our systems
from rag_system import rag_system, get_rag_context, store_rag_knowledge
from graph_memory import graph_memory, store_graph_memory, query_graph_memory_tool

logger = logging.getLogger("pai-mcp-server")


class MCPTool(BaseModel):
    """MCP tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]


class PAIMCPServer:
    """PAI Agent MCP 2.0 Server"""

    def __init__(self):
        self.server = Server("pai-agent")
        self.setup_handlers()

    def setup_handlers(self):
        """Setup MCP server handlers"""

        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name="rag_query",
                    description="Query the RAG system for relevant context",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The query to search for in the knowledge base"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="rag_store",
                    description="Store knowledge in the RAG system",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Content to store"
                            },
                            "source": {
                                "type": "string",
                                "description": "Source identifier",
                                "default": "mcp"
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Additional metadata",
                                "default": {}
                            }
                        },
                        "required": ["content"]
                    }
                ),
                types.Tool(
                    name="graph_store",
                    description="Store information in the graph memory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Content to store"
                            },
                            "relationships": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of relationships"
                            },
                            "context": {
                                "type": "object",
                                "description": "Additional context",
                                "default": {}
                            }
                        },
                        "required": ["content", "relationships"]
                    }
                ),
                types.Tool(
                    name="graph_query",
                    description="Query the graph memory system",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Query for graph memory search"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="get_system_status",
                    description="Get the status of PAI Agent systems",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="store_conversation",
                    description="Store a conversation in both RAG and graph memory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_message": {
                                "type": "string",
                                "description": "User message"
                            },
                            "assistant_response": {
                                "type": "string",
                                "description": "Assistant response"
                            },
                            "session_id": {
                                "type": "string",
                                "description": "Session identifier",
                                "default": "default"
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Additional metadata",
                                "default": {}
                            }
                        },
                        "required": ["user_message", "assistant_response"]
                    }
                ),
                types.Tool(
                    name="analyze_context",
                    description="Analyze and extract insights from stored context",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "analysis_type": {
                                "type": "string",
                                "enum": ["summary", "entities", "relationships", "timeline"],
                                "description": "Type of analysis to perform"
                            },
                            "scope": {
                                "type": "string",
                                "description": "Scope of analysis (e.g., entity name, time period)",
                                "default": "all"
                            }
                        },
                        "required": ["analysis_type"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> List[types.TextContent]:
            """Handle tool calls"""
            try:
                if name == "rag_query":
                    result = await get_rag_context(
                        arguments["query"],
                        {"max_results": arguments.get("max_results", 5)}
                    )
                    return [types.TextContent(type="text", text=result)]

                elif name == "rag_store":
                    result = await store_rag_knowledge(
                        arguments["content"],
                        arguments.get("source", "mcp"),
                        arguments.get("metadata", {})
                    )
                    return [types.TextContent(type="text", text=result)]

                elif name == "graph_store":
                    result = await store_graph_memory(
                        arguments["content"],
                        arguments["relationships"],
                        arguments.get("context", {})
                    )
                    return [types.TextContent(type="text", text=result)]

                elif name == "graph_query":
                    result = await query_graph_memory_tool(arguments["query"])
                    return [types.TextContent(type="text", text=result)]

                elif name == "get_system_status":
                    status = await self._get_system_status()
                    return [types.TextContent(type="text", text=json.dumps(status, indent=2))]

                elif name == "store_conversation":
                    result = await self._store_conversation(
                        arguments["user_message"],
                        arguments["assistant_response"],
                        arguments.get("session_id", "default"),
                        arguments.get("metadata", {})
                    )
                    return [types.TextContent(type="text", text=result)]

                elif name == "analyze_context":
                    result = await self._analyze_context(
                        arguments["analysis_type"],
                        arguments.get("scope", "all")
                    )
                    return [types.TextContent(type="text", text=result)]

                else:
                    raise ValueError(f"Unknown tool: {name}")

            except Exception as e:
                logger.error(f"Tool call error: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]

        @self.server.list_resources()
        async def handle_list_resources() -> List[types.Resource]:
            """List available resources"""
            return [
                types.Resource(
                    uri="pai://system/status",
                    name="System Status",
                    description="Current status of PAI Agent systems",
                    mimeType="application/json"
                ),
                types.Resource(
                    uri="pai://rag/stats",
                    name="RAG Statistics",
                    description="Statistics about the RAG system",
                    mimeType="application/json"
                ),
                types.Resource(
                    uri="pai://graph/stats",
                    name="Graph Statistics",
                    description="Statistics about the graph memory system",
                    mimeType="application/json"
                ),
                types.Resource(
                    uri="pai://conversation/recent",
                    name="Recent Conversations",
                    description="Recent conversation history",
                    mimeType="application/json"
                )
            ]

        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read resource content"""
            try:
                if uri == "pai://system/status":
                    status = await self._get_system_status()
                    return json.dumps(status, indent=2)

                elif uri == "pai://rag/stats":
                    stats = await rag_system.health_check()
                    return json.dumps(stats, indent=2)

                elif uri == "pai://graph/stats":
                    stats = await graph_memory.health_check()
                    return json.dumps(stats, indent=2)

                elif uri == "pai://conversation/recent":
                    # Get recent conversations from multiple sessions
                    recent = await self._get_recent_conversations()
                    return json.dumps(recent, indent=2)

                else:
                    raise ValueError(f"Unknown resource: {uri}")

            except Exception as e:
                logger.error(f"Resource read error: {e}")
                return json.dumps({"error": str(e)})

        @self.server.list_prompts()
        async def handle_list_prompts() -> List[types.Prompt]:
            """List available prompts"""
            return [
                types.Prompt(
                    name="analyze_conversation",
                    description="Analyze a conversation using RAG and graph memory",
                    arguments=[
                        types.PromptArgument(
                            name="conversation_text",
                            description="The conversation text to analyze",
                            required=True
                        ),
                        types.PromptArgument(
                            name="analysis_depth",
                            description="Depth of analysis (basic, detailed, comprehensive)",
                            required=False
                        )
                    ]
                ),
                types.Prompt(
                    name="knowledge_synthesis",
                    description="Synthesize knowledge from multiple sources",
                    arguments=[
                        types.PromptArgument(
                            name="query",
                            description="Query for knowledge synthesis",
                            required=True
                        ),
                        types.PromptArgument(
                            name="sources",
                            description="Comma-separated list of sources to include",
                            required=False
                        )
                    ]
                ),
                types.Prompt(
                    name="memory_timeline",
                    description="Generate a timeline of memories related to an entity",
                    arguments=[
                        types.PromptArgument(
                            name="entity",
                            description="The entity to create a timeline for",
                            required=True
                        ),
                        types.PromptArgument(
                            name="days_back",
                            description="Number of days to look back",
                            required=False
                        )
                    ]
                )
            ]

        @self.server.get_prompt()
        async def handle_get_prompt(
            name: str, arguments: Dict[str, str]
        ) -> types.GetPromptResult:
            """Handle prompt requests"""
            try:
                if name == "analyze_conversation":
                    content = await self._analyze_conversation_prompt(
                        arguments["conversation_text"],
                        arguments.get("analysis_depth", "detailed")
                    )
                    return types.GetPromptResult(
                        description="Conversation analysis with RAG and graph insights",
                        messages=[
                            types.PromptMessage(
                                role="user",
                                content=types.TextContent(type="text", text=content)
                            )
                        ]
                    )

                elif name == "knowledge_synthesis":
                    content = await self._knowledge_synthesis_prompt(
                        arguments["query"],
                        arguments.get("sources", "").split(",") if arguments.get("sources") else []
                    )
                    return types.GetPromptResult(
                        description="Knowledge synthesis from multiple sources",
                        messages=[
                            types.PromptMessage(
                                role="user",
                                content=types.TextContent(type="text", text=content)
                            )
                        ]
                    )

                elif name == "memory_timeline":
                    content = await self._memory_timeline_prompt(
                        arguments["entity"],
                        int(arguments.get("days_back", "30"))
                    )
                    return types.GetPromptResult(
                        description="Memory timeline for entity",
                        messages=[
                            types.PromptMessage(
                                role="user",
                                content=types.TextContent(type="text", text=content)
                            )
                        ]
                    )

                else:
                    raise ValueError(f"Unknown prompt: {name}")

            except Exception as e:
                logger.error(f"Prompt error: {e}")
                return types.GetPromptResult(
                    description=f"Error generating prompt: {str(e)}",
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(type="text", text=f"Error: {str(e)}")
                        )
                    ]
                )

    async def _get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        rag_status = await rag_system.health_check()
        graph_status = await graph_memory.health_check()

        return {
            "timestamp": datetime.now().isoformat(),
            "systems": {
                "rag": rag_status,
                "graph": graph_status
            },
            "overall_health": rag_status.get("database_connected", False) and graph_status.get("connected", False)
        }

    async def _store_conversation(
        self,
        user_message: str,
        assistant_response: str,
        session_id: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Store conversation in both systems"""
        try:
            # Store in RAG system
            conversation_text = f"User: {user_message}\nAssistant: {assistant_response}"
            rag_result = await store_rag_knowledge(
                conversation_text,
                f"conversation_{session_id}",
                {"session_id": session_id, **metadata}
            )

            # Store in graph memory
            conv_id = f"{session_id}_{int(datetime.now().timestamp())}"
            graph_result = await graph_memory.store_conversation_memory(
                conversation_id=conv_id,
                user_message=user_message,
                assistant_response=assistant_response,
                context=metadata
            )

            return f"Conversation stored: RAG={rag_result}, Graph={graph_result}"

        except Exception as e:
            return f"Storage error: {str(e)}"

    async def _analyze_context(self, analysis_type: str, scope: str) -> str:
        """Analyze stored context"""
        try:
            if analysis_type == "summary":
                # Get summary from both systems
                rag_results = await get_rag_context(f"summary of {scope}")
                graph_results = await query_graph_memory_tool(f"summarize {scope}")
                return f"RAG Summary:\n{rag_results}\n\nGraph Summary:\n{graph_results}"

            elif analysis_type == "entities":
                # Extract entities from graph
                graph_results = await query_graph_memory_tool(f"entities related to {scope}")
                return f"Entities:\n{graph_results}"

            elif analysis_type == "relationships":
                # Get relationships from graph
                graph_results = await query_graph_memory_tool(f"relationships involving {scope}")
                return f"Relationships:\n{graph_results}"

            elif analysis_type == "timeline":
                # Get timeline from graph
                if scope != "all":
                    timeline = await graph_memory.get_memory_timeline(scope)
                    return json.dumps(timeline, indent=2, default=str)
                else:
                    return "Timeline analysis requires a specific entity scope"

            else:
                return f"Unknown analysis type: {analysis_type}"

        except Exception as e:
            return f"Analysis error: {str(e)}"

    async def _get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversations from graph memory"""
        try:
            # This would need to be implemented in graph_memory
            # For now, return placeholder
            return [
                {
                    "id": "sample_conv",
                    "timestamp": datetime.now().isoformat(),
                    "user_message": "Sample user message",
                    "assistant_response": "Sample assistant response"
                }
            ]
        except Exception as e:
            return [{"error": str(e)}]

    async def _analyze_conversation_prompt(self, conversation_text: str, depth: str) -> str:
        """Generate conversation analysis prompt"""
        rag_context = await get_rag_context(conversation_text[:200])  # First 200 chars
        graph_context = await query_graph_memory_tool(conversation_text[:200])

        return f"""Analyze the following conversation with {depth} depth:

Conversation:
{conversation_text}

Related RAG Context:
{rag_context}

Related Graph Context:
{graph_context}

Please provide a {depth} analysis covering:
1. Key topics and entities mentioned
2. Relationships between concepts
3. Connections to previous conversations
4. Insights and patterns
5. Suggested follow-up questions or actions
"""

    async def _knowledge_synthesis_prompt(self, query: str, sources: List[str]) -> str:
        """Generate knowledge synthesis prompt"""
        rag_context = await get_rag_context(query)
        graph_context = await query_graph_memory_tool(query)

        source_filter = f" from sources: {', '.join(sources)}" if sources else ""

        return f"""Synthesize knowledge for the query: "{query}"{source_filter}

RAG Retrieved Context:
{rag_context}

Graph Memory Context:
{graph_context}

Please synthesize this information to provide:
1. A comprehensive answer to the query
2. Key insights from different sources
3. Connections and relationships between concepts
4. Areas where information might be incomplete
5. Suggestions for further investigation
"""

    async def _memory_timeline_prompt(self, entity: str, days_back: int) -> str:
        """Generate memory timeline prompt"""
        timeline = await graph_memory.get_memory_timeline(entity, days_back)

        return f"""Generate a timeline analysis for entity: "{entity}" (last {days_back} days)

Timeline Data:
{json.dumps(timeline, indent=2, default=str)}

Please create:
1. A chronological summary of events/mentions
2. Key patterns or trends over time
3. Significant relationships or changes
4. Context for understanding the entity's evolution
5. Insights about the entity's importance or relevance
"""

    async def run(self):
        """Run the MCP server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="pai-agent",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities={}
                    )
                )
            )


async def main():
    """Main entry point for MCP server"""
    logging.basicConfig(level=logging.INFO)
    server = PAIMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())