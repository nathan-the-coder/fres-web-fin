"""
FRES Ping Endpoint - Vercel Serverless Function
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from base import success_response, cors_preflight

def handler(event, context):
    """Health check endpoint."""
    if event.get("httpMethod") == "OPTIONS":
        return cors_preflight(event)

    return success_response({
        "status": "online",
        "message": "FRES Backend active!",
        "version": "2.0.0"
    })
