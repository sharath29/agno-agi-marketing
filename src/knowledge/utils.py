"""
Knowledge utilities for easy integration with marketing agents.

Provides convenient functions for agents to access marketing knowledge,
best practices, and templates.
"""

from typing import Any, Dict, List, Optional

from .knowledge_manager import marketing_knowledge_base, rag_retriever


async def get_marketing_guidance(topic: str) -> str:
    """Get marketing guidance for a specific topic."""
    guidance = await rag_retriever.get_best_practice_guidance(topic)
    return guidance


async def search_marketing_knowledge(
    query: str, category: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search marketing knowledge base."""
    return await marketing_knowledge_base.search_knowledge(query=query, category=category, limit=3)


async def get_email_templates() -> List[Dict[str, str]]:
    """Get email marketing templates."""
    return await rag_retriever.get_template_suggestions("email_marketing")


async def get_personalization_strategies() -> str:
    """Get personalization strategies and best practices."""
    return await get_marketing_guidance("personalization")


async def get_lead_qualification_framework() -> str:
    """Get lead qualification frameworks and guidance."""
    return await get_marketing_guidance("lead qualification")


async def get_campaign_best_practices(campaign_type: str) -> str:
    """Get best practices for specific campaign types."""
    return await get_marketing_guidance(f"{campaign_type} campaign")


async def enhance_agent_prompt(base_prompt: str, knowledge_context: str) -> str:
    """Enhance an agent prompt with relevant knowledge."""
    return await rag_retriever.enhance_prompt_with_knowledge(
        base_prompt=base_prompt, knowledge_query=knowledge_context
    )


async def add_campaign_insights(campaign_type: str, insights: Dict[str, Any]) -> None:
    """Add insights from a completed campaign."""
    await marketing_knowledge_base.add_campaign_learnings(
        campaign_type=campaign_type,
        what_worked=insights.get("successes", []),
        what_didnt_work=insights.get("failures", []),
        metrics=insights.get("metrics", {}),
        recommendations=insights.get("recommendations", []),
    )
