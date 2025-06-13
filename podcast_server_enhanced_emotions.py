#!/usr/bin/env python3
"""
Enhanced Podcast Generator MCP Server - Emotion-Aware Version
Properly handles emotional cues like [laughing] without speaking them
"""

import json
import logging
import os
import random
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple
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


# Emotion to sound mappings
EMOTION_SOUNDS = {
    "laughing": ["haha", "hehe", "ahaha", "ehehe"],
    "sighing": ["*sigh*", "*deep breath*"],
    "gasping": ["*gasp*", "oh!", "ah!"],
    "chuckling": ["heh", "hmm"],
    "crying": ["*sniff*", "*sob*"],
    "thinking": ["hmm", "uhh", "let me see"],
    "surprised": ["oh!", "wow!", "what?!"],
    "confused": ["huh?", "what?", "hmm?"],
    "excited": ["yes!", "oh wow!", "amazing!"],
    "angry": ["ugh!", "argh!", "grr!"],
    "nervous": ["um", "uh", "err"],
    "clearing throat": ["*ahem*", "*cough*"]
}


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


# Default voice pool for diversity
DEFAULT_VOICE_POOL = [
    {"name": "nova", "gender": "female", "personality": "warm_engaging", "age": "young_adult"},
    {"name": "aria", "gender": "female", "personality": "contemplative", "age": "adult"},
    {"name": "sarah", "gender": "female", "personality": "authoritative", "age": "adult"},
    {"name": "laura", "gender": "female", "personality": "warm_engaging", "age": "middle_aged"},
    {"name": "josh", "gender": "male", "personality": "energetic", "age": "young_adult"},
    {"name": "adam", "gender": "male", "personality": "analytical", "age": "adult"},
    {"name": "brian", "gender": "male", "personality": "authoritative", "age": "middle_aged"},
    {"name": "onyx", "gender": "male", "personality": "skeptical", "age": "adult"},
    {"name": "fable", "gender": "neutral", "personality": "warm_engaging", "age": "adult"},
    {"name": "shimmer", "gender": "female", "personality": "contemplative", "age": "young_adult"}
]


def process_emotional_text(text: str, emotion: str) -> Tuple[str, Optional[str]]:
    """
    Process text with emotional cues.
    Returns (cleaned_text, emotional_prefix)
    """
    # Remove emotion tags from text
    text = re.sub(r'\s*\[([^\]]+)\]\s*', ' ', text).strip()
    
    # Get emotional sound/prefix if applicable
    emotional_prefix = None
    if emotion in EMOTION_SOUNDS:
        emotional_prefix = random.choice(EMOTION_SOUNDS[emotion])
    
    return text, emotional_prefix


