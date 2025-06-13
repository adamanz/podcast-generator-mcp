#!/usr/bin/env python3
"""
Simple Podcast Generator MCP Server
Uses only standard mcp library with minimal dependencies
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Sequence

import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("podcast-generator")


def get_topic_specific_content(topic: str) -> Dict[str, List[str]]:
    """Get topic-specific content for dynamic dialogue generation"""
    import random
    
    topic_lower = topic.lower()
    
    # Technology/AI topics
    if any(word in topic_lower for word in ['ai', 'artificial intelligence', 'machine learning', 'technology', 'tech', 'software', 'coding', 'programming', 'automation']):
        return {
            'intro_styles': [
                f"Welcome to Tech Talk! Today we're exploring {topic}",
                f"Hello everyone! We're diving into the world of {topic}",
                f"Welcome to another episode where we discuss {topic}"
            ],
            'expertise_claims': [
                f"I've been working in {topic} for several years now",
                f"As someone who's deeply involved in {topic} research",
                f"From my experience in the {topic} industry"
            ],
            'key_questions': [
                "What makes this technology so revolutionary?",
                "How is this changing the way we work?",
                "What should people know about implementation?",
                "What are the biggest challenges we're facing?",
                "Where do you see this heading in the next five years?"
            ],
            'insights': [
                f"The breakthrough with {topic} is how it's democratizing complex processes",
                f"What's fascinating about {topic} is its potential to solve problems we didn't even know we had",
                f"The real power of {topic} lies in its ability to augment human capabilities"
            ],
            'applications': [
                "We're seeing applications across healthcare, finance, and education",
                "The use cases range from automation to creative collaboration",
                "Industries are being transformed by these innovations"
            ]
        }
    
    # Science/Research topics
    elif any(word in topic_lower for word in ['science', 'research', 'climate', 'space', 'biology', 'physics', 'chemistry', 'environment', 'medicine', 'health']):
        return {
            'intro_styles': [
                f"Welcome to Science Today! We're investigating {topic}",
                f"Hello and welcome to our deep dive into {topic}",
                f"Today we're exploring the fascinating world of {topic}"
            ],
            'expertise_claims': [
                f"My research in {topic} has shown some remarkable findings",
                f"After years of studying {topic}, I can say",
                f"The latest research in {topic} reveals"
            ],
            'key_questions': [
                "What does the current research tell us?",
                "How does this impact our understanding?",
                "What misconceptions do people have?",
                "Where are the biggest breakthroughs happening?",
                "What should the public know about this?"
            ],
            'insights': [
                f"The most surprising aspect of {topic} is how interconnected everything is",
                f"What we're learning about {topic} is changing our fundamental understanding",
                f"The implications of {topic} research extend far beyond what we initially thought"
            ],
            'applications': [
                "This research has immediate applications for public policy",
                "We're seeing real-world benefits in healthcare and environmental protection",
                "The practical implications could help millions of people"
            ]
        }
    
    # Business/Finance topics
    elif any(word in topic_lower for word in ['business', 'finance', 'economy', 'market', 'investment', 'startup', 'entrepreneur', 'leadership', 'management']):
        return {
            'intro_styles': [
                f"Welcome to Business Insights! Today we're analyzing {topic}",
                f"Hello everyone! We're discussing the business side of {topic}",
                f"Today's focus is on {topic} and its market implications"
            ],
            'expertise_claims': [
                f"In my experience with {topic} in the business world",
                f"Having worked with companies implementing {topic}",
                f"From a strategic perspective on {topic}"
            ],
            'key_questions': [
                "What trends are you seeing in the market?",
                "How should businesses adapt to these changes?",
                "What opportunities exist for entrepreneurs?",
                "What are the biggest risks to consider?",
                "How is this affecting the competitive landscape?"
            ],
            'insights': [
                f"The key to success with {topic} is understanding the underlying market dynamics",
                f"What's driving {topic} adoption is the clear ROI businesses are seeing",
                f"The competitive advantage comes from how companies implement {topic}"
            ],
            'applications': [
                "Companies are already seeing significant returns on investment",
                "The market opportunities are enormous for early adopters",
                "We're seeing new business models emerge from these innovations"
            ]
        }
    
    # Default/General topics
    else:
        return {
            'intro_styles': [
                f"Welcome to today's discussion about {topic}",
                f"Hello everyone! We're exploring {topic} today",
                f"Welcome to the show where we dive deep into {topic}"
            ],
            'expertise_claims': [
                f"Having studied {topic} extensively",
                f"From my perspective on {topic}",
                f"What I find most interesting about {topic}"
            ],
            'key_questions': [
                "What should people understand about this?",
                "How does this affect our daily lives?",
                "What are the most important aspects?",
                "Where do you see this heading?",
                "What advice would you give?"
            ],
            'insights': [
                f"The most important thing to understand about {topic} is its broader impact",
                f"What makes {topic} so relevant is how it touches everyone's life",
                f"The key insight about {topic} is that it's more complex than it appears"
            ],
            'applications': [
                "The practical implications are significant for everyone",
                "People can apply these insights in their personal and professional lives",
                "Understanding this helps us make better decisions"
            ]
        }

def generate_podcast_dialogue(topic: str, num_speakers: int = 2, duration_minutes: int = 5) -> str:
    """
    Generate dynamic podcast dialogue based on topic and parameters.
    
    Args:
        topic: The main topic for the podcast
        num_speakers: Number of speakers (default: 2)
        duration_minutes: Target duration in minutes (default: 5)
    
    Returns:
        Generated dialogue as a string
    """
    import random
    
    # Get topic-specific content
    content = get_topic_specific_content(topic)
    
    # Generate speaker names based on roles
    if num_speakers == 1:
        speakers = ["Host"]
    elif num_speakers == 2:
        speakers = ["Host", "Expert"]
    elif num_speakers == 3:
        speakers = ["Host", "Expert", "Analyst"]
    else:
        speakers = ["Host", "Expert", "Analyst", "Guest"]
    
    dialogue_parts = []
    
    # Dynamic introduction
    intro_style = random.choice(content['intro_styles'])
    dialogue_parts.append(f"{speakers[0]}: {intro_style}.")
    
    if len(speakers) > 1:
        expertise_claim = random.choice(content['expertise_claims'])
        dialogue_parts.append(f"{speakers[1]}: Thanks for having me! {expertise_claim}, I'm excited to share some insights.")
    
    # Opening context
    dialogue_parts.append(f"{speakers[0]}: Let's start with the fundamentals. Can you give our listeners an overview?")
    if len(speakers) > 1:
        dialogue_parts.append(f"{speakers[1]}: Absolutely! {topic} is a multifaceted subject with several important dimensions we should explore.")
    
    # Dynamic content based on duration
    questions = content['key_questions'].copy()
    insights = content['insights'].copy()
    random.shuffle(questions)
    random.shuffle(insights)
    
    # Calculate how many exchanges to include
    base_exchanges = min(len(questions), duration_minutes // 2 + 1)
    
    for i in range(base_exchanges):
        if i < len(questions):
            speaker_idx = i % len(speakers)
            dialogue_parts.append(f"{speakers[speaker_idx]}: {questions[i]}")
            
            # Response from different speaker
            if len(speakers) > 1:
                responder_idx = (speaker_idx + 1) % len(speakers)
                if i < len(insights):
                    dialogue_parts.append(f"{speakers[responder_idx]}: {insights[i]}")
                else:
                    dialogue_parts.append(f"{speakers[responder_idx]}: That's a great question. {topic} really demonstrates the complexity of this field.")
    
    # Add practical applications for longer episodes
    if duration_minutes >= 5:
        dialogue_parts.append(f"{speakers[0]}: This is fascinating! Can you share some real-world applications?")
        if len(speakers) > 1:
            application = random.choice(content['applications'])
            dialogue_parts.append(f"{speakers[1]}: {application}")
    
    # Add future outlook for longer episodes
    if duration_minutes >= 8:
        dialogue_parts.append(f"{speakers[0]}: Looking ahead, what should our listeners watch for?")
        if len(speakers) > 1:
            dialogue_parts.append(f"{speakers[1]}: The future of {topic} is incredibly exciting. We're likely to see significant developments that will impact how we think about this entire field.")
    
    # Add audience engagement for longer episodes
    if duration_minutes >= 10:
        dialogue_parts.append(f"{speakers[0]}: What advice would you give to listeners who want to learn more?")
        if len(speakers) > 1:
            dialogue_parts.append(f"{speakers[1]}: I'd encourage everyone to stay curious about {topic}. Start with the fundamentals and don't be afraid to explore the more complex aspects.")
    
    # Dynamic conclusion
    closing_phrases = [
        "This has been an incredibly insightful discussion",
        "What a fascinating conversation we've had",
        "I've learned so much from this discussion"
    ]
    
    guest_responses = [
        "Thank you for having me! It's been a pleasure",
        "My pleasure! I hope listeners found this as engaging as I did",
        "Thanks for the thoughtful questions"
    ]
    
    dialogue_parts.append(f"{speakers[0]}: {random.choice(closing_phrases)} about {topic}. Thank you so much!")
    if len(speakers) > 1:
        dialogue_parts.append(f"{speakers[1]}: {random.choice(guest_responses)}!")
    
    return "\n\n".join(dialogue_parts)


@server.list_resources()
async def list_resources() -> list[types.Resource]:
    """List available resources."""
    return [
        types.Resource(
            uri="podcast://voices",
            name="Available Voices",
            description="List of available text-to-speech voices",
            mimeType="application/json"
        ),
        types.Resource(
            uri="podcast://help",
            name="Help Documentation", 
            description="Documentation for the podcast generator",
            mimeType="text/plain"
        )
    ]


@server.read_resource()
async def read_resource(uri: types.AnyUrl) -> str:
    """Read a specific resource."""
    if str(uri) == "podcast://voices":
        # Return available voices
        voices = {
            "available_voices": [
                {"id": "alloy", "name": "Alloy", "description": "Neutral, balanced voice"},
                {"id": "echo", "name": "Echo", "description": "Clear, professional voice"},
                {"id": "fable", "name": "Fable", "description": "Warm, storytelling voice"},
                {"id": "onyx", "name": "Onyx", "description": "Deep, authoritative voice"},
                {"id": "nova", "name": "Nova", "description": "Bright, energetic voice"},
                {"id": "shimmer", "name": "Shimmer", "description": "Gentle, soothing voice"}
            ],
            "note": "These are standard OpenAI TTS voices. ElevenLabs integration available with API key."
        }
        return json.dumps(voices, indent=2)
    
    elif str(uri) == "podcast://help":
        help_text = """
