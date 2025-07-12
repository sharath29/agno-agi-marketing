"""
Main entry point for Agno-AGI Marketing Automation System.

Run this file to start the interactive marketing automation system.
"""

import asyncio
import sys
from pathlib import Path

from src.demo import main as demo_main

# Add src to Python path
sys.path.append(str(Path(__file__).parent / "src"))


def main():
    """Main entry point for Agno-AGI Marketing Automation System."""
    print(
        """
    ╔═══════════════════════════════════════════════════════════════╗
    ║               Agno-AGI Marketing Automation System            ║
    ║                                                               ║
    ║   Intelligent multi-agent system for marketing automation    ║
    ║   Built with Agno framework for production-ready campaigns   ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    )

    # Run demo
    asyncio.run(demo_main())


if __name__ == "__main__":
    main()