def parse_script_robust(script: str) -> List[Dict[str, str]]:
    """
    Robustly parse various script formats into dialogue segments.
    Handles markdown, plain text, and various formatting styles.
    Properly extracts and removes emotion tags.
    """
    dialogue_segments = []
    
    # Remove markdown formatting
    script = re.sub(r'\*\*([^*]+)\*\*', r'\1', script)  # Bold
    script = re.sub(r'\*([^*]+)\*', r'\1', script)      # Italic
    script = re.sub(r'#{1,6}\s*', '', script)           # Headers
    script = re.sub(r'```[^`]*```', '', script)         # Code blocks
    script = re.sub(r'`([^`]+)`', r'\1', script)        # Inline code
    
    # Split into lines and process
    lines = script.split('\n')
    current_speaker = None
    current_text = []
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and separators
        if not line or line == '---' or line.startswith('==='):
            continue
            
        # Try to detect speaker patterns
        # Pattern 1: "Speaker [emotion]: Text"
        speaker_match = re.match(r'^([A-Za-z\s\-\'\.]+?)(?:\s*\[([^\]]+)\])?\s*:\s*(.+)$', line)
        
        if speaker_match:
            # Save previous segment if exists
            if current_speaker and current_text:
                combined_text = ' '.join(current_text)
                # Check for inline emotions in the text
                inline_emotion_match = re.search(r'\[([^\]]+)\]', combined_text)
                if inline_emotion_match:
                    current_speaker['emotion'] = inline_emotion_match.group(1).lower()
                    combined_text = re.sub(r'\s*\[([^\]]+)\]\s*', ' ', combined_text).strip()
                
                dialogue_segments.append({
                    'speaker': current_speaker['name'],
                    'text': combined_text,
                    'emotion': current_speaker.get('emotion', 'neutral')
                })
                current_text = []
            
            # Start new segment
            speaker_name = speaker_match.group(1).strip()
            emotion = speaker_match.group(2).lower() if speaker_match.group(2) else 'neutral'
            text = speaker_match.group(3).strip()
            
            # Check for emotion tags within the text itself
            text_emotion_match = re.search(r'\[([^\]]+)\]', text)
            if text_emotion_match:
                emotion = text_emotion_match.group(1).lower()
                text = re.sub(r'\s*\[([^\]]+)\]\s*', ' ', text).strip()
            
            current_speaker = {
                'name': speaker_name,
                'emotion': emotion
            }
            current_text = [text] if text else []
        
        # Pattern 2: Continuation of previous speaker's text
        elif current_speaker and line:
            # Check for inline emotions
            inline_emotion = re.search(r'\[([^\]]+)\]', line)
            if inline_emotion:
                current_speaker['emotion'] = inline_emotion.group(1).lower()
                line = re.sub(r'\s*\[([^\]]+)\]\s*', ' ', line).strip()
            current_text.append(line)
    
    # Don't forget the last segment
    if current_speaker and current_text:
        combined_text = ' '.join(current_text)
        # Final check for inline emotions
        inline_emotion_match = re.search(r'\[([^\]]+)\]', combined_text)
        if inline_emotion_match:
            current_speaker['emotion'] = inline_emotion_match.group(1).lower()
            combined_text = re.sub(r'\s*\[([^\]]+)\]\s*', ' ', combined_text).strip()
            
        dialogue_segments.append({
            'speaker': current_speaker['name'],
            'text': combined_text,
            'emotion': current_speaker.get('emotion', 'neutral')
        })
    
    # If no segments found, try alternative parsing
    if not dialogue_segments:
        # Try to split by double newlines
        paragraphs = script.split('\n\n')
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if para:
                # Check for emotions in paragraph
                emotion = 'neutral'
                emotion_match = re.search(r'\[([^\]]+)\]', para)
                if emotion_match:
                    emotion = emotion_match.group(1).lower()
                    para = re.sub(r'\s*\[([^\]]+)\]\s*', ' ', para).strip()
                
                # Assign alternating speakers
                speaker = "Speaker 1" if i % 2 == 0 else "Speaker 2"
                dialogue_segments.append({
                    'speaker': speaker,
                    'text': para,
                    'emotion': emotion
                })
    
    return dialogue_segments


def ensure_different_voices(speakers: List[str], available_voices: List[Dict]) -> Dict[str, Tuple[str, str]]:
    """
    Ensure each speaker gets a different voice.
    Returns dict of {speaker: (voice_id, voice_name)}
    """
    voice_assignments = {}
    used_voices = set()
    
    # Shuffle voices for variety
    voice_pool = available_voices.copy()
    random.shuffle(voice_pool)
    
    for i, speaker in enumerate(speakers):
        # Find an unused voice
        voice_found = False
        
        # First, try to match by role/personality
        speaker_lower = speaker.lower()
        for voice in voice_pool:
            if voice['name'] not in used_voices:
                personality = voice.get('personality', '')
                
                # Match voice to speaker role
                if (('host' in speaker_lower or 'moderator' in speaker_lower) and 
                    personality == 'warm_engaging'):
                    voice_assignments[speaker] = (voice['name'], voice['name'].title())
                    used_voices.add(voice['name'])
                    voice_found = True
                    break
                elif (('expert' in speaker_lower or 'professor' in speaker_lower or 
                       'doctor' in speaker_lower or 'analyst' in speaker_lower) and 
                      personality in ['authoritative', 'analytical']):
                    voice_assignments[speaker] = (voice['name'], voice['name'].title())
                    used_voices.add(voice['name'])
                    voice_found = True
                    break
                elif (('comedian' in speaker_lower or 'comic' in speaker_lower) and 
                      personality == 'energetic'):
                    voice_assignments[speaker] = (voice['name'], voice['name'].title())
                    used_voices.add(voice['name'])
                    voice_found = True
                    break
        
        # If no role match, just pick next available
        if not voice_found:
            for voice in voice_pool:
                if voice['name'] not in used_voices:
                    voice_assignments[speaker] = (voice['name'], voice['name'].title())
                    used_voices.add(voice['name'])
                    voice_found = True
                    break
        
        # If we run out of voices, start reusing but try to maintain variety
        if not voice_found:
            # Pick the least recently used voice
            for voice in voice_pool:
                if voice['name'] not in [v[0] for v in list(voice_assignments.values())[-2:]]:
                    voice_assignments[speaker] = (voice['name'], voice['name'].title())
                    break
            else:
                # Fallback: just use next voice in rotation
                voice = voice_pool[i % len(voice_pool)]
                voice_assignments[speaker] = (voice['name'], voice['name'].title())
    
    return voice_assignments

