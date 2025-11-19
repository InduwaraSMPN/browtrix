from fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("browtrix")

@mcp.tool()
def hello() -> str:
    """Say hello from browtrix"""
    return "Hello from browtrix!"

# Run the server with Streamable HTTP transport
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)