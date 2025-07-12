# Agno-AGI Marketing Automation System

A sophisticated multi-agent marketing automation system built with the [Agno framework](https://docs.agno.com), designed to solve top-of-funnel marketing problems through intelligent agent coordination, advanced memory management, and knowledge-augmented decision making.

## 🚀 Key Features

### 🤖 Intelligent Agent Architecture
- **Marketing Expert**: Strategy development, campaign optimization, personalization
- **Company Expert**: ICP validation, compliance rules, lead scoring
- **Resource Agent**: Multi-source lead harvesting and enrichment
- **CRM Agent**: Data hygiene, deduplication, pipeline management
- **Search Agent**: Real-time signal gathering and trend analysis
- **Campaign Director**: Workflow orchestration and quality control

### 🔧 Comprehensive Toolkit Integration
- **Apollo.io**: Lead enrichment and contact search
- **BuiltWith**: Technology stack analysis and competitor research
- **HubSpot**: CRM operations and marketing automation
- **Salesforce**: Advanced CRM integration and opportunity management
- **NewsAPI & Twitter**: Real-time signals and market intelligence
- **LinkedIn & Web Scrapers**: Social media and web intelligence

### 🧠 Advanced Memory & Knowledge Systems
- **Multi-layer Memory**: Short-term conversation, long-term campaign, vector semantic memory
- **RAG Knowledge Base**: Marketing best practices, templates, and domain expertise
- **Campaign Learning**: Automatic capture and reuse of successful patterns
- **Context Management**: Intelligent summarization and progressive context building

### 🔄 Production-Ready Features
- **Workflow Export**: Serialize workflows to Airflow/Temporal DAGs
- **Rate Limiting**: Built-in API quota management and error handling
- **Monitoring**: Comprehensive logging, metrics, and observability
- **Security**: Encrypted credentials and secure API handling

## 📁 Project Structure

```
agentic-marketing/
├── src/
│   ├── agents/              # Agent definitions
│   │   ├── marketing_expert.py
│   │   ├── company_expert.py
│   │   └── resource_agent.py
│   ├── toolkits/            # Custom API toolkits
│   │   ├── apollo_toolkit.py
│   │   ├── builtwith_toolkit.py
│   │   ├── hubspot_toolkit.py
│   │   └── salesforce_toolkit.py
│   ├── workflows/           # Campaign workflows
│   ├── memory/              # Memory management
│   │   ├── memory_manager.py
│   │   └── agno_memory.py
│   ├── knowledge/           # Knowledge management
│   │   ├── knowledge_manager.py
│   │   └── utils.py
│   ├── orchestrator/        # Main orchestration
│   └── config/              # Configuration
│       ├── settings.py
│       └── logging.py
├── config/                  # Configuration files
├── data/                    # Sample data & schemas
├── docs/                    # Documentation
├── tests/                   # Test suites
├── requirements.txt         # Dependencies
├── .env.example            # Environment template
├── main.py                 # Main entry point
└── README.md              # This file
```

## 🛠️ Installation & Setup

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd agentic-marketing
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the environment template and fill in your API keys:

```bash
cp .env.example .env
# Edit .env with your API keys
```

Required API keys:
- **OpenAI or Anthropic**: For LLM capabilities
- **Apollo.io**: For lead enrichment
- **BuiltWith**: For technology analysis
- **HubSpot**: For CRM integration
- **NewsAPI**: For market signals
- **Twitter**: For social intelligence

### 3. Run the Demo

```bash
python main.py
```

This will run a comprehensive demo showcasing all system capabilities.

## 🎯 Quick Start Examples

### Marketing Expert Agent

```python
from src.agents.marketing_expert import create_marketing_expert

# Create marketing expert
expert = create_marketing_expert()

# Generate campaign strategy
strategy = await expert.create_campaign_strategy(
    campaign_goal="Generate qualified B2B leads",
    target_audience="Mid-market tech companies",
    budget="$50K/month",
    timeline="Q1 2024"
)

# Optimize email subject lines
optimization = await expert.optimize_email_subject_lines(
    current_subject="Product Update",
    target_audience="Engineering leaders",
    email_content_type="product_announcement"
)

# Create personalization strategy
personalization = await expert.create_personalization_strategy(
    target_company="TechCorp",
    contact_info={"name": "John Smith", "title": "VP Engineering"},
    research_data={"technologies": ["React", "AWS"], "recent_news": "Series B funding"}
)
```

### Toolkit Usage

```python
from src.toolkits.apollo_toolkit import ApolloToolkit
from src.toolkits.builtwith_toolkit import BuiltWithToolkit

# Apollo lead search
apollo = ApolloToolkit()
contacts = apollo.search_people(
    titles=["VP Engineering", "CTO"],
    company_names=["Microsoft", "Google"],
    per_page=10
)

# BuiltWith technology analysis
builtwith = BuiltWithToolkit()
tech_stack = builtwith.get_domain_technologies("example.com")
```

### Knowledge Integration

```python
from src.knowledge.utils import get_marketing_guidance, get_campaign_best_practices

# Get marketing guidance
guidance = await get_marketing_guidance("email personalization")

# Get campaign best practices
practices = await get_campaign_best_practices("lead generation")
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# LLM Configuration
OPENAI_API_KEY=your_openai_key
DEFAULT_MODEL_ID=gpt-4o-mini
MAX_CONTEXT_LENGTH=8000

# Marketing APIs
APOLLO_API_KEY=your_apollo_key
HUBSPOT_API_KEY=your_hubspot_key
SALESFORCE_USERNAME=your_sf_username

# Memory & Knowledge
MEMORY_PROVIDER=redis
VECTOR_STORE_PROVIDER=chroma
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Database
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379/0
```

### Memory Configuration

The system supports multiple memory providers:

- **Redis**: For fast short-term memory
- **SQLite**: For persistent local storage
- **ChromaDB**: For vector-based semantic memory

### Knowledge Management

Built-in marketing knowledge includes:
- Email marketing best practices
- Lead qualification frameworks (BANT, MEDDIC)
- B2B personalization strategies
- Campaign sequence templates
- ICP development guides

## 🚀 Advanced Usage

### Custom Agents

Create specialized agents by extending the base classes:

```python
from src.agents.marketing_expert import MarketingExpert
from src.memory.agno_memory import MemoryEnhancedAgent

class CustomAgent(MarketingExpert, MemoryEnhancedAgent):
    def __init__(self):
        super().__init__()
        # Add custom functionality
```

### Workflow Orchestration

```python
from agno.workflow import Workflow
from src.agents.marketing_expert import create_marketing_expert

# Create workflow
workflow = Workflow(name="LeadGenCampaign")

# Add agents and steps
marketing_expert = create_marketing_expert()
workflow.add_steps([
    Step("strategy", agent=marketing_expert),
    Step("personalization", agent=marketing_expert),
    Step("execution", agent=crm_agent)
])

# Run workflow
workflow.run()
```

### Production Deployment

Export workflows for production systems:

```python
# Export to DAG format
dag_definition = workflow.to_dag()
dag_definition.save("production_campaign.yaml")

# Import in Airflow/Temporal
```

## 📊 Monitoring & Observability

### Logging

Structured logging with multiple levels:
- **Agent actions**: Decision making and tool usage
- **API calls**: Performance and rate limiting
- **Campaign metrics**: Success rates and optimization
- **Error tracking**: Comprehensive error handling

### Performance Metrics

Key metrics tracked:
- Agent response times
- API call success rates
- Memory usage and efficiency
- Knowledge retrieval accuracy
- Campaign conversion rates

## 🔒 Security

### API Key Management
- Environment-based configuration
- Encrypted storage options
- Rate limiting and quota management

### Data Privacy
- No sensitive data in logs
- Configurable data retention
- GDPR compliance features

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

Test categories:
- Unit tests for individual components
- Integration tests for toolkit functionality
- Agent behavior tests
- Memory and knowledge system tests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📖 Documentation

- **API Reference**: Detailed toolkit and agent APIs
- **Best Practices**: Marketing automation guidelines
- **Troubleshooting**: Common issues and solutions
- **Examples**: Real-world usage scenarios

## 🚀 Roadmap

### Phase 2 Features
- Additional CRM integrations (Pipedrive, Zoho)
- Advanced AI personalization
- Multi-language support
- Enhanced analytics dashboard

### Phase 3 Features
- Predictive lead scoring
- Automated A/B testing
- Advanced workflow triggers
- Enterprise security features

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

- **Documentation**: [Agno Documentation](https://docs.agno.com)
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Email**: support@example.com

---

**Built with ❤️ using the [Agno framework](https://docs.agno.com) for production-ready AI agent systems.**
