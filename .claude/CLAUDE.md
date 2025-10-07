# PAJ - Pavle's Personal AI Infrastructure
## Private Fork of danielmiessler/PAI with Custom Enhancements

### Project Overview
**PAJ** (Pavle's AI Journey) is a private fork of Daniel Miessler's [PAI](https://github.com/danielmiessler/PAI) (Personal AI Infrastructure), customized for Pavle's specific needs and integrated with his infrastructure constellation.

**Pronunciation**: "PAI" is pronounced "pie" 🥧, so **PAJ** is pronounced "паj" (Serbian) or "pye" 😄

### Key Differences from Upstream PAI

#### 1. Voice System (v0.2.3)
**Upstream PAI**: Uses ElevenLabs API (paid, cloud-based)
**PAJ**: macOS native Premium/Enhanced voices (free, offline)

```bash
# PAJ Voice Configuration
PAI_DIRECTORY/voices.json:
- Premium voices: Jamie, Ava, Serena, Isha (high quality)
- Enhanced voices: Tom, Oliver, Samantha
- Zero API costs
- Complete privacy (local processing)
```

#### 2. Browser Automation
**Upstream PAI**: Playwright
**PAJ**: Chrome DevTools MCP (Model Context Protocol)

Aligns with Pavle's MCP strategy (remote unified gateway, no local bloat).

#### 3. Integration with Pavle's Infrastructure
**PAJ is designed to integrate with:**
- **Metamozak** (A2A Orchestrator) - task routing
- **Archon KB** (PCT-110) - long-term memory
- **LiveKit Voice Agent** (PCT-133) - real-time voice interface
- **MCP Gateway** (PCT-134) - tool access

### Current Version Status
- **PAJ**: v0.2.3 (October 2, 2025)
- **Upstream PAI**: v0.2.4 (October 7, 2025)
- **Divergence**: PAJ has custom voice modifications, PAI has README cleanup

### PAI Core Features (Inherited)
PAI is a comprehensive personal AI infrastructure CLI that provides:

1. **Multi-Model Support**: OpenAI, Anthropic, Google, Ollama, etc.
2. **Voice Capabilities**: STT + TTS (PAJ uses macOS native)
3. **Web Automation**: Browser control (PAJ uses Chrome MCP)
4. **Memory System**: Long-term conversation memory
5. **File Operations**: Document processing, code generation
6. **Shell Integration**: Terminal commands, aliases

### PAJ-Specific Use Cases

#### 1. YourBow AdOps Automation
```bash
# Draft client email
pai draft-email "Client wants avails for Q4 campaign, 10M impressions"

# Research GAM best practices
pai research "Google Ad Manager inventory forecasting optimization"
```

#### 2. Infrastructure Management
```bash
# Generate Proxmox LXC deployment script
pai generate-script "Create PCT for Kestra workflow orchestration"

# Troubleshoot AzerothCore issue
pai debug "AzerothCore worldserver crashing on player login"
```

#### 3. Code Review & Generation
```bash
# Review Metamozak code
pai review-code src/orchestrator.py

# Generate FastA2A integration code
pai generate-code "A2A client that sends voice transcriptions to Metamozak"
```

#### 4. Personal Knowledge Management
```bash
# Summarize research
pai summarize "Recent tabs on WoW localization, LiveKit pricing, Tailscale setup"

# Generate daily briefing
pai briefing "What did I work on today? What's pending?"
```

### Installation & Setup

#### Prerequisites
- Python 3.11+
- macOS (for native voice features)
- API keys: OpenAI, Anthropic, etc.

#### Quick Start
```bash
cd C:\dev\PAJ

# Install dependencies (use UV!)
uv venv
uv pip install -r requirements.txt  # TODO: Create if missing

# Setup PAI
./PAI_DIRECTORY/setup.sh  # or PowerShell equivalent

# Configure API keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Test voice system
pai speak "Hello Pavle, PAJ is ready"
```

### Configuration Files

#### voices.json (PAJ Custom)
```json
{
  "default_voice": "Jamie",
  "premium_voices": ["Jamie", "Ava", "Serena", "Isha"],
  "enhanced_voices": ["Tom", "Oliver", "Samantha"],
  "rate": 180,
  "volume": 0.8
}
```

#### pai.config (Main Config)
```yaml
# TODO: Document PAI configuration structure
models:
  default: claude-3-5-sonnet-20241022
  fallback: gpt-4o

voice:
  provider: macos_native  # PAJ custom

browser:
  provider: chrome_mcp  # PAJ custom
```

### Integration with Metamozak System

#### Option 1: Standalone CLI (Current)
PAJ as personal CLI tool, independent of Metamozak.

#### Option 2: A2A Integration (Future)
PAJ as A2A service exposed to Metamozak:

```python
# metamozak/src/tools/pai_client.py
import httpx

async def call_pai(command: str, args: str):
    """Route complex tasks to PAJ via A2A"""
    response = await httpx.post(
        "http://pai.paja.pro/a2a",
        json={
            "command": command,
            "args": args,
            "context_id": "metamozak_session"
        }
    )
    return response.json()
```

### Development Workflow

#### Sync with Upstream PAI
```bash
# Add upstream remote
git remote add upstream https://github.com/danielmiessler/PAI.git

# Fetch updates
git fetch upstream

# View changes
git log main..upstream/main --oneline

# Merge selectively (preserve PAJ customizations)
git merge upstream/main
# Resolve conflicts (keep PAJ voice system, Chrome MCP)
```

#### Feature Development
```bash
# Use specify framework
cd C:\dev\PAJ

/specify "Add Archon KB integration for long-term memory"
/plan
/tasks
/implement
```

#### Testing
```bash
# Test voice system
pai speak "Testing PAJ voice"

# Test with Metamozak context
pai query --context metamozak "What agents are deployed on Proxmox?"

# Test browser automation
pai browse "https://yourbow.com/admanager" --action "check active campaigns"
```

### PAJ Enhancements Roadmap

#### Phase 1: Voice Integration (DONE ✅)
- [x] Migrate from ElevenLabs to macOS voices
- [x] Create voices.json configuration
- [x] Zero-cost, offline voice synthesis

#### Phase 2: MCP Integration (DONE ✅)
- [x] Replace Playwright with Chrome DevTools MCP
- [x] Align with MCP Gateway strategy

#### Phase 3: Metamozak Integration (TODO)
- [ ] Expose PAJ as A2A service
- [ ] Route complex CLI tasks through Metamozak
- [ ] Share context with other agents

#### Phase 4: Archon KB Integration (TODO)
- [ ] Store PAI memories in Archon KB
- [ ] Query Archon for context retrieval
- [ ] Sync learnings across agent system

#### Phase 5: YourBow-Specific Tools (TODO)
- [ ] GAM API integration helpers
- [ ] Client email templates
- [ ] AdOps workflow automation

### Upstream PAI Updates to Consider

#### v0.2.4 Changes (October 7, 2025)
- README cleanup & organization
- Pronunciation clarification
- May want to cherry-pick README improvements

#### Future Monitoring
```bash
# Check for new releases
gh release list --repo danielmiessler/PAI

# View specific release notes
gh release view v0.2.4 --repo danielmiessler/PAI
```

### Security & Privacy

#### PAJ Advantages
- **Offline voice**: No cloud API calls for TTS
- **Local processing**: macOS neural TTS runs locally
- **No telemetry**: PAJ modifications don't send data to third parties

#### API Key Management
```bash
# Store in .env (gitignored)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
ARCHON_API_KEY=...  # PAJ custom

# Never commit API keys
# .gitignore already includes .env
```

### Deployment Options

#### Option 1: Local CLI (Current)
- Run on Windows 11 desktop
- Access via terminal (PowerShell / WSL)
- Voice works only on macOS (if running on Mac)

#### Option 2: Remote Server (Future)
- Deploy on Proxmox PCT (e.g., PCT-150: PAJ-CLI)
- Access via SSH
- Integrate with Tailscale VPN for mobile access

#### Option 3: Dockerized (Future)
- Containerize PAJ
- Deploy on dev VM or Proxmox
- Expose as web service

### Community & Resources

#### Upstream PAI
- **GitHub**: https://github.com/danielmiessler/PAI
- **Video**: https://youtu.be/iKwRWwabkEc
- **License**: MIT

#### PAJ (Private Fork)
- **GitHub**: https://github.com/zipaJopa/PAJ (private)
- **Owner**: Pavle Bradic
- **Integration**: Part of Metamozak constellation

### Quick Reference Commands

```bash
# Voice (PAJ custom - macOS native)
pai speak "message"

# Query with context
pai query "question" --context <source>

# Generate code
pai generate-code "description"

# Summarize
pai summarize <file_or_url>

# Draft email (YourBow use case)
pai draft-email "context and requirements"

# Research
pai research "topic"

# Debug
pai debug "problem description"

# Memory operations
pai remember "key information"
pai recall "what did I..."
```

### File Structure

```
C:\dev\PAJ\
├── .git/                    # Git repository
├── .claude/                 # Specify framework
│   ├── CLAUDE.md           # This file
│   └── commands/           # Slash commands
├── .specify/               # Spec-kit artifacts
├── PAI_DIRECTORY/          # Main PAI code
│   ├── voices.json         # PAJ custom voice config
│   ├── setup.sh            # Setup script
│   └── ...                 # PAI core modules
├── README.md               # Project README
├── LICENSE                 # MIT License
└── SECURITY.md             # Security policy
```

### Next Steps

1. **Test PAJ locally** (if on macOS, test voice; otherwise test core features)
2. **Document requirements.txt** (create if missing)
3. **Merge upstream v0.2.4 changes** (selectively, preserve PAJ mods)
4. **Integrate with Archon KB** (long-term memory)
5. **Expose as A2A service** (for Metamozak integration)
6. **Create YourBow-specific tools** (GAM helpers, email templates)

---

**Created**: 2025-10-07
**Owner**: Pavle Bradic (brad@yourbow.com)
**Status**: Private Fork (PAJ v0.2.3)
**Upstream**: danielmiessler/PAI (v0.2.4)
**Philosophy**: Offline-first, privacy-focused, infrastructure-integrated
