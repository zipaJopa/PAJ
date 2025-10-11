#!/usr/bin/env python3
"""
Neo4j Graph Memory System
Advanced graph-based memory for PAI Agent with relationship tracking and contextual retrieval
"""

import asyncio
import json
import os
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import re

from neo4j import AsyncGraphDatabase, AsyncManagedTransaction
from neo4j.exceptions import ServiceUnavailable, TransientError


class NodeType(Enum):
    """Types of nodes in the graph"""
    PERSON = "Person"
    CONCEPT = "Concept"
    EVENT = "Event"
    DOCUMENT = "Document"
    CONVERSATION = "Conversation"
    TASK = "Task"
    PROJECT = "Project"
    LOCATION = "Location"
    ORGANIZATION = "Organization"
    SKILL = "Skill"
    MEMORY = "Memory"


class RelationType(Enum):
    """Types of relationships in the graph"""
    KNOWS = "KNOWS"
    RELATED_TO = "RELATED_TO"
    PART_OF = "PART_OF"
    OCCURRED_AT = "OCCURRED_AT"
    DISCUSSED_IN = "DISCUSSED_IN"
    CREATED_BY = "CREATED_BY"
    MENTIONED_IN = "MENTIONED_IN"
    DEPENDS_ON = "DEPENDS_ON"
    LEADS_TO = "LEADS_TO"
    LOCATED_IN = "LOCATED_IN"
    WORKS_FOR = "WORKS_FOR"
    SKILLED_IN = "SKILLED_IN"
    COLLABORATES_WITH = "COLLABORATES_WITH"
    SIMILAR_TO = "SIMILAR_TO"
    TRIGGERED_BY = "TRIGGERED_BY"


@dataclass
class GraphNode:
    """Represents a node in the knowledge graph"""
    id: str
    type: NodeType
    name: str
    properties: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    importance_score: float = 0.5
    access_count: int = 0
    last_accessed: Optional[datetime] = field(default=None)


@dataclass
class GraphRelationship:
    """Represents a relationship in the knowledge graph"""
    from_node: str
    to_node: str
    type: RelationType
    properties: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    strength: float = 0.5


@dataclass
class GraphConfig:
    """Configuration for Neo4j Graph Memory"""
    uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    username: str = os.getenv("NEO4J_USERNAME", "neo4j")
    password: str = os.getenv("NEO4J_PASSWORD", "password")
    database: str = os.getenv("NEO4J_DATABASE", "neo4j")
    max_connection_lifetime: int = 30
    max_connection_pool_size: int = 50
    connection_timeout: float = 5.0