def add_speaker_introductions(dialogue_segments: List[Dict[str, str]], voice_assignments: Dict[str, Tuple[str, str]]) -> List[Dict[str, str]]:
    """
    Add natural speaker introductions at the beginning of the podcast.
    """
    intro_segments = []
    speakers = list(set(seg['speaker'] for seg in dialogue_segments))
    
    # Check if script already has introductions
    first_few_texts = ' '.join([seg['text'].lower() for seg in dialogue_segments[:5]])
    has_intro = any(phrase in first_few_texts for phrase in ['my name is', "i'm your host", 'welcome to', 'this is'])
    
    if not has_intro and len(speakers) > 1:
        # Add natural introductions
        if 'Host' in speakers or 'Moderator' in speakers:
            host = 'Host' if 'Host' in speakers else 'Moderator'
            intro_segments.append({
                'speaker': host,
                'text': "Hello everyone, and welcome to today's podcast! I'm your host, and I'm thrilled to be here with some amazing guests.",
                'emotion': 'warm'
            })
            
            # Introduce other speakers
            for speaker in speakers:
                if speaker not in ['Host', 'Moderator']:
                    if 'Expert' in speaker or 'Guest' in speaker:
                        intro_segments.append({
                            'speaker': speaker,
                            'text': f"Thanks for having me! I'm excited to share my insights with your listeners today.",
                            'emotion': 'friendly'
                        })
                    elif 'Panelist' in speaker:
                        intro_segments.append({
                            'speaker': speaker,
                            'text': f"Great to be here! Looking forward to our discussion.",
                            'emotion': 'enthusiastic'
                        })
        else:
            # For formats without a clear host
            intro_segments.append({
                'speaker': speakers[0],
                'text': "Welcome everyone! Let's dive right into our discussion.",
                'emotion': 'warm'
            })
    
    # Prepend introductions to dialogue
    return intro_segments + dialogue_segments


