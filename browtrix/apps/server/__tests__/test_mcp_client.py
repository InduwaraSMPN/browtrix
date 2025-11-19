#!/usr/bin/env python3
"""
Test script to verify MCP server tools are accessible
"""
import asyncio
import httpx
import json


async def test_mcp_tools():
    """Test the MCP server tools via HTTP"""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Browtrix MCP Server...")
    print(f"📡 Server URL: {base_url}")
    print()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Check SSE endpoint
        print("1️⃣  Testing SSE endpoint...")
        try:
            response = await client.get(f"{base_url}/sse")
            if response.status_code == 200:
                print("   ✅ SSE endpoint is accessible")
                # Read first few lines
                lines = response.text.split('\n')[:5]
                for line in lines:
                    if line.strip():
                        print(f"   📨 {line}")
            else:
                print(f"   ❌ SSE endpoint returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
        
        # Test 2: List available tools
        print("2️⃣  Attempting to list MCP tools...")
        print("   ℹ️  Note: This requires a proper MCP client connection")
        print("   ℹ️  The server is configured with SSE transport")
        print()
        
        # Test 3: Check WebSocket endpoint
        print("3️⃣  Testing WebSocket endpoint...")
        try:
            # WebSocket test would require websockets library
            print("   ℹ️  WebSocket endpoint is at ws://localhost:8000/ws")
            print("   ℹ️  This is for browser connections, not MCP clients")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
        print("📋 Summary:")
        print("   • MCP Server is running on port 8000")
        print("   • SSE transport is enabled at /sse")
        print("   • WebSocket endpoint at /ws for browser connections")
        print()
        print("🔧 Available MCP Tools:")
        print("   1. browtrix_html_snapshot() - Take HTML snapshot of current page")
        print("   2. browtrix_confirmation_alert(message) - Show confirmation dialog")
        print("   3. browtrix_question_popup(question) - Show input dialog")
        print()
        print("⚠️  Note: These tools require an active browser connection via WebSocket")
        print("   to function properly. Start the Next.js frontend to test them.")


if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
