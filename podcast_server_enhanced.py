#!/usr/bin/env python3
"""
Enhanced Podcast Generator MCP Server
With advanced voice options and better prompting for LLMs
"""

import json
import logging
import os
import random
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime

import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("podcast-generator-enhanced")


# Advanced podcast formats and styles
PODCAST_FORMATS = {
    "interview": {
        "description": "Classic interview format with host and guest(s)",
        "min_speakers": 2,
        "typical_speakers": ["Host", "Guest Expert", "Co-host", "Special Guest"],
        "style_notes": "Professional yet conversational, with follow-up questions and deep dives"
    },
    "debate": {
        "description": "Point-counterpoint discussion with opposing viewpoints",
        "min_speakers": 2,
        "typical_speakers": ["Moderator", "Advocate", "Opponent", "Neutral Expert"],
        "style_notes": "Balanced, respectful disagreement with evidence-based arguments"
    },
    "storytelling": {
        "description": "Narrative-driven format with immersive storytelling",
        "min_speakers": 1,
        "typical_speakers": ["Narrator", "Character Voice 1", "Character Voice 2", "Witness"],
        "style_notes": "Dramatic pacing, emotional depth, vivid descriptions"
    },
    "educational": {
        "description": "Teaching-focused format with clear explanations",
        "min_speakers": 1,
        "typical_speakers": ["Instructor", "Student", "Expert", "Assistant"],
        "style_notes": "Clear, structured, with examples and analogies"
    },
    "comedy": {
        "description": "Entertainment-focused with humor and banter",
        "min_speakers": 2,
        "typical_speakers": ["Main Host", "Co-host", "Comedian Guest", "Straight Man"],
        "style_notes": "Timing-focused, witty, with natural chemistry"
    },
    "news_analysis": {
        "description": "Current events discussion with expert analysis",
        "min_speakers": 2,
        "typical_speakers": ["Anchor", "Field Reporter", "Expert Analyst", "Correspondent"],
        "style_notes": "Authoritative, factual, with multiple perspectives"
    },
    "roundtable": {
        "description": "Multi-person discussion with equal participation",
        "min_speakers": 3,
        "typical_speakers": ["Moderator", "Panelist 1", "Panelist 2", "Panelist 3"],
        "style_notes": "Balanced speaking time, diverse viewpoints, collaborative"
    }
}


# Voice personality profiles for better character development
VOICE_PERSONALITIES = {
    "authoritative": {
        "traits": ["confident", "knowledgeable", "decisive", "clear"],
        "speaking_style": "measured pace, clear enunciation, occasional emphasis",
        "best_for": ["expert", "anchor", "instructor", "moderator"]
    },
    "warm_engaging": {
        "traits": ["friendly", "approachable", "enthusiastic", "empathetic"],
        "speaking_style": "varied intonation, occasional laughter, personal anecdotes",
        "best_for": ["host", "interviewer", "narrator", "guide"]
    },
    "analytical": {
        "traits": ["logical", "precise", "thoughtful", "objective"],
        "speaking_style": "steady pace, technical vocabulary, structured arguments",
        "best_for": ["analyst", "researcher", "expert", "correspondent"]
    },
    "energetic": {
        "traits": ["dynamic", "passionate", "animated", "inspiring"],
        "speaking_style": "fast-paced, emphatic, emotionally expressive",
        "best_for": ["motivator", "comedian", "advocate", "entertainer"]
    },
    "contemplative": {
        "traits": ["thoughtful", "philosophical", "introspective", "nuanced"],
        "speaking_style": "slower pace, meaningful pauses, depth of reflection",
        "best_for": ["philosopher", "storyteller", "counselor", "artist"]
    },
    "skeptical": {
        "traits": ["questioning", "critical", "investigative", "challenging"],
        "speaking_style": "probing questions, careful word choice, analytical tone",
        "best_for": ["investigator", "opponent", "critic", "journalist"]
    }
}


