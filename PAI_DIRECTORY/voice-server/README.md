# PAI Voice Server

A zero-cost voice notification server for the Personal AI Infrastructure (PAI) system that provides text-to-speech notifications using macOS Premium and Enhanced neural voices.

> **Quick Start**: See [documentation/VOICE-SETUP-GUIDE.md](../documentation/VOICE-SETUP-GUIDE.md) for detailed setup guide.

## 🎯 Features

- **Native macOS Voices**: Uses Premium and Enhanced neural TTS voices (no API costs)
- **Distinct Voice Personalities**: Different Premium voices for Kai and each agent
- **100% Offline**: No cloud APIs, complete privacy
- **Customizable Speed**: Configurable speech rates for each entity
- **Simple HTTP API**: Easy integration via REST endpoints
- **JSON Configuration**: Centralized voice and speed settings in voices.json

## 📋 Prerequisites

- macOS 13.0 (Ventura) or later (for Premium/Enhanced voices)
- [Bun](https://bun.sh) runtime installed
- Premium/Enhanced voices downloaded from System Settings

## 🚀 Quick Start

### 1. Download Premium Voices

1. Open **System Settings**
2. Navigate to **Voice (Live Speech)**
3. Click **System Voice** dropdown → **Manage Voices...**
4. Download these voices:
   - **Jamie (Premium)** - English (UK) - For Kai
   - **Ava (Premium)** - English (US) - For Researcher (highest quality)
   - **Serena (Premium)** - English (UK) - For Architect
   - **Isha (Premium)** - English (India) - For Designer
   - **Tom (Enhanced)** - English (US) - For Engineer
   - **Oliver (Enhanced)** - English (UK) - For Pentester

See [VOICE-SETUP-GUIDE.md](../documentation/VOICE-SETUP-GUIDE.md) for detailed download instructions.

### 2. Start the Voice Server

```bash
cd ${PAI_DIR}/voice-server
bun server.ts &
```

**Expected output:**
```
🚀 PAIVoice Server running on port 8888
🎙️  Using macOS native voices (default: Jamie (Premium))
📡 POST to http://localhost:8888/notify
🔒 Security: CORS restricted to localhost, rate limiting enabled
```

### 3. Test Voice Output

```bash
curl -X POST http://localhost:8888/notify \
  -H "Content-Type: application/json" \
  -d '{"message":"Voice system working perfectly","voice_name":"Jamie (Premium)","rate":228}'
```

## 🔧 Configuration

### Voice Configuration (voices.json)

All voice and speed settings are centralized in `voices.json`:

```json
{
  "default_rate": 175,
  "voices": {
    "kai": {
      "voice_name": "Jamie (Premium)",
      "rate_multiplier": 1.3,
      "rate_wpm": 228,
      "description": "UK Male - Professional, conversational",
      "type": "Premium"
    },
    "researcher": {
      "voice_name": "Ava (Premium)",
      "rate_multiplier": 1.35,
      "rate_wpm": 236,
      "description": "US Female - Analytical, highest quality",
      "type": "Premium"
    }
  }
}
```

**Customizing Voices and Speeds:**
Edit `voices.json` to change:
- `voice_name`: Any Premium or Enhanced macOS voice
- `rate_multiplier`: Speed (1.0 = normal, 1.3 = 30% faster, 1.5 = 50% faster)
- `rate_wpm`: Words per minute (auto-calculated or set manually)

Changes take effect immediately (hooks reload config on each use).

### Environment Variables

Optional configuration in `${PAI_DIR}/.env`:

```bash
# Server port (optional, defaults to 8888)
PORT=8888
```

**No API keys required** - voice system is 100% free and offline.

## 📡 API Reference

### POST /notify

Main endpoint for voice notifications.

**Request:**
```json
{
  "message": "Text to speak",
  "voice_name": "Jamie (Premium)",
  "rate": 228,
  "title": "Optional notification title",
  "voice_enabled": true
}
```

**Parameters:**
- `message` (required): Text to be spoken
- `voice_name` (optional): macOS voice name (e.g., "Jamie (Premium)")
- `rate` (optional): Speech rate in words per minute (default: 175)
- `title` (optional): Visual notification title
- `voice_enabled` (optional): Set to false to skip voice output

**Response:**
```json
{
  "status": "success",
  "message": "Notification sent"
}
```

### POST /pai

Simplified endpoint using Kai's default voice.

**Request:**
```json
{
  "title": "PAI System",
  "message": "System message"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "port": 8888,
  "voice_system": "macOS Native",
  "default_voice": "Jamie (Premium)"
}
```

## 🎙️ Voice Mappings

| Entity | Voice | Type | Speed | Accent | Description |
|--------|-------|------|-------|--------|-------------|
| Kai | Jamie (Premium) | Premium | 1.3x | UK Male | Professional, conversational |
| Researcher | Ava (Premium) | Premium | 1.35x | US Female | Analytical, highest quality |
| Engineer | Tom (Enhanced) | Enhanced | 1.35x | US Male | Steady, professional |
| Architect | Serena (Premium) | Premium | 1.35x | UK Female | Strategic, sophisticated |
| Designer | Isha (Premium) | Premium | 1.35x | Indian Female | Creative, distinct |
| Pentester | Oliver (Enhanced) | Enhanced | 1.35x | UK Male | Technical, sharp |
| Writer | Samantha (Enhanced) | Enhanced | 1.35x | US Female | Articulate, warm |

## 🐛 Troubleshooting

### Server Won't Start

```bash
# Check if port 8888 is in use
lsof -i :8888

# Kill any existing process
lsof -ti :8888 | xargs kill -9

# Restart server
cd ${PAI_DIR}/voice-server && bun server.ts &
```

### Voice Sounds Robotic

**Problem:** Downloaded wrong voice type (Compact/Legacy instead of Premium/Enhanced)

**Solution:**
1. Go to System Settings → Voice (Live Speech) → Manage Voices
2. Ensure you're downloading voices labeled **(Premium)** or **(Enhanced)**
3. Voices without these labels are old robotic voices - don't use them!

### Voice Not Found

```bash
# Verify voice is downloaded
say -v '?' | grep "Jamie (Premium)"

# If not found, download from System Settings
# System Settings → Voice (Live Speech) → Manage Voices
```

### No Sound Output

**Checklist:**
1. System volume not muted
2. Voice server running: `curl http://localhost:8888/health`
3. Voice downloaded: `say -v "Jamie (Premium)" "test"`
4. Correct output device selected (System Settings → Sound)

### Wrong Voice Playing

```bash
# Check voices.json configuration
cat ${PAI_DIR}/voice-server/voices.json

# Check stop-hook is loading config
grep "VOICE_CONFIG" ~/.claude/hooks/stop-hook.ts
```

## 🔐 Security & Privacy

- **100% Local Processing**: All voice generation happens on your Mac
- **Zero Cost**: No cloud APIs, no subscriptions
- **Complete Privacy**: No data sent to external services
- **CORS Protected**: Server only accepts requests from localhost
- **Rate Limited**: 10 requests per minute to prevent abuse

## 📁 File Structure

```
${PAI_DIR}/voice-server/
├── server.ts          # Main voice server
├── voices.json        # Voice configuration (edit this for customization)
└── README.md          # This file

~/.claude/hooks/
├── stop-hook.ts       # Triggers voice notifications on completion
└── context-compression-hook.ts  # Notification for context compression

~/Library/Mobile Documents/com~apple~CloudDocs/Claude/voice-server/
└── Same structure (if using cloud sync)
```

## 🎬 Usage Examples

### Test Individual Voices

```bash
# Test Kai's voice
curl -X POST http://localhost:8888/notify \
  -H "Content-Type: application/json" \
  -d '{"message":"Testing Kai voice","voice_name":"Jamie (Premium)","rate":228}'

# Test Researcher voice
curl -X POST http://localhost:8888/notify \
  -H "Content-Type: application/json" \
  -d '{"message":"Testing Researcher voice","voice_name":"Ava (Premium)","rate":236}'

# Test Engineer voice
curl -X POST http://localhost:8888/notify \
  -H "Content-Type: application/json" \
  -d '{"message":"Testing Engineer voice","voice_name":"Tom (Enhanced)","rate":236}'
```

### Custom Voice Speeds

```bash
# Slow speed (0.8x = 140 wpm)
curl -X POST http://localhost:8888/notify \
  -H "Content-Type: application/json" \
  -d '{"message":"Slow speed test","voice_name":"Jamie (Premium)","rate":140}'

# Fast speed (1.5x = 263 wpm)
curl -X POST http://localhost:8888/notify \
  -H "Content-Type: application/json" \
  -d '{"message":"Fast speed test","voice_name":"Jamie (Premium)","rate":263}'
```

## 🤝 Integration with PAI System

The voice server automatically integrates with PAI hooks:

- **stop-hook.ts**: Sends voice notification when Kai or agents complete tasks
- **context-compression-hook.ts**: Announces when conversation context is compacted
- Both hooks load voice configuration from `voices.json`

No manual integration needed - just start the server and hooks will use it automatically.

## 📖 Documentation

- **[VOICE-SETUP-GUIDE.md](../documentation/VOICE-SETUP-GUIDE.md)** - Complete setup guide
- **[voice-system.md](../documentation/voice-system.md)** - Technical documentation
- **[voices.json](./voices.json)** - Voice configuration file

## 💡 Tips

1. **Choose Premium voices first** - They have the highest quality
2. **Use Enhanced when Premium unavailable** - Still excellent quality
3. **Avoid voices without labels** - These are legacy robotic voices
4. **Customize speech rates** - Edit `voices.json` to adjust speeds
5. **Test voices before committing** - Use the curl commands above
6. **Different accents for clarity** - Mix of US, UK, and Indian helps distinguish speakers

## 🆘 Support

For issues:
1. Check [Troubleshooting](#-troubleshooting) section
2. Verify voices are downloaded (System Settings → Voice (Live Speech))
3. Test voice directly: `say -v "Jamie (Premium)" "test"`
4. Check server is running: `curl http://localhost:8888/health`
5. See [voice-system.md](../documentation/voice-system.md) for detailed documentation

---

**Zero cost. Complete privacy. Natural voices. That's the PAI way.** 🎙️
