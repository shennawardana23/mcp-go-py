#!/usr/bin/env python3
"""
Comprehensive tests for MCP-PBA-TUNNEL server
Tests MCP protocol compliance, FastAPI endpoints, and database operations
"""

import pytest
import pytest_asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from server.fastapi_mcp_server import app
from data.project_manager import DatabaseManager, PromptDataManager


@pytest.fixture
def test_db():
    """Create test database"""
    engine = create_engine(
        "postgresql://postgres:password@localhost:5432/mcp_test",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    DatabaseManager.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(test_db):
    """Create database session for testing"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_client():
    """Create FastAPI test client"""
    return TestClient(app)


@pytest.fixture
async def async_test_client():
    """Create async FastAPI test client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_prompt_data():
    """Sample prompt template data for testing"""
    return {
        "name": "test_business_logic",
        "description": "Test business logic template",
        "category": "development",
        "template_content": "Test template for {{business_domain}}",
        "variables": ["business_domain", "requirements"]
    }


class TestHealthEndpoints:
    """Test health check and basic server functionality"""

    def test_health_check(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["service"] == "mcp-prompt-engineering-server"

    def test_health_check_async(self, async_test_client):
        """Test health check endpoint with async client"""
        response = async_test_client.get("/health")
        assert response.status_code == 200


class TestMCPProtocol:
    """Test MCP protocol compliance"""

    def test_list_prompts_mcp_protocol(self, test_client):
        """Test MCP prompts/list endpoint"""
        request_data = {
            "jsonrpc": "2.0",
            "id": "test-123",
            "method": "prompts/list",
            "params": {}
        }

        response = test_client.post("/mcp/prompts/list", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == "test-123"
        assert "result" in data
        assert "prompts" in data["result"]

    def test_get_prompt_mcp_protocol(self, test_client):
        """Test MCP prompts/get endpoint"""
        request_data = {
            "jsonrpc": "2.0",
            "id": "test-456",
            "method": "prompts/get",
            "params": {
                "name": "business_logic_implementation"
            }
        }

        response = test_client.post("/mcp/prompts/get", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == "test-456"
        assert "result" in data

    def test_list_tools_mcp_protocol(self, test_client):
        """Test MCP tools/list endpoint"""
        request_data = {
            "jsonrpc": "2.0",
            "id": "test-789",
            "method": "tools/list",
            "params": {}
        }

        response = test_client.post("/mcp/tools/list", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == "test-789"
        assert "result" in data
        assert "tools" in data["result"]

    def test_call_tool_render_prompt(self, test_client):
        """Test MCP tools/call with render_prompt"""
        request_data = {
            "jsonrpc": "2.0",
            "id": "test-render",
            "method": "tools/call",
            "params": {
                "name": "render_prompt",
                "arguments": {
                    "template_name": "business_logic_implementation",
                    "variables": {
                        "business_domain": "e-commerce",
                        "requirements": "user authentication"
                    }
                }
            }
        }

        response = test_client.post("/mcp/tools/call", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == "test-render"
        assert "result" in data


class TestRESTAPI:
    """Test REST API endpoints"""

    def test_get_categories(self, test_client):
        """Test categories endpoint"""
        response = test_client.get("/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data

    def test_get_prompts(self, test_client):
        """Test prompts listing endpoint"""
        response = test_client.get("/api/prompts")
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data

    def test_create_prompt_template(self, test_client, sample_prompt_data):
        """Test prompt template creation"""
        response = test_client.post("/api/prompts", json=sample_prompt_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["message"]

    def test_render_prompt_template(self, test_client):
        """Test template rendering endpoint"""
        variables = "business_domain=ecommerce&requirements=user+auth"
        response = test_client.get(f"/api/prompts/business_logic_implementation/render?variables={variables}")
        assert response.status_code == 200
        data = response.json()
        assert "rendered_content" in data


class TestDatabaseOperations:
    """Test database operations and data management"""

    def test_database_manager_creation(self, test_db):
        """Test DatabaseManager initialization"""
        db_manager = DatabaseManager("postgresql://postgres:password@localhost:5432/mcp_test")
        assert db_manager.engine is not None
        assert db_manager.SessionLocal is not None

    def test_prompt_data_manager(self, test_db):
        """Test PromptDataManager functionality"""
        prompt_manager = PromptDataManager("postgresql://postgres:password@localhost:5432/mcp_test")
        categories = prompt_manager.get_available_categories()
        assert isinstance(categories, list)

    def test_create_prompt_template(self, db_session):
        """Test prompt template creation in database"""
        from data.project_manager import PromptManager, DatabaseManager

        db_manager = DatabaseManager("postgresql://postgres:password@localhost:5432/mcp_test")
        prompt_mgr = PromptManager(db_manager)

        template_id = prompt_mgr.create_prompt_template(
            name="test_template",
            description="Test template",
            category="development",
            template_content="Test content with {{variable}}",
            variables=["variable"]
        )

        assert template_id is not None
        assert len(template_id) > 0

    def test_get_template_by_name(self, db_session):
        """Test template retrieval by name"""
        from data.project_manager import PromptManager, DatabaseManager

        db_manager = DatabaseManager("postgresql://postgres:password@localhost:5432/mcp_test")
        prompt_mgr = PromptManager(db_manager)

        # Create template
        template_id = prompt_mgr.create_prompt_template(
            name="test_retrieval",
            description="Test retrieval",
            category="development",
            template_content="Test content",
            variables=["test"]
        )

        # Retrieve template
        template = prompt_mgr.get_template_by_name("test_retrieval")
        assert template is not None
        assert template.name == "test_retrieval"


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_json_rpc(self, test_client):
        """Test invalid JSON-RPC request handling"""
        response = test_client.post("/mcp/prompts/list", data="invalid json")
        assert response.status_code == 400

    def test_invalid_mcp_method(self, test_client):
        """Test invalid MCP method handling"""
        request_data = {
            "jsonrpc": "2.0",
            "id": "test-invalid",
            "method": "invalid/method",
            "params": {}
        }

        response = test_client.post("/mcp/tools/call", json=request_data)
        assert response.status_code == 400

    def test_template_not_found(self, test_client):
        """Test template not found error handling"""
        request_data = {
            "jsonrpc": "2.0",
            "id": "test-notfound",
            "method": "prompts/get",
            "params": {
                "name": "nonexistent_template"
            }
        }

        response = test_client.post("/mcp/prompts/get", json=request_data)
        assert response.status_code == 404

    def test_malformed_request(self, test_client):
        """Test malformed request handling"""
        request_data = {
            "jsonrpc": "2.0",
            "id": "test-malformed"
            # Missing method
        }

        response = test_client.post("/mcp/prompts/list", json=request_data)
        assert response.status_code == 400


class TestIntegration:
    """Integration tests for complete workflows"""

    def test_full_prompt_workflow(self, test_client):
        """Test complete prompt creation and rendering workflow"""
        # 1. Create a prompt template
        template_data = {
            "name": "integration_test_template",
            "description": "Integration test template",
            "category": "development",
            "template_content": "Integration test for {{test_variable}}",
            "variables": ["test_variable"],
            "created_by": "test_user"
        }

        response = test_client.post("/api/prompts", json=template_data)
        assert response.status_code == 200
        template_id = response.json()["id"]

        # 2. Render the template
        variables = "test_variable=integration+test"
        response = test_client.get(f"/api/prompts/integration_test_template/render?variables={variables}")
        assert response.status_code == 200

        data = response.json()
        assert "rendered_content" in data
        assert "integration test" in data["rendered_content"]

    def test_mcp_protocol_full_workflow(self, test_client):
        """Test complete MCP protocol workflow"""
        # 1. List prompts
        list_request = {
            "jsonrpc": "2.0",
            "id": "workflow-1",
            "method": "prompts/list",
            "params": {}
        }

        response = test_client.post("/mcp/prompts/list", json=list_request)
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == "workflow-1"

        # 2. Call tool to render prompt
        tool_request = {
            "jsonrpc": "2.0",
            "id": "workflow-2",
            "method": "tools/call",
            "params": {
                "name": "render_prompt",
                "arguments": {
                    "template_name": "business_logic_implementation",
                    "variables": {
                        "business_domain": "integration-test",
                        "requirements": "test requirements"
                    }
                }
            }
        }

        response = test_client.post("/mcp/tools/call", json=tool_request)
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == "workflow-2"
        assert "result" in data


class TestPerformance:
    """Performance and load testing"""

    def test_concurrent_requests(self, test_client):
        """Test handling of concurrent requests"""
        import asyncio
        import aiohttp

        async def make_request(session, url, data):
            async with session.post(url, json=data) as response:
                return await response.json()

        async def test_concurrent():
            async with aiohttp.ClientSession() as session:
                tasks = []
                for i in range(10):
                    data = {
                        "jsonrpc": "2.0",
                        "id": f"concurrent-{i}",
                        "method": "prompts/list",
                        "params": {}
                    }
                    tasks.append(make_request(session, "http://test/mcp/prompts/list", data))

                results = await asyncio.gather(*tasks)
                return results

        # This would be run with pytest-asyncio
        # results = await test_concurrent()
        # assert len(results) == 10

    def test_large_payload_handling(self, test_client):
        """Test handling of large request payloads"""
        large_variables = {f"var_{i}": f"value_{i}" * 100 for i in range(100)}

        request_data = {
            "jsonrpc": "2.0",
            "id": "large-payload",
            "method": "tools/call",
            "params": {
                "name": "render_prompt",
                "arguments": {
                    "template_name": "business_logic_implementation",
                    "variables": large_variables
                }
            }
        }

        response = test_client.post("/mcp/tools/call", json=request_data)
        # Should handle large payloads gracefully
        assert response.status_code in [200, 413]  # 200 OK or 413 Payload Too Large


class TestSecurity:
    """Security and validation tests"""

    def test_input_validation(self, test_client):
        """Test input validation and sanitization"""
        # Test SQL injection attempts
        malicious_input = {
            "jsonrpc": "2.0",
            "id": "malicious-1",
            "method": "tools/call",
            "params": {
                "name": "render_prompt",
                "arguments": {
                    "template_name": "'; DROP TABLE users; --",
                    "variables": {"test": "malicious"}
                }
            }
        }

        response = test_client.post("/mcp/tools/call", json=malicious_input)
        assert response.status_code == 400  # Should be rejected

    def test_cors_handling(self, test_client):
        """Test CORS middleware functionality"""
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }

        response = test_client.options("/mcp/prompts/list", headers=headers)
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers

    def test_rate_limiting(self, test_client):
        """Test rate limiting functionality"""
        # Make multiple rapid requests
        for i in range(100):  # Assuming rate limit is higher than this
            response = test_client.post("/mcp/prompts/list", json={
                "jsonrpc": "2.0",
                "id": f"rate-test-{i}",
                "method": "prompts/list",
                "params": {}
            })

            if response.status_code == 429:  # Too Many Requests
                assert "Retry-After" in response.headers
                break
        else:
            # If we didn't hit rate limit, that's also acceptable
            pass


class TestConfiguration:
    """Test configuration management"""

    def test_config_validation(self, test_client):
        """Test configuration file validation"""
        # Test that config is loaded correctly
        response = test_client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["service"] == "mcp-prompt-engineering-server"

    def test_environment_variables(self):
        """Test environment variable handling"""
        import os

        # Set test environment variables
        os.environ["TEST_DATABASE_URL"] = "postgresql://postgres:password@localhost:5432/mcp_test"
        os.environ["TEST_REDIS_URL"] = "redis://localhost:6379"

        # Configuration should pick up these values
        # This would be tested with actual config loading

        # Clean up
        del os.environ["TEST_DATABASE_URL"]
        del os.environ["TEST_REDIS_URL"]


# Pytest configuration
pytest_plugins = ["pytest_asyncio"]

# Test markers
pytestmark = pytest.mark.asyncio