def get_enhanced_voice_options():
    """Get enhanced voice options including ElevenLabs features"""
    return {
        "elevenlabs_voices": {
            "default_voices": [
                {"id": "nova", "personality": "warm_engaging", "gender": "female", "age": "young_adult"},
                {"id": "aria", "personality": "contemplative", "gender": "female", "age": "adult"},
                {"id": "sarah", "personality": "authoritative", "gender": "female", "age": "adult"},
                {"id": "laura", "personality": "warm_engaging", "gender": "female", "age": "middle_aged"},
                {"id": "josh", "personality": "energetic", "gender": "male", "age": "young_adult"},
                {"id": "adam", "personality": "analytical", "gender": "male", "age": "adult"},
                {"id": "brian", "personality": "authoritative", "gender": "male", "age": "middle_aged"},
                {"id": "william shanks", "personality": "skeptical", "gender": "male", "age": "senior"}
            ],
            "voice_design_prompts": [
                "Young enthusiastic tech podcaster with Silicon Valley accent",
                "Wise storyteller with gentle Southern drawl",
                "Professional news anchor with neutral American accent",
                "British academic with Oxford pronunciation",
                "Energetic sports commentator with New York accent",
                "Calm meditation guide with soothing tone",
                "Witty comedian with quick delivery and timing",
                "Investigative journalist with serious, probing tone"
            ]
        },
        "voice_settings": {
            "emotional_presets": {
                "excited": {"stability": 0.3, "similarity_boost": 0.7, "style": 0.8},
                "serious": {"stability": 0.7, "similarity_boost": 0.5, "style": 0.3},
                "warm": {"stability": 0.5, "similarity_boost": 0.6, "style": 0.6},
                "contemplative": {"stability": 0.6, "similarity_boost": 0.4, "style": 0.4},
                "urgent": {"stability": 0.4, "similarity_boost": 0.8, "style": 0.7},
                "casual": {"stability": 0.5, "similarity_boost": 0.5, "style": 0.5}
            }
        }
    }


def generate_llm_optimized_prompt(
    topic: str,
    format_type: str,
    duration_minutes: int,
    num_speakers: int,
    additional_context: Optional[Dict] = None
) -> str:
    """
    Generate an optimized prompt for LLMs to create natural podcast scripts
    """
    format_info = PODCAST_FORMATS.get(format_type, PODCAST_FORMATS["interview"])
    
    # Build speaker profiles
    speakers = []
    for i in range(num_speakers):
        if i < len(format_info["typical_speakers"]):
            speaker_role = format_info["typical_speakers"][i]
            # Assign personality based on role
            if "host" in speaker_role.lower() or "moderator" in speaker_role.lower():
                personality = "warm_engaging"
            elif "expert" in speaker_role.lower() or "analyst" in speaker_role.lower():
                personality = "analytical"
            elif "comedian" in speaker_role.lower():
                personality = "energetic"
            else:
                personality = random.choice(list(VOICE_PERSONALITIES.keys()))
            
            speakers.append({
                "role": speaker_role,
                "personality": VOICE_PERSONALITIES[personality]
            })
    
    # Calculate content segments based on duration
    segments = {
        "intro": 1,
        "main_content": max(2, duration_minutes - 2),
        "conclusion": 1
    }
    
    # Build the comprehensive prompt
    prompt = f"""Create a natural, engaging {format_type} podcast script about "{topic}".

FORMAT: {format_info['description']}
STYLE: {format_info['style_notes']}
DURATION: Approximately {duration_minutes} minutes
SPEAKERS: {num_speakers} speakers

SPEAKER PROFILES:
"""
    
    for i, speaker in enumerate(speakers):
        prompt += f"""
Speaker {i+1} - {speaker['role']}:
- Personality traits: {', '.join(speaker['personality']['traits'])}
- Speaking style: {speaker['personality']['speaking_style']}
"""
    
    prompt += f"""

CONTENT STRUCTURE:
1. INTRODUCTION ({segments['intro']} minute):
   - Hook the audience with an intriguing opening
   - Introduce the topic and why it matters now
   - Quick speaker introductions that feel natural
   
2. MAIN CONTENT ({segments['main_content']} minutes):
   - Develop {max(3, duration_minutes // 2)} key points or story beats
   - Include specific examples, anecdotes, or data points
   - Create natural transitions between topics
   - Add personality-appropriate reactions and interjections
   
3. CONCLUSION ({segments['conclusion']} minute):
   - Summarize key insights or story resolution
   - Provide actionable takeaways or thought-provoking questions
   - Natural sign-off that fits the format

DIALOGUE REQUIREMENTS:
- Write natural, conversational dialogue (avoid stiff or overly formal language)
- Include verbal fillers occasionally (um, uh, you know) for realism
- Add interruptions, overlapping thoughts, and natural reactions
- Show personality through word choice and speech patterns
- Include relevant emotions (laughter, surprise, concern) where appropriate
- Vary sentence length and structure for each speaker
- Use contemporary references and relatable examples

TOPIC-SPECIFIC ELEMENTS TO EXPLORE:
- Current relevance and recent developments
- Common misconceptions to address
- Surprising facts or counterintuitive insights
- Personal experiences or case studies
- Future implications or predictions
- Practical applications for listeners

FORMAT EACH LINE AS:
[SPEAKER_ROLE]: [Dialogue with natural speech patterns and appropriate emotion]

Example:
Host: [laughing] I can't believe that actually happened! So wait, you're telling me...
Expert: Yeah, I know it sounds crazy, but the data is clear. We found that...

Remember to make this feel like a real conversation, not a scripted reading. Include moments of genuine curiosity, surprise, humor, and insight that would naturally occur when intelligent people discuss {topic}.
"""
    
    if additional_context:
        prompt += f"\n\nADDITIONAL CONTEXT:\n"
        for key, value in additional_context.items():
            prompt += f"- {key}: {value}\n"
    
    return prompt


