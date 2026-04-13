"""
FRES Ping Endpoint - Vercel Serverless Function
/api/ping
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from base import success_response, cors_preflight


def main(event, context):
    """Health check endpoint."""
    if event.get("httpMethod") == "OPTIONS":
        return cors_preflight(event)

    return success_response({
        "status": "online",
        "message": "FRES Backend active!",
        "version": "2.0.0"
    })
