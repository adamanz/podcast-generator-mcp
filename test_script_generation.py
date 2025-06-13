#!/usr/bin/env python3
"""
Test script to generate a podcast script directly
"""

import os
import sys
import asyncio
import json

# Add the current directory to the path so we can import the server
sys.path.append('.')

async def generate_test_script():
    """Generate a tax strategy podcast script"""
    
    # Simple AI-driven script generation logic
    topic = "2025 Tax Strategy: Optimizing Combined W-2 and LLC Income"
    duration_minutes = 5
    num_speakers = 2
    
    # Calculate approximate words needed (150 words per minute for podcast)
    target_words = duration_minutes * 150
    
    # Create a structured script
    script = {
        "title": f"Podcast: {topic}",
        "description": f"A {duration_minutes}-minute discussion about {topic}",
        "duration_minutes": duration_minutes,
        "speakers": [
            {"name": "Host", "role": "host", "personality": "curious and engaging"},
            {"name": "Expert", "role": "guest", "personality": "knowledgeable tax professional"}
        ],
        "segments": []
    }
    
    # Introduction segment
    intro_segment = {
        "type": "introduction",
        "dialogue": [
            {
                "speaker": "Host",
                "text": f"Welcome to Tax Strategy Today! I'm your host, and today we're diving deep into {topic}. This is especially relevant as we approach the 2025 tax season and many professionals are looking to optimize their income strategies."
            },
            {
                "speaker": "Expert", 
                "text": "Thanks for having me! This is indeed a critical topic. With the evolving tax landscape and the increasing popularity of side businesses and LLCs, understanding how to effectively manage both W-2 and LLC income has never been more important."
            }
        ]
    }
    script["segments"].append(intro_segment)
    
    # Main content segments
    main_topics = [
        {
            "topic": "Understanding the Dual Income Structure",
            "host_question": "Let's start with the basics. Can you explain what it means to have combined W-2 and LLC income, and why this is becoming so common?",
            "expert_response": "Absolutely. Many professionals today have a traditional W-2 job - maybe they're an engineer, teacher, or marketing manager - but they also run a side business through an LLC. This could be consulting, freelancing, e-commerce, or any entrepreneurial venture. The tax implications are quite different for each income stream, which creates both opportunities and complexities."
        },
        {
            "topic": "Key Tax Optimization Strategies",
            "host_question": "What are the main strategies people should consider when optimizing taxes across both income sources?",
            "expert_response": "There are several key strategies. First, maximizing business deductions through your LLC - things like home office expenses, business travel, equipment, and professional development. Second, understanding self-employment tax implications and strategies like S-Corp elections. Third, timing income and expenses strategically between your W-2 and LLC. And fourth, optimizing retirement contributions across both income sources."
        },
        {
            "topic": "Common Mistakes to Avoid",
            "host_question": "What are some common mistakes you see people making with this dual income approach?",
            "expert_response": "The biggest mistake is poor record keeping. You need to clearly separate business and personal expenses. Another common error is not understanding the quarterly estimated tax payments required for LLC income. Many people also miss out on legitimate business deductions because they don't track expenses properly. Finally, some people don't consider the impact on their overall tax bracket when both income sources are combined."
        }
    ]
    
    for topic_info in main_topics:
        segment = {
            "type": "discussion",
            "topic": topic_info["topic"],
            "dialogue": [
                {
                    "speaker": "Host",
                    "text": topic_info["host_question"]
                },
                {
                    "speaker": "Expert",
                    "text": topic_info["expert_response"]
                }
            ]
        }
        script["segments"].append(segment)
    
    # Closing segment
    closing_segment = {
        "type": "conclusion",
        "dialogue": [
            {
                "speaker": "Host",
                "text": "This has been incredibly informative. What's your top piece of advice for someone just starting to navigate combined W-2 and LLC income?"
            },
            {
                "speaker": "Expert",
                "text": "Start with proper organization and record keeping from day one. Use separate bank accounts, track all business expenses, and consider working with a tax professional who understands both traditional employment and business taxation. The key is being proactive rather than reactive when tax season arrives."
            },
            {
                "speaker": "Host",
                "text": "Excellent advice! Thank you so much for sharing your expertise on optimizing combined W-2 and LLC income strategies for 2025. For our listeners, remember that tax situations are individual, so always consult with a qualified tax professional for your specific circumstances. Thanks for tuning in to Tax Strategy Today!"
            }
        ]
    }
    script["segments"].append(closing_segment)
    
    # Calculate actual word count
    total_words = 0
    for segment in script["segments"]:
        for dialogue in segment["dialogue"]:
            total_words += len(dialogue["text"].split())
    
    script["estimated_word_count"] = total_words
    script["estimated_duration_minutes"] = round(total_words / 150, 1)
    
    return script

async def main():
    """Main function to generate and display the script"""
    print("🎙️ Generating Tax Strategy Podcast Script...")
    
    script = await generate_test_script()
    
    print(json.dumps(script, indent=2))
    
    print(f"\n📊 Script Statistics:")
    print(f"   • Word Count: {script['estimated_word_count']}")
    print(f"   • Estimated Duration: {script['estimated_duration_minutes']} minutes")
    print(f"   • Number of Segments: {len(script['segments'])}")

if __name__ == "__main__":
    asyncio.run(main())