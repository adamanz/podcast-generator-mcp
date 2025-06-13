"""
FastMCP Podcast Generator Server with ElevenLabs Integration
Creates two-sided podcasts using actual ElevenLabs API
"""
import os
import json
import subprocess
import tempfile
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path

from fastmcp import FastMCP, Context
from fastmcp.types import TextContent

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, will use system env vars

# You'll need to install these
# uv pip install elevenlabs aiohttp

try:
    from elevenlabs import VoiceSettings, play, save
    from elevenlabs.client import AsyncElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    print("Warning: ElevenLabs not installed. Install with: uv pip install elevenlabs")

# Initialize the FastMCP server
mcp = FastMCP("Podcast Generator 🎙️")

# Default voices for the podcast
DEFAULT_HOST_VOICE = "Adam"
DEFAULT_GUEST_VOICE = "Alice"

# ElevenLabs voice IDs (you can expand this)
VOICE_ID_MAP = {
    "Adam": "pNInz6obpgDQGcFmaJgB",
    "Alice": "Xb7hH8MSUJpSbSDYk0k2",
    "Antoni": "ErXwobaYiN019PkySvjV",
    "Aria": "9BWtsMINqrJLrRacOk9x",
    "Arnold": "VR6AewLTigWG4xSOukaG",
    "Bill": "pqHfZKP75CvOlQylNhV4",
    "Brian": "nPczCjzI2devNBz1zQrb",
    "Callum": "N2lVS1w4EtoT3dr4eOWO",
    "Charlie": "IKne3meq5aSn9XLyUdCD",
    "Charlotte": "XB0fDUnXU5powFXDhCwa",
    "Clyde": "2EiwWnXFnvU5JabPnv8n",
    "Daniel": "onwK4e9ZLuTAKqWW03F9",
    "Dave": "CYw3kZ02Hs0563khs1Fj",
    "Domi": "AZnzlk1XvdvUeBnXmlld",
    "Dorothy": "ThT5KcBeYPX3keUQqHPh",
    "Emily": "LcfcDJNUP1GQjkzn1xUU",
    "Elli": "MF3mGyEYCl7XYWbV9V6O",
    "Grace": "oWAxZDx7w5VEj9dCyTzz",
    "Jessie": "t0jbNlBVZ17f02VDIeMI",
    "Laura": "FGY2WhTYpPnrIDTdsKH5"
}

# Available voices organized by category
AVAILABLE_VOICES = {
    "male": ["Adam", "Antoni", "Arnold", "Bill", "Brian", "Callum", "Charlie", "Clyde", "Daniel", "Dave"],
    "female": ["Alice", "Aria", "Charlotte", "Domi", "Dorothy", "Emily", "Elli", "Grace", "Jessie", "Laura"]
}

@mcp.resource("voices://available")
def get_available_voices() -> Dict[str, List[str]]:
    """Get list of available voices organized by category"""
    return AVAILABLE_VOICES

@mcp.resource("voices://recommended-pairs")
def get_recommended_voice_pairs() -> List[Dict[str, str]]:
    """Get recommended voice pairs for podcasts"""
    return [
        {"host": "Adam", "guest": "Alice", "description": "Classic male host, female guest - clear contrast"},
        {"host": "Charlie", "guest": "Brian", "description": "Two male voices with different tones"},
        {"host": "Emily", "guest": "Daniel", "description": "Female host, male guest - energetic combo"},
        {"host": "Grace", "guest": "Charlotte", "description": "Two female voices with complementary styles"},
        {"host": "Bill", "guest": "Aria", "description": "Deep male voice with bright female voice"},
        {"host": "Dorothy", "guest": "Clyde", "description": "Mature female host with casual male guest"}
    ]

