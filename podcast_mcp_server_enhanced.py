"""
Enhanced FastMCP Podcast Generator Server with Multi-Format Support
Creates two-sided podcasts from various content sources including PDFs, text files, and more
"""
import os
import json
import subprocess
import tempfile
from typing import List, Dict, Optional, Tuple, Any, Union
from datetime import datetime
from pathlib import Path
import mimetypes
import base64
import re

from fastmcp import FastMCP, Context

# You'll need to install these
# uv pip install elevenlabs aiohttp pypdf2 python-docx markdown beautifulsoup4 pydub

try:
    from elevenlabs import VoiceSettings, play, save
    from elevenlabs.client import AsyncElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    print("Warning: ElevenLabs not installed. Install with: uv pip install elevenlabs")

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    print("Warning: PyPDF2 not installed. Install with: uv pip install pypdf2")

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("Warning: python-docx not installed. Install with: uv pip install python-docx")

try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    print("Warning: markdown not installed. Install with: uv pip install markdown")

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("Warning: BeautifulSoup not installed. Install with: uv pip install beautifulsoup4")

try:
    from pydub import AudioSegment
    from pydub.effects import normalize
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("Warning: pydub not installed. Install with: uv pip install pydub")

# Initialize the FastMCP server
mcp = FastMCP("Podcast Generator Pro 🎙️")

# Default voices for the podcast
DEFAULT_HOST_VOICE = "Adam"
DEFAULT_GUEST_VOICE = "Alice"

# ElevenLabs voice IDs (expanded list)
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
    "female": ["Alice", "Aria", "Charlotte", "Domi", "Dorothy", "Emily", "Elli", "Grace", "Jessie", "Laura"],
    "accents": {
        "british": ["Charlie", "Charlotte"],
        "american": ["Adam", "Alice", "Emily", "Daniel"],
        "australian": ["Callum", "Grace"],
        "diverse": ["Antoni", "Aria", "Domi"]
    }
}

# Supported file formats
SUPPORTED_FORMATS = {
    ".pdf": "PDF documents",
    ".txt": "Plain text files",
    ".md": "Markdown files",
    ".docx": "Word documents",
    ".html": "HTML files",
    ".json": "JSON data files",
    ".csv": "CSV data files",
    ".rtf": "Rich text format"
}

# Content extraction functions
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    if not PYPDF2_AVAILABLE:
        return "PDF support not available. Install pypdf2."
    
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            return text.strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file"""
    if not DOCX_AVAILABLE:
        return "DOCX support not available. Install python-docx."
    
    try:
        doc = Document(file_path)
        text = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text.append(paragraph.text)
        return "\n".join(text)
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def extract_text_from_html(file_path: str) -> str:
    """Extract text from HTML file"""
    if not BS4_AVAILABLE:
        return "HTML parsing not available. Install beautifulsoup4."
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            return soup.get_text().strip()
    except Exception as e:
        return f"Error reading HTML: {str(e)}"

def extract_text_from_markdown(file_path: str) -> str:
    """Extract text from Markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            if MARKDOWN_AVAILABLE:
                # Convert to HTML then extract text
                html = markdown.markdown(content)
                if BS4_AVAILABLE:
                    soup = BeautifulSoup(html, 'html.parser')
                    return soup.get_text().strip()
            # Fallback: just return the markdown content
            return content
    except Exception as e:
        return f"Error reading Markdown: {str(e)}"

def extract_text_from_file(file_path: str) -> str:
    """Extract text from various file formats"""
    ext = Path(file_path).suffix.lower()
    
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    elif ext == '.html' or ext == '.htm':
        return extract_text_from_html(file_path)
    elif ext == '.md':
        return extract_text_from_markdown(file_path)
    elif ext in ['.txt', '.csv', '.json', '.rtf']:
        # Plain text formats
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    else:
        return f"Unsupported file format: {ext}"

