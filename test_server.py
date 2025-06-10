#!/usr/bin/env python3
"""
Test if the enhanced server can start
"""
import sys
import subprocess
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_server_start():
    """Test if server starts without errors"""
    print("🧪 Testing server startup...")
    
    # Try to start the server and immediately kill it
    try:
        process = subprocess.Popen(
            [sys.executable, "podcast_mcp_server_enhanced.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start
        import time
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Server started successfully!")
            # Kill the process
            process.terminate()
            process.wait()
            return True
        else:
            # Process died - get error
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start")
            if stderr:
                print(f"Error: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

if __name__ == "__main__":
    # Check environment
    if os.getenv("ELEVENLABS_API_KEY"):
        print("✅ ELEVENLABS_API_KEY is set")
    else:
        print("⚠️  ELEVENLABS_API_KEY not set - using demo mode")
    
    # Test server
    if test_server_start():
        print("\n✨ Server is ready to use!")
        print("\nTo run the server:")
        print("  python podcast_mcp_server_enhanced.py")
    else:
        print("\n⚠️  Please check the errors above")