@mcp.prompt(
    name="podcast_script_prompt",
    description="Generate an engaging podcast script with customizable style and personalities",
    arguments=[
        {"name": "topic", "description": "The main topic for the podcast episode", "required": True},
        {"name": "duration_minutes", "description": "Target duration in minutes (3-15 recommended)", "required": False},
        {"name": "style", "description": "Podcast style: conversational, interview, educational, debate", "required": False},
        {"name": "host_personality", "description": "Description of the host's personality traits", "required": False},
        {"name": "guest_personality", "description": "Description of the guest's personality traits", "required": False}
    ]
)
def podcast_script_prompt(
    topic: str,
    duration_minutes: int = 5,
    style: str = "conversational",
    host_personality: str = "friendly and curious",
    guest_personality: str = "knowledgeable and enthusiastic"
) -> str:
    """Generate a prompt for creating an engaging podcast script"""
    
    # Estimate number of exchanges based on duration
    # Assuming ~30 seconds per exchange on average
    estimated_exchanges = duration_minutes * 2
    
    return f"""Create an engaging {duration_minutes}-minute podcast script about "{topic}".

Style: {style}
Host personality: {host_personality}
Guest personality: {guest_personality}

Guidelines:
1. Start with a warm, natural introduction from the host
2. Include approximately {estimated_exchanges} exchanges between host and guest
3. Use natural conversational language with occasional filler words like "um", "well", "you know"
4. Include follow-up questions that show active listening
5. Add personality through tone, word choice, and speaking patterns
6. Include moments of humor, surprise, or insight
7. End with a meaningful summary and friendly sign-off

Format the output as JSON with this structure:
{{
    "title": "Catchy Episode Title",
    "description": "One-line episode description that hooks listeners",
    "dialogue": [
        {{"speaker": "host", "text": "Welcome to Tech Talk Today! I'm super excited..."}},
        {{"speaker": "guest", "text": "Thanks for having me! I've been looking forward..."}},
        ...
    ]
}}

Important: Keep each dialogue turn concise (1-3 sentences) for natural pacing.
Make the conversation feel authentic and engaging, like a real podcast listeners would enjoy."""
@mcp.tool
async def generate_podcast_script(
    ctx: Context,
    topic: str,
    duration_minutes: int = 5,
    style: str = "conversational",
    host_personality: str = "friendly and curious", 
    guest_personality: str = "knowledgeable and enthusiastic"
) -> Dict:
    """
    Generate a podcast script on any topic using AI.
    
    Args:
        topic: The main topic for the podcast episode
        duration_minutes: Target duration in minutes (affects script length)
        style: Podcast style (conversational, interview, educational, debate, storytelling)
        host_personality: Description of the host's personality
        guest_personality: Description of the guest's personality
        ctx: MCP context for LLM sampling
    
    Returns:
        Dictionary containing the generated script with title, description, and dialogue
    """
    await ctx.info(f"🎬 Generating {duration_minutes}-minute podcast script about '{topic}'...")
    
    # Get the prompt
    prompt = podcast_script_prompt(topic, duration_minutes, style, host_personality, guest_personality)
    
    # Use the LLM to generate the script
    response = await ctx.sample(prompt, max_tokens=4000)
    
    try:
        # Parse the JSON response
        script_data = json.loads(response.text)
        
        # Validate structure
        if not all(key in script_data for key in ["title", "description", "dialogue"]):
            raise ValueError("Missing required fields in generated script")
        
        await ctx.info(f"✅ Generated script: '{script_data['title']}' with {len(script_data['dialogue'])} exchanges")
        return script_data
        
    except (json.JSONDecodeError, ValueError) as e:
        await ctx.error(f"Failed to parse script: {e}")
        # Return a fallback structure
        return {
            "title": f"Podcast about {topic}",
            "description": f"A {style} discussion about {topic}",
            "dialogue": [
                {"speaker": "host", "text": f"Welcome to our podcast about {topic}!"},
                {"speaker": "guest", "text": "Thanks for having me! I'm excited to dive into this topic."}
            ]
        }

