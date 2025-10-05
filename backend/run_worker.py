#!/usr/bin/env python
"""
LLMScope Event Processor Worker

Background worker that processes events from Redis queue
and stores them to TimescaleDB.

Usage:
    python run_worker.py
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.workers.event_processor import EventProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Main entry point"""
    logger.info("="* 60)
    logger.info("🚀 LLMScope Event Processor Worker")
    logger.info("="* 60)

    processor = EventProcessor()

    try:
        await processor.run()
    except KeyboardInterrupt:
        logger.info("\n⚠️  Received interrupt signal, shutting down gracefully...")
        await processor.stop()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Worker stopped")
        sys.exit(0)
