# PAI Quick Start Guide

Get your Personal AI Infrastructure up and running in minutes!

## Prerequisites

- **macOS** 11+ (primary platform)
- **Claude Desktop** or Claude API access
- **Bun runtime** (for voice server)
- **Git** (for version control)

## Installation

### 1. Clone or Create PAI Directory

```bash
# Option A: Clone from repository
git clone https://github.com/yourusername/PAI.git
cd PAI

# Option B: Create new PAI installation
mkdir -p ~/PAI
cd ~/PAI
```

### 2. Set Environment Variables

```bash
# Add to your shell profile (~/.zshrc or ~/.bashrc)
export PAI_HOME="$HOME/PAI"  # Or your installation path
export PATH="$PAI_HOME/bin:$PATH"

# Reload shell
source ~/.zshrc  # or ~/.bashrc
```

### 3. Create Directory Structure

```bash
# Create essential directories
mkdir -p "${PAI_HOME}/.claude/context"
mkdir -p "${PAI_HOME}/.claude/hooks"
mkdir -p "${PAI_HOME}/.claude/commands"
mkdir -p "${PAI_HOME}/Projects"
mkdir -p "${PAI_HOME}/Library/Logs"
mkdir -p "${PAI_HOME}/Documentation"
```

### 4. Configure Environment File

Create `~/.env` with your settings:

```bash
# Essential Configuration
PAI_HOME=/path/to/your/PAI

# Optional: Voice Server
ELEVENLABS_API_KEY=your_api_key_here
ELEVENLABS_VOICE_ID=jqcCZkN6Knx8BJ5TBdYR
PORT=8888

# Optional: API Keys for various services
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

## Core Setup

### 1. Create Main Context File

Create `${PAI_HOME}/.claude/context/CLAUDE.md`:

```markdown
# PAI System Context

## System Information
- PAI_HOME: ${PAI_HOME}
- Platform: macOS
- User: ${USER}

## Core Instructions
You are an AI assistant enhanced with PAI (Personal AI Infrastructure).

## Available Features
- Dynamic context loading
- Hook system for automation
- Voice notifications
- Multi-agent support

## Project Contexts
[Your project-specific information here]
```

### 2. Setup UFC Hook System

Create the main hook file `${PAI_HOME}/.claude/hooks/user-prompt-submit-hook`:

```bash
#!/bin/bash
# UFC Dynamic Context Loader

PROMPT="$1"
PAI_HOME="${PAI_HOME:-$HOME}"

# Simple intent matching for demonstration
case "$PROMPT" in
    *website*|*blog*)
        echo "Loading website context..."
        cat "${PAI_HOME}/.claude/context/projects/website/CLAUDE.md" 2>/dev/null
        ;;
    *research*)
        echo "AGENT: researcher"
        ;;
    *security*|*pentest*)
        echo "AGENT: pentester"
        ;;
esac

exit 0
```

Make it executable:
```bash
chmod +x "${PAI_HOME}/.claude/hooks/user-prompt-submit-hook"
```

### 3. Install Voice Server (Optional)

```bash
# Navigate to voice server
cd "${PAI_HOME}/.claude/voice-server"

# Install dependencies
bun install

# Run installation script
./install.sh

# Test voice server
curl -X POST http://localhost:8888/notify \
  -d '{"message": "PAI system initialized"}'
```

## Basic Usage

### 1. Context Management

Create project-specific contexts:

```bash
# Create a project context
mkdir -p "${PAI_HOME}/.claude/context/projects/myproject"
cat > "${PAI_HOME}/.claude/context/projects/myproject/CLAUDE.md" << EOF
# My Project Context

## Project Details
- Name: My Project
- Path: ${PAI_HOME}/Projects/myproject
- Type: Web Application

## Technical Stack
- Frontend: React
- Backend: Node.js
- Database: PostgreSQL

## Current Tasks
- [ ] Implement user authentication
- [ ] Add dashboard features
EOF
```

### 2. Hook Examples

#### Tool Validation Hook

Create `${PAI_HOME}/.claude/hooks/tool-use-hook`:

```bash
#!/bin/bash
# Validate tool usage

TOOL="$1"
PARAMS="$2"

# Log tool usage
echo "[$(date)] Tool: $TOOL" >> "${PAI_HOME}/Library/Logs/tools.log"

# Validate dangerous operations
if [[ "$TOOL" == "Bash" ]] && [[ "$PARAMS" =~ "rm -rf" ]]; then
    echo "BLOCKED: Dangerous command"
    exit 1
fi

exit 0
```

#### Notification Hook

Create `${PAI_HOME}/.claude/hooks/post-execution-hook`:

```bash
#!/bin/bash
# Send completion notifications

COMMAND="$1"
STATUS="$2"

if [ "$STATUS" -eq 0 ]; then
    curl -X POST http://localhost:8888/notify \
        -d '{"message": "Task completed successfully"}' \
        2>/dev/null
fi

