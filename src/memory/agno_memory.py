"""
Agno Memory Integration for Marketing Automation.

Integrates with Agno's native memory system while providing enhanced
functionality for marketing campaign memory and context management.
"""

from typing import Dict, List, Optional, Any
from agno.memory import Memory
from agno.storage import PgAgentStorage
from loguru import logger

from .memory_manager import memory_manager
from ..config.settings import get_settings


class MarketingMemory(Memory):
    """Enhanced memory class for marketing automation agents."""
    
    def __init__(self, 
                 agent_name: str,
                 session_id: Optional[str] = None,
                 max_memories: int = 100):
        super().__init__()
        self.agent_name = agent_name
        self.session_id = session_id or f"{agent_name}_session"
        self.max_memories = max_memories
        self.settings = get_settings()
        
    async def add_memory(self, 
                        user_message: str, 
                        agent_response: str,
                        metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a memory of user-agent interaction."""
        try:
            await memory_manager.store_conversation(
                session_id=self.session_id,
                agent_name=self.agent_name,
                user_input=user_message,
                agent_response=agent_response,
                metadata=metadata or {}
            )
            
            # Also store in parent memory system
            memory_content = f"User: {user_message}\nResponse: {agent_response}"
            super().add(memory=memory_content, metadata=metadata or {})
            
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
    
    async def get_relevant_memories(self, 
                                  query: str, 
                                  limit: int = 5) -> List[Dict[str, Any]]:
        """Get memories relevant to the current query."""
        try:
            memories = await memory_manager.retrieve_similar_conversations(query, limit)
            return [
                {
                    "content": memory.content,
                    "timestamp": memory.timestamp,
                    "metadata": memory.metadata
                }
                for memory in memories
            ]
        except Exception as e:
            logger.error(f"Failed to get relevant memories: {e}")
            return []
    
    async def get_conversation_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get conversation history for current session."""
        try:
            memories = await memory_manager.get_conversation_history(self.session_id, limit)
            return [
                {
                    "content": memory.content,
                    "timestamp": memory.timestamp,
                    "metadata": memory.metadata
                }
                for memory in memories
            ]
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []


class CampaignMemory:
    """Memory system specifically for marketing campaigns."""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def store_campaign_result(self,
                                  campaign_id: str,
                                  campaign_type: str,
                                  metrics: Dict[str, Any],
                                  lessons: List[str],
                                  metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Store results and learnings from a campaign."""
        try:
            return await memory_manager.store_campaign_memory(
                campaign_id=campaign_id,
                campaign_type=campaign_type,
                success_metrics=metrics,
                lessons_learned=lessons,
                metadata=metadata or {}
            )
        except Exception as e:
            logger.error(f"Failed to store campaign result: {e}")
            return False
    
    async def get_campaign_insights(self,
                                  campaign_type: Optional[str] = None,
                                  limit: int = 10) -> List[Dict[str, Any]]:
        """Get insights from previous campaigns."""
        try:
            memories = await memory_manager.retrieve_campaign_insights(campaign_type, limit)
            return [
                {
                    "campaign_id": getattr(memory, 'campaign_id', 'unknown'),
                    "campaign_type": getattr(memory, 'campaign_type', 'unknown'),
                    "metrics": getattr(memory, 'success_metrics', {}),
                    "lessons": getattr(memory, 'lessons_learned', []),
                    "timestamp": memory.timestamp,
                    "metadata": memory.metadata
                }
                for memory in memories
            ]
        except Exception as e:
            logger.error(f"Failed to get campaign insights: {e}")
            return []
    
    async def find_similar_campaigns(self,
                                   description: str,
                                   limit: int = 5) -> List[Dict[str, Any]]:
        """Find campaigns similar to the description."""
        try:
            memories = await memory_manager.semantic_search(
                query_text=description,
                memory_type="campaign",
                limit=limit
            )
            return [
                {
                    "campaign_id": getattr(memory, 'campaign_id', 'unknown'),
                    "campaign_type": getattr(memory, 'campaign_type', 'unknown'),
                    "similarity_content": memory.content,
                    "metrics": getattr(memory, 'success_metrics', {}),
                    "lessons": getattr(memory, 'lessons_learned', []),
                    "timestamp": memory.timestamp
                }
                for memory in memories
            ]
        except Exception as e:
            logger.error(f"Failed to find similar campaigns: {e}")
            return []


def create_agent_memory(agent_name: str, session_id: Optional[str] = None) -> MarketingMemory:
    """Factory function to create memory for an agent."""
    return MarketingMemory(
        agent_name=agent_name,
        session_id=session_id
    )


def create_campaign_memory() -> CampaignMemory:
    """Factory function to create campaign memory."""
    return CampaignMemory()


class MemoryEnhancedAgent:
    """Mixin class to add enhanced memory capabilities to agents."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enhanced_memory = create_agent_memory(self.name)
        self.campaign_memory = create_campaign_memory()
    
    async def remember_interaction(self, 
                                 user_input: str, 
                                 response: str,
                                 context: Optional[Dict[str, Any]] = None):
        """Remember a user interaction with context."""
        await self.enhanced_memory.add_memory(
            user_message=user_input,
            agent_response=response,
            metadata=context or {}
        )
    
    async def recall_similar_interactions(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Recall similar past interactions."""
        return await self.enhanced_memory.get_relevant_memories(query, limit)
    
    async def get_conversation_context(self, limit: int = 10) -> str:
        """Get formatted conversation context."""
        history = await self.enhanced_memory.get_conversation_history(limit)
        if not history:
            return "No previous conversation history."
        
        context_lines = []
        for memory in reversed(history[-5:]):  # Last 5 interactions
            context_lines.append(memory["content"])
        
        return "\n".join(context_lines)
    
    async def learn_from_campaign(self,
                                campaign_id: str,
                                campaign_type: str,
                                metrics: Dict[str, Any],
                                lessons: List[str]):
        """Store learnings from a campaign."""
        await self.campaign_memory.store_campaign_result(
            campaign_id=campaign_id,
            campaign_type=campaign_type,
            metrics=metrics,
            lessons=lessons
        )
    
    async def get_campaign_wisdom(self, campaign_type: Optional[str] = None) -> str:
        """Get wisdom from previous campaigns."""
        insights = await self.campaign_memory.get_campaign_insights(campaign_type)
        if not insights:
            return "No previous campaign insights available."
        
        wisdom_lines = ["Previous campaign insights:"]
        for insight in insights[:3]:  # Top 3 insights
            lessons = insight.get("lessons", [])
            if lessons:
                wisdom_lines.append(f"- {campaign_type or 'Campaign'}: {', '.join(lessons[:2])}")
        
        return "\n".join(wisdom_lines)