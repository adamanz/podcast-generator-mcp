#!/bin/bash
# Installation script for Podcast Generator MCP

echo "🎙️ Podcast Generator MCP - Installation Script"
echo "============================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION detected"

# Check if venv module is available
if ! python3 -c "import venv" &> /dev/null; then
    echo "❌ Python venv module not found. Please install python3-venv."
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing requirements..."
pip install -r requirements.txt

# Check if ffmpeg is installed
echo ""
if command -v ffmpeg &> /dev/null; then
    echo "✅ ffmpeg is installed"
else
    echo "⚠️  ffmpeg is not installed. Please install it:"
    echo "   macOS: brew install ffmpeg"
    echo "   Ubuntu: sudo apt install ffmpeg"
    echo "   Windows: choco install ffmpeg"
fi

# Check for ElevenLabs API key
echo ""
if [ -z "$ELEVENLABS_API_KEY" ]; then
    echo "⚠️  ELEVENLABS_API_KEY environment variable not set"
    echo "   To set it: export ELEVENLABS_API_KEY='your-key-here'"
else
    echo "✅ ELEVENLABS_API_KEY is configured"
fi

echo ""
echo "============================================="
echo "✅ Installation complete!"
echo ""
echo "To use the server:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Set your API key: export ELEVENLABS_API_KEY='your-key'"
echo "3. Run the server: python podcast_mcp_server_enhanced.py"
echo ""
echo "For Claude Desktop integration, add this to your config:"
echo '  "podcast-generator": {'
echo '    "command": "python",'
echo "    \"args\": [\"$(pwd)/podcast_mcp_server_enhanced.py\"],"
echo '    "env": {'
echo '      "ELEVENLABS_API_KEY": "your-key"'
echo '    }'
echo '  }'