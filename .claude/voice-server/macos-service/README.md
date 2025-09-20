# PAIVoice Server - Personal AI Voice Framework for macOS

This directory contains all the components needed to run the PAIVoice Server as a macOS LaunchAgent service that starts automatically on login. PAIVoice is a framework for giving ANY Personal AI (PAI) system voice capabilities on macOS.

## 🚀 Quick Start

### Prerequisites

1. **Install Bun** (if not already installed):
   ```bash
   curl -fsSL https://bun.sh/install | bash
   ```

2. **Set up API Keys** (Optional but recommended):
   
   The server can work in two modes:
   - **Basic Mode**: Uses macOS built-in 'say' command (no API key needed)
   - **AI Voice Mode**: Uses ElevenLabs for natural AI voices (requires API key)

   To enable AI voices:
   ```bash
   # Add to ~/.env file:
   echo "ELEVENLABS_API_KEY=your_api_key_here" >> ~/.env
   echo "ELEVENLABS_VOICE_ID=voice_id_here" >> ~/.env  # Optional
   ```
   
   Get a free API key from [ElevenLabs](https://elevenlabs.io) (includes 10,000 characters/month free)

### Install and Start the Service

```bash
cd ~/.claude/voice-server/macos-service
./install.sh
```

That's it! The server will now start automatically when you log in.

### Validate Setup (Recommended)

Check if everything is configured correctly:
```bash
./validate-setup.sh
```

### Test the Service

```bash
./voice-server-ctl.sh test
```

## 📁 Files in this Directory

- **`com.paivoice.server.plist`** - macOS LaunchAgent configuration file
- **`install.sh`** - Installs the service
- **`uninstall.sh`** - Removes the service
- **`voice-server-ctl.sh`** - Service management utility
- **`validate-setup.sh`** - Checks if everything is configured correctly
- **`README.md`** - This documentation

## 🛠️ Service Management

Use the control script for all service operations:

```bash
# Check service status
./voice-server-ctl.sh status

# Start the service
./voice-server-ctl.sh start

# Stop the service
./voice-server-ctl.sh stop

# Restart the service
./voice-server-ctl.sh restart

# View live logs
./voice-server-ctl.sh logs

# Test with a notification
./voice-server-ctl.sh test
```

## 📋 Manual Commands

If you prefer using launchctl directly:

```bash
# Start service
launchctl start com.paivoice.server

# Stop service
launchctl stop com.paivoice.server

# Check if running
launchctl list | grep com.paivoice.server

# View logs
tail -f ~/.claude/voice-server/logs/voice-server.log
```

## 🔧 Configuration

### Environment Variables

All configuration is done via `~/.env` file in your home directory:

```bash
# Required for AI voices (get free at https://elevenlabs.io)
ELEVENLABS_API_KEY=your_api_key_here

# Optional - customize voice (defaults to default voice)
ELEVENLABS_VOICE_ID=voice_id_here

# Optional - change port (default 8888)
PORT=8888
```

### Available Voice IDs

Popular ElevenLabs voices you can use:
- `jqcCZkN6Knx8BJ5TBdYR` - Default voice (friendly assistant)
- `21m00Tcm4TlvDq8ikWAM` - Rachel (calm, professional)
- `AZnzlk1XvdvUeBnXmlld` - Domi (energetic)
- `EXAVITQu4vr4xnSDxMaL` - Bella (warm, friendly)

Find more voices at [ElevenLabs Voice Library](https://elevenlabs.io/voice-library)

### Service Settings

The service configuration is stored in the plist file:

- **Port**: 8888 (default, configurable via ~/.env)
- **Auto-start**: Yes (RunAtLoad)
- **Keep-alive**: Yes (restarts on crash)
- **Logs**: `~/.claude/voice-server/logs/`

### Modify Settings

After changing `~/.env`:
```bash
./voice-server-ctl.sh restart
```

For plist changes:
```bash
./uninstall.sh
./install.sh
```

## 📡 API Endpoints

Once running, the server provides:

- `POST http://localhost:8888/notify` - Send notification with optional voice
- `POST http://localhost:8888/pai` - Send PAI assistant notification
- `GET http://localhost:8888/health` - Health check

### Example Request

```bash
curl -X POST http://localhost:8888/notify \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test",
    "message": "Hello from Voice Server",
    "voice_enabled": true
  }'
```

## 🗑️ Uninstall

To completely remove the service:

```bash
./uninstall.sh
```

This will:
- Stop the running service
- Remove it from LaunchAgents
- Preserve log files for reference

## 🔑 About ElevenLabs API Keys

### What is ElevenLabs?
ElevenLabs provides state-of-the-art AI voice synthesis. Their voices sound natural and expressive, far superior to traditional text-to-speech.

### Do I Need an API Key?
- **No** - The server works without one, using macOS 'say' command
- **Recommended** - For natural AI voices that sound like real people

### How to Get a Free API Key
1. Visit [ElevenLabs](https://elevenlabs.io)
2. Sign up for a free account
3. Go to your [API Keys page](https://elevenlabs.io/api-keys)
4. Copy your API key
5. Add it to `~/.env`:
   ```bash
   echo "ELEVENLABS_API_KEY=your_key_here" >> ~/.env
   ```

### Free Tier Limits
- **10,000 characters/month** free
- Approximately 1,500-2,000 notifications
- Resets monthly
- No credit card required

### Is My API Key Safe?
- Stored only in your local `~/.env` file
- Never committed to git (add `.env` to `.gitignore`)
- Only accessible by your user account
- Not included in the service configuration files

## 🐛 Troubleshooting

### Service won't start

1. Check logs:
   ```bash
   cat ~/.claude/voice-server/logs/voice-server-error.log
   ```

2. Verify bun is installed:
   ```bash
   which bun
   ```

3. Check port 8888 is free:
   ```bash
   lsof -i :8888
   ```

### Service starts but no voice

1. Test ElevenLabs API key in the plist file
2. Check network connectivity
3. Verify audio permissions in System Preferences

### Permission Issues

If you get permission denied errors:
```bash
chmod +x ~/.claude/voice-server/macos-service/*.sh
```

## 📊 Service Architecture

```
User Login
    ↓
launchd reads plist
    ↓
Starts bun process
    ↓
server.ts runs
    ↓
Listens on port 8888
    ↓
Ready for notifications
```

## 🔐 Security Notes

- Service runs as your user (not root)
- Only accepts local connections (localhost)
- API keys stored in plist (user-readable only)
- Logs stored in user home directory

## 📝 License

Internal tool - not for distribution