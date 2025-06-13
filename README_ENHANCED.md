# Enhanced Podcast Generator MCP Server

A sophisticated podcast generation tool that creates natural, engaging podcast scripts with advanced voice options and emotional depth.

## 🚀 Key Improvements

### 1. **Advanced Podcast Formats**
- **Interview**: Classic Q&A with expert guests
- **Debate**: Balanced discussion with opposing viewpoints
- **Storytelling**: Narrative-driven content with immersive elements
- **Educational**: Teaching-focused with clear explanations
- **Comedy**: Entertainment with natural humor and timing
- **News Analysis**: Current events with expert commentary
- **Roundtable**: Multi-person collaborative discussions

### 2. **Natural Dialogue Generation**
The enhanced prompt system creates scripts with:
- Realistic speech patterns and verbal fillers
- Personality-driven word choices
- Natural interruptions and reactions
- Emotional depth (laughter, surprise, concern)
- Format-appropriate pacing and structure

### 3. **Sophisticated Voice Options**

#### Voice Personalities
- **Authoritative**: Confident experts and anchors
- **Warm & Engaging**: Friendly hosts and interviewers  
- **Analytical**: Data-driven researchers
- **Energetic**: Dynamic entertainers
- **Contemplative**: Thoughtful philosophers
- **Skeptical**: Critical investigators

#### ElevenLabs Integration
- Access to full voice library (5000+ voices)
- Voice design for custom characters
- Emotional voice modulation
- Multi-language support
- Sound effects integration

### 4. **Emotional Voice Control**
Dynamic emotion detection and application:
- **Excited**: Lower stability, higher similarity (0.3/0.7/0.8)
- **Serious**: Higher stability for authority (0.7/0.5/0.3)
- **Warm**: Balanced for friendliness (0.5/0.6/0.6)
- **Contemplative**: Thoughtful pacing (0.6/0.4/0.4)
- **Urgent**: Breaking news energy (0.4/0.8/0.7)
- **Casual**: Natural conversation (0.5/0.5/0.5)

## 📋 Prerequisites

```bash
# Install required packages
pip install mcp elevenlabs

# Set your API key
export ELEVENLABS_API_KEY="your_api_key_here"
```

## 🎯 Usage Examples

### Basic Interview Podcast
```python
# Generate script
generate_enhanced_script(
    topic="The Future of AI",
    format_type="interview",
    duration_minutes=10,
    num_speakers=2
)

# Create audio with auto-assigned voices
create_enhanced_audio(
    script="[Generated script here]",
    output_filename="ai_future_interview.mp3",
    auto_assign_voices=True
)
```

### Dynamic Debate with Custom Context
```python
generate_enhanced_script(
    topic="Remote Work vs Office Culture",
    format_type="debate",
    duration_minutes=15,
    num_speakers=3,
    additional_context={
        "stance_1": "Remote work maximizes productivity and work-life balance",
        "stance_2": "Office culture drives innovation and team cohesion",
        "moderator_style": "Neutral but probing"
    }
)
```

### Storytelling Podcast with Sound Effects
```python
# Generate narrative script
generate_enhanced_script(
    topic="The Mystery of the Missing Startup Funds",
    format_type="storytelling",
    duration_minutes=20,
    num_speakers=4,
    additional_context={
        "genre": "tech thriller",
        "setting": "Silicon Valley startup",
        "tone": "suspenseful with moments of humor"
    }
)

# Create with custom voices and effects
create_enhanced_audio(
    script="[Generated script]",
    output_filename="startup_mystery.mp3",
    voice_assignments={
        "Narrator": "william shanks",  # Deep, mysterious voice
        "CEO": "josh",                  # Young, energetic
        "Investigator": "sarah",        # Authoritative female
        "Witness": "adam"               # Analytical male
    },
    include_sound_effects=True
)
```

### Educational Content with Voice Design
```python
# Search for specific voice types
search_voices("british female professor educational clear")

# Or design a custom voice
design_voice(
    description="Wise elderly professor with slight German accent, warm but authoritative, speaks slowly and clearly with occasional chuckles",
    sample_text="Let me tell you about the fascinating world of quantum mechanics. You see, at the subatomic level, particles behave in ways that would seem impossible in our everyday experience...",
    save_as="professor_quantum"
)
```

## 🎨 Advanced Features

### Voice Library Search
Search for voices using natural language:
```python
search_voices("young female british narrator audiobook")
search_voices("deep male voice podcast host american")
search_voices("warm spanish accent female educational")
```

### Custom Voice Assignments
Manually assign specific voices or descriptions:
```python
create_enhanced_audio(
    script="[Your script]",
    voice_assignments={
        "Host": "nova",  # Use specific ElevenLabs voice
        "Expert": "British professor with Oxford accent, measured pace",  # Voice design
        "Guest": "voice_id_from_library"  # Use voice ID directly
    }
)
```

### Emotional Scene Direction
Add emotion indicators in your script:
```
Host [excited]: This is absolutely fascinating! Tell me more!
Expert [contemplative]: Well, when you really think about it...
Guest [laughing]: I can't believe that actually happened!
```

## 🎭 Best Practices

### 1. **Format Selection**
- **Interview**: Best for expert insights and Q&A
- **Debate**: When exploring controversial topics
- **Storytelling**: For case studies or narratives
- **Educational**: For how-to content or tutorials
- **Roundtable**: For diverse perspectives

### 2. **Voice Matching**
- Match voice personality to speaker role
- Use contrasting voices for clarity
- Consider accent diversity for global appeal
- Apply consistent voices for recurring characters

### 3. **Emotional Dynamics**
- Vary emotional tones throughout the episode
- Match emotions to content (serious for data, warm for stories)
- Use excitement sparingly for impact
- Keep baseline conversational for accessibility

### 4. **Script Optimization**
- Provide detailed context for better AI generation
- Include specific examples or data points
- Specify desired tone and style
- Consider your target audience

## 🔧 Configuration

### Environment Variables
```bash
ELEVENLABS_API_KEY=your_api_key_here
ELEVENLABS_MODEL=eleven_turbo_v2_5  # or eleven_multilingual_v2
```

### Server Configuration
```python
# In your MCP config
{
    "mcpServers": {
        "podcast-generator": {
            "command": "python",
            "args": ["podcast_server_enhanced.py"],
            "env": {
                "ELEVENLABS_API_KEY": "your_key"
            }
        }
    }
}
```

## 📊 Output Structure

Generated podcasts include:
- **Combined MP3**: Full podcast with all speakers
- **Individual Segments**: Each speaker part separately
- **Metadata**: Speaker assignments, emotions, timing
- **Project Files**: Organized in ~/Desktop/podcast_output/

## 🎯 Tips for LLM Integration

When using with Claude or GPT-4:

1. **Use the Enhanced Prompt**: The `generate_enhanced_script` tool creates optimized prompts
2. **Provide Context**: Additional context improves script quality
3. **Iterate**: Generate multiple versions and combine the best parts
4. **Edit Before Audio**: Review and refine scripts before converting to audio

## 🚧 Future Enhancements

Potential additions:
- Real-time voice cloning
- Multi-language podcast generation
- Automatic music bed integration
- Dynamic ad insertion
- Live podcast streaming
- Transcript generation with timestamps

## 📝 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional podcast formats
- More voice personality types
- Enhanced emotion detection
- Better audio mixing
- Integration with other TTS services