class GraphMemorySystem:
    """Advanced Neo4j-based graph memory system"""

    def __init__(self, config: Optional[GraphConfig] = None):
        self.config = config or GraphConfig()
        self.driver = None
        self._initialized = False

    async def initialize(self):
        """Initialize Neo4j connection and create constraints"""
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.config.uri,
                auth=(self.config.username, self.config.password),
                max_connection_lifetime=self.config.max_connection_lifetime,
                max_connection_pool_size=self.config.max_connection_pool_size,
                connection_timeout=self.config.connection_timeout
            )

            # Verify connectivity
            await self.driver.verify_connectivity()

            # Create constraints and indexes
            await self._create_constraints()
            self._initialized = True

        except Exception as e:
            raise ConnectionError(f"Failed to initialize Neo4j connection: {e}")

    async def close(self):
        """Close Neo4j connection"""
        if self.driver:
            await self.driver.close()

    async def _create_constraints(self):
        """Create database constraints and indexes"""
        constraints = [
            "CREATE CONSTRAINT node_id_unique IF NOT EXISTS FOR (n:Node) REQUIRE n.id IS UNIQUE",
            "CREATE INDEX node_type_index IF NOT EXISTS FOR (n:Node) ON (n.type)",
            "CREATE INDEX node_name_index IF NOT EXISTS FOR (n:Node) ON (n.name)",
            "CREATE INDEX node_importance_index IF NOT EXISTS FOR (n:Node) ON (n.importance_score)",
            "CREATE INDEX node_created_index IF NOT EXISTS FOR (n:Node) ON (n.created_at)",
            "CREATE INDEX relationship_type_index IF NOT EXISTS FOR ()-[r:RELATIONSHIP]-() ON (r.type)",
            "CREATE INDEX relationship_strength_index IF NOT EXISTS FOR ()-[r:RELATIONSHIP]-() ON (r.strength)"
        ]

        async with self.driver.session(database=self.config.database) as session:
            for constraint in constraints:
                try:
                    await session.run(constraint)
                except Exception as e:
                    # Constraints may already exist
                    pass

    def _generate_node_id(self, name: str, node_type: NodeType) -> str:
        """Generate unique node ID"""
        content = f"{node_type.value}:{name}".lower()
        return hashlib.md5(content.encode()).hexdigest()

    async def create_node(
        self,
        name: str,
        node_type: NodeType,
        properties: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new node in the graph"""
        if not self._initialized:
            await self.initialize()

        node_id = self._generate_node_id(name, node_type)
        now = datetime.now()

        node_properties = {
            "id": node_id,
            "name": name,
            "type": node_type.value,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "importance_score": 0.5,
            "access_count": 0,
            **(properties or {})
        }

        query = """
        MERGE (n:Node {id: $node_id})
        SET n += $properties, n:""" + node_type.value + """
        RETURN n.id as id
        """

        async with self.driver.session(database=self.config.database) as session:
            result = await session.run(query, node_id=node_id, properties=node_properties)
            record = await result.single()
            return record["id"] if record else node_id

    async def create_relationship(
        self,
        from_node_id: str,
        to_node_id: str,
        relationship_type: RelationType,
        properties: Optional[Dict[str, Any]] = None,
        strength: float = 0.5
    ) -> bool:
        """Create a relationship between two nodes"""
        if not self._initialized:
            await self.initialize()

        now = datetime.now()
        rel_properties = {
            "type": relationship_type.value,
            "strength": strength,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            **(properties or {})
        }

        query = f"""
        MATCH (a:Node {{id: $from_id}}), (b:Node {{id: $to_id}})
        MERGE (a)-[r:{relationship_type.value}]->(b)
        SET r += $properties
        RETURN r
        """

        async with self.driver.session(database=self.config.database) as session:
            result = await session.run(
                query,
                from_id=from_node_id,
                to_id=to_node_id,
                properties=rel_properties
            )
            return await result.single() is not None

    async def store_conversation_memory(
        self,
        conversation_id: str,
        user_message: str,
        assistant_response: str,
        entities: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store conversation as a connected memory graph"""
        if not self._initialized:
            await self.initialize()

        # Create conversation node
        conv_node_id = await self.create_node(
            name=f"Conversation {conversation_id}",
            node_type=NodeType.CONVERSATION,
            properties={
                "conversation_id": conversation_id,
                "user_message": user_message,
                "assistant_response": assistant_response,
                "context": context or {}
            }
        )

        # Extract and create entity nodes
        entity_nodes = []
        if entities:
            for entity in entities:
                entity_id = await self.create_node(
                    name=entity["name"],
                    node_type=NodeType(entity.get("type", "CONCEPT")),
                    properties=entity.get("properties", {})
                )
                entity_nodes.append(entity_id)

                # Connect entity to conversation
                await self.create_relationship(
                    conv_node_id,
                    entity_id,
                    RelationType.MENTIONED_IN,
                    properties={"confidence": entity.get("confidence", 0.8)}
                )

        # Auto-extract entities from text if not provided
        if not entities:
            extracted_entities = await self._extract_entities(user_message + " " + assistant_response)
            for entity_name, entity_type in extracted_entities:
                entity_id = await self.create_node(
                    name=entity_name,
                    node_type=entity_type,
                    properties={"auto_extracted": True}
                )
                entity_nodes.append(entity_id)

                await self.create_relationship(
                    conv_node_id,
                    entity_id,
                    RelationType.MENTIONED_IN,
                    properties={"auto_extracted": True, "confidence": 0.6}
                )

        return conv_node_id

    async def _extract_entities(self, text: str) -> List[Tuple[str, NodeType]]:
        """Simple entity extraction from text"""
        entities = []

        # Simple patterns for entity extraction
        patterns = {
            NodeType.PERSON: r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Names
            NodeType.ORGANIZATION: r'\b[A-Z][a-zA-Z]*(?: [A-Z][a-zA-Z]*)*(?:Inc|Corp|LLC|Ltd|Company|Organization)\b',
            NodeType.LOCATION: r'\b[A-Z][a-z]+(?:, [A-Z][a-z]+)*\b',  # Cities, countries
        }

        for node_type, pattern in patterns.items():
            matches = re.findall(pattern, text)
            for match in matches:
                entities.append((match.strip(), node_type))

        # Remove duplicates
        return list(set(entities))

    async def find_related_memories(
        self,
        query_entities: List[str],
        relationship_types: Optional[List[RelationType]] = None,
        max_depth: int = 2,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find memories related to given entities"""
        if not self._initialized:
            await self.initialize()

        if not query_entities:
            return []

        # Build relationship type filter
        rel_filter = ""
        if relationship_types:
            rel_types = "|".join([rt.value for rt in relationship_types])
            rel_filter = f":{rel_types}"

        query = f"""
        MATCH (query_node:Node)
        WHERE query_node.name IN $entity_names

        MATCH path = (query_node)-[r{rel_filter}*1..{max_depth}]-(related:Node)
        WHERE related.type = 'Conversation'

        WITH related,
             length(path) as distance,
             avg(r.strength) as avg_strength,
             count(DISTINCT query_node) as entity_matches

        RETURN related.id as id,
               related.name as name,
               related.user_message as user_message,
               related.assistant_response as assistant_response,
               related.created_at as created_at,
               distance,
               avg_strength,
               entity_matches

        ORDER BY entity_matches DESC, avg_strength DESC, distance ASC
        LIMIT $limit
        """

        async with self.driver.session(database=self.config.database) as session:
            result = await session.run(
                query,
                entity_names=query_entities,
                limit=limit
            )

            memories = []
            async for record in result:
                memories.append({
                    "id": record["id"],
                    "name": record["name"],
                    "user_message": record["user_message"],
                    "assistant_response": record["assistant_response"],
                    "created_at": record["created_at"],
                    "distance": record["distance"],
                    "strength": record["avg_strength"],
                    "entity_matches": record["entity_matches"],
                    "relevance_score": self._calculate_relevance_score(
                        record["entity_matches"],
                        record["avg_strength"],
                        record["distance"]
                    )
                })

            return sorted(memories, key=lambda x: x["relevance_score"], reverse=True)

    def _calculate_relevance_score(
        self,
        entity_matches: int,
        avg_strength: float,
        distance: int
    ) -> float:
        """Calculate relevance score for memory retrieval"""
        # Weight entity matches heavily, then strength, then inverse distance
        score = (entity_matches * 0.5) + (avg_strength * 0.3) + ((1.0 / distance) * 0.2)
        return min(score, 1.0)

    async def update_node_importance(self, node_id: str, access_weight: float = 0.1):
        """Update node importance based on access patterns"""
        if not self._initialized:
            await self.initialize()

        query = """
        MATCH (n:Node {id: $node_id})
        SET n.access_count = n.access_count + 1,
            n.last_accessed = datetime(),
            n.importance_score = n.importance_score + $access_weight
        RETURN n.importance_score as new_score
        """

        async with self.driver.session(database=self.config.database) as session:
            result = await session.run(query, node_id=node_id, access_weight=access_weight)
            record = await result.single()
            return record["new_score"] if record else None

    async def find_memory_clusters(
        self,
        min_cluster_size: int = 3,
        relationship_strength_threshold: float = 0.6
    ) -> List[Dict[str, Any]]:
        """Find clusters of related memories"""
        if not self._initialized:
            await self.initialize()

        query = """
        MATCH (n:Node)-[r:RELATIONSHIP]-(m:Node)
        WHERE r.strength >= $strength_threshold
        WITH n, collect(m) as connected_nodes
        WHERE size(connected_nodes) >= $min_size

        RETURN n.id as central_node,
               n.name as central_name,
               n.type as central_type,
               [node in connected_nodes | {id: node.id, name: node.name, type: node.type}] as cluster_nodes,
               size(connected_nodes) as cluster_size

        ORDER BY cluster_size DESC
        """

        async with self.driver.session(database=self.config.database) as session:
            result = await session.run(
                query,
                strength_threshold=relationship_strength_threshold,
                min_size=min_cluster_size
            )

            clusters = []
            async for record in result:
                clusters.append({
                    "central_node": record["central_node"],
                    "central_name": record["central_name"],
                    "central_type": record["central_type"],
                    "cluster_nodes": record["cluster_nodes"],
                    "cluster_size": record["cluster_size"]
                })

            return clusters

    async def get_memory_timeline(
        self,
        entity_name: str,
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """Get timeline of memories related to an entity"""
        if not self._initialized:
            await self.initialize()

        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()

        query = """
        MATCH (entity:Node {name: $entity_name})-[:MENTIONED_IN]-(conv:Conversation)
        WHERE conv.created_at >= $cutoff_date

        RETURN conv.id as id,
               conv.name as name,
               conv.user_message as user_message,
               conv.assistant_response as assistant_response,
               conv.created_at as created_at

        ORDER BY conv.created_at DESC
        """

        async with self.driver.session(database=self.config.database) as session:
            result = await session.run(
                query,
                entity_name=entity_name,
                cutoff_date=cutoff_date
            )

            timeline = []
            async for record in result:
                timeline.append({
                    "id": record["id"],
                    "name": record["name"],
                    "user_message": record["user_message"],
                    "assistant_response": record["assistant_response"],
                    "created_at": record["created_at"]
                })

            return timeline

    async def health_check(self) -> Dict[str, Any]:
        """Check graph database health"""
        try:
            if not self._initialized:
                await self.initialize()

            async with self.driver.session(database=self.config.database) as session:
                # Count nodes and relationships
                node_count_result = await session.run("MATCH (n:Node) RETURN count(n) as count")
                node_count = (await node_count_result.single())["count"]

                rel_count_result = await session.run("MATCH ()-[r]->() RETURN count(r) as count")
                rel_count = (await rel_count_result.single())["count"]

                # Check recent activity
                recent_result = await session.run("""
                MATCH (n:Node)
                WHERE n.created_at >= datetime() - duration('P7D')
                RETURN count(n) as recent_nodes
                """)
                recent_nodes = (await recent_result.single())["recent_nodes"]

                return {
                    "connected": True,
                    "node_count": node_count,
                    "relationship_count": rel_count,
                    "recent_nodes": recent_nodes,
                    "database": self.config.database
                }

        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "database": self.config.database
            }

    async def query_graph(self, cypher_query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute custom Cypher query"""
        if not self._initialized:
            await self.initialize()

        async with self.driver.session(database=self.config.database) as session:
            result = await session.run(cypher_query, parameters or {})
            return [record.data() for record in await result.data()]


# Global graph memory instance
graph_memory = GraphMemorySystem()


async def initialize_graph_memory():
    """Initialize graph memory system"""
    await graph_memory.initialize()


async def store_graph_memory(
    content: str,
    relationships: List[str],
    context: Optional[Dict[str, Any]] = None
) -> str:
    """Store memory in graph - used by PydanticAI tools"""
    try:
        # Generate a simple conversation ID
        conv_id = f"manual_{int(datetime.now().timestamp())}"

        # Extract entities from relationships
        entities = []
        for rel in relationships:
            # Simple parsing of "entity1 RELATES_TO entity2" format
            parts = rel.split()
            if len(parts) >= 3:
                entities.extend([
                    {"name": parts[0], "type": "CONCEPT"},
                    {"name": parts[-1], "type": "CONCEPT"}
                ])

        node_id = await graph_memory.store_conversation_memory(
            conversation_id=conv_id,
            user_message=f"Manual entry: {content}",
            assistant_response="Stored in graph memory",
            entities=entities,
            context=context
        )

        return f"Stored in graph memory with ID: {node_id}"

    except Exception as e:
        return f"Graph storage error: {str(e)}"


async def query_graph_memory_tool(query: str) -> str:
    """Query graph memory - used by PydanticAI tools"""
    try:
        # Extract entities from query (simple approach)
        words = [word.strip('.,!?') for word in query.split() if len(word) > 3]
        entity_candidates = [word.title() for word in words if word[0].isupper()]

        if not entity_candidates:
            entity_candidates = words  # Fallback to all words

        memories = await graph_memory.find_related_memories(
            query_entities=entity_candidates[:3],  # Limit to top 3 entities
            max_depth=2,
            limit=5
        )

        if not memories:
            return f"No related memories found for: {query}"

        # Format results
        result_parts = []
        for memory in memories:
            result_parts.append(
                f"Memory (relevance: {memory['relevance_score']:.2f}): "
                f"{memory['user_message'][:100]}... -> {memory['assistant_response'][:100]}..."
            )

        return "\n\n".join(result_parts)

    except Exception as e:
        return f"Graph query error: {str(e)}"