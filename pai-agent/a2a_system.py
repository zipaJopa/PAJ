#!/usr/bin/env python3
"""
FastA2A (Agent-to-Agent) Communication System
Advanced inter-agent communication and coordination for PAI Agent
"""

import asyncio
import json
import os
import time
from typing import Dict, List, Any, Optional, Set, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import httpx
import logging

logger = logging.getLogger("pai-a2a")


class MessageType(Enum):
    """Types of A2A messages"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    BROADCAST = "broadcast"
    COORDINATION = "coordination"
    HEALTH_CHECK = "health_check"
    CAPABILITY_QUERY = "capability_query"
    TASK_DELEGATION = "task_delegation"


class AgentCapability(Enum):
    """Agent capabilities for coordination"""
    RAG_RETRIEVAL = "rag_retrieval"
    GRAPH_MEMORY = "graph_memory"
    WEB_SEARCH = "web_search"
    CODE_EXECUTION = "code_execution"
    IMAGE_GENERATION = "image_generation"
    DOCUMENT_PROCESSING = "document_processing"
    API_INTEGRATION = "api_integration"
    DATA_ANALYSIS = "data_analysis"
    KNOWLEDGE_SYNTHESIS = "knowledge_synthesis"
    CONVERSATION_MANAGEMENT = "conversation_management"


@dataclass
class AgentProfile:
    """Profile of an agent in the A2A network"""
    agent_id: str
    name: str
    description: str
    capabilities: Set[AgentCapability]
    endpoint: str
    last_seen: datetime
    health_status: str = "unknown"
    response_time_avg: float = 0.0
    success_rate: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class A2AMessage:
    """A2A communication message"""
    message_id: str
    from_agent: str
    to_agent: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: datetime
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    ttl: Optional[int] = None
    priority: int = 0


@dataclass
class TaskDelegation:
    """Task delegation request"""
    task_id: str
    task_type: str
    description: str
    parameters: Dict[str, Any]
    required_capabilities: Set[AgentCapability]
    deadline: Optional[datetime] = None
    priority: int = 0
    delegate_to: Optional[str] = None


class A2ANetworkManager:
    """Manages agent-to-agent communication network"""

    def __init__(self, agent_id: str, agent_name: str, endpoint: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.endpoint = endpoint
        self.agents: Dict[str, AgentProfile] = {}
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.capability_handlers: Dict[AgentCapability, Callable] = {}
        self.active_tasks: Dict[str, TaskDelegation] = {}
        self.message_history: List[A2AMessage] = []
        self.client = httpx.AsyncClient(timeout=30.0)
        self._setup_default_handlers()

    def _setup_default_handlers(self):
        """Setup default message handlers"""
        self.register_handler(MessageType.HEALTH_CHECK, self._handle_health_check)
        self.register_handler(MessageType.CAPABILITY_QUERY, self._handle_capability_query)
        self.register_handler(MessageType.TASK_DELEGATION, self._handle_task_delegation)

    def register_handler(
        self,
        message_type: MessageType,
        handler: Callable[[A2AMessage], Awaitable[Dict[str, Any]]]
    ):
        """Register a message handler"""
        self.message_handlers[message_type] = handler

    def register_capability_handler(
        self,
        capability: AgentCapability,
        handler: Callable[[Dict[str, Any]], Awaitable[Any]]
    ):
        """Register a capability handler"""
        self.capability_handlers[capability] = handler

    async def register_agent(
        self,
        agent_id: str,
        name: str,
        description: str,
        capabilities: Set[AgentCapability],
        endpoint: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Register a new agent in the network"""
        profile = AgentProfile(
            agent_id=agent_id,
            name=name,
            description=description,
            capabilities=capabilities,
            endpoint=endpoint,
            last_seen=datetime.now(),
            metadata=metadata or {}
        )
        self.agents[agent_id] = profile
        logger.info(f"Registered agent: {name} ({agent_id}) with {len(capabilities)} capabilities")

    async def discover_agents(self, discovery_endpoints: List[str]) -> List[str]:
        """Discover other agents in the network"""
        discovered = []

        for endpoint in discovery_endpoints:
            try:
                response = await self.client.get(f"{endpoint}/a2a/v1/profile")
                if response.status_code == 200:
                    profile_data = response.json()
                    await self.register_agent(
                        agent_id=profile_data["agent_id"],
                        name=profile_data["name"],
                        description=profile_data["description"],
                        capabilities=set(AgentCapability(cap) for cap in profile_data["capabilities"]),
                        endpoint=endpoint,
                        metadata=profile_data.get("metadata", {})
                    )
                    discovered.append(profile_data["agent_id"])

            except Exception as e:
                logger.warning(f"Failed to discover agent at {endpoint}: {e}")

        return discovered

    async def send_message(
        self,
        to_agent: str,
        message_type: MessageType,
        content: Dict[str, Any],
        correlation_id: Optional[str] = None,
        reply_to: Optional[str] = None,
        ttl: Optional[int] = None,
        priority: int = 0
    ) -> Optional[A2AMessage]:
        """Send a message to another agent"""
        if to_agent not in self.agents:
            logger.error(f"Agent {to_agent} not found in network")
            return None

        message_id = self._generate_message_id()
        message = A2AMessage(
            message_id=message_id,
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=message_type,
            content=content,
            timestamp=datetime.now(),
            correlation_id=correlation_id,
            reply_to=reply_to,
            ttl=ttl,
            priority=priority
        )

        agent_profile = self.agents[to_agent]

        try:
            start_time = time.time()
            response = await self.client.post(
                f"{agent_profile.endpoint}/a2a/v1/message",
                json=self._message_to_dict(message),
                headers={"Content-Type": "application/json"}
            )
            response_time = time.time() - start_time

            # Update agent metrics
            self._update_agent_metrics(to_agent, response.status_code == 200, response_time)

            if response.status_code == 200:
                self.message_history.append(message)
                logger.info(f"Message sent to {to_agent}: {message_type.value}")
                return message
            else:
                logger.error(f"Failed to send message to {to_agent}: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error sending message to {to_agent}: {e}")
            self._update_agent_metrics(to_agent, False, None)
            return None

    async def broadcast_message(
        self,
        message_type: MessageType,
        content: Dict[str, Any],
        exclude_agents: Optional[Set[str]] = None
    ) -> List[str]:
        """Broadcast a message to all agents in the network"""
        exclude_agents = exclude_agents or set()
        successful_sends = []

        for agent_id in self.agents:
            if agent_id not in exclude_agents and agent_id != self.agent_id:
                message = await self.send_message(agent_id, message_type, content)
                if message:
                    successful_sends.append(agent_id)

        return successful_sends

    async def handle_incoming_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming A2A message"""
        try:
            message = self._dict_to_message(message_data)

            # Check TTL
            if message.ttl and (datetime.now() - message.timestamp).seconds > message.ttl:
                return {"status": "expired", "message": "Message TTL exceeded"}

            # Find appropriate handler
            handler = self.message_handlers.get(message.message_type)
            if not handler:
                return {"status": "error", "message": f"No handler for {message.message_type.value}"}

            # Execute handler
            result = await handler(message)
            self.message_history.append(message)

            return {"status": "success", "result": result}

        except Exception as e:
            logger.error(f"Error handling incoming message: {e}")
            return {"status": "error", "message": str(e)}

    async def delegate_task(
        self,
        task_type: str,
        description: str,
        parameters: Dict[str, Any],
        required_capabilities: Set[AgentCapability],
        deadline: Optional[datetime] = None,
        priority: int = 0
    ) -> Optional[str]:
        """Delegate a task to the most suitable agent"""
        # Find agents with required capabilities
        suitable_agents = []
        for agent_id, profile in self.agents.items():
            if agent_id != self.agent_id and required_capabilities.issubset(profile.capabilities):
                suitable_agents.append((agent_id, profile))

        if not suitable_agents:
            logger.warning(f"No suitable agents found for task requiring {required_capabilities}")
            return None

        # Select best agent based on success rate and response time
        best_agent = min(
            suitable_agents,
            key=lambda x: (1 - x[1].success_rate, x[1].response_time_avg)
        )

        task_id = self._generate_task_id()
        task = TaskDelegation(
            task_id=task_id,
            task_type=task_type,
            description=description,
            parameters=parameters,
            required_capabilities=required_capabilities,
            deadline=deadline,
            priority=priority,
            delegate_to=best_agent[0]
        )

        self.active_tasks[task_id] = task

        # Send task delegation message
        message = await self.send_message(
            to_agent=best_agent[0],
            message_type=MessageType.TASK_DELEGATION,
            content={
                "task_id": task_id,
                "task_type": task_type,
                "description": description,
                "parameters": parameters,
                "required_capabilities": [cap.value for cap in required_capabilities],
                "deadline": deadline.isoformat() if deadline else None,
                "priority": priority
            }
        )

        if message:
            logger.info(f"Task {task_id} delegated to {best_agent[0]}")
            return task_id
        else:
            del self.active_tasks[task_id]
            return None

    async def query_capabilities(
        self,
        required_capabilities: Set[AgentCapability]
    ) -> List[Dict[str, Any]]:
        """Query which agents have specific capabilities"""
        matching_agents = []

        for agent_id, profile in self.agents.items():
            if agent_id != self.agent_id:
                matching_caps = required_capabilities.intersection(profile.capabilities)
                if matching_caps:
                    matching_agents.append({
                        "agent_id": agent_id,
                        "name": profile.name,
                        "matching_capabilities": [cap.value for cap in matching_caps],
                        "all_capabilities": [cap.value for cap in profile.capabilities],
                        "health_status": profile.health_status,
                        "response_time": profile.response_time_avg,
                        "success_rate": profile.success_rate
                    })

        return sorted(matching_agents, key=lambda x: (x["success_rate"], -x["response_time"]), reverse=True)

    async def health_check_network(self) -> Dict[str, Any]:
        """Perform health check on all agents in the network"""
        results = {}

        for agent_id in self.agents:
            if agent_id != self.agent_id:
                message = await self.send_message(
                    to_agent=agent_id,
                    message_type=MessageType.HEALTH_CHECK,
                    content={"timestamp": datetime.now().isoformat()}
                )
                results[agent_id] = "sent" if message else "failed"

        return results

    async def get_network_status(self) -> Dict[str, Any]:
        """Get comprehensive network status"""
        now = datetime.now()
        active_agents = sum(1 for p in self.agents.values() if (now - p.last_seen).seconds < 300)

        return {
            "network_size": len(self.agents),
            "active_agents": active_agents,
            "self_agent": {
                "id": self.agent_id,
                "name": self.agent_name,
                "endpoint": self.endpoint
            },
            "active_tasks": len(self.active_tasks),
            "message_history": len(self.message_history),
            "agents": [
                {
                    "id": agent_id,
                    "name": profile.name,
                    "capabilities": [cap.value for cap in profile.capabilities],
                    "health": profile.health_status,
                    "last_seen": profile.last_seen.isoformat(),
                    "response_time": profile.response_time_avg,
                    "success_rate": profile.success_rate
                }
                for agent_id, profile in self.agents.items()
            ]
        }

    # Default message handlers
    async def _handle_health_check(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle health check message"""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "capabilities": [cap.value for cap in self.capability_handlers.keys()]
        }

    async def _handle_capability_query(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle capability query message"""
        requested_caps = message.content.get("capabilities", [])
        available_caps = [cap.value for cap in self.capability_handlers.keys()]

        matching = [cap for cap in requested_caps if cap in available_caps]

        return {
            "agent_id": self.agent_id,
            "requested_capabilities": requested_caps,
            "available_capabilities": available_caps,
            "matching_capabilities": matching,
            "can_handle": len(matching) == len(requested_caps)
        }

    async def _handle_task_delegation(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle task delegation message"""
        task_data = message.content
        task_type = task_data.get("task_type")
        required_caps = set(AgentCapability(cap) for cap in task_data.get("required_capabilities", []))

        # Check if we can handle this task
        can_handle = required_caps.issubset(self.capability_handlers.keys())

        if can_handle:
            # Execute the task (simplified for demo)
            try:
                result = await self._execute_delegated_task(task_data)
                return {
                    "task_id": task_data["task_id"],
                    "status": "completed",
                    "result": result
                }
            except Exception as e:
                return {
                    "task_id": task_data["task_id"],
                    "status": "failed",
                    "error": str(e)
                }
        else:
            return {
                "task_id": task_data["task_id"],
                "status": "rejected",
                "reason": "insufficient_capabilities",
                "required": [cap.value for cap in required_caps],
                "available": [cap.value for cap in self.capability_handlers.keys()]
            }

    async def _execute_delegated_task(self, task_data: Dict[str, Any]) -> Any:
        """Execute a delegated task based on its type"""
        task_type = task_data["task_type"]
        parameters = task_data.get("parameters", {})

        # This would dispatch to appropriate capability handlers
        # For demo purposes, we'll just return a success message
        return f"Task {task_type} executed with parameters: {parameters}"

    def _generate_message_id(self) -> str:
        """Generate unique message ID"""
        return f"msg_{self.agent_id}_{int(time.time())}_{os.urandom(4).hex()}"

    def _generate_task_id(self) -> str:
        """Generate unique task ID"""
        return f"task_{self.agent_id}_{int(time.time())}_{os.urandom(4).hex()}"

    def _message_to_dict(self, message: A2AMessage) -> Dict[str, Any]:
        """Convert message to dictionary for JSON serialization"""
        return {
            "message_id": message.message_id,
            "from_agent": message.from_agent,
            "to_agent": message.to_agent,
            "message_type": message.message_type.value,
            "content": message.content,
            "timestamp": message.timestamp.isoformat(),
            "correlation_id": message.correlation_id,
            "reply_to": message.reply_to,
            "ttl": message.ttl,
            "priority": message.priority
        }

    def _dict_to_message(self, data: Dict[str, Any]) -> A2AMessage:
        """Convert dictionary to A2AMessage"""
        return A2AMessage(
            message_id=data["message_id"],
            from_agent=data["from_agent"],
            to_agent=data["to_agent"],
            message_type=MessageType(data["message_type"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            correlation_id=data.get("correlation_id"),
            reply_to=data.get("reply_to"),
            ttl=data.get("ttl"),
            priority=data.get("priority", 0)
        )

    def _update_agent_metrics(self, agent_id: str, success: bool, response_time: Optional[float]):
        """Update agent performance metrics"""
        if agent_id in self.agents:
            profile = self.agents[agent_id]
            profile.last_seen = datetime.now()

            if response_time is not None:
                # Simple moving average
                profile.response_time_avg = (profile.response_time_avg * 0.8) + (response_time * 0.2)

            # Update success rate with exponential moving average
            profile.success_rate = (profile.success_rate * 0.9) + (1.0 if success else 0.0) * 0.1

            profile.health_status = "healthy" if success else "degraded"


# Global A2A network manager
a2a_manager = None


def initialize_a2a_network(agent_id: str, agent_name: str, endpoint: str) -> A2ANetworkManager:
    """Initialize A2A network manager"""
    global a2a_manager
    a2a_manager = A2ANetworkManager(agent_id, agent_name, endpoint)

    # Register our capabilities
    from rag_system import rag_system
    from graph_memory import graph_memory

    a2a_manager.register_capability_handler(
        AgentCapability.RAG_RETRIEVAL,
        lambda params: rag_system.agentic_retrieve(params["query"], params.get("context"))
    )

    a2a_manager.register_capability_handler(
        AgentCapability.GRAPH_MEMORY,
        lambda params: graph_memory.find_related_memories(
            params["entities"],
            max_depth=params.get("max_depth", 2)
        )
    )

    a2a_manager.register_capability_handler(
        AgentCapability.KNOWLEDGE_SYNTHESIS,
        lambda params: _synthesize_knowledge(params["query"], params.get("sources", []))
    )

    logger.info(f"A2A network initialized for {agent_name} ({agent_id})")
    return a2a_manager


async def _synthesize_knowledge(query: str, sources: List[str]) -> Dict[str, Any]:
    """Synthesize knowledge from RAG and graph memory"""
    from rag_system import get_rag_context
    from graph_memory import query_graph_memory_tool

    rag_results = await get_rag_context(query)
    graph_results = await query_graph_memory_tool(query)

    return {
        "query": query,
        "rag_context": rag_results,
        "graph_context": graph_results,
        "synthesis": f"Combined insights from RAG and graph memory for: {query}",
        "sources": sources
    }