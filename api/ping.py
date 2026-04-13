"""
FRES Ping Endpoint - Vercel Serverless Function
/api/ping
"""
import os
import sys

# Add api directory to path for imports
_api_dir = os.path.dirname(os.path.abspath(__file__))
if _api_dir not in sys.path:
    sys.path.insert(0, _api_dir)

from base import success_response, cors_preflight

# Handler function for Vercel
def handler(event, context):
    """Health check endpoint."""
    if event.get("httpMethod") == "OPTIONS":
        return cors_preflight(event)

    return success_response({
        "status": "online",
        "message": "FRES Backend active!",
        "version": "2.0.0"
    })
