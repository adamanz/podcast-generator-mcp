"""
Simple example of generating a podcast
"""
import asyncio
from fastmcp import Client

async def main():
    # Connect to the MCP server
    async with Client("../podcast_mcp_server.py") as client:
        # Generate a simple 5-minute podcast
        result = await client.call_tool(
            "generate_full_podcast",
            {
                "topic": "The Benefits of Morning Routines",
                "duration_minutes": 5,
                "style": "conversational"
            }
        )
        print(f"Podcast created! Check: {result.text}")

if __name__ == "__main__":
    asyncio.run(main())