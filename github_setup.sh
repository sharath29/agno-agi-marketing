#!/bin/bash

# GitHub Setup Script for Agno-AGI Marketing Automation System
echo "🚀 Setting up GitHub repository and issues..."

# Check if gh is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ GitHub CLI not authenticated. Please run:"
    echo "   gh auth login"
    echo "   Then run this script again."
    exit 1
fi

# Create the repository
echo "📁 Creating GitHub repository..."
gh repo create agno-agi-marketing --public --description "Intelligent multi-agent marketing automation system built with Agno framework" --add-readme=false

# Set the remote and push
echo "🔗 Adding remote and pushing code..."
git remote add origin https://github.com/$(gh api user --jq .login)/agno-agi-marketing.git
git branch -M main
git push -u origin main

# Create labels for better issue organization
echo "🏷️  Creating issue labels..."
gh label create "agent" --description "Related to agent development" --color "0052CC" || true
gh label create "api-integration" --description "API toolkit integration" --color "FF6B6B" || true
gh label create "medium-priority" --description "Medium priority feature" --color "FFA500" || true
gh label create "low-priority" --description "Low priority feature" --color "90EE90" || true
gh label create "orchestration" --description "Workflow orchestration" --color "9932CC" || true
gh label create "workflow" --description "Workflow engine features" --color "20B2AA" || true
gh label create "deployment" --description "Deployment and production" --color "708090" || true
gh label create "monitoring" --description "Monitoring and observability" --color "FF69B4" || true

# Create issues for pending features
echo "📝 Creating GitHub issues for pending features..."

# Medium Priority Issues
gh issue create \
    --title "🔧 Build Salesforce API Toolkit for Advanced CRM" \
    --body "Implement comprehensive Salesforce API toolkit for advanced CRM operations.

## Features Needed
- Lead and opportunity management
- Advanced reporting and analytics
- Custom field handling
- Bulk operations support
- Integration with existing memory and knowledge systems

## Technical Requirements
- Salesforce REST API integration
- OAuth authentication flow
- Rate limiting and error handling
- Data transformation utilities
- Unit tests and documentation

## Priority
Medium - Extends CRM capabilities beyond HubSpot