exit 0
```

### 3. Custom Commands

Create custom command `${PAI_HOME}/.claude/commands/status.sh`:

```bash
#!/bin/bash
# Show PAI system status

echo "PAI System Status"
echo "================="
echo "PAI_HOME: ${PAI_HOME}"
echo "Contexts: $(find ${PAI_HOME}/.claude/context -name "*.md" | wc -l)"
echo "Hooks: $(find ${PAI_HOME}/.claude/hooks -type f | wc -l)"
echo "Projects: $(ls -1 ${PAI_HOME}/Projects 2>/dev/null | wc -l)"

# Check voice server
if curl -s http://localhost:8888/health > /dev/null 2>&1; then
    echo "Voice Server: ✅ Running"
else
    echo "Voice Server: ❌ Stopped"
fi
```

## Testing Your Installation

### 1. Test Context Loading

In Claude, try:
```
"Help me with my website"
# Should load website context

"Research AI trends"
# Should launch researcher agent
```

### 2. Test Voice Server

```bash
# Send test notification
curl -X POST http://localhost:8888/notify \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from PAI"}'
```

### 3. Test Hooks

```bash
# Test hook directly
${PAI_HOME}/.claude/hooks/user-prompt-submit-hook "test website"

# Check output
echo $?  # Should be 0
```

## Common Tasks

### Adding a New Project Context

```bash
# 1. Create project directory
mkdir -p "${PAI_HOME}/Projects/newproject"

# 2. Create context file
cat > "${PAI_HOME}/.claude/context/projects/newproject/CLAUDE.md" << EOF
# New Project Context
[Project specific information]
EOF

# 3. Add to hook system (optional)
# Edit user-prompt-submit-hook to include new project triggers
```

### Creating Agent-Specific Contexts

```bash
# Research agent context
cat > "${PAI_HOME}/.claude/context/agents/researcher.md" << EOF
# Researcher Agent Context
Focus on finding accurate, recent information
Cite sources when possible
EOF
```

### Setting Up Automation

```bash
# Create automation hook
cat > "${PAI_HOME}/.claude/hooks/automation-hook" << EOF
#!/bin/bash
# Automated tasks
if [[ "\$1" =~ "daily report" ]]; then
    generate_daily_report
fi
EOF
chmod +x "${PAI_HOME}/.claude/hooks/automation-hook"
```

## Troubleshooting

### Context Not Loading

```bash
# Check hook permissions
ls -la "${PAI_HOME}/.claude/hooks/"

# Test hook manually
"${PAI_HOME}/.claude/hooks/user-prompt-submit-hook" "test prompt"

# Check PAI_HOME is set
echo $PAI_HOME
```

### Voice Server Issues

```bash
# Check if running
lsof -i :8888

# View logs
tail -f "${PAI_HOME}/Library/Logs/pai-voice-server.log"

# Restart service
cd "${PAI_HOME}/.claude/voice-server"
./restart.sh
```

### Hook Not Executing

```bash
# Check if executable
chmod +x "${PAI_HOME}/.claude/hooks/"*

# Enable debug mode
export HOOK_DEBUG=true

# Check logs
tail -f "${PAI_HOME}/Library/Logs/hooks.log"
```

## Next Steps

1. **Explore Documentation**
   - [System Architecture](./architecture.md)
   - [UFC Context System](./ufc-context-system.md)
   - [Hook System](./hook-system.md)

2. **Customize Your Setup**
   - Add project-specific contexts
   - Create custom hooks
   - Configure voice personalities

3. **Advanced Features**
   - Set up multiple agents
   - Create command shortcuts
   - Integrate with external services

## Quick Reference

### Essential Commands

```bash
# Check system status
"${PAI_HOME}/.claude/commands/status.sh"

# Reload context
source ~/.zshrc

# Test voice
curl -X POST http://localhost:8888/notify -d '{"message":"test"}'

# View logs
tail -f "${PAI_HOME}/Library/Logs/"*.log
```

### File Locations

| Component | Location |
|-----------|----------|
| Main Context | `${PAI_HOME}/.claude/context/CLAUDE.md` |
| Hooks | `${PAI_HOME}/.claude/hooks/` |
| Commands | `${PAI_HOME}/.claude/commands/` |
| Projects | `${PAI_HOME}/Projects/` |
| Logs | `${PAI_HOME}/Library/Logs/` |
| Voice Server | `${PAI_HOME}/.claude/voice-server/` |

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `PAI_HOME` | PAI installation directory | `$HOME` |
| `ELEVENLABS_API_KEY` | Voice synthesis API | None |
| `PORT` | Voice server port | 8888 |
| `HOOK_DEBUG` | Enable hook debugging | false |

## Getting Help

- Check the [Documentation](./README.md)
- Review [Troubleshooting Guide](#troubleshooting)
- File issues on GitHub
- Check logs in `${PAI_HOME}/Library/Logs/`

---

*Welcome to PAI! Your personal AI infrastructure is ready to enhance your workflow.*