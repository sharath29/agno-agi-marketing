"""
Knowledge Management System with RAG Capabilities for Agno-AGI Marketing Automation.

Provides intelligent knowledge storage, retrieval, and augmentation for marketing
domain expertise, best practices, and campaign insights.
"""

import asyncio
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import json

from agno.knowledge import Knowledge
from agno.knowledge.vector import VectorKnowledge
import chromadb
from sentence_transformers import SentenceTransformer
from loguru import logger
import pandas as pd

from ..config.settings import get_settings


@dataclass
class KnowledgeDocument:
    """Structured knowledge document."""
    id: str
    title: str
    content: str
    document_type: str  # "best_practice", "case_study", "template", "guide"
    category: str  # "email_marketing", "lead_generation", "personalization", etc.
    tags: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "document_type": self.document_type,
            "category": self.category,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class MarketingKnowledgeBase:
    """Marketing domain knowledge base with RAG capabilities."""
    
    def __init__(self, 
                 chroma_path: str = "./data/knowledge_db",
                 embedding_model: str = "all-MiniLM-L6-v2"):
        self.chroma_path = Path(chroma_path)
        self.chroma_path.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=str(self.chroma_path))
        self.collection = self.client.get_or_create_collection("marketing_knowledge")
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Initialize with default marketing knowledge
        asyncio.create_task(self._initialize_default_knowledge())
    
    async def _initialize_default_knowledge(self):
        """Initialize with marketing best practices and templates."""
        if self.collection.count() == 0:
            await self._load_default_knowledge()
    
    async def _load_default_knowledge(self):
        """Load default marketing knowledge base."""
        default_knowledge = [
            {
                "title": "Email Subject Line Best Practices",
                "content": """
                Effective email subject lines:
                - Keep under 50 characters for mobile optimization
                - Use personalization tokens (name, company)
                - Create urgency without being spammy
                - A/B test different approaches
                - Avoid spam trigger words (FREE, URGENT, GUARANTEED)
                - Use numbers and specific benefits
                - Ask questions to increase engagement
                - Examples: "Quick question about [Company]", "5 ways to improve [specific metric]"
                """,
                "document_type": "best_practice",
                "category": "email_marketing",
                "tags": ["subject_lines", "email", "personalization"]
            },
            {
                "title": "Lead Qualification Framework (BANT)",
                "content": """
                BANT qualification criteria:
                - Budget: Does the prospect have allocated budget?
                - Authority: Are you speaking with the decision maker?
                - Need: Is there a genuine business need?
                - Timeline: When do they plan to make a decision?
                
                Modern alternatives include MEDDIC, SPICED, and GPCTBA/C&I.
                Use discovery questions to uncover these elements naturally.
                """,
                "document_type": "guide",
                "category": "lead_qualification", 
                "tags": ["BANT", "qualification", "discovery"]
            },
            {
                "title": "B2B Personalization Strategies",
                "content": """
                Effective B2B personalization approaches:
                - Company-specific research: Recent news, funding, expansions
                - Technology stack personalization: Reference their current tools
                - Industry-specific pain points: Common challenges in their sector
                - Role-based messaging: Tailor to their specific job function
                - Mutual connections: Leverage LinkedIn networks
                - Recent company triggers: Job postings, press releases, events
                
                Tools: Apollo for data, BuiltWith for tech stack, NewsAPI for triggers.
                """,
                "document_type": "template",
                "category": "personalization",
                "tags": ["B2B", "personalization", "research"]
            },
            {
                "title": "ICP Development Framework",
                "content": """
                Ideal Customer Profile (ICP) development process:
                1. Analyze best customers: Revenue, retention, satisfaction
                2. Identify firmographic data: Company size, industry, location
                3. Determine technographic data: Current tools and tech stack
                4. Map behavioral patterns: Buying process, decision timeline
                5. Define pain points: Specific challenges they face
                6. Validate with data: Use analytics to confirm assumptions
                
                Key metrics: Customer lifetime value, time to close, churn rate.
                """,
                "document_type": "guide", 
                "category": "target_audience",
                "tags": ["ICP", "targeting", "segmentation"]
            },
            {
                "title": "Multi-touch Campaign Sequences",
                "content": """
                Effective multi-touch campaign structure:
                
                Touch 1: Introduction + Value proposition
                Touch 2: Social proof + case study (3-5 days later)
                Touch 3: Educational content + insights (1 week later)
                Touch 4: Specific offer + CTA (1 week later)
                Touch 5: Breakup email + final value (2 weeks later)
                
                Channel mix: Email primary, LinkedIn secondary, phone for high-value prospects.
                Personalize each touch based on engagement with previous messages.
                """,
                "document_type": "template",
                "category": "campaign_sequence",
                "tags": ["sequences", "multi-touch", "cadence"]
            }
        ]
        
        for knowledge_item in default_knowledge:
            await self.add_knowledge(
                title=knowledge_item["title"],
                content=knowledge_item["content"],
                document_type=knowledge_item["document_type"],
                category=knowledge_item["category"],
                tags=knowledge_item["tags"]
            )
    
    async def add_knowledge(self,
                          title: str,
                          content: str,
                          document_type: str,
                          category: str,
                          tags: List[str],
                          metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add knowledge document to the knowledge base."""
        doc_id = hashlib.md5(f"{title}_{content}".encode()).hexdigest()
        
        document = KnowledgeDocument(
            id=doc_id,
            title=title,
            content=content,
            document_type=document_type,
            category=category,
            tags=tags,
            metadata=metadata or {},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(f"{title} {content}").tolist()
            
            # Store in ChromaDB
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                metadatas=[{
                    "title": title,
                    "document_type": document_type,
                    "category": category,
                    "tags": ",".join(tags),
                    "created_at": document.created_at.isoformat()
                }],
                documents=[content]
            )
            
            logger.info(f"Added knowledge document: {title}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to add knowledge: {e}")
            raise
    
    async def search_knowledge(self,
                             query: str,
                             category: Optional[str] = None,
                             document_type: Optional[str] = None,
                             limit: int = 5) -> List[Dict[str, Any]]:
        """Search knowledge base using semantic similarity."""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Build where clause
            where_clause = {}
            if category:
                where_clause["category"] = category
            if document_type:
                where_clause["document_type"] = document_type
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause if where_clause else None
            )
            
            knowledge_results = []
            if results["ids"] and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    metadata = results["metadatas"][0][i]
                    content = results["documents"][0][i]
                    distance = results["distances"][0][i] if "distances" in results else 0
                    
                    knowledge_results.append({
                        "id": doc_id,
                        "title": metadata["title"],
                        "content": content,
                        "document_type": metadata["document_type"],
                        "category": metadata["category"],
                        "tags": metadata["tags"].split(",") if metadata["tags"] else [],
                        "relevance_score": 1 - distance,  # Convert distance to similarity
                        "created_at": metadata["created_at"]
                    })
            
            return knowledge_results
            
        except Exception as e:
            logger.error(f"Failed to search knowledge: {e}")
            return []
    
    async def get_knowledge_by_category(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get all knowledge documents for a specific category."""
        return await self.search_knowledge("", category=category, limit=limit)
    
    async def get_best_practices(self, topic: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Get best practices for a specific topic."""
        return await self.search_knowledge(
            query=topic,
            document_type="best_practice",
            limit=limit
        )
    
    async def get_templates(self, category: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get templates for a specific category."""
        return await self.search_knowledge(
            query="",
            category=category,
            document_type="template",
            limit=limit
        )
    
    async def add_campaign_learnings(self,
                                   campaign_type: str,
                                   what_worked: List[str],
                                   what_didnt_work: List[str],
                                   metrics: Dict[str, Any],
                                   recommendations: List[str]) -> str:
        """Add learnings from a completed campaign."""
        content = f"""
        Campaign Learnings - {campaign_type}
        
        What Worked:
        {chr(10).join(f"- {item}" for item in what_worked)}
        
        What Didn't Work:
        {chr(10).join(f"- {item}" for item in what_didnt_work)}
        
        Key Metrics:
        {chr(10).join(f"- {k}: {v}" for k, v in metrics.items())}
        
        Recommendations for Future:
        {chr(10).join(f"- {item}" for item in recommendations)}
        """
        
        return await self.add_knowledge(
            title=f"Campaign Learnings: {campaign_type}",
            content=content,
            document_type="case_study",
            category="campaign_learnings",
            tags=["learnings", campaign_type, "metrics"],
            metadata={
                "campaign_type": campaign_type,
                "metrics": metrics,
                "success_factors": what_worked,
                "failure_factors": what_didnt_work
            }
        )


class RAGKnowledgeRetriever:
    """Retrieval-Augmented Generation knowledge retriever for agents."""
    
    def __init__(self, knowledge_base: MarketingKnowledgeBase):
        self.knowledge_base = knowledge_base
        self.settings = get_settings()
    
    async def get_context_for_query(self,
                                  query: str,
                                  context_type: str = "general",
                                  max_context_length: int = 2000) -> str:
        """Get relevant knowledge context for a query."""
        try:
            # Search for relevant knowledge
            knowledge_results = await self.knowledge_base.search_knowledge(
                query=query,
                limit=3
            )
            
            if not knowledge_results:
                return "No relevant knowledge found."
            
            # Build context string
            context_parts = []
            current_length = 0
            
            for result in knowledge_results:
                content_preview = result["content"][:500] + "..." if len(result["content"]) > 500 else result["content"]
                part = f"**{result['title']}** ({result['category']}):\n{content_preview}\n"
                
                if current_length + len(part) > max_context_length:
                    break
                
                context_parts.append(part)
                current_length += len(part)
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Failed to get context: {e}")
            return "Error retrieving knowledge context."
    
    async def get_best_practice_guidance(self, topic: str) -> str:
        """Get best practice guidance for a specific topic."""
        best_practices = await self.knowledge_base.get_best_practices(topic)
        
        if not best_practices:
            return f"No specific best practices found for {topic}."
        
        guidance_parts = []
        for practice in best_practices:
            guidance_parts.append(f"**{practice['title']}**:\n{practice['content'][:300]}...")
        
        return "\n\n".join(guidance_parts)
    
    async def get_template_suggestions(self, category: str) -> List[Dict[str, str]]:
        """Get template suggestions for a category."""
        templates = await self.knowledge_base.get_templates(category)
        
        return [
            {
                "title": template["title"],
                "content": template["content"],
                "tags": template["tags"]
            }
            for template in templates
        ]
    
    async def enhance_prompt_with_knowledge(self,
                                          base_prompt: str,
                                          knowledge_query: str,
                                          max_knowledge_tokens: int = 1000) -> str:
        """Enhance a prompt with relevant knowledge context."""
        knowledge_context = await self.get_context_for_query(
            query=knowledge_query,
            max_context_length=max_knowledge_tokens
        )
        
        enhanced_prompt = f"""
{base_prompt}

**Relevant Knowledge Context:**
{knowledge_context}

Use the above knowledge context to inform your response while maintaining accuracy and relevance.
"""
        return enhanced_prompt


class AgnoKnowledgeIntegration(Knowledge):
    """Integration with Agno's native knowledge system."""
    
    def __init__(self, knowledge_base: MarketingKnowledgeBase):
        super().__init__()
        self.knowledge_base = knowledge_base
        self.rag_retriever = RAGKnowledgeRetriever(knowledge_base)
    
    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search knowledge base (implements Agno Knowledge interface)."""
        return await self.knowledge_base.search_knowledge(query, limit=limit)
    
    async def get_context(self, query: str) -> str:
        """Get knowledge context for a query."""
        return await self.rag_retriever.get_context_for_query(query)
    
    async def add_document(self, title: str, content: str, metadata: Dict[str, Any]) -> str:
        """Add a document to the knowledge base."""
        return await self.knowledge_base.add_knowledge(
            title=title,
            content=content,
            document_type=metadata.get("document_type", "guide"),
            category=metadata.get("category", "general"),
            tags=metadata.get("tags", []),
            metadata=metadata
        )


# Global knowledge components
marketing_knowledge_base = MarketingKnowledgeBase()
rag_retriever = RAGKnowledgeRetriever(marketing_knowledge_base)
agno_knowledge = AgnoKnowledgeIntegration(marketing_knowledge_base)