@mcp.resource("voices://available")
def get_available_voices() -> Dict[str, Any]:
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

@mcp.resource("formats://supported")
def get_supported_formats() -> Dict[str, str]:
    """Get list of supported file formats"""
    return SUPPORTED_FORMATS

@mcp.resource("status://system")
def check_system_status() -> Dict[str, Any]:
    """Check system status and available features"""
    return {
        "elevenlabs_available": ELEVENLABS_AVAILABLE,
        "api_key_configured": bool(os.getenv("ELEVENLABS_API_KEY")),
        "ffmpeg_available": subprocess.run(["which", "ffmpeg"], capture_output=True).returncode == 0,
        "pdf_support": PYPDF2_AVAILABLE,
        "docx_support": DOCX_AVAILABLE,
        "markdown_support": MARKDOWN_AVAILABLE,
        "html_support": BS4_AVAILABLE,
        "advanced_audio": PYDUB_AVAILABLE,
        "ready": ELEVENLABS_AVAILABLE and bool(os.getenv("ELEVENLABS_API_KEY"))
    }

@mcp.tool
async def extract_content_from_file(
    ctx: Context,
    file_path: str,
    max_length: Optional[int] = None
) -> Dict[str, Any]:
    """
    Extract text content from various file formats.
    
    Args:
        file_path: Path to the file to extract content from
        max_length: Maximum length of extracted text (optional)
        ctx: MCP context
    
    Returns:
        Dictionary with extracted content and metadata
    """
    await ctx.info(f"📄 Extracting content from {file_path}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        await ctx.error(f"File not found: {file_path}")
        return {"success": False, "error": "File not found"}
    
    # Get file info
    file_stat = os.stat(file_path)
    file_ext = Path(file_path).suffix.lower()
    
    # Extract content
    content = extract_text_from_file(file_path)
    
    if content.startswith("Error"):
        await ctx.error(content)
        return {"success": False, "error": content}
    
    # Truncate if needed
    if max_length and len(content) > max_length:
        content = content[:max_length] + "..."
        await ctx.warning(f"Content truncated to {max_length} characters")
    
    await ctx.info(f"✅ Extracted {len(content)} characters from {file_ext} file")
    
    return {
        "success": True,
        "file_path": file_path,
        "file_type": file_ext,
        "file_size": file_stat.st_size,
        "content": content,
        "content_length": len(content),
        "extracted_at": datetime.now().isoformat()
    }

@mcp.tool
async def generate_podcast_from_file(
    ctx: Context,
    file_path: str,
    podcast_style: str = "summary",
    duration_minutes: int = 5,
    host_voice: str = DEFAULT_HOST_VOICE,
    guest_voice: str = DEFAULT_GUEST_VOICE,
    elevenlabs_api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a podcast from a file (PDF, TXT, DOCX, etc).
    
    Args:
        file_path: Path to the source file
        podcast_style: Style of podcast (summary, analysis, discussion, tutorial)
        duration_minutes: Target duration
        host_voice: Voice for the host
        guest_voice: Voice for the guest
        elevenlabs_api_key: Optional API key
        ctx: MCP context
    
    Returns:
        Dictionary with generated podcast data
    """
    await ctx.info(f"🎙️ Generating podcast from {file_path}")
    
    # Extract content
    extracted = await extract_content_from_file(ctx, file_path, max_length=10000)
    
    if not extracted["success"]:
        return extracted
    
    content = extracted["content"]
    file_type = extracted["file_type"]
    
    # Generate appropriate topic based on style
    if podcast_style == "summary":
        topic = f"Summary and key insights from this {file_type} document"
    elif podcast_style == "analysis":
        topic = f"Deep analysis and critique of this {file_type} content"
    elif podcast_style == "discussion":
        topic = f"Open discussion about the ideas in this {file_type} file"
    elif podcast_style == "tutorial":
        topic = f"Educational breakdown of concepts from this {file_type} document"
    else:
        topic = f"Podcast about this {file_type} content"
    
    # Create a specialized prompt for file-based podcasts
    prompt = f"""Create a {duration_minutes}-minute podcast script based on the following content:

File Type: {file_type}
Podcast Style: {podcast_style}

CONTENT:
{content[:5000]}...

Guidelines for {podcast_style} style:
1. Host should introduce what document/file they're discussing
2. Extract and discuss the main points clearly
3. Add relevant context and explanations
4. Make it engaging and accessible to listeners
5. Include specific quotes or examples from the content
6. End with key takeaways

Format as JSON with structure:
{{
    "title": "Episode Title",
    "description": "Episode description",
    "dialogue": [
        {{"speaker": "host", "text": "..."}},
        {{"speaker": "guest", "text": "..."}}
    ]
}}"""
    
    # Generate script
    response = await ctx.sample(prompt, max_tokens=4000)
    
    try:
        script = json.loads(response.text)
        await ctx.info(f"✅ Generated script from {file_type} file")
        
        # Continue with audio generation
        audio_data = await create_podcast_audio(
            ctx=ctx,
            script=script,
            host_voice=host_voice,
            guest_voice=guest_voice,
            elevenlabs_api_key=elevenlabs_api_key
        )
        
        # Combine audio
        final_path = ""
        if audio_data.get("has_audio", False):
            final_path = await combine_podcast_audio(
                ctx=ctx,
                podcast_data=audio_data,
                normalize_audio=True,
                add_fade=True
            )
        
        return {
            "success": True,
            "source_file": file_path,
            "script": script,
            "audio_data": audio_data,
            "final_podcast": final_path,
            "output_directory": audio_data["output_dir"]
        }
        
    except Exception as e:
        await ctx.error(f"Failed to generate podcast: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool
async def create_podcast_series(
    ctx: Context,
    file_paths: List[str],
    series_title: str,
    episode_duration: int = 5,
    host_voice: str = DEFAULT_HOST_VOICE,
    guest_voice: str = DEFAULT_GUEST_VOICE
) -> Dict[str, Any]:
    """
    Create a podcast series from multiple files.
    
    Args:
        file_paths: List of file paths to create episodes from
        series_title: Title for the podcast series
        episode_duration: Duration for each episode
        host_voice: Consistent host voice across episodes
        guest_voice: Consistent guest voice across episodes
        ctx: MCP context
    
    Returns:
        Dictionary with series data and episode information
    """
    await ctx.info(f"🎬 Creating podcast series: {series_title}")
    
    # Create series directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    series_dir = os.path.expanduser(f"~/Desktop/podcast_series_{timestamp}")
    Path(series_dir).mkdir(parents=True, exist_ok=True)
    
    episodes = []
    
    for i, file_path in enumerate(file_paths):
        await ctx.info(f"Creating episode {i+1}/{len(file_paths)} from {file_path}")
        
        # Generate episode
        episode_data = await generate_podcast_from_file(
            ctx=ctx,
            file_path=file_path,
            podcast_style="discussion",
            duration_minutes=episode_duration,
            host_voice=host_voice,
            guest_voice=guest_voice
        )
        
        if episode_data.get("success"):
            episodes.append({
                "episode_number": i + 1,
                "source_file": file_path,
                "title": episode_data["script"]["title"],
                "audio_path": episode_data.get("final_podcast", ""),
                "output_dir": episode_data["output_directory"]
            })
    
    # Create series metadata
    series_metadata = {
        "series_title": series_title,
        "total_episodes": len(episodes),
        "episodes": episodes,
        "created_at": datetime.now().isoformat(),
        "series_directory": series_dir
    }
    
    # Save series info
    with open(os.path.join(series_dir, "series_info.json"), 'w') as f:
        json.dump(series_metadata, f, indent=2)
    
    await ctx.info(f"✅ Created series with {len(episodes)} episodes")
    
    return series_metadata

@mcp.tool
async def add_background_music(
    ctx: Context,
    podcast_path: str,
    music_path: Optional[str] = None,
    music_volume: float = 0.1,
    fade_duration: int = 3
) -> str:
    """
    Add background music to a podcast.
    
    Args:
        podcast_path: Path to the podcast audio file
        music_path: Path to background music (optional, uses default if not provided)
        music_volume: Volume level for music (0.0 to 1.0)
        fade_duration: Fade in/out duration in seconds
        ctx: MCP context
    
    Returns:
        Path to the podcast with background music
    """
    if not PYDUB_AVAILABLE:
        await ctx.error("Advanced audio features not available. Install pydub.")
        return ""
    
    await ctx.info("🎵 Adding background music to podcast")
    
    try:
        # Load podcast
        podcast = AudioSegment.from_mp3(podcast_path)
        
        # Create or load background music
        if music_path and os.path.exists(music_path):
            music = AudioSegment.from_file(music_path)
        else:
            # Generate simple background music using ffmpeg
            await ctx.info("Generating ambient background music")
            temp_music = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            
            # Create a simple ambient tone
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", f"anoisesrc=d={len(podcast)/1000}:c=brown:r=44100",
                "-af", "volume=0.1,lowpass=f=200",
                temp_music.name
            ]
            subprocess.run(cmd, capture_output=True)
            music = AudioSegment.from_mp3(temp_music.name)
            os.unlink(temp_music.name)
        
        # Adjust music length to match podcast
        if len(music) < len(podcast):
            music = music * (len(podcast) // len(music) + 1)
        music = music[:len(podcast)]
        
        # Adjust music volume
        music = music - (20 * (1 - music_volume))  # Reduce volume
        
        # Apply fade to music
        music = music.fade_in(fade_duration * 1000).fade_out(fade_duration * 1000)
        
        # Mix podcast with music
        combined = podcast.overlay(music)
        
        # Save output
        output_path = podcast_path.replace(".mp3", "_with_music.mp3")
        combined.export(output_path, format="mp3")
        
        await ctx.info(f"✅ Added background music: {output_path}")
        return output_path
        
    except Exception as e:
        await ctx.error(f"Error adding music: {str(e)}")
        return ""

@mcp.tool
async def analyze_audio_quality(
    ctx: Context,
    audio_path: str
) -> Dict[str, Any]:
    """
    Analyze the quality of generated podcast audio.
    
    Args:
        audio_path: Path to the audio file
        ctx: MCP context
    
    Returns:
        Dictionary with audio quality metrics
    """
    await ctx.info("🔍 Analyzing audio quality")
    
    try:
        # Use ffmpeg to get audio stats
        cmd = [
            "ffmpeg", "-i", audio_path, "-af", "astats", "-f", "null", "-"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Parse basic info
        duration_cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration,bit_rate", "-of", "json", audio_path
        ]
        
        duration_result = subprocess.run(duration_cmd, capture_output=True, text=True)
        info = json.loads(duration_result.stdout)
        
        # Get file size
        file_size = os.path.getsize(audio_path)
        
        quality_data = {
            "file_path": audio_path,
            "duration_seconds": float(info["format"]["duration"]),
            "duration_formatted": f"{int(float(info['format']['duration']) // 60)}:{int(float(info['format']['duration']) % 60):02d}",
            "bit_rate": info["format"].get("bit_rate", "unknown"),
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "quality_notes": []
        }
        
        # Add quality assessments
        bit_rate_int = int(info["format"].get("bit_rate", 0))
        if bit_rate_int > 192000:
            quality_data["quality_notes"].append("High quality audio (>192 kbps)")
        elif bit_rate_int > 128000:
            quality_data["quality_notes"].append("Good quality audio (>128 kbps)")
        else:
            quality_data["quality_notes"].append("Lower quality audio - consider higher bitrate")
        
        if PYDUB_AVAILABLE:
            # Additional analysis with pydub
            audio = AudioSegment.from_mp3(audio_path)
            quality_data["channels"] = audio.channels
            quality_data["frame_rate"] = audio.frame_rate
            quality_data["sample_width"] = audio.sample_width
            quality_data["max_dbfs"] = audio.max_dBFS
            
            if audio.max_dBFS < -20:
                quality_data["quality_notes"].append("Audio might be too quiet")
            elif audio.max_dBFS > -3:
                quality_data["quality_notes"].append("Audio might be too loud or clipping")
        
        await ctx.info("✅ Audio analysis complete")
        return quality_data
        
    except Exception as e:
        await ctx.error(f"Error analyzing audio: {str(e)}")
        return {"error": str(e)}

@mcp.prompt
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

@mcp.prompt
def content_to_podcast_prompt(
    content: str,
    content_type: str,
    style: str = "educational"
) -> str:
    """Convert document content into an engaging podcast script"""
    
    return f"""Convert this {content_type} content into an engaging podcast script.

Style: {style}
Content to discuss:
{content[:3000]}...

Create a natural conversation where:
1. The host introduces the document/content being discussed
2. The guest provides expert insights and explanations
3. Complex ideas are broken down into simple terms
4. Specific examples and quotes from the content are discussed
5. Listeners who haven't read the content can still follow along
6. The discussion adds value beyond just reading the content

Format as JSON with the standard podcast structure.
Make it feel like a genuine discussion, not just reading the document aloud."""

@mcp.prompt
def podcast_series_planning_prompt(
    topic: str,
    num_episodes: int,
    episode_length: int
) -> str:
    """Plan a podcast series with multiple episodes"""
    
    return f"""Plan a {num_episodes}-episode podcast series about "{topic}".

Each episode should be approximately {episode_length} minutes long.

For each episode, provide:
1. Episode title (catchy and specific)
2. Main focus/theme
3. 3-4 key points to cover
4. How it connects to other episodes
5. A compelling hook for that episode

Also provide:
- An overall series arc/progression
- Suggested guest types for each episode
- Recurring segments or themes
- Ways to keep listeners engaged across episodes

Format as a structured plan that shows how the series builds knowledge and maintains interest."""

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

@mcp.prompt
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

@mcp.prompt
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

# Resources for help and examples
@mcp.resource("help://quickstart")
def get_quickstart_guide() -> str:
    """Get a quickstart guide for the podcast generator"""
    return """# 🎙️ Podcast Generator Pro Quick Start Guide

## Prerequisites:
- Set your ElevenLabs API key: export ELEVENLABS_API_KEY="your-key"
- Install ffmpeg for audio processing
- Install dependencies: pip install elevenlabs pypdf2 python-docx markdown beautifulsoup4 pydub

## Generate Your First Podcast:

### Method 1: From Topic (Recommended)
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

### Method 2: From File (PDF, TXT, DOCX)
Use the `generate_podcast_from_file` tool:
```
{
  "file_path": "/path/to/document.pdf",
  "podcast_style": "summary",
  "duration_minutes": 5
}
```

### Method 3: Step-by-Step
1. Extract content: `extract_content_from_file`
2. Generate script: `generate_podcast_script`
3. Create audio: `create_podcast_audio` 
4. Combine: `combine_podcast_audio`
5. Add music: `add_background_music`

## Voice Options:
- Male voices: Adam, Bill, Charlie, Daniel, Brian
- Female voices: Alice, Emily, Grace, Charlotte, Aria
- See `voices://available` for full list

## Supported File Types:
- PDF documents (.pdf)
- Word documents (.docx)
- Text files (.txt)
- Markdown files (.md)
- HTML files (.html)
- JSON/CSV data files

## Advanced Features:
- Create podcast series from multiple files
- Add background music
- Analyze audio quality
- Custom voice personalities

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

if __name__ == "__main__":
    # Run the server with stdio transport (default)
    mcp.run()