async def generate_audio_elevenlabs(
    text: str,
    voice_name: str,
    output_path: str,
    api_key: Optional[str] = None
) -> bool:
    """Generate audio using ElevenLabs API"""
    if not ELEVENLABS_AVAILABLE:
        return False
    
    try:
        # Initialize client
        if api_key:
            client = AsyncElevenLabs(api_key=api_key)
        else:
            # Will use ELEVENLABS_API_KEY env variable
            client = AsyncElevenLabs()
        
        voice_id = VOICE_ID_MAP.get(voice_name, VOICE_ID_MAP["Adam"])
        
        # Generate audio
        audio = await client.generate(
            text=text,
            voice=voice_id,
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.0,
                use_speaker_boost=True
            ),
            model="eleven_turbo_v2"
        )
        
        # Save the audio
        save(audio, output_path)
        return True
        
    except Exception as e:
        print(f"ElevenLabs API error: {e}")
        return False
@mcp.tool
async def create_podcast_audio(
    ctx: Context,
    script: Dict,
    host_voice: str = DEFAULT_HOST_VOICE,
    guest_voice: str = DEFAULT_GUEST_VOICE,
    output_dir: Optional[str] = None,
    add_pauses: bool = True,
    elevenlabs_api_key: Optional[str] = None
) -> Dict:
    """
    Create audio files from a podcast script using ElevenLabs voices.
    
    Args:
        script: Podcast script dictionary with dialogue array
        host_voice: Voice name for the host
        guest_voice: Voice name for the guest 
        output_dir: Directory to save audio files (defaults to Desktop/podcast_[timestamp])
        add_pauses: Whether to add pauses between speakers
        elevenlabs_api_key: Optional API key (otherwise uses env variable)
        ctx: MCP context for progress reporting
    
    Returns:
        Dictionary with paths to created audio files and metadata
    """
    # Create output directory
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.expanduser(f"~/Desktop/podcast_{timestamp}")
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Save script for reference
    script_path = os.path.join(output_dir, "script.json")
    with open(script_path, 'w', encoding='utf-8') as f:
        json.dump(script, f, indent=2, ensure_ascii=False)
    
    await ctx.info(f"🎙️ Creating podcast audio in {output_dir}")
    
    audio_files = []
    total_lines = len(script.get("dialogue", []))
    
    # Check if we can use ElevenLabs
    use_elevenlabs = ELEVENLABS_AVAILABLE and (elevenlabs_api_key or os.getenv("ELEVENLABS_API_KEY"))
    
    if not use_elevenlabs:
        await ctx.warning("ElevenLabs not available. Creating placeholder files instead.")
    
    # Generate audio for each line
    for i, line in enumerate(script.get("dialogue", [])):
        speaker = line.get("speaker", "host")
        text = line.get("text", "")
        voice = host_voice if speaker == "host" else guest_voice
        
        await ctx.report_progress((i + 1) / total_lines, f"Generating audio {i+1}/{total_lines}: {speaker}")
        
        # Create filename
        filename = f"{i:03d}_{speaker}.mp3"
        filepath = os.path.join(output_dir, filename)
        
        # Generate audio
        if use_elevenlabs:
            success = await generate_audio_elevenlabs(text, voice, filepath, elevenlabs_api_key)
            if success:
                await ctx.info(f"✅ Generated: {filename} with {voice}'s voice")
            else:
                await ctx.warning(f"⚠️ Failed to generate {filename}, creating placeholder")
                # Create a placeholder file
                with open(filepath, 'wb') as f:
                    f.write(b'placeholder')
        else:
            # Create placeholder
            with open(filepath, 'wb') as f:
                f.write(b'placeholder')
        
        audio_files.append({
            "index": i,
            "speaker": speaker,
            "voice": voice,
            "text": text,
            "filepath": filepath
        })
    
    # Create silence file for pauses
    silence_path = None
    if add_pauses:
        silence_path = os.path.join(output_dir, "silence.mp3")
        await ctx.info("Creating pause file...")
        
        # Use ffmpeg to create 0.5 second silence
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
            "-t", "0.5", "-q:a", "9", "-acodec", "mp3", silence_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            await ctx.warning("Could not create silence file")
            add_pauses = False
    
    # Generate concat file for ffmpeg
    concat_file = os.path.join(output_dir, "concat_list.txt")
    with open(concat_file, 'w') as f:
        for i, audio in enumerate(audio_files):
            # Escape single quotes in filepath
            escaped_path = audio['filepath'].replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")
            if add_pauses and i < len(audio_files) - 1 and silence_path:
                f.write(f"file '{silence_path}'\n")
    
    return {
        "output_dir": output_dir,
        "script_path": script_path,
        "audio_files": audio_files,
        "concat_file": concat_file,
        "title": script.get("title", "Untitled Podcast"),
        "description": script.get("description", ""),
        "has_audio": use_elevenlabs
    }
