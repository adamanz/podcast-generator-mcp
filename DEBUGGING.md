# Debugging Guide - Podcast Generator MCP Server

> A comprehensive guide to debugging the Podcast Generator MCP server integration

This guide covers debugging tools and approaches specific to the Podcast Generator MCP server, building on general MCP debugging practices.

## Quick Start Debugging

### 1. Check Server Status
First, verify your server is properly configured:

```bash
# Test the simple server directly
python podcast_server_simple.py

# Test the enhanced server directly  
python podcast_mcp_server_enhanced.py
```

### 2. View Claude Desktop Logs
Monitor MCP logs to see connection and runtime issues:

```bash
# Follow logs in real-time
tail -n 20 -F ~/Library/Logs/Claude/mcp*.log
```

### 3. Test with MCP Inspector
Use the MCP Inspector for isolated testing:

```bash
# Install inspector if not already installed
npm install -g @modelcontextprotocol/inspector

# Test simple server
npx @modelcontextprotocol/inspector python podcast_server_simple.py

# Test enhanced server
npx @modelcontextprotocol/inspector python podcast_mcp_server_enhanced.py
```

## Common Issues & Solutions

### Configuration Issues

#### Claude Desktop Config
Ensure your `claude_desktop_config.json` uses absolute paths:

```json
{
  "mcpServers": {
    "podcast-generator": {
      "command": "python",
      "args": ["/absolute/path/to/podcast_server_simple.py"],
      "env": {
        "OPENAI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

#### Environment Variables
The server requires specific environment variables:

```bash
# Check if required variables are set
echo $OPENAI_API_KEY
echo $ELEVENLABS_API_KEY  # For enhanced version

# Set variables if missing
export OPENAI_API_KEY="your-key-here"
export ELEVENLABS_API_KEY="your-key-here"  # For enhanced version
```

### Server Connection Problems

#### Permission Issues
```bash
# Ensure Python script is executable
chmod +x podcast_server_simple.py
chmod +x podcast_mcp_server_enhanced.py

# Check Python path
which python
```

#### Dependency Issues
```bash
# Install required packages
pip install -r requirements_simple.txt
# or for enhanced version
pip install -r requirements.txt

# Verify installations
python -c "import mcp, openai; print('Dependencies OK')"
```

### Runtime Errors

#### API Key Issues
Common error: `openai.AuthenticationError`

**Solution:**
1. Verify API key is correct
2. Check key has proper permissions
3. Ensure key is set in environment

```python
# Add to server for debugging
import os
print(f"API Key present: {'OPENAI_API_KEY' in os.environ}")
```

#### Audio Generation Issues (Enhanced Version)
Common error: ElevenLabs API failures

**Debugging steps:**
1. Check ElevenLabs API key
2. Verify voice ID exists
3. Test with shorter text

### Tool Execution Problems

#### generate_podcast Tool
If podcast generation fails:

1. **Check input validation:**
   ```python
   # Debug in server code
   logging.info(f"Received topic: {topic}")
   logging.info(f"Received style: {style}")
   ```

2. **Monitor OpenAI API calls:**
   - Check rate limits
   - Verify model availability
   - Test with simpler prompts

3. **File system issues:**
   ```bash
   # Check write permissions
   ls -la /path/to/output/directory
   
   # Test file creation
   touch test_output.json
   ```

## Debugging Workflow

### 1. Development Testing
```bash
# Test server startup
python podcast_server_simple.py --debug

# Use inspector for tool testing
npx @modelcontextprotocol/inspector python podcast_server_simple.py
```

### 2. Integration Testing
```bash
# Restart Claude Desktop after config changes
# Use Command-R to reload after code changes

# Monitor logs during testing
tail -f ~/Library/Logs/Claude/mcp*.log | grep podcast
```

### 3. Production Debugging
```bash
# Check server process
ps aux | grep podcast

# Monitor resource usage
top -p $(pgrep -f podcast_server)
```

## Logging Implementation

### Server-Side Logging
Add comprehensive logging to your server:

```python
import logging
import sys

# Configure logging to stderr (captured by Claude Desktop)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger("podcast-generator")

# Log important events
logger.info("Server starting up")
logger.info(f"Available tools: {len(server.list_tools())}")
logger.error(f"API call failed: {error}")
```

### Client-Side Debugging
Enable Chrome DevTools in Claude Desktop:

```bash
# Create developer settings
echo '{"allowDevTools": true}' > ~/Library/Application\ Support/Claude/developer_settings.json

# Open DevTools: Command-Option-Shift-i
```

## Performance Monitoring

### Track Key Metrics
```python
import time

def generate_podcast_with_metrics(topic, style, duration):
    start_time = time.time()
    logger.info(f"Starting podcast generation: {topic}")
    
    try:
        result = generate_podcast(topic, style, duration)
        execution_time = time.time() - start_time
        logger.info(f"Podcast generated in {execution_time:.2f}s")
        return result
    except Exception as e:
        logger.error(f"Generation failed after {time.time() - start_time:.2f}s: {e}")
        raise
```

### Monitor API Usage
```python
# Track OpenAI API calls
api_calls = 0
total_tokens = 0

def track_api_usage(response):
    global api_calls, total_tokens
    api_calls += 1
    total_tokens += response.usage.total_tokens
    logger.info(f"API calls: {api_calls}, Total tokens: {total_tokens}")
```

## Troubleshooting Checklist

### Before Reporting Issues
- [ ] Server starts without errors
- [ ] All dependencies installed
- [ ] API keys configured correctly
- [ ] Configuration file syntax valid
- [ ] Logs show connection to Claude Desktop
- [ ] Tools appear in Claude interface
- [ ] Test with MCP Inspector passes

### Information to Provide
When seeking help, include:

1. **Server version:** Simple or Enhanced
2. **Error messages:** From logs and console
3. **Configuration:** `claude_desktop_config.json` (sanitized)
4. **Steps to reproduce:** Exact sequence
5. **Environment:** Python version, OS, dependencies

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: No module named 'mcp'` | Missing dependencies | Run `pip install -r requirements_simple.txt` |
| `openai.AuthenticationError` | Invalid API key | Check and reset `OPENAI_API_KEY` |
| `Connection refused` | Server not running | Verify server process and configuration |
| `JSON decode error` | Invalid response format | Check API response format |

## Getting Help

1. **Check logs first:** Most issues are revealed in the logs
2. **Test in isolation:** Use MCP Inspector before Claude Desktop
3. **GitHub Issues:** Report bugs with full context
4. **Include logs:** Sanitized log excerpts help diagnosis

## Next Steps

- Use MCP Inspector for development testing
- Monitor logs during production use  
- Implement structured logging for better debugging
- Consider adding health check endpoints for monitoring