## Related Files
- \`src/toolkits/salesforce_toolkit.py\` (to be created)
- \`src/agents/crm_agent.py\` (enhancement)" \
    --label "enhancement,api-integration,medium-priority"

gh issue create \
    --title "📡 Build NewsAPI and Twitter Toolkits for Market Signals" \
    --body "Create toolkits for real-time market intelligence gathering.

## NewsAPI Toolkit Features
- Company and industry news monitoring
- Funding announcement detection
- Market trend analysis
- Sentiment analysis integration

## Twitter Toolkit Features
- Social media monitoring
- Competitor activity tracking
- Industry influencer insights
- Trending topic analysis

## Technical Requirements
- API authentication and rate limiting
- Data filtering and relevance scoring
- Integration with knowledge management system
- Real-time signal processing

## Priority
Medium - Enhances market intelligence capabilities

## Related Files
- \`src/toolkits/newsapi_toolkit.py\` (to be created)
- \`src/toolkits/twitter_toolkit.py\` (to be created)" \
    --label "enhancement,api-integration,medium-priority"

gh issue create \
    --title "🏢 Create Company Expert Agent for ICP Validation" \
    --body "Develop specialized agent for Ideal Customer Profile validation and compliance.

## Core Capabilities
- ICP criteria validation
- Lead scoring and qualification
- Compliance rule enforcement
- Market segmentation analysis
- Competitive positioning

## Integration Requirements
- Access to all data toolkits
- Memory system for learning patterns
- Knowledge base for ICP frameworks
- Real-time scoring algorithms

## Priority
Medium - Critical for lead qualification

## Related Files
- \`src/agents/company_expert.py\` (to be created)
- \`src/knowledge/icp_frameworks.py\` (enhancement)" \
    --label "enhancement,agent,medium-priority"

gh issue create \
    --title "🎯 Create Resource Agent for Multi-Source Lead Harvesting" \
    --body "Build intelligent agent for automated lead harvesting from multiple sources.

## Features
- Multi-API waterfall lead searches
- Data deduplication and enrichment
- Quality scoring and filtering
- Automated research and validation
- Export to CRM systems

## Data Sources
- Apollo.io integration
- BuiltWith technology data
- Social media platforms
- Company websites and directories
- Industry databases

## Priority
Medium - Core lead generation functionality

## Related Files
- \`src/agents/resource_agent.py\` (to be created)
- Integration with existing toolkits" \
    --label "enhancement,agent,medium-priority"

gh issue create \
    --title "🗃️ Create CRM Agent for Data Hygiene and Management" \
    --body "Develop CRM management agent for data quality and pipeline operations.

## Capabilities
- Duplicate detection and merging
- Data validation and cleansing
- Pipeline stage management
- Automated follow-up scheduling
- Performance analytics and reporting

## CRM Integrations
- HubSpot operations
- Salesforce management
- Custom CRM connectors
- Data synchronization across platforms

## Priority
Medium - Essential for data quality

## Related Files
- \`src/agents/crm_agent.py\` (to be created)
- Enhancement to existing CRM toolkits" \
    --label "enhancement,agent,medium-priority"

gh issue create \
    --title "🎭 Build Campaign Director Orchestrator Agent" \
    --body "Create master orchestrator agent for coordinating multi-agent campaigns.

## Orchestration Features
- Campaign workflow management
- Agent task delegation
- Quality control and validation
- Progress monitoring and reporting
- Dynamic strategy adjustment

## Workflow Management
- Sequential and parallel task execution
- Conditional logic and branching
- Error handling and recovery
- Performance optimization
- Campaign analytics

## Priority
Medium - Core orchestration functionality

## Related Files
- \`src/orchestrator/campaign_director.py\` (to be created)
- \`src/workflows/campaign_workflows.py\` (to be created)" \
    --label "enhancement,orchestration,medium-priority"

gh issue create \
    --title "⚙️ Implement Core Workflow Engine with Lead Generation Pipeline" \
    --body "Build comprehensive workflow engine for automated campaign execution.

## Pipeline Stages
1. ICP Definition and Validation
2. Multi-source Lead Harvesting
3. Data Enrichment and Scoring
4. Personalization Strategy Creation
5. Campaign Execution and Monitoring
6. Performance Analysis and Optimization

## Engine Features
- Visual workflow designer
- Step-by-step execution tracking
- Conditional branching logic
- Error handling and recovery
- Performance metrics and analytics

## Priority
Medium - Core automation engine

## Related Files
- \`src/workflows/workflow_engine.py\` (to be created)
- \`src/workflows/lead_generation_pipeline.py\` (to be created)" \
    --label "enhancement,workflow,medium-priority"

# Low Priority Issues
gh issue create \
    --title "🔍 Create Search Agent for Real-Time Signal Gathering" \
    --body "Develop agent for continuous market intelligence and signal detection.

## Priority
Low - Enhancement for advanced intelligence

## Related Files
- \`src/agents/search_agent.py\` (to be created)" \
    --label "enhancement,agent,low-priority"

gh issue create \
    --title "🕷️ Create Crawling Agent for Social Media Intelligence" \
    --body "Build specialized agent for social media monitoring and intelligence gathering.

## Priority
Low - Advanced social intelligence

## Related Files
- \`src/agents/crawling_agent.py\` (to be created)" \
    --label "enhancement,agent,low-priority"

gh issue create \
    --title "📄 Create Context Summarizer Agent for Compression" \
    --body "Implement agent for intelligent context compression and summarization.

## Priority
Low - Optimization feature

## Related Files
- \`src/agents/context_summarizer.py\` (to be created)" \
    --label "enhancement,agent,low-priority"

gh issue create \
    --title "📊 Add DAG Export Functionality for Production Deployment" \
    --body "Add capability to export workflows as DAGs for Airflow/Temporal deployment.

## Priority
Low - Production deployment enhancement

## Related Files
- \`src/workflows/dag_export.py\` (to be created)" \
    --label "enhancement,deployment,low-priority"

gh issue create \
    --title "📈 Add Monitoring and Observability Features" \
    --body "Enhance system with comprehensive monitoring, metrics, and alerting capabilities.

## Priority
Low - Operations enhancement

## Related Files
- \`src/monitoring/\` (to be created)" \
    --label "enhancement,monitoring,low-priority"

echo "✅ GitHub repository and issues created successfully!"
echo ""
echo "🔗 Repository URL: https://github.com/$(gh api user --jq .login)/agno-agi-marketing"
echo "📋 Issues created: 12 total (7 medium priority, 5 low priority)"
echo ""
echo "Next steps:"
echo "1. Visit your repository to see all issues"
echo "2. Prioritize and assign issues as needed"
echo "3. Start contributing to extend the system!"