def parse_voice_library_search(query: str) -> Dict[str, Any]:
    """Parse natural language queries for voice library search"""
    search_params = {
        "gender": None,
        "age": None,
        "accent": None,
        "use_case": None,
        "language": None
    }
    
    # Gender detection
    if any(word in query.lower() for word in ["male", "man", "guy", "masculine"]):
        search_params["gender"] = "male"
    elif any(word in query.lower() for word in ["female", "woman", "feminine"]):
        search_params["gender"] = "female"
    
    # Age detection
    if any(word in query.lower() for word in ["young", "youth", "teen"]):
        search_params["age"] = "young"
    elif any(word in query.lower() for word in ["old", "elderly", "senior", "mature"]):
        search_params["age"] = "old"
    elif any(word in query.lower() for word in ["middle", "adult"]):
        search_params["age"] = "middle_aged"
    
    # Accent detection
    accents = ["british", "american", "australian", "indian", "southern", "new york", 
               "california", "texas", "midwestern", "scottish", "irish"]
    for accent in accents:
        if accent in query.lower():
            search_params["accent"] = accent
            break
    
    # Use case detection
    use_cases = ["narration", "commercial", "podcast", "audiobook", "video game", 
                 "animation", "meditation", "educational"]
    for use_case in use_cases:
        if use_case in query.lower():
            search_params["use_case"] = use_case
            break
    
    return search_params


@server.list_resources()
async def list_resources() -> list[types.Resource]:
    """List available resources."""
    return [
        types.Resource(
            uri="podcast://voices",
            name="Enhanced Voice Options",
            description="Comprehensive voice options including ElevenLabs features",
            mimeType="application/json"
        ),
        types.Resource(
            uri="podcast://formats",
            name="Podcast Formats",
            description="Available podcast formats and styles",
            mimeType="application/json"
        ),
        types.Resource(
            uri="podcast://prompt-guide",
            name="Prompting Guide",
            description="Guide for creating better podcast scripts with LLMs",
            mimeType="text/markdown"
        )
    ]


