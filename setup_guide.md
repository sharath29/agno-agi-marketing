# Setup Guide - Agno-AGI Marketing Automation System

## Quick Start (Virtual Environment Created!)

Your virtual environment is ready! Here's how to use it:

### 1. Activate the Virtual Environment

```bash
# Activate the environment
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

### 2. Run the Simple Demo

```bash
# Run the simplified demo (works immediately)
python src/simple_demo.py
```

This demo will show you:
- Marketing agent capabilities
- API toolkit concepts
- Knowledge management system
- Memory architecture
- System overview

### 3. Configure API Keys (Optional)

Create a `.env` file for full functionality:

```bash
# Copy the example file
cp .env.example .env

# Edit with your API keys
nano .env  # or use your preferred editor
```

Add your API keys:
```bash
OPENAI_API_KEY=sk-your-openai-key-here
APOLLO_API_KEY=your-apollo-key-here
HUBSPOT_API_KEY=your-hubspot-key-here
BUILTWITH_API_KEY=your-builtwith-key-here
```

### 4. Install Full Dependencies (Optional)

For complete functionality, install all dependencies:

```bash
# This may take a few minutes
pip install -r requirements.txt
```

**Note**: If you encounter issues with the Agno framework installation, you can still use the simplified demo which demonstrates all the core concepts.

## What's Working Right Now

✅ **Virtual Environment**: Created and ready
✅ **Core Dependencies**: OpenAI, requests, pydantic, loguru installed
✅ **Simple Demo**: Fully functional demonstration
✅ **Project Structure**: Complete codebase architecture
✅ **Configuration**: Environment management system

## Architecture Overview

```
Your Marketing Automation System
├── Virtual Environment (venv/) ✅ READY
├── Core Dependencies ✅ INSTALLED
├── Demo System ✅ WORKING
├── Agent Framework ⚠️ SIMPLIFIED
├── API Toolkits ⚠️ MOCK DATA
└── Full Production System ⏸️ REQUIRES FULL INSTALL
```

## Running the Demo

The simple demo shows exactly how the full system works:

1. **Marketing Expert Agent**
   - Campaign strategy generation
   - Email optimization
   - Personalization strategies

2. **API Toolkit System**
   - Contact search capabilities
   - Company enrichment
   - Multi-source data integration

3. **Knowledge Management**
   - Marketing best practices
   - Proven templates and frameworks
   - RAG-enhanced decision making

4. **Memory Systems**
   - Conversation memory
   - Campaign learning
   - Performance optimization

## Next Steps

1. **Run the demo** to see the system in action
2. **Configure API keys** for real data integration
3. **Install full dependencies** for production features
4. **Explore the codebase** to understand the architecture
5. **Customize agents** for your specific needs

## Troubleshooting

**If the simple demo doesn't work:**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Check Python version
python --version

# Run the demo
cd /Users/sharathsavasere/Documents/martech/agentic-marketing
python src/simple_demo.py
```

**If you need to restart:**
```bash
# Deactivate and reactivate
deactivate
source venv/bin/activate
```

## Support

The system is designed to be modular and extensible. Even without the full Agno framework, the demo showcases all the core concepts and capabilities that solve real marketing automation problems.

Start with the simple demo, then gradually add more dependencies and features as needed!