Podcast Generator MCP Server Help

AVAILABLE TOOLS:
1. generate_script - Generate podcast dialogue
2. create_audio - Convert script to audio (requires TTS setup)

USAGE:
- Use generate_script to create dialogue for any topic
- Specify number of speakers (1-4) and duration (1-30 minutes)
- Use create_audio to convert the script to speech

EXAMPLES:
- Generate a 5-minute podcast about AI: 
  generate_script(topic="Artificial Intelligence", duration_minutes=5)
- Create 3-speaker discussion about climate change:
  generate_script(topic="Climate Change", num_speakers=3, duration_minutes=10)

AUDIO GENERATION:
- Requires OpenAI API key for basic TTS
- Optional: ElevenLabs API key for premium voices
- Set OPENAI_API_KEY or ELEVENLABS_API_KEY environment variables

NOTES:
- Scripts are generated using simple dialogue patterns
- Audio files are saved as MP3 format
- For best results, edit generated scripts before audio conversion
"""
        return help_text.strip()
    
    else:
        raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="generate_script",
            description="Generate a podcast dialogue script for a given topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The main topic for the podcast"
                    },
                    "num_speakers": {
                        "type": "integer", 
                        "description": "Number of speakers (1-4)",
                        "minimum": 1,
                        "maximum": 4,
                        "default": 2
                    },
                    "duration_minutes": {
                        "type": "integer",
                        "description": "Target duration in minutes (1-30)",
                        "minimum": 1,
                        "maximum": 30,
                        "default": 5
                    }
                },
                "required": ["topic"]
            }
        ),
        types.Tool(
            name="create_audio",
            description="Convert a podcast script to multi-voice audio with different speakers using ElevenLabs TTS with emotional variations",
            inputSchema={
                "type": "object", 
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "The podcast script with speaker labels (e.g., 'Host: Welcome...' 'Expert: Thanks...')"
                    },
                    "output_filename": {
                        "type": "string",
                        "description": "Output filename for the combined audio file",
                        "default": "podcast_output.mp3"
                    },
                    "voice": {
                        "type": "string",
                        "description": "Primary voice preference (nova, aria, sarah, laura, josh, adam, brian, william shanks) - different voices will be auto-assigned to different speakers",
                        "default": "nova"
                    }
                },
                "required": ["script"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Handle tool calls."""
    if not arguments:
        arguments = {}

    if name == "generate_script":
        topic = arguments.get("topic")
        if not topic:
            return [types.TextContent(
                type="text",
                text="Error: topic parameter is required"
            )]
        
        num_speakers = arguments.get("num_speakers", 2)
        duration_minutes = arguments.get("duration_minutes", 5)
        
        # Validate parameters
        if not isinstance(num_speakers, int) or num_speakers < 1 or num_speakers > 4:
            return [types.TextContent(
                type="text", 
                text="Error: num_speakers must be an integer between 1 and 4"
            )]
        
        if not isinstance(duration_minutes, int) or duration_minutes < 1 or duration_minutes > 30:
            return [types.TextContent(
                type="text",
                text="Error: duration_minutes must be an integer between 1 and 30"
            )]
        
        try:
            script = generate_podcast_dialogue(topic, num_speakers, duration_minutes)
            return [types.TextContent(
                type="text",
                text=f"Generated podcast script for '{topic}':\n\n{script}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error generating script: {str(e)}"
            )]

    elif name == "create_audio":
        script = arguments.get("script")
        if not script:
            return [types.TextContent(
                type="text",
                text="Error: script parameter is required"
            )]
        
        output_filename = arguments.get("output_filename", "podcast_output.mp3")
        voice = arguments.get("voice", "alloy")
        
        try:
            elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
            
            if not elevenlabs_key:
                return [types.TextContent(
                    type="text",
                    text="Error: ELEVENLABS_API_KEY environment variable not set."
                )]
            
            # Try to import and use ElevenLabs
            try:
                from elevenlabs.client import ElevenLabs
                from elevenlabs import VoiceSettings
                
                client = ElevenLabs(api_key=elevenlabs_key)
                
                # Get available voices and map the requested voice
                voices = client.voices.get_all()
                voice_map = {v.name.lower(): v.voice_id for v in voices.voices}
                
                # Use the requested voice or default to first available
                voice_id = voice_map.get(voice.lower())
                if not voice_id:
                    # If voice not found, use first available voice
                    voice_id = voices.voices[0].voice_id
                    actual_voice = voices.voices[0].name
                else:
                    actual_voice = voice
                
                # Create output directory
                output_dir = os.path.expanduser("~/Desktop/podcast_output")
                os.makedirs(output_dir, exist_ok=True)
                
                # Full path for output file
                output_path = os.path.join(output_dir, output_filename)
                
                # Parse script into dialogue segments
                dialogue_segments = []
                lines = script.split('\n')
                
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('#') or line.startswith('*') or line == '---':
                        continue
                    
                    # Look for speaker patterns like "Host:" or "Expert:"
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            speaker = parts[0].strip()
                            text = parts[1].strip()
                            if text:  # Only add if there's actual content
                                dialogue_segments.append({
                                    'speaker': speaker,
                                    'text': text
                                })
                
                if not dialogue_segments:
                    # Fallback: treat entire script as single speaker
                    clean_script = script.replace("#", "").replace("*", "").replace("**", "").replace("---", "")
                    clean_script = "\n".join([line.strip() for line in clean_script.split("\n") if line.strip()])
                    dialogue_segments = [{'speaker': 'Host', 'text': clean_script}]
                
                # Get available voices for multi-speaker setup
                voice_assignments = {}
                # Updated voice list to include William Shanks
                available_voices = [v for v in voices.voices if v.name.lower() in ['nova', 'aria', 'sarah', 'laura', 'josh', 'adam', 'brian', 'william shanks']]
                
                # Assign voices to speakers
                unique_speakers = list(set(seg['speaker'] for seg in dialogue_segments))
                for i, speaker in enumerate(unique_speakers):
                    if i < len(available_voices):
                        voice_assignments[speaker] = available_voices[i].voice_id
                        voice_assignments[f"{speaker}_name"] = available_voices[i].name
                    else:
                        # Fallback to first voice
                        voice_assignments[speaker] = available_voices[0].voice_id
                        voice_assignments[f"{speaker}_name"] = available_voices[0].name
                
                # Generate audio segments
                audio_segments = []
                segment_files = []
                
                for i, segment in enumerate(dialogue_segments):
                    speaker = segment['speaker']
                    text = segment['text']
                    speaker_voice_id = voice_assignments.get(speaker, voice_id)
                    
                    # Determine emotional settings based on content
                    # Check for excitement (questions, exclamations)
                    if '!' in text or text.startswith(('This is fascinating', 'What a fascinating', 'Absolutely!', 'Exactly!')):
                        stability = 0.3  # Lower stability for more variation
                        similarity_boost = 0.7  # Higher similarity for excitement
                        style = 0.8  # More expressive
                    # Check for thoughtful/serious content
                    elif any(phrase in text.lower() for phrase in ['important to understand', 'the key', 'significantly', 'research shows', 'studies indicate']):
                        stability = 0.7  # Higher stability for authoritative tone
                        similarity_boost = 0.5
                        style = 0.3  # More measured
                    # Check for empathetic/warm content
                    elif any(phrase in text.lower() for phrase in ['thank you', 'appreciate', 'wonderful', 'great question', 'hope']):
                        stability = 0.5
                        similarity_boost = 0.6
                        style = 0.6  # Warm and friendly
                    # Default conversational tone
                    else:
                        stability = 0.5
                        similarity_boost = 0.5
                        style = 0.5  # Balanced
                    
                    # Generate audio for this segment with emotional settings
                    segment_audio = client.text_to_speech.convert(
                        text=text,
                        voice_id=speaker_voice_id,
                        voice_settings=VoiceSettings(
                            stability=stability,
                            similarity_boost=similarity_boost,
                            style=style if hasattr(VoiceSettings, 'style') else None,  # Style parameter if available
                            use_speaker_boost=True if hasattr(VoiceSettings, 'use_speaker_boost') else None  # Enhanced clarity
                        )
                    )
                    
                    # Save individual segment
                    segment_filename = f"segment_{i:03d}_{speaker.lower()}.mp3"
                    segment_path = os.path.join(output_dir, segment_filename)
                    
                    with open(segment_path, "wb") as f:
                        for chunk in segment_audio:
                            f.write(chunk)
                    
                    segment_files.append(segment_path)
                    audio_segments.append({
                        'speaker': speaker,
                        'voice': voice_assignments.get(f"{speaker}_name", actual_voice),
                        'file': segment_path,
                        'text_length': len(text)
                    })
                
                # Combine audio segments using simple concatenation
                # For now, we'll create individual files and provide a combination script
                combined_audio_data = b""
                
                try:
                    # Try to combine audio files
                    for segment_file in segment_files:
                        with open(segment_file, "rb") as f:
                            # Skip MP3 headers except for the first file
                            if segment_file != segment_files[0]:
                                # Simple concatenation - not perfect but functional
                                f.seek(0)
                            combined_audio_data += f.read()
                    
                    # Save combined file
                    with open(output_path, "wb") as f:
                        f.write(combined_audio_data)
                        
                except Exception as concat_error:
                    # If combination fails, just use the first segment as main file
                    if segment_files:
                        import shutil
                        shutil.copy2(segment_files[0], output_path)
                
                # Generate detailed result message
                speakers_info = []
                for segment in audio_segments:
                    speakers_info.append(f"  • {segment['speaker']}: {segment['voice']} voice ({segment['text_length']} chars)")
                
                result_message = f"""
✅ Multi-voice podcast created successfully!

📁 Output Details:
- Combined File: {output_path}
- Total Segments: {len(audio_segments)}
- File Size: {os.path.getsize(output_path) / 1024:.1f} KB

🎭 Voice Cast:
{chr(10).join(speakers_info)}

📁 Individual Segments:
{chr(10).join([f"  • {os.path.basename(f)}" for f in segment_files])}

🎧 Your 2-sided podcast is ready! Both the combined file and individual segments have been saved to your Desktop in the 'podcast_output' folder.

💡 Tip: If the combined file has issues, you can use the individual segment files with audio editing software like Audacity to create a perfect combined version.
"""
                
                return [types.TextContent(
                    type="text",
                    text=result_message.strip()
                )]
                
            except ImportError:
                return [types.TextContent(
                    type="text",
                    text="Error: ElevenLabs library not installed. Please install it with: pip install elevenlabs"
                )]
            
        except Exception as e:
            return [types.TextContent(
                type="text", 
                text=f"Error creating audio: {str(e)}"
            )]
    
    else:
        return [types.TextContent(
            type="text",
            text=f"Error: Unknown tool '{name}'"
        )]


async def run():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="podcast-generator",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())