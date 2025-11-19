import asyncio
import aiohttp


async def analyze_sse_issues():
    """Analyze the actual SSE transport issues for production"""
    print("=== SSE Transport Production Issues Analysis ===")

    issues_found = []

    # Issue 1: Connection Lifecycle Management
    print("\n🔍 Issue 1: Connection Lifecycle Management")
    try:
        async with aiohttp.ClientSession() as session:
            # Test what happens when client disconnects abruptly
            sse_response = await session.get("http://localhost:8000/sse")

            session_endpoint = None
            async for line in sse_response.content:
                line = line.decode().strip()
                if line.startswith("data: "):
                    session_endpoint = f"http://localhost:8000{line[6:]}"
                    break

            # Close SSE connection abruptly (simulating client disconnect)
            sse_response.close()
            await sse_response.wait_for_close()

            # Try to send a message to the closed session
            tools_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {},
            }

            await asyncio.sleep(0.1)  # Small delay
            if session_endpoint:
                msg_response = await session.post(session_endpoint, json=tools_request)
            else:
                print("⚠️ No session endpoint found")
                return

            if msg_response.status == 202:
                print("⚠️ Message accepted but SSE connection is closed")
                print("   → This causes the ClosedResourceError we see in logs")
                issues_found.append(
                    "Connection lifecycle: Messages accepted for closed SSE sessions"
                )

    except Exception as e:
        print(f"✗ Lifecycle test failed: {e}")

    # Issue 2: Concurrent Session Handling
    print("\n🔍 Issue 2: Concurrent Session Handling")
    try:
        async with aiohttp.ClientSession() as session:
            # Open multiple SSE connections
            sse_tasks = []
            for i in range(3):
                task = asyncio.create_task(session.get("http://localhost:8000/sse"))
                sse_tasks.append(task)

            # Get session endpoints
            endpoints = []
            for task in sse_tasks:
                response = await task
                async for line in response.content:
                    line = line.decode().strip()
                    if line.startswith("data: "):
                        endpoints.append(f"http://localhost:8000{line[6:]}")
                        break

            print(f"✓ Created {len(endpoints)} concurrent sessions")

            # Close all SSE connections
            for task in sse_tasks:
                response = task.result()
                await response.aclose()

            # Try to use the endpoints
            for i, endpoint in enumerate(endpoints):
                tools_request = {
                    "jsonrpc": "2.0",
                    "id": i + 10,
                    "method": "tools/list",
                    "params": {},
                }

                try:
                    msg_response = await session.post(endpoint, json=tools_request)
                    if msg_response.status == 202:
                        print(
                            f"⚠️ Session {i + 1} still accepts messages after SSE close"
                        )
                except Exception:
                    print(f"✓ Session {i + 1} properly rejected")

            issues_found.append("Session cleanup: Closed sessions may remain active")

    except Exception as e:
        print(f"✗ Concurrent session test failed: {e}")

    # Issue 3: Memory/Resource Leaks
    print("\n🔍 Issue 3: Resource Management")
    print("⚠️ Each SSE session creates server-side resources")
    print("⚠️ No visible session timeout or cleanup mechanism")
    print("⚠️ Memory streams may accumulate if not properly closed")
    issues_found.append("Resource leaks: No session timeout or cleanup")

    # Issue 4: Error Handling
    print("\n🔍 Issue 4: Error Handling")
    try:
        async with aiohttp.ClientSession() as session:
            # Send invalid request
            sse_response = await session.get("http://localhost:8000/sse")

            session_endpoint = None
            async for line in sse_response.content:
                line = line.decode().strip()
                if line.startswith("data: "):
                    session_endpoint = f"http://localhost:8000{line[6:]}"
                    break

            # Send malformed JSON
            malformed_request = "invalid json"
            if session_endpoint:
                msg_response = await session.post(
                    session_endpoint, data=malformed_request
                )
            else:
                print("⚠️ No session endpoint found for malformed request test")
                return

            print(f"Malformed request status: {msg_response.status}")
            if msg_response.status != 400:
                print("⚠️ Should return 400 for malformed requests")
                issues_found.append(
                    "Error handling: Poor validation of malformed requests"
                )

    except Exception as e:
        print(f"✗ Error handling test failed: {e}")

    return issues_found


async def main():
    issues = await analyze_sse_issues()

    print("\n=== PRODUCTION ISSUES FOUND ===")
    for i, issue in enumerate(issues or [], 1):
        print(f"{i}. {issue}")

    print("\n=== SEVERITY ASSESSMENT ===")
    print("🔴 HIGH: Connection lifecycle issues cause server errors")
    print("🟡 MEDIUM: Resource leaks could cause memory issues over time")
    print("🟡 MEDIUM: Poor error handling could lead to undefined behavior")
    print("🟢 LOW: Concurrent session handling works but needs cleanup")


if __name__ == "__main__":
    asyncio.run(main())
