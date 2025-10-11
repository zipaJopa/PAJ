#!/usr/bin/env python3
"""
RAG System with PostgreSQL + pgvector
Agentic RAG capabilities for PAI Agent
"""

import asyncio
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import hashlib

import asyncpg
import httpx
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, Text, Integer, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
import numpy as np

# Configuration
@dataclass
class RAGConfig:
    database_url: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/pai_db")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_results: int = 5
    similarity_threshold: float = 0.7


class Base(DeclarativeBase):
    pass


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    embedding: Mapped[List[float]] = mapped_column(Vector(1536), nullable=False)
    chunk_metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=True)
    source: Mapped[str] = mapped_column(String(255), nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=True, default="text")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ConversationContext(Base):
    __tablename__ = "conversation_contexts"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    user_message: Mapped[str] = mapped_column(Text, nullable=False)
    assistant_response: Mapped[str] = mapped_column(Text, nullable=False)
    retrieved_chunks: Mapped[List[str]] = mapped_column(JSONB, nullable=True)
    embedding: Mapped[List[float]] = mapped_column(Vector(1536), nullable=False)
    chunk_metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AgenticRAGSystem:
    """Agentic RAG system with PostgreSQL + pgvector"""

    def __init__(self, config: Optional[RAGConfig] = None):
        self.config = config or RAGConfig()
        self.engine = create_async_engine(
            self.config.database_url,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300
        )
        self.async_session = async_sessionmaker(self.engine)
        self.openai_client = AsyncOpenAI(api_key=self.config.openai_api_key) if self.config.openai_api_key else None

    async def initialize(self):
        """Initialize database and tables"""
        async with self.engine.begin() as conn:
            # Create pgvector extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            # Create tables
            await conn.run_sync(Base.metadata.create_all)

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        if not self.openai_client:
            # Fallback to dummy embedding for testing
            return [0.0] * self.config.embedding_dimensions

        try:
            response = await self.openai_client.embeddings.create(
                model=self.config.embedding_model,
                input=text.replace("\n", " "),
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding generation error: {e}")
            return [0.0] * self.config.embedding_dimensions

    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap"""
        if len(text) <= self.config.chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + self.config.chunk_size
            if end > len(text):
                end = len(text)

            chunk = text[start:end]

            # Try to break at sentence boundaries
            if end < len(text) and '.' in chunk[-100:]:
                last_period = chunk.rfind('.')
                if last_period > len(chunk) - 100:
                    chunk = chunk[:last_period + 1]
                    end = start + len(chunk)

            chunks.append(chunk.strip())

            if end >= len(text):
                break

            start = end - self.config.chunk_overlap

        return chunks

    def calculate_content_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    async def store_knowledge(
        self,
        content: str,
        source: str = "manual",
        source_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Store knowledge in vector database"""
        chunks = self.chunk_text(content)
        chunk_ids = []

        async with self.async_session() as session:
            for i, chunk in enumerate(chunks):
                content_hash = self.calculate_content_hash(chunk)

                # Check if chunk already exists
                existing = await session.execute(
                    "SELECT id FROM knowledge_chunks WHERE content_hash = :hash",
                    {"hash": content_hash}
                )

                if existing.fetchone():
                    continue  # Skip duplicate content

                # Generate embedding
                embedding = await self.generate_embedding(chunk)

                # Create chunk ID
                chunk_id = f"{source}_{i}_{int(datetime.now().timestamp())}"

                # Store chunk
                knowledge_chunk = KnowledgeChunk(
                    id=chunk_id,
                    content=chunk,
                    content_hash=content_hash,
                    embedding=embedding,
                    chunk_metadata=metadata or {},
                    source=source,
                    source_type=source_type
                )

                session.add(knowledge_chunk)
                chunk_ids.append(chunk_id)

            await session.commit()

        return chunk_ids

    async def retrieve_relevant_context(
        self,
        query: str,
        max_results: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant context using semantic similarity"""
        max_results = max_results or self.config.max_results
        similarity_threshold = similarity_threshold or self.config.similarity_threshold

        # Generate query embedding
        query_embedding = await self.generate_embedding(query)

        # Perform vector similarity search
        async with self.async_session() as session:
            # Use pgvector cosine similarity
            sql = """
            SELECT
                id, content, chunk_metadata, source, source_type,
                1 - (embedding <=> :query_embedding) as similarity
            FROM knowledge_chunks
            WHERE 1 - (embedding <=> :query_embedding) > :threshold
            ORDER BY embedding <=> :query_embedding
            LIMIT :limit
            """

            result = await session.execute(
                sql,
                {
                    "query_embedding": str(query_embedding),
                    "threshold": similarity_threshold,
                    "limit": max_results
                }
            )

            return [
                {
                    "id": row.id,
                    "content": row.content,
                    "metadata": row.chunk_metadata,
                    "source": row.source,
                    "source_type": row.source_type,
                    "similarity": float(row.similarity)
                }
                for row in result.fetchall()
            ]

    async def store_conversation(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        retrieved_chunks: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store conversation context for future retrieval"""
        conversation_text = f"User: {user_message}\nAssistant: {assistant_response}"
        embedding = await self.generate_embedding(conversation_text)

        conversation_id = f"conv_{session_id}_{int(datetime.now().timestamp())}"

        async with self.async_session() as session:
            conversation = ConversationContext(
                id=conversation_id,
                session_id=session_id,
                user_message=user_message,
                assistant_response=assistant_response,
                retrieved_chunks=retrieved_chunks or [],
                embedding=embedding,
                chunk_metadata=metadata or {}
            )

            session.add(conversation)
            await session.commit()

        return conversation_id

    async def get_conversation_history(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        async with self.async_session() as session:
            sql = """
            SELECT user_message, assistant_response, retrieved_chunks, chunk_metadata, created_at
            FROM conversation_contexts
            WHERE session_id = :session_id
            ORDER BY created_at DESC
            LIMIT :limit
            """

            result = await session.execute(
                sql,
                {"session_id": session_id, "limit": limit}
            )

            return [
                {
                    "user_message": row.user_message,
                    "assistant_response": row.assistant_response,
                    "retrieved_chunks": row.retrieved_chunks,
                    "metadata": row.chunk_metadata,
                    "created_at": row.created_at
                }
                for row in result.fetchall()
            ]

    async def agentic_retrieve(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Agentic retrieval that adapts based on context and query complexity
        """
        context = context or {}

        # Analyze query complexity and intent
        query_analysis = await self._analyze_query(query)

        # Adaptive retrieval strategy
        if query_analysis["complexity"] == "simple":
            # Direct semantic search
            results = await self.retrieve_relevant_context(query, max_results=3)
        elif query_analysis["complexity"] == "complex":
            # Multi-step retrieval with query decomposition
            results = await self._complex_retrieval(query, query_analysis)
        else:
            # Hybrid approach
            results = await self._hybrid_retrieval(query, context)

        # Re-rank results based on context
        ranked_results = await self._rerank_results(results, query, context)

        return {
            "query": query,
            "analysis": query_analysis,
            "results": ranked_results,
            "context_used": context,
            "retrieval_strategy": query_analysis["complexity"]
        }

    async def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query to determine retrieval strategy"""
        # Simple heuristics for query analysis
        # In a real implementation, this could use an LLM

        word_count = len(query.split())
        has_questions = any(word in query.lower() for word in ["what", "how", "why", "when", "where", "who"])
        has_multiple_concepts = "and" in query.lower() or "or" in query.lower()

        if word_count <= 5 and not has_multiple_concepts:
            complexity = "simple"
        elif word_count > 15 or has_multiple_concepts:
            complexity = "complex"
        else:
            complexity = "medium"

        return {
            "complexity": complexity,
            "word_count": word_count,
            "has_questions": has_questions,
            "has_multiple_concepts": has_multiple_concepts,
            "intent": "informational" if has_questions else "search"
        }

    async def _complex_retrieval(
        self,
        query: str,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Handle complex queries with decomposition"""
        # For complex queries, retrieve more results and use different strategies
        results = await self.retrieve_relevant_context(
            query,
            max_results=self.config.max_results * 2,
            similarity_threshold=self.config.similarity_threshold * 0.8
        )

        return results

    async def _hybrid_retrieval(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Hybrid retrieval combining semantic and contextual search"""
        # Standard semantic search
        semantic_results = await self.retrieve_relevant_context(query)

        # Context-aware adjustments
        if "session_id" in context:
            # Get recent conversation context
            conversation_history = await self.get_conversation_history(
                context["session_id"],
                limit=3
            )

            # Combine with conversation context
            # This could be expanded to include conversation-based retrieval

        return semantic_results

    async def _rerank_results(
        self,
        results: List[Dict[str, Any]],
        query: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Re-rank results based on additional context"""
        # Simple re-ranking based on recency and source type
        for result in results:
            # Boost recent content
            if "created_at" in result.get("metadata", {}):
                # Add recency boost logic here
                pass

            # Boost certain source types based on context
            if context.get("prefer_source_type"):
                if result.get("source_type") == context["prefer_source_type"]:
                    result["similarity"] *= 1.1

        # Sort by adjusted similarity
        return sorted(results, key=lambda x: x["similarity"], reverse=True)

    async def health_check(self) -> Dict[str, Any]:
        """Check system health"""
        try:
            async with self.engine.connect() as conn:
                result = await conn.execute("SELECT 1")
                db_connected = result.fetchone() is not None
        except Exception as e:
            db_connected = False

        async with self.async_session() as session:
            # Count stored chunks
            chunk_count_result = await session.execute("SELECT COUNT(*) FROM knowledge_chunks")
            chunk_count = chunk_count_result.scalar()

            # Count conversations
            conv_count_result = await session.execute("SELECT COUNT(*) FROM conversation_contexts")
            conv_count = conv_count_result.scalar()

        return {
            "database_connected": db_connected,
            "knowledge_chunks": chunk_count,
            "conversations": conv_count,
            "embedding_model": self.config.embedding_model,
            "dimensions": self.config.embedding_dimensions
        }


# Global RAG instance
rag_system = AgenticRAGSystem()


async def initialize_rag():
    """Initialize RAG system"""
    await rag_system.initialize()


async def get_rag_context(query: str, context: Optional[Dict[str, Any]] = None) -> str:
    """Get RAG context for query - used by PydanticAI tools"""
    try:
        result = await rag_system.agentic_retrieve(query, context)

        if not result["results"]:
            return f"No relevant context found for: {query}"

        # Format context for agent
        context_parts = []
        for item in result["results"]:
            context_parts.append(
                f"[Source: {item['source']}] {item['content']} (similarity: {item['similarity']:.2f})"
            )

        return "\n\n".join(context_parts)

    except Exception as e:
        return f"RAG retrieval error: {str(e)}"


async def store_rag_knowledge(
    content: str,
    source: str = "manual",
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Store knowledge in RAG system - used by PydanticAI tools"""
    try:
        chunk_ids = await rag_system.store_knowledge(content, source, metadata=metadata)
        return f"Stored {len(chunk_ids)} chunks from {source}"
    except Exception as e:
        return f"Storage error: {str(e)}"