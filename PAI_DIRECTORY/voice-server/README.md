# PAI Voice Server

A voice notification server for the Personal AI Infrastructure (PAI) system that provides text-to-speech notifications using ElevenLabs API or macOS's built-in `say` command as fallback.

> **Quick Start**: See [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide.

## 🎯 Features

- **ElevenLabs Integration**: High-quality AI voices for notifications
- **Fallback Support**: Uses macOS `say` command when ElevenLabs is not configured
- **Multiple Voice Support**: Different voices for different AI agents
- **macOS Service**: Runs automatically in the background
- **Menu Bar Indicator**: Visual status indicator in macOS menu bar
- **Simple HTTP API**: Easy integration with any tool or script

## 📋 Prerequisites

- macOS (tested on macOS 11+)
- [Bun](https://bun.sh) runtime installed
- ElevenLabs API key (optional, for AI voices)

## 🚀 Quick Start

### 1. Install Bun (if not already installed)
```bash
curl -fsSL https://bun.sh/install | bash
```

### 2. Configure API Key (Optional but Recommended)
Add your ElevenLabs API key to `${PAI_DIR}/.env`:
```bash
echo "ELEVENLABS_API_KEY=your_api_key_here" >> ${PAI_DIR}/.env
echo "ELEVENLABS_VOICE_ID=jqcCZkN6Knx8BJ5TBdYR" >> ${PAI_DIR}/.env
```

> Get your free API key at [elevenlabs.io](https://elevenlabs.io) (10,000 characters/month free)

### 3. Install Voice Server
```bash
cd ${PAI_DIR}/voice-server
./install.sh
```

This will:
- Install dependencies
- Create a macOS LaunchAgent for auto-start
- Start the voice server on port 8888
- Verify the installation
- Optionally install menu bar indicator (requires SwiftBar/BitBar)

## 🛠️ Service Management

### Start Server
```bash
./start.sh
# or
launchctl load ~/Library/LaunchAgents/com.pai.voice-server.plist
```

### Stop Server
```bash
./stop.sh
# or
launchctl unload ~/Library/LaunchAgents/com.pai.voice-server.plist
```

### Restart Server
```bash
./restart.sh
```

### Check Status
```bash
./status.sh
```

### Uninstall
```bash
./uninstall.sh
```
This will stop the service and remove the LaunchAgent.

## 📡 API Usage

### Send a Voice Notification
```bash
curl -X POST http://localhost:8888/notify \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Task completed successfully",
    "voice_id": "jqcCZkN6Knx8BJ5TBdYR",
    "voice_enabled": true
  }'
```

### Parameters
- `message` (required): The text to speak
- `voice_id` (optional): ElevenLabs voice ID to use
- `voice_enabled` (optional): Whether to speak the notification (default: true)
- `title` (optional): Notification title (default: "PAI Notification")

### Available Voice IDs
```javascript
// PAI System Agents
Kai:        jqcCZkN6Knx8BJ5TBdYR  // Main assistant
Researcher: AXdMgz6evoL7OPd7eU12  // Research agent
Engineer:   kmSVBPu7loj4ayNinwWM  // Engineering agent
Designer:   ZF6FPAbjXT4488VcRRnw  // Design agent
Pentester:  hmMWXCj9K7N5mCPcRkfC  // Security agent
Architect:  muZKMsIDGYtIkjjiUS82  // Architecture agent
Writer:     gfRt6Z3Z8aTbpLfexQ7N  // Content agent
```

## 🖥️ Menu Bar Indicator

The voice server includes an optional menu bar indicator that shows the server status.

### Installing the Menu Bar

1. **Install SwiftBar** (recommended) or BitBar:
```bash
brew install --cask swiftbar
# OR
brew install --cask bitbar
```

2. **Run the menu bar installer**:
```bash
cd ${PAI_DIR}/voice-server/menubar
./install-menubar.sh
```

### Menu Bar Features
- **Visual Status**: 🎙️ (running) or 🎙️⚫ (stopped)
- **Quick Controls**: Start/Stop/Restart server from menu
- **Status Info**: Shows voice type (ElevenLabs/macOS Say)
- **Quick Test**: Test voice with one click
- **View Logs**: Access server logs directly

### Manual Installation
If you prefer manual installation:
1. Copy `menubar/pai-voice.5s.sh` to your SwiftBar/BitBar plugins folder
2. Make it executable: `chmod +x pai-voice.5s.sh`
3. Refresh SwiftBar/BitBar

## 🔧 Configuration

### Environment Variables
Create or edit `${PAI_DIR}/.env`:

```bash
# Required for ElevenLabs voices (optional)
ELEVENLABS_API_KEY=your_api_key_here

# Default voice ID (optional, defaults to Kai)
ELEVENLABS_VOICE_ID=jqcCZkN6Knx8BJ5TBdYR

# Server port (optional, defaults to 8888)
PORT=8888
```

### Finding Your Voice ID
1. Go to [ElevenLabs Voice Library](https://elevenlabs.io/voice-library)
2. Select a voice you like
3. Click "Use" and copy the Voice ID
4. Update `ELEVENLABS_VOICE_ID` in your `${PAI_DIR}/.env`

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 8888 is already in use
lsof -i :8888

# Kill any existing process
lsof -ti :8888 | xargs kill -9

# Restart the server
./restart.sh
```

### No voice output
```bash
# Check if ElevenLabs key is configured
grep ELEVENLABS_API_KEY ${PAI_DIR}/.env

# Test with fallback (macOS say)
curl -X POST http://localhost:8888/notify \
  -H "Content-Type: application/json" \
  -d '{"message": "Testing voice output"}'

# Check server logs
tail -f ~/Library/Logs/pai-voice-server.log
```

### Service not auto-starting
```bash
# Check LaunchAgent status
launchctl list | grep pai.voice

# Reload LaunchAgent
launchctl unload ~/Library/LaunchAgents/com.pai.voice-server.plist
launchctl load ~/Library/LaunchAgents/com.pai.voice-server.plist

# Check for errors
tail -f ~/Library/Logs/pai-voice-server.log
```

## 📁 File Structure
```
${PAI_DIR}/voice-server/
├── server.ts              # Main server code
├── install.sh             # Installation script
├── start.sh              # Start server
├── stop.sh               # Stop server
├── restart.sh            # Restart server
├── status.sh             # Check server status
├── uninstall.sh          # Uninstall service
├── README.md             # This file
└── menubar/
    ├── pai-voice.5s.sh   # Menu bar status script
    └── install-menubar.sh # Menu bar installer

~/Library/LaunchAgents/
└── com.pai.voice-server.plist  # macOS service definition

~/Library/Logs/
└── pai-voice-server.log        # Server logs
```

## 🔐 Security Notes

- **No hardcoded API keys**: All sensitive data is read from `${PAI_DIR}/.env`
- **Local only**: Server only listens on localhost (127.0.0.1)
- **User-specific**: Each user maintains their own API keys
- **Safe for public repos**: No sensitive data in the codebase

## 🤝 Integration with PAI System

This voice server integrates with the PAI (Personal AI Infrastructure) system to provide voice notifications when:
- Tasks are completed
- Agents finish their work
- Important events occur
- User notifications are needed

The PAI hooks automatically send notifications to this server when configured.

## 📝 License

Part of the PAI (Personal AI Infrastructure) system.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs at `~/Library/Logs/pai-voice-server.log`
3. Ensure your ElevenLabs API key is valid
4. Try the fallback mode (without API key) to isolate issues