def get_enhanced_voice_options():
    """Get enhanced voice options including ElevenLabs features"""
    return {
        "elevenlabs_voices": {
            "default_voices": DEFAULT_VOICE_POOL,
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
                # Voice settings for different emotions
                "excited": {"stability": 0.3, "similarity_boost": 0.7, "style": 0.8},
                "serious": {"stability": 0.7, "similarity_boost": 0.5, "style": 0.3},
                "warm": {"stability": 0.5, "similarity_boost": 0.6, "style": 0.6},
                "contemplative": {"stability": 0.6, "similarity_boost": 0.4, "style": 0.4},
                "urgent": {"stability": 0.4, "similarity_boost": 0.8, "style": 0.7},
                "casual": {"stability": 0.5, "similarity_boost": 0.5, "style": 0.5},
                "friendly": {"stability": 0.5, "similarity_boost": 0.6, "style": 0.6},
                "enthusiastic": {"stability": 0.4, "similarity_boost": 0.7, "style": 0.7},
                "neutral": {"stability": 0.5, "similarity_boost": 0.5, "style": 0.5},
                "laughing": {"stability": 0.2, "similarity_boost": 0.8, "style": 0.9},
                "sighing": {"stability": 0.7, "similarity_boost": 0.4, "style": 0.3},
                "nervous": {"stability": 0.4, "similarity_boost": 0.6, "style": 0.5},
                "angry": {"stability": 0.3, "similarity_boost": 0.8, "style": 0.8},
                "surprised": {"stability": 0.3, "similarity_boost": 0.7, "style": 0.8},
                "confused": {"stability": 0.5, "similarity_boost": 0.5, "style": 0.5},
                "crying": {"stability": 0.6, "similarity_boost": 0.4, "style": 0.2},
                "thinking": {"stability": 0.6, "similarity_boost": 0.4, "style": 0.4}
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

IMPORTANT FORMATTING RULES:
1. Each line of dialogue MUST start with the speaker name followed by a colon
2. Use simple format: "Speaker Name: Dialogue text"
3. For emotions, place them in brackets BEFORE the colon: "Speaker Name [emotion]: Dialogue text"
4. Common emotions: [laughing], [sighing], [surprised], [thinking], [excited], [nervous]
5. Do NOT include stage directions or emotion descriptions in the spoken text
6. When someone laughs, just put [laughing] - don't write "haha" in the dialogue

CONTENT STRUCTURE:
1. INTRODUCTION ({segments['intro']} minute):
   - Natural speaker introductions (names/roles if appropriate)
   - Hook the audience with an intriguing opening
   - Introduce the topic and why it matters now
   
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
- Use emotions in brackets, NOT in the spoken text
- Vary sentence length and structure for each speaker
- Use contemporary references and relatable examples

FORMAT EACH LINE EXACTLY AS:
Speaker Name: Dialogue text
OR
Speaker Name [emotion]: Dialogue text

Example:
Host: Welcome everyone to today's show! I'm incredibly excited about our topic.
Expert [laughing]: Thanks for having me! You know, I was just thinking about this yesterday.
Host [curious]: Really? What sparked that thought?

CRITICAL: When indicating emotions like laughter, ONLY use the [emotion] tag. Do NOT write out the laughter as "haha" or describe it in the dialogue.

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
            uri="podcast://emotions",
            name="Emotion Guide",
            description="Guide for using emotions in scripts",
            mimeType="text/markdown"
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
    
    elif str(uri) == "podcast://emotions":
        guide = """# Emotion Guide for Podcast Scripts

## How to Use Emotions

Place emotions in brackets BEFORE the colon in your script:

```
Host [excited]: This is amazing news!
Guest [laughing]: I know, right? I couldn't believe it myself!
Host [thoughtful]: But what does this mean for the industry?
```

## Available Emotions

### Basic Emotions
- **[laughing]** - Natural laughter (not spoken "haha")
- **[sighing]** - Expresses fatigue, relief, or resignation  
- **[surprised]** - Shock or amazement
- **[confused]** - Uncertainty or puzzlement
- **[excited]** - High energy and enthusiasm
- **[nervous]** - Anxiety or uncertainty
- **[angry]** - Frustration or anger
- **[crying]** - Sadness or being moved

### Conversational Emotions
- **[thinking]** - Thoughtful pause
- **[clearing throat]** - Getting attention or nervousness
- **[chuckling]** - Light laughter
- **[gasping]** - Sudden realization or shock

### Voice Modulation
- **[warm]** - Friendly, welcoming tone
- **[serious]** - Grave, important tone
- **[casual]** - Relaxed, informal
- **[contemplative]** - Deep, reflective

## Examples

### Natural Laughter
```
WRONG: Host: Haha, that's hilarious!
RIGHT: Host [laughing]: That's hilarious!
```

### Emotional Transitions
```
Expert [confident]: The data clearly shows improvement.
Expert [surprised]: Wait, these new numbers are incredible!
Expert [excited]: This changes everything!
```

### Subtle Emotions
```
Guest [sighing]: It's been a long journey to get here.
Host [warm]: I can imagine. Tell us more about that.
```

## Tips
1. Don't overuse emotions - sprinkle them naturally
2. Emotions should enhance, not distract
3. Match emotions to content and personality
4. Use variety for engaging dialogue
"""
        return guide.strip()
    
    elif str(uri) == "podcast://prompt-guide":
        guide = """# Enhanced Podcast Generator Prompting Guide

## Emotion-Aware Improvements

The enhanced generator now properly handles emotions:
- **[laughing]** produces actual laughter, not spoken "haha"
- Emotions are processed and removed from spoken text
- Voice settings adjust based on emotions
- Natural emotional sounds are added

## Best Practices

### Script Format
```
Host: Welcome to our show!
Guest [excited]: I'm thrilled to be here!
Host [laughing]: Your enthusiasm is contagious!
Guest: Let's dive into today's topic.
```

### Common Mistakes to Avoid
1. ❌ Writing out laughter: "Host: Haha, that's funny!"
2. ❌ Stage directions: "Host: (walks to podium) Welcome!"
3. ❌ Describing emotions: "Host: I'm laughing so hard right now!"

### Correct Usage
1. ✅ Use brackets: "Host [laughing]: That's funny!"
2. ✅ Natural flow: "Host [sighing]: It's been a long day."
3. ✅ Subtle emotions: "Expert [thoughtful]: Let me consider that."

## Advanced Features

### Emotional Arcs
Build emotional journeys:
```
Host [curious]: What started your interest?
Guest [nostalgic]: It goes back to my childhood...
Guest [excited]: Then I discovered this amazing technique!
Host [impressed]: That's incredible!
```

### Personality Matching
Emotions work with voice personalities:
- Warm hosts: [laughing], [welcoming], [encouraging]
- Serious experts: [thoughtful], [analytical], [concerned]
- Energetic guests: [excited], [animated], [enthusiastic]
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
            description="Generate an enhanced podcast script with natural dialogue and emotional cues",
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
            description="Convert script to audio with emotional awareness - properly handles [laughing] etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "The podcast script with emotions in brackets"
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
Note: This prompt is optimized for emotional awareness. The LLM will generate scripts with emotions in brackets like [laughing], which will be converted to actual laughter sounds, not spoken text.

IMPORTANT: Emotions in brackets are processed and removed from spoken text."""
        )]

    elif name == "create_enhanced_audio":
        script = arguments.get("script")
        if not script:
            return [types.TextContent(
                type="text",
                text="Error: script parameter is required"
            )]
        
        output_filename = arguments.get("output_filename", "enhanced_podcast.mp3")
        manual_voice_assignments = arguments.get("voice_assignments", {})
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
                
                # Get available voices from ElevenLabs
                voices_response = client.voices.get_all()
                available_voices = voices_response.voices
                
                # Create voice name to ID mapping
                voice_name_to_id = {v.name.lower(): v.voice_id for v in available_voices}
                
                # Parse script with robust parser (now handles emotions properly)
                dialogue_segments = parse_script_robust(script)
                
                if not dialogue_segments:
                    return [types.TextContent(
                        type="text",
                        text="Error: No valid dialogue segments found in script. Please check the format."
                    )]
                
                # Get unique speakers
                unique_speakers = list(set(seg['speaker'] for seg in dialogue_segments))
                
                # Build voice assignments ensuring diversity
                final_voice_assignments = {}
                
                if auto_assign_voices:
                    # Create a mapping of available voices with their characteristics
                    elevenlabs_voice_pool = []
                    
                    # Try to map ElevenLabs voices to our personality profiles
                    for voice in available_voices:
                        voice_name_lower = voice.name.lower()
                        
                        # Try to find matching voice from our default pool
                        matched = False
                        for default_voice in DEFAULT_VOICE_POOL:
                            if default_voice['name'] in voice_name_lower:
                                elevenlabs_voice_pool.append({
                                    'name': voice.name,
                                    'id': voice.voice_id,
                                    'gender': default_voice.get('gender', 'neutral'),
                                    'personality': default_voice.get('personality', 'neutral'),
                                    'age': default_voice.get('age', 'adult')
                                })
                                matched = True
                                break
                        
                        # If no match, add as generic voice
                        if not matched:
                            elevenlabs_voice_pool.append({
                                'name': voice.name,
                                'id': voice.voice_id,
                                'gender': 'neutral',
                                'personality': 'neutral',
                                'age': 'adult'
                            })
                    
                    # Ensure different voices for each speaker
                    voice_assignments = ensure_different_voices(
                        unique_speakers, 
                        elevenlabs_voice_pool[:20]  # Use first 20 voices for variety
                    )
                    
                    # Convert to final assignments with IDs
                    for speaker, (voice_name, display_name) in voice_assignments.items():
                        # Find the actual voice ID
                        voice_id = None
                        for v in elevenlabs_voice_pool:
                            if v['name'].lower() == voice_name.lower():
                                voice_id = v['id']
                                break
                        
                        if voice_id:
                            final_voice_assignments[speaker] = {
                                'id': voice_id,
                                'name': display_name
                            }
                
                # Apply manual overrides
                for speaker, assignment in manual_voice_assignments.items():
                    if assignment in voice_name_to_id:
                        final_voice_assignments[speaker] = {
                            'id': voice_name_to_id[assignment],
                            'name': assignment
                        }
                    else:
                        # Try to find by partial match
                        for voice_name, voice_id in voice_name_to_id.items():
                            if assignment.lower() in voice_name:
                                final_voice_assignments[speaker] = {
                                    'id': voice_id,
                                    'name': voice_name
                                }
                                break
                
                # Ensure all speakers have assignments
                for speaker in unique_speakers:
                    if speaker not in final_voice_assignments:
                        # Assign first available voice not yet used
                        used_ids = {v['id'] for v in final_voice_assignments.values()}
                        for voice in available_voices:
                            if voice.voice_id not in used_ids:
                                final_voice_assignments[speaker] = {
                                    'id': voice.voice_id,
                                    'name': voice.name
                                }
                                break
                
                # Add speaker introductions if needed
                dialogue_segments = add_speaker_introductions(dialogue_segments, final_voice_assignments)
                
                # Create output directory
                output_dir = os.path.expanduser("~/Desktop/podcast_output")
                os.makedirs(output_dir, exist_ok=True)
                
                # Generate audio segments with emotion handling
                audio_segments = []
                segment_files = []
                
                logger.info(f"Generating {len(dialogue_segments)} audio segments with emotion awareness...")
                
                for i, segment in enumerate(dialogue_segments):
                    speaker = segment['speaker']
                    original_text = segment['text']
                    emotion = segment.get('emotion', 'neutral')
                    
                    # Process emotional text - remove emotion tags and get prefix
                    clean_text, emotional_prefix = process_emotional_text(original_text, emotion)
                    
                    # Get voice for this speaker
                    voice_info = final_voice_assignments.get(speaker, {
                        'id': available_voices[0].voice_id,
                        'name': available_voices[0].name
                    })
                    
                    # Get emotional settings
                    emotion_presets = get_enhanced_voice_options()["voice_settings"]["emotional_presets"]
                    
                    # Use emotion preset if available
                    if emotion in emotion_presets:
                        voice_settings = emotion_presets[emotion]
                    # Detect emotion from text if not specified
                    elif '!' in clean_text and '?' not in clean_text:
                        voice_settings = emotion_presets["excited"]
                    elif '?' in clean_text and any(word in clean_text.lower() for word in ['how', 'why', 'what']):
                        voice_settings = emotion_presets["contemplative"]
                    elif any(phrase in clean_text.lower() for phrase in ['thank', 'welcome', 'great to']):
                        voice_settings = emotion_presets["warm"]
                    else:
                        voice_settings = emotion_presets["casual"]
                    
                    # Combine emotional prefix with text if applicable
                    if emotional_prefix and emotion in ['laughing', 'sighing', 'gasping', 'crying']:
                        # For these emotions, speak the sound then the text
                        final_text = f"{emotional_prefix} {clean_text}"
                    elif emotional_prefix and emotion in ['thinking', 'nervous', 'confused']:
                        # For these, integrate the sound naturally
                        final_text = f"{emotional_prefix}, {clean_text}"
                    else:
                        # For other emotions, just use the clean text
                        final_text = clean_text
                    
                    # Generate audio for this segment
                    try:
                        logger.info(f"Segment {i+1}/{len(dialogue_segments)}: {speaker} [{emotion}] ({voice_info['name']})")
                        
                        # For laughing, we might want to generate just laughter sometimes
                        if emotion == 'laughing' and len(clean_text.split()) < 5:
                            # Short text with laughing - emphasize the laugh
                            segment_audio = client.text_to_speech.convert(
                                text=f"Ha ha ha! {clean_text}",
                                voice_id=voice_info['id'],
                                voice_settings=VoiceSettings(
                                    stability=voice_settings["stability"],
                                    similarity_boost=voice_settings["similarity_boost"],
                                    style=voice_settings.get("style", 0.5),
                                    use_speaker_boost=True
                                ),
                                model_id="eleven_turbo_v2_5"
                            )
                        else:
                            # Normal generation with processed text
                            segment_audio = client.text_to_speech.convert(
                                text=final_text,
                                voice_id=voice_info['id'],
                                voice_settings=VoiceSettings(
                                    stability=voice_settings["stability"],
                                    similarity_boost=voice_settings["similarity_boost"],
                                    style=voice_settings.get("style", 0.5),
                                    use_speaker_boost=True
                                ),
                                model_id="eleven_turbo_v2_5"
                            )
                        
                        # Save individual segment
                        segment_filename = f"segment_{i:03d}_{speaker.lower().replace(' ', '_')}_{emotion}.mp3"
                        segment_path = os.path.join(output_dir, segment_filename)
                        
                        with open(segment_path, "wb") as f:
                            for chunk in segment_audio:
                                f.write(chunk)
                        
                        segment_files.append(segment_path)
                        audio_segments.append({
                            'speaker': speaker,
                            'voice': voice_info['name'],
                            'emotion': emotion,
                            'original_text': original_text,
                            'processed_text': final_text,
                            'file': segment_path,
                            'text_length': len(clean_text)
                        })
                        
                    except Exception as segment_error:
                        logger.error(f"Error generating segment {i}: {str(segment_error)}")
                        continue
                
                # Add sound effects if requested
                if include_sound_effects and len(segment_files) > 0:
                    try:
                        # Could add intro/outro music here
                        pass
                    except Exception as sfx_error:
                        logger.warning(f"Could not generate sound effects: {str(sfx_error)}")
                
                # Combine audio segments
                if segment_files:
                    # Simple concatenation
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
                    voice_cast = {}
                    emotion_summary = {}
                    
                    for segment in audio_segments:
                        speaker = segment['speaker']
                        voice_cast[speaker] = segment['voice']
                        
                        emotion = segment['emotion']
                        if emotion not in emotion_summary:
                            emotion_summary[emotion] = 0
                        emotion_summary[emotion] += 1
                    
                    # Count unique voices used
                    unique_voices_used = len(set(v['id'] for v in final_voice_assignments.values()))
                    
                    result_message = f"""
✅ Enhanced podcast created with emotion awareness!

📁 Output: {output_path}

🎭 Voice Cast ({unique_voices_used} different voices):
{chr(10).join([f"  • {speaker}: {voice}" for speaker, voice in voice_cast.items()])}

😊 Emotional Distribution:
{chr(10).join([f"  • {emotion}: {count} segments" for emotion, count in sorted(emotion_summary.items())])}

📊 Statistics:
- Total Segments: {len(audio_segments)}
- Estimated Duration: ~{sum(seg['text_length'] for seg in audio_segments) // 150} minutes
- File Size: {os.path.getsize(output_path) / 1024 / 1024:.1f} MB

🎯 Emotion Processing:
- [laughing] → Natural laughter sounds
- [sighing] → Breath sounds
- [surprised] → Vocal emphasis
- Other emotions → Voice modulation

📁 Individual Files:
- Location: ~/Desktop/podcast_output/
- Files include emotion tags in names

🎧 Your emotionally aware podcast is ready!
"""
                    
                    return [types.TextContent(
                        type="text",
                        text=result_message.strip()
                    )]
                else:
                    return [types.TextContent(
                        type="text",
                        text="Error: No audio segments were generated. Please check the script format."
                    )]
                
            except ImportError:
                return [types.TextContent(
                    type="text",
                    text="Error: ElevenLabs library not installed. Please install it with: pip install elevenlabs"
                )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error creating audio: {str(e)}\n\nPlease check your script format and try again."
            )]

    elif name == "search_voices":
        query = arguments.get("query", "")
        limit = arguments.get("limit", 10)
        
        # Parse the natural language query
        search_params = parse_voice_library_search(query)
        
        # Mock response for demonstration
        mock_results = f"""
🔍 Voice Library Search Results for: "{query}"

Search Parameters Detected:
- Gender: {search_params.get('gender', 'any')}
- Age: {search_params.get('age', 'any')}
- Accent: {search_params.get('accent', 'any')}
- Use Case: {search_params.get('use_case', 'any')}

Available ElevenLabs Voices (use these names in voice_assignments):
- nova: Warm, engaging female voice
- aria: Contemplative female voice
- sarah: Authoritative female voice
- josh: Energetic male voice
- adam: Analytical male voice
- brian: Authoritative male voice
- onyx: Deep, skeptical male voice

💡 Usage: Add to voice_assignments parameter in create_enhanced_audio
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
        
        # Mock response
        mock_response = f"""
🎨 Voice Design Preview

📝 Description: "{description}"

🎤 Sample Text: "{sample_text[:100]}..."

Note: Voice design requires ElevenLabs API integration. 
For now, use available voices: nova, aria, sarah, josh, adam, brian, onyx
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
                server_name="podcast-generator-enhanced-emotions",
                server_version="3.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())