@mcp.tool
async def combine_podcast_audio(
    ctx: Context,
    podcast_data: Dict,
    output_filename: Optional[str] = None,
    normalize_audio: bool = True,
    add_fade: bool = True
) -> str:
    """
    Combine individual audio files into a single podcast episode.
    
    Args:
        podcast_data: Output from create_podcast_audio tool
        output_filename: Name for the final podcast file
        normalize_audio: Whether to normalize audio levels
        add_fade: Whether to add fade in/out effects
        ctx: MCP context
    
    Returns:
        Path to the final combined podcast file
    """
    output_dir = podcast_data["output_dir"]
    concat_file = podcast_data["concat_file"]
    
    if not podcast_data.get("has_audio", False):
        await ctx.warning("No real audio files were generated. Skipping combination.")
        return ""
    
    if output_filename is None:
        # Clean title for filename
        clean_title = podcast_data['title'].replace(' ', '_').replace('/', '_')
        output_filename = f"{clean_title}.mp3"
    
    output_path = os.path.join(output_dir, output_filename)
    
    await ctx.info(f"🎵 Combining audio files into {output_filename}...")
    
    try:
        # Check if ffmpeg is available
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            await ctx.error("ffmpeg not found. Please install ffmpeg to combine audio files.")
            return ""
        
        # Basic concatenation
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_file, "-c", "copy", output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            await ctx.error(f"ffmpeg error: {result.stderr}")
            return ""
        
        # Apply audio filters if requested
        if normalize_audio or add_fade:
            processed_path = output_path.replace(".mp3", "_processed.mp3")
            filters = []
            
            if normalize_audio:
                filters.append("loudnorm=I=-16:TP=-1.5:LRA=11")
            
            if add_fade:
                # Add 2 second fade in and 3 second fade out
                # We need to get the duration first
                duration_cmd = [
                    "ffprobe", "-v", "error", "-show_entries", 
                    "format=duration", "-of", "json", output_path
                ]
                duration_result = subprocess.run(duration_cmd, capture_output=True, text=True)
                
                try:
                    duration_data = json.loads(duration_result.stdout)
                    duration = float(duration_data["format"]["duration"])
                    fade_out_start = max(0, duration - 3)
                    filters.append(f"afade=t=in:st=0:d=2,afade=t=out:st={fade_out_start}:d=3")
                except:
                    # If we can't get duration, just do fade in
                    filters.append("afade=t=in:st=0:d=2")
            
            if filters:
                filter_string = ",".join(filters)
                cmd = [
                    "ffmpeg", "-y", "-i", output_path,
                    "-af", filter_string,
                    processed_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    output_path = processed_path
                    await ctx.info("✅ Applied audio processing")
        
        # Create a metadata file
        metadata_path = os.path.join(output_dir, "metadata.json")
        metadata = {
            "title": podcast_data["title"],
            "description": podcast_data["description"],
            "created_at": datetime.now().isoformat(),
            "final_audio": output_path,
            "duration_estimate": f"{len(podcast_data['audio_files']) * 0.5} minutes"
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        await ctx.info(f"✅ Podcast created successfully: {output_path}")
        return output_path
        
    except Exception as e:
        await ctx.error(f"Error combining audio: {str(e)}")
        return ""
@mcp.tool
async def generate_full_podcast(
    ctx: Context,
    topic: str,
    duration_minutes: int = 5,
    host_voice: str = DEFAULT_HOST_VOICE,
    guest_voice: str = DEFAULT_GUEST_VOICE,
    style: str = "conversational",
    elevenlabs_api_key: Optional[str] = None
) -> Dict:
    """
    Generate a complete podcast from topic to final audio file.
    
    This is an all-in-one tool that:
    1. Generates a script using AI
    2. Creates audio for each line using ElevenLabs
    3. Combines into a final podcast with effects
    
    Args:
        topic: The podcast topic
        duration_minutes: Target duration (3-15 minutes recommended)
        host_voice: Voice for the host (see voices://available)
        guest_voice: Voice for the guest
        style: Podcast style (conversational, interview, educational, debate)
        elevenlabs_api_key: Optional API key (otherwise uses ELEVENLABS_API_KEY env var)
        ctx: MCP context
    
    Returns:
        Dictionary with all generated assets and paths
    """
    await ctx.info(f"🚀 Starting full podcast generation about '{topic}'...")
    
    # Step 1: Generate script
    await ctx.info("Step 1/3: Generating script...")
    script = await generate_podcast_script(
        ctx=ctx,
        topic=topic,
        duration_minutes=duration_minutes,
        style=style
    )
    
    # Step 2: Create audio files
    await ctx.info("Step 2/3: Creating audio files...")
    audio_data = await create_podcast_audio(
        ctx=ctx,
        script=script,
        host_voice=host_voice,
        guest_voice=guest_voice,
        elevenlabs_api_key=elevenlabs_api_key
    )
    
    # Step 3: Combine audio
    final_path = ""
    if audio_data.get("has_audio", False):
        await ctx.info("Step 3/3: Combining audio files...")
        final_path = await combine_podcast_audio(
            ctx=ctx,
            podcast_data=audio_data,
            normalize_audio=True,
            add_fade=True
        )
    
    await ctx.info(f"✅ Podcast generation complete!")
    
    return {
        "script": script,
        "audio_data": audio_data,
        "final_podcast": final_path,
        "output_directory": audio_data["output_dir"],
        "success": bool(final_path)
    }

@mcp.prompt(
    name="podcast_topic_suggestions",
    description="Generate 5 engaging podcast topic ideas with hooks and talking points",
    arguments=[
        {"name": "genre", "description": "Genre for topics: technology, science, business, health, culture, etc.", "required": False}
    ]
)
def podcast_topic_suggestions(genre: str = "technology") -> str:
    """Generate engaging podcast topic suggestions"""
    return f"""Suggest 5 engaging podcast topics in the {genre} genre.

For each topic, provide:
1. A catchy, specific title (not generic)
2. A compelling hook/description (2-3 sentences that make people want to listen)
3. Three unique talking points or questions to explore
4. An interesting angle or controversy to discuss
5. A potential surprising fact or story to include

Format as a numbered list with clear structure. Make each topic feel fresh and timely."""

@mcp.prompt(
    name="improve_podcast_dialogue",
    description="Enhance existing podcast dialogue with natural speech patterns and emotions",
    arguments=[
        {"name": "dialogue_text", "description": "The dialogue text to improve", "required": True}
    ]
)
def improve_podcast_dialogue(dialogue_text: str) -> str:
    """Improve podcast dialogue to make it more engaging"""
    return f"""Improve this podcast dialogue to make it more natural and engaging:

{dialogue_text}

Guidelines:
1. Add natural speech patterns (um, well, you know) sparingly
2. Include interruptions or overlapping thoughts
3. Add emotional reactions (laughs, gasps, "wow!")
4. Make questions more conversational
5. Include specific examples or anecdotes
6. Add personality quirks to each speaker

Return the improved dialogue in the same format."""

@mcp.prompt(
    name="podcast_series_workflow",
    description="Create a multi-episode podcast series plan with consistent themes and progression",
    arguments=[
        {"name": "series_topic", "description": "Overall topic for the podcast series", "required": True},
        {"name": "num_episodes", "description": "Number of episodes to plan (3-10)", "required": True},
        {"name": "target_audience", "description": "Description of the target audience", "required": False},
        {"name": "series_style", "description": "Consistent style across episodes", "required": False}
    ]
)
def podcast_series_workflow(
    series_topic: str,
    num_episodes: int = 6,
    target_audience: str = "general audience interested in learning",
    series_style: str = "educational with conversational tone"
) -> str:
    """Create a structured plan for a podcast series"""
    return f"""Design a {num_episodes}-episode podcast series about "{series_topic}".

Target Audience: {target_audience}
Series Style: {series_style}

For the series, provide:

1. Series Overview:
   - Compelling series title
   - Series description (2-3 sentences)
   - Key themes and learning objectives
   - Ideal host/guest dynamic

2. Episode Breakdown:
   For each episode, include:
   - Episode number and title
   - Specific focus/subtopic
   - Key questions to explore
   - Guest expertise needed
   - Connection to previous/next episodes
   - One unique hook or revelation

3. Series Arc:
   - How topics build on each other
   - Recurring segments or features
   - Series finale payoff

4. Production Notes:
   - Recommended host/guest voice pairings
   - Music/tone suggestions
   - Engagement strategies

Create a cohesive series that keeps listeners coming back."""

# Resources for help and examples
@mcp.resource("help://quickstart")
def get_quickstart_guide() -> str:
    """Get a quickstart guide for the podcast generator"""
    return """# 🎙️ Podcast Generator Quick Start Guide

## Prerequisites:
- Set your ElevenLabs API key: export ELEVENLABS_API_KEY="your-key"
- Install ffmpeg for audio processing

## Generate Your First Podcast:

### Method 1: All-in-One (Recommended)
Use the `generate_full_podcast` tool:
```
{
  "topic": "The Future of Space Travel",
  "duration_minutes": 5,
  "host_voice": "Adam",
  "guest_voice": "Alice",
  "style": "conversational"
}
```

### Method 2: Step-by-Step
1. Generate script: `generate_podcast_script`
2. Create audio: `create_podcast_audio` 
3. Combine: `combine_podcast_audio`

## Voice Options:
- Male voices: Adam, Bill, Charlie, Daniel, Brian
- Female voices: Alice, Emily, Grace, Charlotte, Aria
- See `voices://available` for full list

## Styles:
- conversational: Natural back-and-forth
- interview: Question-focused
- educational: Teaching-oriented
- debate: Point-counterpoint

## Tips:
- 5-10 minutes is ideal length
- Mix voice genders for contrast
- Use specific, timely topics
- Check output folder on Desktop"""

@mcp.resource("examples://topics")
def get_example_topics() -> List[Dict[str, str]]:
    """Get example podcast topics that work well"""
    return [
        {
            "topic": "AI Taking Over Creative Jobs: Threat or Opportunity?",
            "style": "debate",
            "description": "A balanced discussion on AI's impact on creative industries"
        },
        {
            "topic": "The Psychology of Social Media Addiction",
            "style": "educational",
            "description": "Expert insights on how platforms hook us and how to break free"
        },
        {
            "topic": "My Journey from Burnout to Balance",
            "style": "conversational",
            "description": "Personal stories and practical tips for work-life balance"
        },
        {
            "topic": "Cryptocurrency for Complete Beginners",
            "style": "educational",
            "description": "Demystifying crypto without the jargon"
        },
        {
            "topic": "The Future of Food: Lab Grown Meat",
            "style": "interview",
            "description": "Scientists explain how we'll eat in 2050"
        }
    ]

@mcp.resource("status://api")
def check_api_status() -> Dict[str, Any]:
    """Check if ElevenLabs API is configured"""
    return {
        "elevenlabs_available": ELEVENLABS_AVAILABLE,
        "api_key_configured": bool(os.getenv("ELEVENLABS_API_KEY")),
        "ffmpeg_available": subprocess.run(["which", "ffmpeg"], capture_output=True).returncode == 0,
        "ready": ELEVENLABS_AVAILABLE and bool(os.getenv("ELEVENLABS_API_KEY"))
    }

if __name__ == "__main__":
    # Run the server with stdio transport (default)
    mcp.run()
