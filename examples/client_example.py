#!/usr/bin/env python3
"""
Example: Using the Podcast Generator MCP Server with FastMCP Client
"""
import asyncio
import os
from fastmcp import Client

async def main():
    # Make sure the server is running first:
    # python podcast_mcp_server.py
    
    # Connect to the MCP server
    async with Client("podcast_mcp_server.py") as client:
        print("🎙️ Connected to Podcast Generator MCP Server")
        
        # Check API status
        print("\n📊 Checking API status...")
        status = await client.read_resource("status://api")
        print(f"Status: {status.text}")
        
        # Get available voices
        print("\n🎭 Available voices:")
        voices = await client.read_resource("voices://available")
        print(voices.text)
        
        # Get recommended voice pairs
        print("\n👥 Recommended voice pairs:")
        pairs = await client.read_resource("voices://recommended-pairs")
        print(pairs.text)
        
        # Example 1: Generate a complete podcast
        print("\n🚀 Generating a complete podcast...")
        result = await client.call_tool(
            "generate_full_podcast",
            {
                "topic": "The Impact of AI on Education",
                "duration_minutes": 5,
                "host_voice": "Charlie",
                "guest_voice": "Emily",
                "style": "conversational"
            }
        )
        print(f"Result: {result.text}")
        
        # Example 2: Step-by-step generation
        print("\n📝 Step-by-step generation...")
        
        # Step 1: Generate script
        script_result = await client.call_tool(
            "generate_podcast_script",
            {
                "topic": "The Future of Remote Work",
                "duration_minutes": 3,
                "style": "interview",
                "host_personality": "curious journalist",
                "guest_personality": "experienced remote work consultant"
            }
        )
        print(f"Script generated: {script_result.text[:200]}...")
        
        # Parse the script from the result
        import json
        script = json.loads(script_result.text)
        
        # Step 2: Create audio (only if API key is available)
        if os.getenv("ELEVENLABS_API_KEY"):
            audio_result = await client.call_tool(
                "create_podcast_audio",
                {
                    "script": script,
                    "host_voice": "Adam",
                    "guest_voice": "Grace"
                }
            )
            print(f"Audio created: {audio_result.text[:200]}...")
            
            # Step 3: Combine audio
            audio_data = json.loads(audio_result.text)
            if audio_data.get("has_audio"):
                combine_result = await client.call_tool(
                    "combine_podcast_audio",
                    {
                        "podcast_data": audio_data,
                        "normalize_audio": True,
                        "add_fade": True
                    }
                )
                print(f"Final podcast: {combine_result.text}")
        
        # Example 3: Get topic suggestions
        print("\n💡 Getting topic suggestions...")
        suggestions = await client.get_prompt(
            "podcast_topic_suggestions",
            {"genre": "science"}
        )
        print(f"Suggestions: {suggestions.text[:300]}...")

if __name__ == "__main__":
    asyncio.run(main())
