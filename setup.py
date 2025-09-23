#!/usr/bin/env python3
"""
Setup script for MCP-PBA-TUNNEL
Installs dependencies and configures the environment
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔧 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def main():
    """Main setup process"""
    print("🚀 MCP-PBA-TUNNEL Setup")
    print("=" * 50)

    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)

    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} detected")

    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        sys.exit(1)

    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print("✅ Data directory created")

    # Initialize database
    print("🔧 Initializing database...")
    try:
        result = subprocess.run([sys.executable, "-c", "from mcp_pba_tunnel.data.project_manager import DatabaseManager; db = DatabaseManager(); print('✅ Database initialized')"], check=True, capture_output=True, text=True)
        print("✅ Database initialized")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Database initialization failed: {e.stderr}")
        print("   This is normal if you haven't set up the database yet")

    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the FastAPI MCP server:")
    print("   python -m mcp_pba_tunnel.server.fastapi_mcp_server")
    print("\n2. Test the server:")
    print("   curl http://localhost:9001/health")
    print("\n3. List prompt categories:")
    print("   curl http://localhost:9001/api/categories")
    print("\n📖 For more information, see README.md")

if __name__ == "__main__":
    main()
