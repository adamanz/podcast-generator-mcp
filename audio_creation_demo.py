#!/usr/bin/env python3
"""
Demo script showing how to use the create_audio tool with the tax strategy podcast script.
This demonstrates the exact parameters needed for the create_audio tool call.
"""

import json
import os

# The complete script content for "2025 Tax Strategy: Optimizing Combined W-2 and LLC Income"
SCRIPT_JSON = {
    "title": "2025 Tax Strategy: Optimizing Combined W-2 and LLC Income",
    "description": "A comprehensive guide to maximizing tax efficiency when earning from both employment and business income",
    "dialogue": [
        {"speaker": "host", "text": "Welcome to Tax Strategy Today! I'm here with Sarah, a CPA who specializes in helping professionals optimize their tax situation when they have both W-2 and business income. Sarah, this is such a relevant topic for 2025!"},
        {"speaker": "guest", "text": "Thanks for having me! You're absolutely right - we're seeing more people than ever with side businesses or consulting work alongside their day jobs. The tax implications can be complex, but there are some real opportunities to save money."},
        {"speaker": "host", "text": "Let's start with the basics. What's the fundamental difference in how W-2 and LLC income are taxed?"},
        {"speaker": "guest", "text": "Great question! W-2 income is subject to payroll taxes that are split between you and your employer. But with LLC income, you're paying self-employment tax on the full amount. However, you also get access to business deductions that W-2 employees can't claim."},
        {"speaker": "host", "text": "So it's not just about the tax rate - it's about what you can deduct?"},
        {"speaker": "guest", "text": "Exactly! Business expenses, home office deductions, equipment purchases - these can significantly reduce your taxable LLC income. Plus, there's the QBI deduction which can give you up to a 20% deduction on qualified business income."},
        {"speaker": "host", "text": "The QBI deduction sounds powerful. How does that work when you have both types of income?"},
        {"speaker": "guest", "text": "The QBI deduction is calculated separately from your W-2 income. So if your LLC generates qualifying income, you could potentially deduct 20% of that, subject to certain limitations based on your total income."},
        {"speaker": "host", "text": "What about retirement planning? I imagine having both income sources opens up more options?"},
        {"speaker": "guest", "text": "Absolutely! With W-2 income, you might max out your 401k. But LLC income allows you to also contribute to a SEP-IRA or Solo 401k, potentially allowing you to save much more for retirement while reducing current taxes."},
        {"speaker": "host", "text": "That's a huge advantage. Are there any pitfalls people should watch out for?"},
        {"speaker": "guest", "text": "The biggest mistake I see is not making quarterly estimated tax payments on LLC income. Unlike W-2 income where taxes are withheld automatically, you're responsible for paying as you go. Miss those payments and you'll face penalties."},
        {"speaker": "host", "text": "What's your top piece of advice for someone just starting to navigate this dual-income situation?"},
        {"speaker": "guest", "text": "Track everything! Keep meticulous records of business expenses, and consider working with a tax professional who understands both sides. The tax savings from proper planning often far exceed the cost of professional help."},
        {"speaker": "host", "text": "Excellent advice, Sarah. Thanks for breaking down these complex tax strategies in such a clear way. For our listeners, remember that tax planning is a year-round activity, not just something to think about in April!"},
        {"speaker": "guest", "text": "Thanks for having me! And yes, the earlier you start optimizing your tax strategy, the more you can save."}
    ]
}

def convert_json_to_script_text(script_json):
    """Convert JSON dialogue format to plain text script format."""
    script_text = ""
    for line in script_json["dialogue"]:
        speaker = line["speaker"].title()
        text = line["text"]
        script_text += f"{speaker}: {text}\n\n"
    return script_text

def create_audio_tool_parameters():
    """Generate the exact parameters needed for the create_audio tool."""
    script_text = convert_json_to_script_text(SCRIPT_JSON)
    
    tool_parameters = {
        "script": script_text,
        "voice": "nova",
        "output_filename": "tax_strategy_2025_podcast.mp3"
    }
    
    return tool_parameters

def main():
    print("=== 2025 Tax Strategy Podcast Audio Creation Demo ===\n")
    
    # Show the original JSON script
    print("📄 Original Script (JSON format):")
    print(json.dumps(SCRIPT_JSON, indent=2))
    print("\n" + "="*80 + "\n")
    
    # Show the converted plain text script
    script_text = convert_json_to_script_text(SCRIPT_JSON)
    print("📝 Converted Script (Plain text format for create_audio tool):")
    print(script_text)
    print("="*80 + "\n")
    
    # Show the exact tool parameters
    params = create_audio_tool_parameters()
    print("🎙️ create_audio Tool Parameters:")
    print(json.dumps(params, indent=2))
    print("\n" + "="*80 + "\n")
    
    # Show setup requirements
    print("⚙️  Setup Requirements:")
    print("1. Set ElevenLabs API key: export ELEVENLABS_API_KEY='your-api-key-here'")
    print("2. Install dependencies: pip install -r requirements_simple.txt")
    print("3. Run the simple server: python3 podcast_server_simple.py")
    print("4. Use the create_audio tool with the parameters shown above")
    print("\n" + "="*80 + "\n")
    
    # Show expected output
    print("📁 Expected Output:")
    print("- Audio file: ~/Desktop/podcast_output/tax_strategy_2025_podcast.mp3")
    print("- Voice: Nova (ElevenLabs)")
    print("- Duration: ~8-10 minutes (estimated based on script length)")
    print("- Format: MP3")
    
    # Check current environment
    print("\n" + "="*80 + "\n")
    print("🔍 Current Environment Status:")
    api_key_set = bool(os.getenv("ELEVENLABS_API_KEY"))
    print(f"ElevenLabs API Key: {'✅ Set' if api_key_set else '❌ Not set'}")
    
    if not api_key_set:
        print("\n⚠️  To create the audio file, you need to:")
        print("   1. Get an ElevenLabs API key from https://elevenlabs.io")
        print("   2. Set it as an environment variable: export ELEVENLABS_API_KEY='your-key'")
        print("   3. Then run the create_audio tool with the parameters shown above")

if __name__ == "__main__":
    main()