#!/bin/bash
# Setup script for Enhanced Podcast Generator

echo "🎙️ Setting up Enhanced Podcast Generator..."

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv podcast_env
source podcast_env/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install mcp elevenlabs

# Check for API key
if [ -z "$ELEVENLABS_API_KEY" ]; then
    echo "⚠️  Warning: ELEVENLABS_API_KEY not set"
    echo "Please set your API key:"
    echo "export ELEVENLABS_API_KEY='your_key_here'"
fi

# Create output directory
echo "📁 Creating output directory..."
mkdir -p ~/Desktop/podcast_output

# Create sample configuration
echo "⚙️  Creating sample MCP configuration..."
cat > mcp_config_sample.json << 'EOF'
{
  "mcpServers": {
    "podcast-generator-enhanced": {
      "command": "python",
      "args": ["podcast_server_enhanced.py"],
      "env": {
        "ELEVENLABS_API_KEY": "your_elevenlabs_api_key_here"
      }
    }
  }
}
EOF

echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Set your ElevenLabs API key:"
echo "   export ELEVENLABS_API_KEY='your_key_here'"
echo ""
echo "2. Run the enhanced server:"
echo "   python podcast_server_enhanced.py"
echo ""
echo "3. Or add to your MCP configuration using mcp_config_sample.json"
echo ""
echo "🎯 Quick test:"
echo "   python -c \"from podcast_server_enhanced import generate_llm_optimized_prompt; print(generate_llm_optimized_prompt('AI Ethics', 'interview', 5, 2))\""