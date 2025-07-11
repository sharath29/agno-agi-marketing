"""
Marketing Expert Agent for Agno-AGI Marketing Automation.

A sophisticated agent that provides marketing strategy, campaign planning,
personalization guidance, and leverages the full marketing knowledge base.
"""

from typing import Dict, List, Optional, Any
from agno import Agent
from agno.models.openai import OpenAIChat
from loguru import logger

from ..memory.agno_memory import create_agent_memory, MemoryEnhancedAgent
from ..knowledge.knowledge_manager import agno_knowledge
from ..knowledge.utils import (
    get_marketing_guidance,
    get_personalization_strategies,
    get_campaign_best_practices,
    enhance_agent_prompt
)
from ..config.settings import get_settings
from ..config.logging import get_agent_logger


class MarketingExpert(Agent, MemoryEnhancedAgent):
    """
    Expert marketing agent specializing in campaign strategy, personalization,
    and marketing automation best practices.
    """
    
    def __init__(self):
        settings = get_settings()
        
        # Initialize enhanced memory and knowledge
        super().__init__(
            name="MarketingExpert",
            model=OpenAIChat(
                id=settings.llm.default_model_id,
                api_key=settings.llm.openai_api_key
            ),
            description="""
            I am a senior marketing strategist with deep expertise in B2B marketing automation,
            personalization, and campaign optimization. I help create data-driven marketing 
            strategies that generate qualified leads and drive revenue growth.
            
            My specialties include:
            - Campaign strategy and planning
            - Personalization and targeting
            - Message optimization and A/B testing
            - Marketing automation workflows
            - Lead nurturing sequences
            - Performance analysis and optimization
            """,
            instructions="""
            You are a senior marketing expert with 10+ years of experience in B2B marketing.
            
            Always:
            - Provide data-driven recommendations based on best practices
            - Consider the target audience and personalization opportunities
            - Suggest A/B testing strategies for optimization
            - Reference specific metrics and KPIs for success measurement
            - Incorporate current marketing trends and technologies
            - Use the knowledge base to enhance your recommendations
            
            When asked about campaigns:
            1. First understand the goal and target audience
            2. Research relevant best practices from the knowledge base
            3. Provide specific, actionable recommendations
            4. Include measurement and optimization strategies
            5. Consider multi-channel approaches when appropriate
            
            Always maintain a strategic perspective while being practical and actionable.
            """,
            knowledge=agno_knowledge,
            memory=create_agent_memory("MarketingExpert"),
            show_tool_calls=True,
            markdown=True
        )
        
        self.logger = get_agent_logger("MarketingExpert")
        self.settings = settings
    
    async def create_campaign_strategy(self,
                                     campaign_goal: str,
                                     target_audience: str,
                                     budget: Optional[str] = None,
                                     timeline: Optional[str] = None,
                                     industry: Optional[str] = None) -> Dict[str, Any]:
        """Create a comprehensive campaign strategy."""
        self.logger.info(f"Creating campaign strategy for goal: {campaign_goal}")
        
        # Get relevant knowledge and best practices
        knowledge_context = f"campaign strategy {campaign_goal} {industry or ''}"
        best_practices = await get_campaign_best_practices(campaign_goal)
        
        # Build enhanced prompt
        base_prompt = f"""
        Create a comprehensive campaign strategy with the following requirements:
        
        Campaign Goal: {campaign_goal}
        Target Audience: {target_audience}
        Budget: {budget or 'Not specified'}
        Timeline: {timeline or 'Not specified'}
        Industry: {industry or 'Not specified'}
        
        Please provide:
        1. Campaign overview and key objectives
        2. Target audience analysis and segmentation
        3. Channel strategy and mix
        4. Content and messaging approach
        5. Timeline and milestones
        6. Budget allocation recommendations
        7. KPIs and success metrics
        8. Risk assessment and mitigation strategies
        """
        
        enhanced_prompt = await enhance_agent_prompt(base_prompt, knowledge_context)
        
        try:
            response = self.run(enhanced_prompt)
            
            # Remember this interaction
            await self.remember_interaction(
                user_input=f"Campaign strategy request: {campaign_goal}",
                response=response.content,
                context={
                    "campaign_goal": campaign_goal,
                    "target_audience": target_audience,
                    "budget": budget,
                    "timeline": timeline,
                    "industry": industry
                }
            )
            
            return {
                "strategy": response.content,
                "campaign_goal": campaign_goal,
                "target_audience": target_audience,
                "best_practices_used": best_practices[:500] + "..." if len(best_practices) > 500 else best_practices
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create campaign strategy: {e}")
            return {"error": str(e)}
    
    async def optimize_email_subject_lines(self,
                                         current_subject: str,
                                         target_audience: str,
                                         email_content_type: str) -> Dict[str, Any]:
        """Optimize email subject lines for better open rates."""
        self.logger.info("Optimizing email subject lines")
        
        # Get subject line best practices
        subject_guidance = await get_marketing_guidance("email subject lines")
        
        prompt = f"""
        Optimize this email subject line for better open rates:
        
        Current Subject: "{current_subject}"
        Target Audience: {target_audience}
        Email Type: {email_content_type}
        
        Best Practices Context:
        {subject_guidance}
        
        Please provide:
        1. Analysis of the current subject line (strengths/weaknesses)
        2. 5 improved subject line variations
        3. A/B testing recommendations
        4. Personalization opportunities
        5. Expected impact on open rates
        
        Focus on mobile optimization, personalization, and avoiding spam triggers.
        """
        
        try:
            response = self.run(prompt)
            
            await self.remember_interaction(
                user_input=f"Subject line optimization: {current_subject}",
                response=response.content,
                context={
                    "original_subject": current_subject,
                    "target_audience": target_audience,
                    "content_type": email_content_type
                }
            )
            
            return {
                "optimization": response.content,
                "original_subject": current_subject,
                "guidance_used": subject_guidance[:300] + "..."
            }
            
        except Exception as e:
            self.logger.error(f"Failed to optimize subject lines: {e}")
            return {"error": str(e)}
    
    async def create_personalization_strategy(self,
                                            target_company: str,
                                            contact_info: Dict[str, Any],
                                            research_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a personalization strategy for a specific prospect."""
        self.logger.info(f"Creating personalization strategy for {target_company}")
        
        # Get personalization strategies
        personalization_guide = await get_personalization_strategies()
        
        # Build context
        research_context = ""
        if research_data:
            research_context = f"""
            Available Research Data:
            - Company: {research_data.get('company_info', 'N/A')}
            - Technology Stack: {research_data.get('technologies', 'N/A')}
            - Recent News: {research_data.get('news', 'N/A')}
            - Funding: {research_data.get('funding', 'N/A')}
            """
        
        prompt = f"""
        Create a personalization strategy for this prospect:
        
        Company: {target_company}
        Contact: {contact_info.get('name', 'N/A')} - {contact_info.get('title', 'N/A')}
        Email: {contact_info.get('email', 'N/A')}
        
        {research_context}
        
        Personalization Best Practices:
        {personalization_guide}
        
        Please provide:
        1. Key personalization angles based on available data
        2. Specific message customization recommendations
        3. Research gaps that should be filled
        4. Channel-specific personalization strategies
        5. Follow-up personalization ideas
        6. Recommended timing and triggers
        
        Focus on genuine value and relevance, not just name insertion.
        """
        
        try:
            response = self.run(prompt)
            
            await self.remember_interaction(
                user_input=f"Personalization strategy for {target_company}",
                response=response.content,
                context={
                    "target_company": target_company,
                    "contact_info": contact_info,
                    "research_available": bool(research_data)
                }
            )
            
            return {
                "personalization_strategy": response.content,
                "target_company": target_company,
                "contact_info": contact_info,
                "research_used": bool(research_data)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create personalization strategy: {e}")
            return {"error": str(e)}
    
    async def analyze_campaign_performance(self,
                                         campaign_metrics: Dict[str, Any],
                                         campaign_type: str,
                                         target_metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze campaign performance and provide optimization recommendations."""
        self.logger.info(f"Analyzing {campaign_type} campaign performance")
        
        # Get campaign best practices for comparison
        campaign_guidance = await get_campaign_best_practices(campaign_type)
        
        # Get historical insights
        campaign_wisdom = await self.get_campaign_wisdom(campaign_type)
        
        prompt = f"""
        Analyze this campaign performance and provide optimization recommendations:
        
        Campaign Type: {campaign_type}
        
        Current Metrics:
        {chr(10).join(f"- {k}: {v}" for k, v in campaign_metrics.items())}
        
        Target Metrics: {target_metrics or 'Not specified'}
        
        Best Practices Context:
        {campaign_guidance}
        
        Historical Insights:
        {campaign_wisdom}
        
        Please provide:
        1. Performance analysis (what's working/not working)
        2. Comparison to industry benchmarks
        3. Specific optimization recommendations
        4. Priority areas for improvement
        5. A/B testing suggestions
        6. Resource allocation recommendations
        7. Timeline for implementing changes
        
        Focus on actionable insights that can drive immediate improvements.
        """
        
        try:
            response = self.run(prompt)
            
            # Learn from this campaign analysis
            if campaign_metrics.get('success_rate', 0) > 0.1:  # Consider successful if >10%
                lessons = [
                    f"Campaign type {campaign_type} achieved {campaign_metrics.get('success_rate', 0)*100:.1f}% success rate",
                    "Performance analysis completed with actionable recommendations"
                ]
                await self.learn_from_campaign(
                    campaign_id=f"analysis_{campaign_type}_{hash(str(campaign_metrics))}",
                    campaign_type=campaign_type,
                    metrics=campaign_metrics,
                    lessons=lessons
                )
            
            await self.remember_interaction(
                user_input=f"Campaign performance analysis: {campaign_type}",
                response=response.content,
                context={
                    "campaign_type": campaign_type,
                    "metrics": campaign_metrics,
                    "target_metrics": target_metrics
                }
            )
            
            return {
                "analysis": response.content,
                "campaign_type": campaign_type,
                "metrics_analyzed": campaign_metrics,
                "historical_context": campaign_wisdom[:200] + "..."
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze campaign performance: {e}")
            return {"error": str(e)}
    
    async def create_multi_touch_sequence(self,
                                        campaign_goal: str,
                                        target_persona: str,
                                        sequence_length: int = 5,
                                        channels: List[str] = None) -> Dict[str, Any]:
        """Create a multi-touch campaign sequence."""
        self.logger.info(f"Creating {sequence_length}-touch sequence for {campaign_goal}")
        
        channels = channels or ["email", "linkedin"]
        sequence_guidance = await get_marketing_guidance("multi-touch sequences")
        
        prompt = f"""
        Create a multi-touch campaign sequence with these specifications:
        
        Campaign Goal: {campaign_goal}
        Target Persona: {target_persona}
        Number of Touches: {sequence_length}
        Channels: {', '.join(channels)}
        
        Sequence Best Practices:
        {sequence_guidance}
        
        Please provide:
        1. Complete sequence overview and strategy
        2. Touch-by-touch breakdown with:
           - Touch number and timing
           - Channel selection rationale
           - Message theme and key points
           - Call-to-action strategy
           - Personalization opportunities
        3. Sequence flow logic and decision points
        4. Success metrics for each touch
        5. Optimization and testing recommendations
        6. Breakup email strategy
        
        Ensure progressive value delivery and avoid being pushy or repetitive.
        """
        
        try:
            response = self.run(prompt)
            
            await self.remember_interaction(
                user_input=f"Multi-touch sequence: {campaign_goal}",
                response=response.content,
                context={
                    "campaign_goal": campaign_goal,
                    "target_persona": target_persona,
                    "sequence_length": sequence_length,
                    "channels": channels
                }
            )
            
            return {
                "sequence": response.content,
                "campaign_goal": campaign_goal,
                "target_persona": target_persona,
                "channels": channels,
                "sequence_length": sequence_length
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create multi-touch sequence: {e}")
            return {"error": str(e)}
    
    async def get_marketing_insights(self, topic: str) -> Dict[str, Any]:
        """Get marketing insights and recommendations for a specific topic."""
        self.logger.info(f"Providing marketing insights for: {topic}")
        
        # Get relevant knowledge
        insights = await get_marketing_guidance(topic)
        context = await self.get_conversation_context()
        
        prompt = f"""
        Provide comprehensive marketing insights and actionable recommendations for: {topic}
        
        Context from our conversation:
        {context}
        
        Relevant Knowledge:
        {insights}
        
        Please provide:
        1. Current best practices and trends
        2. Actionable recommendations
        3. Common pitfalls to avoid
        4. Success metrics to track
        5. Tools and technologies to consider
        6. Implementation timeline suggestions
        
        Be specific and practical in your recommendations.
        """
        
        try:
            response = self.run(prompt)
            
            await self.remember_interaction(
                user_input=f"Marketing insights request: {topic}",
                response=response.content,
                context={"topic": topic, "insights_type": "general"}
            )
            
            return {
                "insights": response.content,
                "topic": topic,
                "knowledge_base_used": bool(insights)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to provide marketing insights: {e}")
            return {"error": str(e)}


# Factory function to create marketing expert
def create_marketing_expert() -> MarketingExpert:
    """Create and return a MarketingExpert agent instance."""
    return MarketingExpert()