"""
Memory Management System for Agno-AGI Marketing Automation.

Implements multi-layer memory architecture including short-term conversation memory,
long-term campaign memory, and vector-based semantic memory for intelligent retrieval.
"""

import json
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import redis
import sqlite3
from pathlib import Path

from agno.memory import Memory
from loguru import logger
import chromadb
from sentence_transformers import SentenceTransformer

from ..config.settings import get_settings


@dataclass
class MemoryEntry:
    """Base memory entry structure."""
    id: str
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime
    memory_type: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class ConversationMemory(MemoryEntry):
    """Short-term conversation memory entry."""
    session_id: str
    agent_name: str
    user_input: Optional[str] = None
    agent_response: Optional[str] = None
    
    def __post_init__(self):
        self.memory_type = "conversation"


@dataclass
class CampaignMemory(MemoryEntry):
    """Long-term campaign memory entry."""
    campaign_id: str
    campaign_type: str
    success_metrics: Dict[str, Any]
    lessons_learned: List[str]
    
    def __post_init__(self):
        self.memory_type = "campaign"


@dataclass
class VectorMemory(MemoryEntry):
    """Vector-based semantic memory entry."""
    embedding: List[float]
    similarity_threshold: float = 0.8
    
    def __post_init__(self):
        self.memory_type = "vector"


class BaseMemoryProvider(ABC):
    """Abstract base class for memory providers."""
    
    @abstractmethod
    async def store(self, entry: MemoryEntry) -> bool:
        """Store a memory entry."""
        pass
    
    @abstractmethod
    async def retrieve(self, query: Dict[str, Any], limit: int = 10) -> List[MemoryEntry]:
        """Retrieve memory entries based on query."""
        pass
    
    @abstractmethod
    async def delete(self, entry_id: str) -> bool:
        """Delete a memory entry."""
        pass
    
    @abstractmethod
    async def clear(self, memory_type: Optional[str] = None) -> bool:
        """Clear memory entries."""
        pass


class RedisMemoryProvider(BaseMemoryProvider):
    """Redis-based memory provider for fast access."""
    
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
        self.key_prefix = "agno_memory"
    
    def _get_key(self, memory_type: str, entry_id: str) -> str:
        return f"{self.key_prefix}:{memory_type}:{entry_id}"
    
    def _get_pattern(self, memory_type: str) -> str:
        return f"{self.key_prefix}:{memory_type}:*"
    
    async def store(self, entry: MemoryEntry) -> bool:
        """Store memory entry in Redis."""
        try:
            key = self._get_key(entry.memory_type, entry.id)
            data = json.dumps(entry.to_dict())
            
            # Set with expiration for conversation memory
            if entry.memory_type == "conversation":
                ttl = 86400  # 24 hours
                self.redis_client.setex(key, ttl, data)
            else:
                self.redis_client.set(key, data)
            
            # Add to type index
            type_key = f"{self.key_prefix}:index:{entry.memory_type}"
            self.redis_client.sadd(type_key, entry.id)
            
            return True
        except Exception as e:
            logger.error(f"Failed to store memory entry: {e}")
            return False
    
    async def retrieve(self, query: Dict[str, Any], limit: int = 10) -> List[MemoryEntry]:
        """Retrieve memory entries from Redis."""
        try:
            memory_type = query.get("memory_type")
            if not memory_type:
                return []
            
            # Get all entry IDs for this type
            type_key = f"{self.key_prefix}:index:{memory_type}"
            entry_ids = self.redis_client.smembers(type_key)
            
            entries = []
            for entry_id in entry_ids:
                key = self._get_key(memory_type, entry_id.decode())
                data = self.redis_client.get(key)
                if data:
                    entry_dict = json.loads(data)
                    entry = MemoryEntry.from_dict(entry_dict)
                    
                    # Apply filters
                    if self._matches_query(entry, query):
                        entries.append(entry)
            
            # Sort by timestamp (most recent first)
            entries.sort(key=lambda x: x.timestamp, reverse=True)
            return entries[:limit]
            
        except Exception as e:
            logger.error(f"Failed to retrieve memory entries: {e}")
            return []
    
    def _matches_query(self, entry: MemoryEntry, query: Dict[str, Any]) -> bool:
        """Check if entry matches query criteria."""
        for key, value in query.items():
            if key == "memory_type":
                continue
            if hasattr(entry, key) and getattr(entry, key) != value:
                return False
            if key in entry.metadata and entry.metadata[key] != value:
                return False
        return True
    
    async def delete(self, entry_id: str) -> bool:
        """Delete memory entry from Redis."""
        try:
            # Find and delete from all types
            for memory_type in ["conversation", "campaign", "vector"]:
                key = self._get_key(memory_type, entry_id)
                if self.redis_client.exists(key):
                    self.redis_client.delete(key)
                    # Remove from index
                    type_key = f"{self.key_prefix}:index:{memory_type}"
                    self.redis_client.srem(type_key, entry_id)
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete memory entry: {e}")
            return False
    
    async def clear(self, memory_type: Optional[str] = None) -> bool:
        """Clear memory entries."""
        try:
            if memory_type:
                pattern = self._get_pattern(memory_type)
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                # Clear index
                type_key = f"{self.key_prefix}:index:{memory_type}"
                self.redis_client.delete(type_key)
            else:
                # Clear all
                pattern = f"{self.key_prefix}:*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
            return False


