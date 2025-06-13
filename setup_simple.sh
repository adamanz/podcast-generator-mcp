#!/bin/bash
# Simple setup script for podcast generator

echo "🎙️ Setting up Simple Podcast Generator..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Install pip if needed
if ! python3 -m pip --version &> /dev/null; then
    echo "📦 Installing pip..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py --user
    rm get-pip.py
fi

# Install requirements
echo "📦 Installing dependencies..."
python3 -m pip install --user -r requirements_simple.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To use with Claude Desktop:"
echo "1. Set your ElevenLabs API key (optional):"
echo "   export ELEVENLABS_API_KEY='your-key-here'"
echo ""
echo "2. Update your Claude Desktop config:"
echo "   ~/.config/claude/claude_desktop_config.json (Linux/Mac)"
echo "   %APPDATA%\Claude\claude_desktop_config.json (Windows)"
echo ""
echo "Add this to mcpServers:"
echo '{'
echo '  "podcast-generator": {'
echo '    "command": "python3",'
echo '    "args": ["'$(pwd)'/podcast_server_simple.py"]'
echo '  }'
echo '}'