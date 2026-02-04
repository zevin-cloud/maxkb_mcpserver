"""Test MCP client connection."""
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def test():
    print("Connecting to MCP server...")
    async with sse_client("http://192.168.123.237:3000/sse") as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            print("Initializing...")
            await session.initialize()
            
            print("\nListing tools...")
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            print("\nCalling list_knowledge_bases...")
            result = await session.call_tool("list_knowledge_bases", {})
            print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(test())
