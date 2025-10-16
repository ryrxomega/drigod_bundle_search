#!/usr/bin/env python3
"""
Development server runner for AI Outfit Bundle Recommendation Engine
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "outfit_engine.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
