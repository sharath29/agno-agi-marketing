"""
Demo script for Agno-AGI Marketing Automation System.

Demonstrates the key capabilities of the marketing automation system
including agents, toolkits, memory, and knowledge integration.
"""

import asyncio

from loguru import logger

from config.settings import get_missing_apis, get_settings

from .agents.marketing_expert import create_marketing_expert
from .toolkits.apollo_toolkit import ApolloToolkit
from .toolkits.builtwith_toolkit import BuiltWithToolkit
from .toolkits.hubspot_toolkit import HubSpotToolkit


async def demo_marketing_expert():
    """Demonstrate the Marketing Expert agent capabilities."""
    print("\n🚀 Agno-AGI Marketing Automation Demo")
    print("=" * 50)

    # Check configuration
    get_settings()
    missing_apis = get_missing_apis()

    if missing_apis:
        print(f"⚠️  Missing API configurations: {', '.join(missing_apis)}")
        print("Some features may not work without proper API keys.\n")
    else:
        print("✅ All API configurations found!\n")

    # Create marketing expert
    print("1. Creating Marketing Expert Agent...")
    marketing_expert = create_marketing_expert()
    print("✅ Marketing Expert ready!\n")

    # Demo 1: Campaign Strategy
    print("2. Demo: Campaign Strategy Creation")
    print("-" * 35)

    strategy_result = await marketing_expert.create_campaign_strategy(
        campaign_goal="Generate qualified B2B leads for SaaS product",
        target_audience="Mid-market companies (100-1000 employees) in technology sector",
        budget="$50,000/month",
        timeline="Q1 2024 (3 months)",
        industry="Technology",
    )

    if "error" not in strategy_result:
        print("✅ Campaign strategy created successfully!")
        print(f"Preview: {strategy_result['strategy'][:200]}...\n")
    else:
        print(f"❌ Error: {strategy_result['error']}\n")

    # Demo 2: Email Subject Line Optimization
    print("3. Demo: Email Subject Line Optimization")
    print("-" * 40)

    subject_result = await marketing_expert.optimize_email_subject_lines(
        current_subject="New product announcement",
        target_audience="CTOs and VPs of Engineering",
        email_content_type="product_announcement",
    )

    if "error" not in subject_result:
        print("✅ Subject line optimized!")
        print(f"Preview: {subject_result['optimization'][:200]}...\n")
    else:
        print(f"❌ Error: {subject_result['error']}\n")

    # Demo 3: Personalization Strategy
    print("4. Demo: Personalization Strategy")
    print("-" * 35)

    personalization_result = await marketing_expert.create_personalization_strategy(
        target_company="TechCorp Inc",
        contact_info={
            "name": "John Smith",
            "title": "VP of Engineering",
            "email": "john@techcorp.com",
        },
        research_data={
            "company_info": "Fast-growing SaaS company, recently raised Series B",
            "technologies": ["React", "Node.js", "AWS", "Docker"],
            "news": "Expanding engineering team, focusing on platform scalability",
        },
    )

    if "error" not in personalization_result:
        print("✅ Personalization strategy created!")
        print(f"Preview: {personalization_result['personalization_strategy'][:200]}...\n")
    else:
        print(f"❌ Error: {personalization_result['error']}\n")

    # Demo 4: Multi-touch Sequence
    print("5. Demo: Multi-touch Campaign Sequence")
    print("-" * 38)

    sequence_result = await marketing_expert.create_multi_touch_sequence(
        campaign_goal="Schedule product demos",
        target_persona="Engineering leaders at mid-market tech companies",
        sequence_length=5,
        channels=["email", "linkedin"],
    )

    if "error" not in sequence_result:
        print("✅ Multi-touch sequence created!")
        print(f"Preview: {sequence_result['sequence'][:200]}...\n")
    else:
        print(f"❌ Error: {sequence_result['error']}\n")

    print("🎉 Demo completed! The Marketing Expert agent successfully demonstrated:")
    print("   • Campaign strategy development")
    print("   • Email optimization")
    print("   • Personalization strategies")
    print("   • Multi-touch sequence creation")
    print("   • Integration with knowledge base and memory systems")


async def demo_toolkits():
    """Demonstrate the toolkit capabilities (if API keys are configured)."""
    print("\n🔧 Toolkit Capabilities Demo")
    print("=" * 30)

    settings = get_settings()

    # Demo Apollo Toolkit
    if settings.marketing_apis.apollo_api_key:
        print("1. Apollo Toolkit Demo")
        print("-" * 20)
        apollo = ApolloToolkit()

        # Search for people
        people_result = apollo.search_people(
            query="VP Engineering", company_names=["Microsoft", "Google"], per_page=5
        )
        print(f"✅ Found {len(people_result.get('contacts', []))} contacts")
    else:
        print("⏭️  Skipping Apollo demo (API key not configured)")

    # Demo BuiltWith Toolkit
    if settings.marketing_apis.builtwith_api_key:
        print("\n2. BuiltWith Toolkit Demo")
        print("-" * 22)
        builtwith = BuiltWithToolkit()

        # Get domain technologies
        tech_result = builtwith.get_domain_technologies("example.com")
        print(f"✅ Found {tech_result.get('total_technologies', 0)} technologies")
    else:
        print("\n⏭️  Skipping BuiltWith demo (API key not configured)")

    # Demo HubSpot Toolkit
    if settings.marketing_apis.hubspot_api_key:
        print("\n3. HubSpot Toolkit Demo")
        print("-" * 21)
        hubspot = HubSpotToolkit()

        # Search contacts
        contacts_result = hubspot.search_contacts(query="test", limit=5)
        print(f"✅ Found {len(contacts_result.get('contacts', []))} contacts")
    else:
        print("\n⏭️  Skipping HubSpot demo (API key not configured)")


async def main():
    """Main demo function."""
    try:
        # Run marketing expert demo
        await demo_marketing_expert()

        # Run toolkit demo if APIs are configured
        settings = get_settings()
        if any(
            [
                settings.marketing_apis.apollo_api_key,
                settings.marketing_apis.builtwith_api_key,
                settings.marketing_apis.hubspot_api_key,
            ]
        ):
            await demo_toolkits()
        else:
            print("\n⏭️  Skipping toolkit demos (no API keys configured)")
            print("   To see toolkit demos, configure API keys in .env file")

        print("\n" + "=" * 60)
        print("🎯 Next Steps:")
        print("1. Configure API keys in .env file for full functionality")
        print("2. Explore src/agents/ for more specialized agents")
        print("3. Check src/workflows/ for campaign automation")
        print("4. Review src/knowledge/ for knowledge management")
        print("5. See src/memory/ for conversation and campaign memory")
        print("=" * 60)

    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n❌ Demo failed: {e}")
        print("Check your configuration and try again.")


if __name__ == "__main__":
    asyncio.run(main())
