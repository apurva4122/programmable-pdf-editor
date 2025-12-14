#!/usr/bin/env python3
import os
import sys
import uvicorn

if __name__ == "__main__":
    # Get port from environment variable (Railway sets this)
    port = int(os.environ.get("PORT", 8000))
    
    # Print startup info for debugging
    print(f"Starting server on port {port}")
    print(f"PORT environment variable: {os.environ.get('PORT', 'NOT SET')}")
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)

