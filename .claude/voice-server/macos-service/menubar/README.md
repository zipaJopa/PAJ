# PAIVoice Server Menu Bar Icon

Adds a status icon to your macOS menu bar that shows if the PAIVoice server is running and provides quick controls for your Personal AI voice system.

## 🚀 Quick Install

```bash
cd ~/.claude/voice-server/macos-service/menubar
./install-menubar.sh
```

## 📊 What It Shows

### Menu Bar Icons
- **🎙️** = Voice server is running (active)
- **🔇** = Voice server is stopped (inactive)

### Click Menu Options
When you click the icon, you'll see:
- Server status (running/stopped)
- Port number
- Voice type (AI/macOS)
- Quick actions:
  - Test notification
  - Start/Stop/Restart server
  - View logs
  - Check setup

## 🛠️ Requirements

### SwiftBar (Required)
The menu bar icon uses SwiftBar, a free app that runs scripts in your menu bar.

**Install SwiftBar:**
- **Option 1:** Download from [swiftbar.app](https://swiftbar.app)
- **Option 2:** Install with Homebrew:
  ```bash
  brew install --cask swiftbar
  ```

## 📁 Files

- `voice-server.5s.sh` - The SwiftBar plugin script (refreshes every 5 seconds)
- `install-menubar.sh` - Automated installer
- `README.md` - This documentation

## 🔧 Manual Installation

If you prefer to install manually:

1. Install SwiftBar from [swiftbar.app](https://swiftbar.app)

2. Copy the plugin to SwiftBar's plugins folder:
   ```bash
   cp voice-server.5s.sh ~/Library/Application\ Support/SwiftBar/Plugins/
   chmod +x ~/Library/Application\ Support/SwiftBar/Plugins/voice-server.5s.sh
   ```

3. Open SwiftBar and select the plugins folder when prompted

## ⚙️ Customization

### Change Refresh Rate
The `5s` in the filename means it refreshes every 5 seconds. You can change this:
- `voice-server.1s.sh` - Refresh every second (more responsive)
- `voice-server.10s.sh` - Refresh every 10 seconds (less CPU usage)
- `voice-server.30s.sh` - Refresh every 30 seconds (minimal CPU)

### Modify Icons
Edit `voice-server.5s.sh` and change the emoji icons:
```bash
echo "🎙️"  # Change this to any emoji or text
```

Popular alternatives:
- `🔊` - Speaker
- `🎵` - Musical note
- `🗣️` - Speaking head
- `📢` - Megaphone
- `●` - Simple dot (red/green with colors)

## 🗑️ Uninstall

Remove the menu bar icon:
```bash
rm ~/Library/Application\ Support/SwiftBar/Plugins/voice-server.5s.sh
```

Or keep SwiftBar and just disable the plugin in SwiftBar preferences.

## 🐛 Troubleshooting

### Icon not appearing
1. Make sure SwiftBar is running
2. Check SwiftBar is using the correct plugins folder:
   - Click SwiftBar icon → Preferences
   - Verify Plugin Folder path
3. Ensure plugin is executable:
   ```bash
   chmod +x ~/Library/Application\ Support/SwiftBar/Plugins/voice-server.5s.sh
   ```

### Icon not updating
- Click the icon and select "Refresh"
- Check if the server is actually running:
  ```bash
  curl http://localhost:8888/health
  ```

### SwiftBar using too much CPU
- Rename the plugin file to use a longer refresh interval (e.g., `voice-server.30s.sh`)

## 🎨 How It Works

The plugin is a simple bash script that:
1. Checks if the server is running (via health endpoint)
2. Outputs text in SwiftBar format
3. Provides clickable menu items that run commands

SwiftBar runs this script at the specified interval and displays the output in your menu bar.