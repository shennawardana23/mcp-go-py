#!/usr/bin/env python3
"""
AWS Lambda Handler for MCP-PBA-TUNNEL
Provides serverless deployment for the FastAPI application
"""

import json
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import uvicorn
from mangum import Mangum
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

from mcp_pba_tunnel.data.project_manager import DatabaseManager, PromptDataManager
from mcp_pba_tunnel.server.fastapi_mcp_server import app

# AWS Lambda Powertools
logger = Logger()
tracer = Tracer()

# Global instances
db_manager: Optional[DatabaseManager] = None
prompt_manager: Optional[PromptDataManager] = None

def get_database_manager() -> DatabaseManager:
    """Get or create database manager instance"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager

def get_prompt_manager() -> PromptDataManager:
    """Get or create prompt manager instance"""
    global prompt_manager
    if prompt_manager is None:
        db_manager = get_database_manager()
        prompt_manager = PromptDataManager(db_manager.engine.url)
    return prompt_manager

def create_lambda_handler(app: FastAPI):
    """Create Lambda handler with proper middleware"""

    # Create Mangum handler
    handler = Mangum(
        app,
        lifespan="off",  # Disable lifespan events in Lambda
        api_gateway_base_path="",  # Handle API Gateway base path
    )

    @logger.inject_lambda_context
    @tracer.capture_lambda_handler
    def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
        """Main Lambda handler function"""

        logger.info(f"Received event: {event.get('httpMethod', 'UNKNOWN')} {event.get('path', 'UNKNOWN')}")

        try:
            # Initialize database connection
            db_manager = get_database_manager()

            # Log Lambda context
            logger.info(f"Remaining time: {context.get_remaining_time_in_millis()}ms")
            logger.info(f"Function name: {context.function_name}")
            logger.info(f"Function version: {context.function_version}")

            # Process the request
            response = handler(event, context)

            # Log successful processing
            logger.info(f"Request processed successfully: {response.get('statusCode', 500)}")

            return response

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            logger.exception(e)

            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "error": "Internal server error",
                    "message": "An error occurred while processing your request"
                })
            }

    return lambda_handler

def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """Main Lambda handler function"""
    return create_lambda_handler(app)(event, context)

# Health check for Lambda
def health_check_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """Health check endpoint for Lambda"""
    try:
        db_manager = get_database_manager()

        # Test database connection
        with db_manager.get_session() as session:
            session.execute("SELECT 1")

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "status": "healthy",
                "service": "mcp-pba-tunnel",
                "environment": "lambda"
            })
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "statusCode": 503,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "status": "unhealthy",
                "error": str(e)
            })
        }

# Local development server
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MCP-PBA-TUNNEL Lambda Handler")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=9001, help="Port to bind to")
    parser.add_argument("--workers", type=int, default=1, help="Number of workers")

    args = parser.parse_args()

    # Initialize database for local development
    db_manager = get_database_manager()

    print("🚀 Starting MCP-PBA-TUNNEL Lambda Handler")
    print(f"📊 Database: {db_manager.engine.url}")
    print(f"🌐 Host: {args.host}")
    print(f"🔌 Port: {args.port}")

    uvicorn.run(
        "lambda_handler:app",
        host=args.host,
        port=args.port,
        workers=args.workers,
        reload=True
    )