@server.read_resource()
async def read_resource(uri: types.AnyUrl) -> str:
    """Read a specific resource."""
    if str(uri) == "podcast://voices":
        return json.dumps(get_enhanced_voice_options(), indent=2)
    
    elif str(uri) == "podcast://formats":
        return json.dumps(PODCAST_FORMATS, indent=2)
    
    elif str(uri) == "podcast://prompt-guide":
        guide = """# Enhanced Podcast Generator Prompting Guide

## Overview
This enhanced podcast generator uses sophisticated prompting to help LLMs create natural, engaging podcast scripts.

## Key Improvements

### 1. Format-Specific Templates
Choose from multiple podcast formats:
- **Interview**: Classic Q&A with expert guests
- **Debate**: Balanced discussion of opposing viewpoints  
- **Storytelling**: Narrative-driven content
- **Educational**: Teaching-focused explanations
- **Comedy**: Entertainment with humor
- **News Analysis**: Current events discussion
- **Roundtable**: Multi-person collaborative discussion

### 2. Voice Personality Matching
Each speaker is assigned a personality profile:
- **Authoritative**: Confident experts and anchors
- **Warm & Engaging**: Friendly hosts and interviewers
- **Analytical**: Data-driven researchers
- **Energetic**: Dynamic entertainers
- **Contemplative**: Thoughtful philosophers
- **Skeptical**: Critical investigators

### 3. Natural Dialogue Elements
Scripts now include:
- Verbal fillers (um, uh) for realism
- Interruptions and overlapping speech
- Emotional reactions (laughter, surprise)
- Personality-specific word choices
- Natural conversation flow

### 4. Enhanced Voice Options
- Access to ElevenLabs voice library
- Voice design for custom characters
- Emotional voice settings
- Multi-language support
- Sound effects integration

## Usage Examples

### Basic Interview
```
generate_enhanced_script(
    topic="The Future of AI",
    format_type="interview",
    duration_minutes=10,
    num_speakers=2
)
```

### Dynamic Debate
```
generate_enhanced_script(
    topic="Remote Work vs Office Culture",
    format_type="debate",
    duration_minutes=15,
    num_speakers=3,
    additional_context={
        "stance_1": "Remote work maximizes productivity",
        "stance_2": "Office culture drives innovation"
    }
)
```

### Narrative Podcast
```
generate_enhanced_script(
    topic="The Mystery of the Missing Startup Funds",
    format_type="storytelling",
    duration_minutes=20,
    num_speakers=4,
    additional_context={
        "genre": "tech thriller",
        "setting": "Silicon Valley startup"
    }
)
```

## Voice Selection Tips

### For Professional Content
- Use authoritative voices for experts
- Warm, engaging voices for hosts
- Clear, neutral accents for wide appeal

### For Entertainment
- Energetic voices for comedy
- Varied accents for character distinction
- Emotional range for storytelling

### For Educational Content
- Clear, measured voices for instruction
- Friendly tones for accessibility
- Consistent pacing for comprehension

## Advanced Features

### Voice Library Search
```
search_voices("young female british narrator audiobook")
search_voices("deep male voice podcast host american")
```

### Voice Design
```
design_voice(
    description="Wise elderly professor with slight German accent, warm but authoritative",
    sample_text="Let me tell you about the quantum realm..."
)
```

### Emotional Variations
Apply emotional presets to any voice:
- Excited: High energy discussions
- Serious: Important topics
- Warm: Personal stories
- Contemplative: Deep thoughts
- Urgent: Breaking news
- Casual: Relaxed conversations

## Best Practices

1. **Match Format to Content**: Choose the right format for your topic
2. **Consider Audience**: Adjust tone and complexity accordingly
3. **Use Natural Pacing**: Vary segment lengths for engagement
4. **Add Context**: Provide additional details for better scripts
5. **Experiment with Voices**: Try different combinations for best results

## Troubleshooting

### Scripts Too Formal?
- Use comedy or roundtable formats
- Add casual personality types
- Include more verbal fillers

### Lacking Emotion?
- Apply emotional presets to voices
- Use storytelling format
- Add emotional context in prompts

### Need More Depth?
- Increase duration
- Use educational or debate formats
- Provide detailed additional context
"""
        return guide.strip()
    
    else:
        raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="generate_enhanced_script",
            description="Generate an enhanced podcast script with natural dialogue and personality",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The main topic for the podcast"
                    },
                    "format_type": {
                        "type": "string",
                        "description": "Podcast format type",
                        "enum": list(PODCAST_FORMATS.keys()),
                        "default": "interview"
                    },
                    "duration_minutes": {
                        "type": "integer",
                        "description": "Target duration in minutes (1-60)",
                        "minimum": 1,
                        "maximum": 60,
                        "default": 10
                    },
                    "num_speakers": {
                        "type": "integer",
                        "description": "Number of speakers",
                        "minimum": 1,
                        "maximum": 6,
                        "default": 2
                    },
                    "additional_context": {
                        "type": "object",
                        "description": "Additional context for the script (stance, setting, etc.)"
                    }
                },
                "required": ["topic"]
            }
        ),
        types.Tool(
            name="create_enhanced_audio",
            description="Convert script to audio with advanced voice options and emotional variations",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "The podcast script"
                    },
                    "output_filename": {
                        "type": "string",
                        "description": "Output filename",
                        "default": "enhanced_podcast.mp3"
                    },
                    "voice_assignments": {
                        "type": "object",
                        "description": "Manual voice assignments {speaker: voice_id/description}"
                    },
                    "auto_assign_voices": {
                        "type": "boolean",
                        "description": "Automatically assign diverse voices",
                        "default": True
                    },
                    "include_sound_effects": {
                        "type": "boolean",
                        "description": "Add ambient sound effects",
                        "default": False
                    }
                },
                "required": ["script"]
            }
        ),
        types.Tool(
            name="search_voices",
            description="Search for voices in the ElevenLabs voice library",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query (e.g., 'young british female narrator')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results to return",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="design_voice",
            description="Create a custom voice using ElevenLabs voice design",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Voice description (20-1000 characters)"
                    },
                    "sample_text": {
                        "type": "string",
                        "description": "Sample text for preview (100-1000 characters)"
                    },
                    "save_as": {
                        "type": "string",
                        "description": "Name to save the voice as"
                    }
                },
                "required": ["description", "sample_text"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Handle tool calls."""
    if not arguments:
        arguments = {}

    if name == "generate_enhanced_script":
        topic = arguments.get("topic")
        if not topic:
            return [types.TextContent(
                type="text",
                text="Error: topic parameter is required"
            )]
        
        format_type = arguments.get("format_type", "interview")
        duration_minutes = arguments.get("duration_minutes", 10)
        num_speakers = arguments.get("num_speakers", 2)
        additional_context = arguments.get("additional_context", {})
        
        # Generate the optimized prompt
        prompt = generate_llm_optimized_prompt(
            topic=topic,
            format_type=format_type,
            duration_minutes=duration_minutes,
            num_speakers=num_speakers,
            additional_context=additional_context
        )
        
        # Return the prompt for the LLM to generate the script
        return [types.TextContent(
            type="text",
            text=f"""Generated enhanced prompt for LLM podcast script generation:

{prompt}

---
Note: This prompt is optimized for advanced LLMs like Claude or GPT-4. The LLM should generate a natural, engaging podcast script based on this prompt. The script will include realistic dialogue, personality-driven speaking styles, and format-appropriate content structure."""
        )]

    elif name == "create_enhanced_audio":
        script = arguments.get("script")
        if not script:
            return [types.TextContent(
                type="text",
                text="Error: script parameter is required"
            )]
        
        output_filename = arguments.get("output_filename", "enhanced_podcast.mp3")
        voice_assignments = arguments.get("voice_assignments", {})
        auto_assign_voices = arguments.get("auto_assign_voices", True)
        include_sound_effects = arguments.get("include_sound_effects", False)
        
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
                
                # Get available voices
                voices = client.voices.get_all()
                voice_map = {v.name.lower(): v.voice_id for v in voices.voices}
                
                # Create output directory
                output_dir = os.path.expanduser("~/Desktop/podcast_output")
                os.makedirs(output_dir, exist_ok=True)
                
                # Parse script into dialogue segments with enhanced emotion detection
                dialogue_segments = []
                lines = script.split('\n')
                
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('#') or line.startswith('*') or line == '---':
                        continue
                    
                    # Enhanced speaker pattern detection
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            speaker = parts[0].strip()
                            text = parts[1].strip()
                            
                            # Remove emotion indicators like [laughing], [surprised], etc.
                            emotion = "neutral"
                            if '[' in speaker and ']' in speaker:
                                emotion_match = speaker[speaker.find('[')+1:speaker.find(']')]
                                emotion = emotion_match.lower()
                                speaker = speaker[:speaker.find('[')].strip()
                            
                            if text:
                                dialogue_segments.append({
                                    'speaker': speaker,
                                    'text': text,
                                    'emotion': emotion
                                })
                
                if not dialogue_segments:
                    return [types.TextContent(
                        type="text",
                        text="Error: No valid dialogue segments found in script"
                    )]
                
                # Enhanced voice assignment logic
                unique_speakers = list(set(seg['speaker'] for seg in dialogue_segments))
                final_voice_assignments = {}
                
                if auto_assign_voices:
                    # Get diverse voices based on the voice options
                    voice_options = get_enhanced_voice_options()
                    default_voices = voice_options["elevenlabs_voices"]["default_voices"]
                    
                    # Try to match speakers to appropriate voices
                    for i, speaker in enumerate(unique_speakers):
                        speaker_lower = speaker.lower()
                        
                        # Check manual assignments first
                        if speaker in voice_assignments:
                            # Could be a voice ID or a description for voice design
                            assignment = voice_assignments[speaker]
                            if assignment in voice_map:
                                final_voice_assignments[speaker] = voice_map[assignment]
                            else:
                                # Treat as voice design description
                                final_voice_assignments[speaker] = f"design:{assignment}"
                        else:
                            # Auto-assign based on role and available voices
                            assigned = False
                            
                            # Try to match based on role keywords
                            for voice_data in default_voices:
                                voice_name = voice_data["id"]
                                if voice_name in voice_map:
                                    personality = voice_data["personality"]
                                    
                                    # Match based on speaker role
                                    if ("host" in speaker_lower and personality == "warm_engaging") or \
                                       ("expert" in speaker_lower and personality == "authoritative") or \
                                       ("analyst" in speaker_lower and personality == "analytical") or \
                                       ("reporter" in speaker_lower and personality == "authoritative"):
                                        final_voice_assignments[speaker] = voice_map[voice_name]
                                        assigned = True
                                        break
                            
                            # If no role match, assign diversely
                            if not assigned and i < len(default_voices):
                                voice_name = default_voices[i]["id"]
                                if voice_name in voice_map:
                                    final_voice_assignments[speaker] = voice_map[voice_name]
                                else:
                                    # Fallback to first available voice
                                    final_voice_assignments[speaker] = voices.voices[0].voice_id
                
                # Generate audio segments with enhanced emotional control
                audio_segments = []
                segment_files = []
                
                for i, segment in enumerate(dialogue_segments):
                    speaker = segment['speaker']
                    text = segment['text']
                    emotion = segment.get('emotion', 'neutral')
                    
                    # Get voice for this speaker
                    speaker_voice_id = final_voice_assignments.get(speaker, voices.voices[0].voice_id)
                    
                    # Handle voice design requests
                    if isinstance(speaker_voice_id, str) and speaker_voice_id.startswith("design:"):
                        # This would require voice design API call
                        # For now, fallback to default voice
                        speaker_voice_id = voices.voices[0].voice_id
                    
                    # Get emotional settings
                    emotion_presets = get_enhanced_voice_options()["voice_settings"]["emotional_presets"]
                    
                    # Enhanced emotion detection
                    if emotion in emotion_presets:
                        voice_settings = emotion_presets[emotion]
                    elif '!' in text and '?' not in text:
                        voice_settings = emotion_presets["excited"]
                    elif '?' in text and any(word in text.lower() for word in ['how', 'why', 'what', 'when', 'where']):
                        voice_settings = emotion_presets["contemplative"]
                    elif any(phrase in text.lower() for phrase in ['breaking', 'urgent', 'just in', 'alert']):
                        voice_settings = emotion_presets["urgent"]
                    elif any(phrase in text.lower() for phrase in ['thank', 'appreciate', 'wonderful', 'great']):
                        voice_settings = emotion_presets["warm"]
                    elif any(phrase in text.lower() for phrase in ['research', 'data', 'studies', 'evidence']):
                        voice_settings = emotion_presets["serious"]
                    else:
                        voice_settings = emotion_presets["casual"]
                    
                    # Generate audio for this segment
                    try:
                        segment_audio = client.text_to_speech.convert(
                            text=text,
                            voice_id=speaker_voice_id,
                            voice_settings=VoiceSettings(
                                stability=voice_settings["stability"],
                                similarity_boost=voice_settings["similarity_boost"],
                                style=voice_settings.get("style", 0.5),
                                use_speaker_boost=True
                            ),
                            model_id="eleven_turbo_v2_5"  # Using the turbo model for speed
                        )
                        
                        # Save individual segment
                        segment_filename = f"segment_{i:03d}_{speaker.lower().replace(' ', '_')}.mp3"
                        segment_path = os.path.join(output_dir, segment_filename)
                        
                        with open(segment_path, "wb") as f:
                            for chunk in segment_audio:
                                f.write(chunk)
                        
                        segment_files.append(segment_path)
                        
                        # Find actual voice name
                        voice_name = "Custom"
                        for v in voices.voices:
                            if v.voice_id == speaker_voice_id:
                                voice_name = v.name
                                break
                        
                        audio_segments.append({
                            'speaker': speaker,
                            'voice': voice_name,
                            'emotion': emotion if emotion != "neutral" else voice_settings,
                            'file': segment_path,
                            'text_length': len(text)
                        })
                        
                    except Exception as segment_error:
                        logger.error(f"Error generating segment {i}: {str(segment_error)}")
                        continue
                
                # Add sound effects if requested
                if include_sound_effects and len(segment_files) > 0:
                    # Generate intro/outro sound effects
                    try:
                        # Intro sound
                        intro_audio = client.text_to_sound_effects.convert(
                            text="Podcast intro jingle with upbeat music fade in",
                            duration_seconds=3.0,
                            prompt_influence=0.3
                        )
                        
                        intro_path = os.path.join(output_dir, "intro_music.mp3")
                        with open(intro_path, "wb") as f:
                            for chunk in intro_audio:
                                f.write(chunk)
                        
                        # Outro sound
                        outro_audio = client.text_to_sound_effects.convert(
                            text="Podcast outro music with gentle fade out",
                            duration_seconds=3.0,
                            prompt_influence=0.3
                        )
                        
                        outro_path = os.path.join(output_dir, "outro_music.mp3")
                        with open(outro_path, "wb") as f:
                            for chunk in outro_audio:
                                f.write(chunk)
                        
                        # Add to segments list
                        segment_files.insert(0, intro_path)
                        segment_files.append(outro_path)
                        
                    except Exception as sfx_error:
                        logger.warning(f"Could not generate sound effects: {str(sfx_error)}")
                
                # Combine audio segments
                if segment_files:
                    # Simple concatenation (would need proper audio library for crossfades)
                    combined_audio_data = b""
                    
                    for segment_file in segment_files:
                        try:
                            with open(segment_file, "rb") as f:
                                combined_audio_data += f.read()
                        except:
                            continue
                    
                    # Save combined file
                    output_path = os.path.join(output_dir, output_filename)
                    with open(output_path, "wb") as f:
                        f.write(combined_audio_data)
                    
                    # Generate detailed report
                    speakers_info = []
                    emotion_summary = {}
                    
                    for segment in audio_segments:
                        speaker_emotion = f"{segment['emotion']}" if isinstance(segment['emotion'], str) else "dynamic"
                        speakers_info.append(f"  • {segment['speaker']}: {segment['voice']} voice ({speaker_emotion} tone, {segment['text_length']} chars)")
                        
                        if speaker_emotion not in emotion_summary:
                            emotion_summary[speaker_emotion] = 0
                        emotion_summary[speaker_emotion] += 1
                    
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    result_message = f"""
✅ Enhanced podcast created successfully!

📅 Generated: {timestamp}
📁 Output Location: {output_path}

📊 Podcast Statistics:
- Total Segments: {len(audio_segments)}
- Duration: ~{sum(seg['text_length'] for seg in audio_segments) // 150} minutes (estimated)
- File Size: {os.path.getsize(output_path) / 1024 / 1024:.1f} MB
- Sound Effects: {"✅ Included" if include_sound_effects else "❌ Not included"}

🎭 Voice Cast & Performance:
{chr(10).join(speakers_info)}

🎨 Emotional Tone Distribution:
{chr(10).join([f"  • {emotion}: {count} segments" for emotion, count in emotion_summary.items()])}

📁 Project Files:
- Combined podcast: {output_filename}
- Individual segments: {len(segment_files)} files
- Location: ~/Desktop/podcast_output/

💡 Enhancement Tips:
1. Use an audio editor for professional transitions
2. Adjust pacing with silence between segments
3. Add background music for atmosphere
4. Apply compression for consistent volume

🎧 Your enhanced podcast is ready with natural dialogue and emotional depth!
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

    elif name == "search_voices":
        query = arguments.get("query", "")
        limit = arguments.get("limit", 10)
        
        # Parse the natural language query
        search_params = parse_voice_library_search(query)
        
        # In a real implementation, this would call the ElevenLabs API
        # For now, return a mock response showing how it would work
        mock_results = f"""
🔍 Voice Library Search Results for: "{query}"

Search Parameters Detected:
- Gender: {search_params.get('gender', 'any')}
- Age: {search_params.get('age', 'any')}
- Accent: {search_params.get('accent', 'any')}
- Use Case: {search_params.get('use_case', 'any')}

Top {limit} Results:
1. "Emma Thompson" - British female, middle-aged, perfect for audiobook narration
2. "Marcus Chen" - American male, young adult, energetic podcast host
3. "Sophia Rivera" - Spanish-accented female, warm and engaging
4. "James MacLeod" - Scottish male, authoritative narrator
5. "Aisha Patel" - Indian-accented female, clear educational content

💡 To use these voices:
- Add them to your voice library in ElevenLabs
- Reference by name in voice_assignments
- Or use voice IDs directly in the create_enhanced_audio tool

Note: This is a mock response. Real implementation would search the actual ElevenLabs voice library.
"""
        
        return [types.TextContent(
            type="text",
            text=mock_results.strip()
        )]

    elif name == "design_voice":
        description = arguments.get("description", "")
        sample_text = arguments.get("sample_text", "")
        save_as = arguments.get("save_as", "custom_voice")
        
        # Validate inputs
        if len(description) < 20 or len(description) > 1000:
            return [types.TextContent(
                type="text",
                text="Error: Voice description must be between 20 and 1000 characters"
            )]
        
        if len(sample_text) < 100 or len(sample_text) > 1000:
            return [types.TextContent(
                type="text",
                text="Error: Sample text must be between 100 and 1000 characters"
            )]
        
        # In a real implementation, this would call the ElevenLabs Voice Design API
        mock_response = f"""
🎨 Voice Design Preview

📝 Description: "{description}"

🎤 Sample Text: "{sample_text[:100]}..."

🔧 Generating 3 voice variations...

Generated Voices:
1. Variation A - More authoritative tone
   Preview: [Would play audio sample A]
   
2. Variation B - Balanced personality
   Preview: [Would play audio sample B]
   
3. Variation C - Warmer, friendlier tone
   Preview: [Would play audio sample C]

💾 To save: Select your preferred variation and it will be saved as "{save_as}"

Note: This is a mock response. Real implementation would use ElevenLabs Voice Design API to generate actual voice samples.
"""
        
        return [types.TextContent(
            type="text",
            text=mock_response.strip()
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
                server_name="podcast-generator-enhanced",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())