# PAIVoice - Personal AI Voice Framework

PAIVoice is a flexible voice notification framework for Personal AI (PAI) systems on macOS. It provides natural-sounding voice notifications using ElevenLabs AI voices or fallback to macOS's built-in text-to-speech.

## 🎯 Purpose

This framework enables ANY Personal AI system to:
- Send voice notifications to users
- Provide audio feedback for completed tasks
- Create more engaging AI interactions
- Work with any AI assistant (not limited to a specific name or personality)

## 🚀 Features

- **AI Voice Support**: Natural voices via ElevenLabs API
- **Fallback Mode**: Works without API key using macOS 'say' command
- **Menu Bar Icon**: Visual status indicator with quick controls
- **Service Management**: Runs as a background service
- **Simple API**: Easy HTTP endpoints for notifications
- **Customizable**: Choose your own voice and personality

## 📦 Quick Setup

### 1. Install Prerequisites
```bash
# Install Bun (JavaScript runtime)
curl -fsSL https://bun.sh/install | bash
```

### 2. Configure API Keys (Optional)
```bash
# Add to ~/.env for AI voices
echo "ELEVENLABS_API_KEY=your_key_here" >> ~/.env
echo "ELEVENLABS_VOICE_ID=voice_id_here" >> ~/.env
```

Get a free API key from [ElevenLabs](https://elevenlabs.io) (10,000 chars/month free)

### 3. Install as Service
```bash
cd ~/.claude/voice-server/macos-service
./install.sh
```

### 4. Add Menu Bar Icon (Optional)
```bash
cd ~/.claude/voice-server/macos-service/menubar
./install-menubar.sh
```

## 🎙️ Usage

### Send a Notification
```bash
curl -X POST http://localhost:8888/notify \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Your PAI Name",
    "message": "Task completed successfully",
    "voice_enabled": true
  }'
```

### PAI Assistant Notification
```bash
curl -X POST http://localhost:8888/pai \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Assistant",
    "message": "I've finished analyzing your data"
  }'
```

## 🔧 Customization

### Choose Your Voice

Popular ElevenLabs voice IDs:
- `jqcCZkN6Knx8BJ5TBdYR` - Friendly assistant (default)
- `21m00Tcm4TlvDq8ikWAM` - Rachel (calm, professional)
- `AZnzlk1XvdvUeBnXmlld` - Domi (energetic)
- `EXAVITQu4vr4xnSDxMaL` - Bella (warm, friendly)

Set in `~/.env`:
```bash
ELEVENLABS_VOICE_ID=your_chosen_voice_id
```

### Customize for Your PAI

The framework is designed to work with ANY Personal AI system:
- Use your PAI's name in the `title` field
- Customize messages to match your PAI's personality
- Integrate with your existing AI tools and workflows

## 📡 API Endpoints

- `POST /notify` - General notification with optional voice
- `POST /pai` - PAI-specific notification (always with voice)
- `GET /health` - Service health check

### Request Format
```json
{
  "title": "Your PAI Name",
  "message": "Notification text",
  "voice_enabled": true,
  "voice_id": "optional_voice_override"
}
```

## 🛠️ Service Management

```bash
# Control the service
./macos-service/voice-server-ctl.sh status
./macos-service/voice-server-ctl.sh start
./macos-service/voice-server-ctl.sh stop
./macos-service/voice-server-ctl.sh restart

# View logs
./macos-service/voice-server-ctl.sh logs

# Test the service
./macos-service/voice-server-ctl.sh test
```

## 📊 Menu Bar Icon

The menu bar icon shows:
- 🎙️ = Server running
- 🔇 = Server stopped

Click for quick access to controls and status.

## 🔒 Security

- API keys stored locally in `~/.env`
- Service runs as user (not root)
- Only accepts local connections
- No data sent except to ElevenLabs (if configured)

## 📁 Project Structure

```
voice-server/
├── server.ts                 # Main server code
├── start.sh                  # Manual start script
├── macos-service/           
│   ├── com.paivoice.server.plist  # Service configuration
│   ├── install.sh           # Service installer
│   ├── uninstall.sh         # Service remover
│   ├── voice-server-ctl.sh  # Service control
│   ├── validate-setup.sh    # Setup validator
│   └── menubar/             # Menu bar icon
└── README.md                # This file
```

## 🤝 Integration Examples

### With Python AI Agent
```python
import requests

def send_voice_notification(message):
    requests.post('http://localhost:8888/pai', json={
        'title': 'My AI Assistant',
        'message': message
    })

# Use in your AI workflow
send_voice_notification("Analysis complete. Found 3 insights.")
```

### With Node.js/Bun
```javascript
async function notify(message) {
  await fetch('http://localhost:8888/pai', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      title: 'AI Helper',
      message: message
    })
  });
}
```

## 📝 License

Open source - Customize for your needs!

## 🙏 Credits

Built as a framework for Personal AI systems, inspired by the need for better human-AI interaction through voice.