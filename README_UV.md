# Podcast Generator MCP Server with UV

Super simple setup using `uv` package manager.

## Quick Setup (30 seconds)

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # or on Mac:
   brew install uv
   ```

2. **Clone and setup**:
   ```bash
   git clone <your-repo>
   cd podcast-generator-mcp-1
   uv sync  # Installs all dependencies automatically
   ```

3. **Configure Claude Desktop**:
   Add to `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "podcast-generator": {
         "command": "uv",
         "args": [
           "run",
           "--project",
           "/path/to/podcast-generator-mcp-1",
           "python",
           "/path/to/podcast-generator-mcp-1/podcast_server_simple.py"
         ]
       }
     }
   }
   ```

4. **Restart Claude Desktop**

Done! No virtual environments to manage, no pip issues.

## Test it works

```bash
# Test directly
uv run python podcast_server_simple.py

# Or use MCP inspector
uv run npx @modelcontextprotocol/inspector python podcast_server_simple.py
```

## For ElevenLabs (optional)

Set your API key:
```bash
export ELEVENLABS_API_KEY="your-key"
```

## Why UV?

- ✅ No virtual environment headaches
- ✅ Fast (10-100x faster than pip)
- ✅ Handles Python versions automatically
- ✅ Works identically on all platforms
- ✅ Single command installation