class SQLiteMemoryProvider(BaseMemoryProvider):
    """SQLite-based memory provider for persistent storage."""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_entries (
                    id TEXT PRIMARY KEY,
                    memory_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_type ON memory_entries(memory_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memory_entries(timestamp)")
    
    async def store(self, entry: MemoryEntry) -> bool:
        """Store memory entry in SQLite."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO memory_entries 
                    (id, memory_type, content, metadata, timestamp) 
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    entry.id,
                    entry.memory_type,
                    entry.content,
                    json.dumps(entry.metadata),
                    entry.timestamp.isoformat()
                ))
            return True
        except Exception as e:
            logger.error(f"Failed to store memory entry: {e}")
            return False
    
    async def retrieve(self, query: Dict[str, Any], limit: int = 10) -> List[MemoryEntry]:
        """Retrieve memory entries from SQLite."""
        try:
            sql = "SELECT * FROM memory_entries WHERE 1=1"
            params = []
            
            if "memory_type" in query:
                sql += " AND memory_type = ?"
                params.append(query["memory_type"])
            
            sql += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(sql, params)
                
                entries = []
                for row in cursor.fetchall():
                    entry_dict = {
                        "id": row["id"],
                        "content": row["content"],
                        "metadata": json.loads(row["metadata"]),
                        "timestamp": row["timestamp"],
                        "memory_type": row["memory_type"]
                    }
                    entry = MemoryEntry.from_dict(entry_dict)
                    entries.append(entry)
                
                return entries
                
        except Exception as e:
            logger.error(f"Failed to retrieve memory entries: {e}")
            return []
    
    async def delete(self, entry_id: str) -> bool:
        """Delete memory entry from SQLite."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("DELETE FROM memory_entries WHERE id = ?", (entry_id,))
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to delete memory entry: {e}")
            return False
    
    async def clear(self, memory_type: Optional[str] = None) -> bool:
        """Clear memory entries from SQLite."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if memory_type:
                    conn.execute("DELETE FROM memory_entries WHERE memory_type = ?", (memory_type,))
                else:
                    conn.execute("DELETE FROM memory_entries")
            return True
        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
            return False


class VectorMemoryProvider(BaseMemoryProvider):
    """ChromaDB-based vector memory provider for semantic search."""
    
    def __init__(self, chroma_path: str, embedding_model: str = "all-MiniLM-L6-v2"):
        self.chroma_path = Path(chroma_path)
        self.chroma_path.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=str(self.chroma_path))
        self.collection = self.client.get_or_create_collection("agno_memory")
        self.embedding_model = SentenceTransformer(embedding_model)
    
    async def store(self, entry: MemoryEntry) -> bool:
        """Store memory entry with vector embedding."""
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(entry.content).tolist()
            
            self.collection.add(
                ids=[entry.id],
                embeddings=[embedding],
                metadatas=[{
                    "memory_type": entry.memory_type,
                    "timestamp": entry.timestamp.isoformat(),
                    **entry.metadata
                }],
                documents=[entry.content]
            )
            return True
        except Exception as e:
            logger.error(f"Failed to store vector memory: {e}")
            return False
    
    async def retrieve(self, query: Dict[str, Any], limit: int = 10) -> List[MemoryEntry]:
        """Retrieve memory entries using semantic search."""
        try:
            query_text = query.get("content", "")
            if not query_text:
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query_text).tolist()
            
            # Prepare where clause
            where_clause = {}
            if "memory_type" in query:
                where_clause["memory_type"] = query["memory_type"]
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause if where_clause else None
            )
            
            entries = []
            if results["ids"] and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    metadata = results["metadatas"][0][i]
                    content = results["documents"][0][i]
                    
                    entry = MemoryEntry(
                        id=doc_id,
                        content=content,
                        metadata={k: v for k, v in metadata.items() 
                                if k not in ["memory_type", "timestamp"]},
                        timestamp=datetime.fromisoformat(metadata["timestamp"]),
                        memory_type=metadata["memory_type"]
                    )
                    entries.append(entry)
            
            return entries
            
        except Exception as e:
            logger.error(f"Failed to retrieve vector memory: {e}")
            return []
    
    async def delete(self, entry_id: str) -> bool:
        """Delete memory entry from vector store."""
        try:
            self.collection.delete(ids=[entry_id])
            return True
        except Exception as e:
            logger.error(f"Failed to delete vector memory: {e}")
            return False
    
    async def clear(self, memory_type: Optional[str] = None) -> bool:
        """Clear vector memory entries."""
        try:
            if memory_type:
                self.collection.delete(where={"memory_type": memory_type})
            else:
                # Recreate collection to clear all
                self.client.delete_collection("agno_memory")
                self.collection = self.client.create_collection("agno_memory")
            return True
        except Exception as e:
            logger.error(f"Failed to clear vector memory: {e}")
            return False


class MultiLayerMemoryManager:
    """Multi-layer memory manager coordinating different memory providers."""
    
    def __init__(self):
        self.settings = get_settings()
        self.providers = {}
        self._init_providers()
    
    def _init_providers(self):
        """Initialize memory providers based on configuration."""
        # Short-term memory (Redis)
        if self.settings.memory.memory_provider == "redis":
            self.providers["short_term"] = RedisMemoryProvider(self.settings.database.redis_url)
        else:
            self.providers["short_term"] = SQLiteMemoryProvider("./data/short_term_memory.db")
        
        # Long-term memory (SQLite)
        self.providers["long_term"] = SQLiteMemoryProvider("./data/long_term_memory.db")
        
        # Vector memory (ChromaDB)
        self.providers["vector"] = VectorMemoryProvider(
            self.settings.database.chroma_db_path,
            self.settings.memory.embedding_model
        )
    
    async def store_conversation(
        self,
        session_id: str,
        agent_name: str,
        user_input: str,
        agent_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Store conversation memory."""
        entry = ConversationMemory(
            id=f"{session_id}_{datetime.now().timestamp()}",
            content=f"User: {user_input}\nAgent: {agent_response}",
            metadata=metadata or {},
            timestamp=datetime.now(),
            memory_type="conversation",
            session_id=session_id,
            agent_name=agent_name,
            user_input=user_input,
            agent_response=agent_response
        )
        
        # Store in both short-term and vector memory
        results = await asyncio.gather(
            self.providers["short_term"].store(entry),
            self.providers["vector"].store(entry),
            return_exceptions=True
        )
        
        return any(isinstance(r, bool) and r for r in results)
    
    async def store_campaign_memory(
        self,
        campaign_id: str,
        campaign_type: str,
        success_metrics: Dict[str, Any],
        lessons_learned: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Store campaign memory."""
        content = f"Campaign: {campaign_type}\nMetrics: {success_metrics}\nLessons: {lessons_learned}"
        
        entry = CampaignMemory(
            id=f"campaign_{campaign_id}_{datetime.now().timestamp()}",
            content=content,
            metadata=metadata or {},
            timestamp=datetime.now(),
            memory_type="campaign",
            campaign_id=campaign_id,
            campaign_type=campaign_type,
            success_metrics=success_metrics,
            lessons_learned=lessons_learned
        )
        
        # Store in both long-term and vector memory
        results = await asyncio.gather(
            self.providers["long_term"].store(entry),
            self.providers["vector"].store(entry),
            return_exceptions=True
        )
        
        return any(isinstance(r, bool) and r for r in results)
    
    async def retrieve_similar_conversations(
        self,
        query_text: str,
        limit: int = 5
    ) -> List[MemoryEntry]:
        """Retrieve similar conversations using semantic search."""
        return await self.providers["vector"].retrieve({
            "content": query_text,
            "memory_type": "conversation"
        }, limit)
    
    async def retrieve_campaign_insights(
        self,
        campaign_type: Optional[str] = None,
        limit: int = 10
    ) -> List[MemoryEntry]:
        """Retrieve campaign insights and lessons learned."""
        query = {"memory_type": "campaign"}
        if campaign_type:
            query["campaign_type"] = campaign_type
        
        return await self.providers["long_term"].retrieve(query, limit)
    
    async def get_conversation_history(
        self,
        session_id: str,
        limit: int = 20
    ) -> List[MemoryEntry]:
        """Get conversation history for a session."""
        return await self.providers["short_term"].retrieve({
            "memory_type": "conversation",
            "session_id": session_id
        }, limit)
    
    async def semantic_search(
        self,
        query_text: str,
        memory_type: Optional[str] = None,
        limit: int = 10
    ) -> List[MemoryEntry]:
        """Perform semantic search across all memory."""
        query = {"content": query_text}
        if memory_type:
            query["memory_type"] = memory_type
        
        return await self.providers["vector"].retrieve(query, limit)
    
    async def cleanup_old_conversations(self, days: int = 7) -> bool:
        """Clean up old conversation memories."""
        cutoff = datetime.now() - timedelta(days=days)
        # This would require additional implementation in providers
        # to support time-based deletion
        return True


# Global memory manager instance
memory_manager = MultiLayerMemoryManager()