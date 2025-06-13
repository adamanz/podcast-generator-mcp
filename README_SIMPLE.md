# Simple Podcast Generator MCP Server

A minimal MCP server for generating podcast scripts and audio with ElevenLabs.

## Features
- Generate podcast scripts on any topic
- Create audio using ElevenLabs voices (optional)
- Works out of the box with minimal setup

## Quick Install

### Option 1: Using Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Mac/Linux
# or
venv\Scripts\activate  # On Windows

# Install requirements
pip install mcp elevenlabs
```

### Option 2: Using pipx (Alternative)
```bash
# Install pipx if you don't have it
brew install pipx  # On Mac
# or
python3 -m pip install --user pipx

# Install packages
pipx install mcp
pipx install elevenlabs
```

## Setup Claude Desktop

1. Find your Claude Desktop config:
   - Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add this to the config:
```json
{
  "mcpServers": {
    "podcast-generator": {
      "command": "python3",
      "args": ["/path/to/podcast_server_simple.py"]
    }
  }
}
```

If using virtual environment, use the venv Python:
```json
{
  "mcpServers": {
    "podcast-generator": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/podcast_server_simple.py"]
    }
  }
}
```

## Usage

### Without ElevenLabs (Script Only)
The server works without ElevenLabs - it will generate scripts that you can read yourself.

### With ElevenLabs (Full Audio)
1. Sign up at https://elevenlabs.io
2. Get your API key from profile settings
3. Set environment variable:
   ```bash
   export ELEVENLABS_API_KEY="your-key-here"
   ```

### Tools Available

1. **generate_script** - Create a podcast script
   - `topic` (required): What to discuss
   - `duration_minutes`: Target length (default: 5)
   - `host_voice`: Adam, Brian, or Daniel
   - `guest_voice`: Alice, Charlotte, or Emily

2. **create_audio** - Generate audio files (requires ElevenLabs)
   - `script`: Output from generate_script
   - `output_dir`: Where to save files

## Troubleshooting

### "No module named 'mcp'"
Make sure you activated the virtual environment or installed with pipx.

### "ELEVENLABS_API_KEY not set"
The audio generation requires an API key. Scripts still work without it.

### Claude Desktop can't find the server
- Check the path in your config is absolute (not relative)
- Make sure Python path is correct (use `which python3` to find it)
- Restart Claude Desktop after config changes