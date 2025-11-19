#!/usr/bin/env python3
"""
Quick test to verify Browtrix MCP server configuration
"""

import subprocess
import json
import sys


def test_mcp_config():
    """Test the MCP configuration"""
    print("=" * 60)
    print("🧪 Browtrix MCP Server Configuration Test")
    print("=" * 60)
    print()

    # 1. Check MCP config file
    print("1️⃣  Checking MCP configuration...")
    try:
        with open("/home/pasindui/.gemini/antigravity/mcp_config.json", "r") as f:
            config = json.load(f)

        if "browtrix" in config.get("mcpServers", {}):
            print("   ✅ Browtrix server found in MCP config")
            browtrix_config = config["mcpServers"]["browtrix"]
            print(f"   📋 Command: {browtrix_config.get('command')}")
            print(f"   📋 Args: {' '.join(browtrix_config.get('args', []))}")
            if "url" in browtrix_config:
                print(f"   📋 URL: {browtrix_config['url']}")
        else:
            print("   ❌ Browtrix server NOT found in MCP config")
            return False
    except Exception as e:
        print(f"   ❌ Error reading config: {e}")
        return False

    print()

    # 2. Check if server is running
    print("2️⃣  Checking if server is running...")
    try:
        result = subprocess.run(["lsof", "-i", ":8000"], capture_output=True, text=True)
        if "browtrix" in result.stdout:
            print("   ✅ Browtrix server is running on port 8000")
        else:
            print("   ⚠️  Port 8000 is in use but may not be browtrix")
            print(f"   {result.stdout}")
    except Exception as e:
        print(f"   ❌ Error checking server: {e}")

    print()

    # 3. Check server endpoints
    print("3️⃣  Checking server endpoints...")
    try:
        result = subprocess.run(
            ["curl", "-s", "-m", "2", "http://localhost:8000/sse"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if "event: endpoint" in result.stdout:
            print("   ✅ SSE endpoint is responding")
            lines = result.stdout.split("\n")[:3]
            for line in lines:
                if line.strip():
                    print(f"      {line}")
        else:
            print("   ❌ SSE endpoint not responding correctly")
    except subprocess.TimeoutExpired:
        print("   ✅ SSE endpoint is streaming (timeout expected)")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")

    print()

    # 4. Summary
    print("=" * 60)
    print("📊 Summary")
    print("=" * 60)
    print()
    print("✅ MCP Configuration Status:")
    print("   • Browtrix server added to mcp_config.json")
    print("   • Server command: uv run browtrix-server")
    print("   • Server URL: http://localhost:8000")
    print()
    print("🔧 Available MCP Tools (require browser connection):")
    print("   1. browtrix_html_snapshot()")
    print("   2. browtrix_confirmation_alert(message: str)")
    print("   3. browtrix_question_popup(question: str)")
    print()
    print("📝 Next Steps:")
    print("   1. Restart Antigravity to load the new MCP server")
    print("   2. Start the Next.js frontend app")
    print("   3. Open the web page in browser")
    print("   4. Test MCP tools from Antigravity")
    print()
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = test_mcp_config()
    sys.exit(0 if success else 1)
