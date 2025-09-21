<div align="center">

![PAI Logo](./pai-logo.png)

# `PAI` - Personal AI Infrastructure

### <code>PAI</code> is an open-source personal AI infrastructure for orchestrating your life and work

<br />

![Static Badge](https://img.shields.io/badge/mission-upgrade_humans_using_AI-purple)
![GitHub last commit](https://img.shields.io/github/last-commit/danielmiessler/PAI)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Powered%20by-Claude%20Code-blue)](https://claude.ai/code)
[![PAI Video](https://img.shields.io/badge/🎥_Watch-PAI_Video-6B46C1)](https://youtu.be/iKwRWwabkEc)

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-getting-started">Getting Started</a> •
  <a href="#-philosophy">Philosophy</a> •
  <a href="#-examples">Examples</a> •
  <a href="#-contribute">Contribute</a>
</p>

---

</div>

## 💥 Updates

**September 21, 2025**
- Cleaned up voice server code for secure command execution
- Added PAI_HOME support to eliminate all hardcoded paths
- Created comprehensive documentation under `~/.claude/documentation/`
- Dynamic MCP detection using `claude mcp list` (PR #12)
- Voice server improvements with input validation and rate limiting

**September 20, 2025**
- Added `/voice-server` directory with ElevenLabs integration
- Closed PRs fixing hardcoded path issues
- Working on missing hooks from Issues

**September 12, 2025**  
- Uploaded dynamic resource loading system to `/hooks` and `/commands`
- Submit-user-hook dynamically loads context and agents
- Dynamic routing via `/commands/load-dynamic-requirements.md`

## 🎯 **What is PAI?**

PAI is a project designed to give anyone in the world a personal AI infrastructure for orchestrating their personal and professional lives.

Based off my own personal Digital Assistant, **Kai**, it combines a scaffolding framework with a growing set of real-world examples.

<table>
<tr>
<td width="33%" align="center"><b>🧠 Life Management</b><br/>Research • Writing • Health • Finances</td>
<td width="33%" align="center"><b>💼 Professional</b><br/>Code • Content • Analytics • Automation<br/>Department Management • Program Management • Startups</td>
<td width="33%" align="center"><b>🎯 Personal</b><br/>Learning • Family • Goals • Habits</td>
</tr>
</table>

> **💡 Core Mission:** Augment humans with AI capabilities so they can survive and thrive in a world full of AI.

<br/>

## ✨ **Features**

<details open>
<summary><b>🏗️ UFC Context Architecture - Your Persistent AI Brain</b></summary>

```
~/.claude/context/
├── 🧠 projects/         # Active work and initiatives
├── 🛠️ tools/           # AI agents and capabilities  
├── 💰 finances/        # Financial tracking and analysis
├── 🏥 health/          # Wellness and medical data
└── 🎯 telos/           # Objectives and progress tracking
```

- **Persistent Memory**: Never lose context between sessions
- **Hierarchical Organization**: Intuitive file-based structure
- **Complete Portability**: Your entire AI brain in plain text
- **Dynamic Loading**: Context loads based on current task

</details>

<details>
<summary><b>🤖 Specialized Digital Assistants</b></summary>

| Assistant | Purpose | Voice ID | Specialization |
|-----------|---------|----------|----------------|
| **Researcher** | Deep information synthesis | `AXdMgz6...` | Web research, analysis |
| **Engineer** | Production code development | `kmSVBPu7...` | Full-stack, testing |
| **Designer** | UX/UI and visual design | `ZF6FPAb...` | Interfaces, experiences |
| **Pentester** | Security assessment | `hmMWXCj9...` | Vulnerability testing |
| **Architect** | System design | `muZKMsID...` | Technical specifications |

</details>

<details>
<summary><b>🔧 Integrated Tool Ecosystem</b></summary>

- **MCP Servers**: Playwright, Stripe, Apify, and more
- **Voice System**: Natural conversation with TTS/STT
- **Browser Automation**: Visual testing and web interaction
- **API Integrations**: Connect any service to your PAI

</details>

<br/>

## 🚀 **Getting Started**

> **📢 Note:** Lots more examples and templates coming soon, including the full voice implementation. This repo will be continuously updated with real-world implementations from my [YouTube channel](https://www.youtube.com/@unsupervised-learning).

### **Quick Start**

I use *Typescript* as my main language (instead of Python), and I use `bun` as my main Javascript/Typescript system. Think: runtime, package management, etc. So if you want to use this system as-is, make sure you have `bun` installed before getting started.

`brew install bun`

One thing to note is that when you download the project, the `.claude` directory is hidden by default because it's a dot directory. So cd into `.claude` when you're done with the instructions. (Or cd into `claude_directory` which is just a symlink to it)

`cd .claude`

```bash
# 1. Clone the repository
git clone https://github.com/danielmiessler/PAI.git

# 2. Check out the files (the folder is hidden with default `ls`)

ls -lah
cd ~/.claude/
ls -lah

# 3. Put your keys into your own .env file, which is not in the repo itself. Use the example as a template if needed

nvim .env

# 4. Export your own PAI_HOME in your shell config. Change for your desired home

PAI_HOME="/Users/daniel/"

### **Testing PAI in Custom Locations**

PAI uses the `PAI_HOME` environment variable to determine its installation path. By default, it uses `~/.claude/`, but you can test PAI in any directory:

# Test PAI in a custom directory
export PAI_HOME="/path/to/directory"

# The system will look for context files at ${PAI_HOME}/.claude/context/
```

**Important Notes:**
- Set `PAI_HOME` before starting Claude Code for the environment variable to take effect
- The `.claude` directory structure should exist at your custom `PAI_HOME` location
- This is particularly useful for developers testing multiple PAI configurations

### **Prerequisites**

- [Claude Code](https://claude.ai/code) - The primary AI interface, which can ultimately be any similar system, e.g., Gemini, Codex, etc.
- [Bun](https://bun.com/) - The node.js system we're using
- Text editor (Neovim recommended, but any will work—it's all Markdown/Text!)
- Ideal: Decent Command Line Interface skills

<br/>

## 💡 **Philosophy**

<div align="center">

### **Human 3.0: Augmentation, Not Replacement**

</div>

The PAI system embodies a fundamental belief: **AI should amplify human capability, not replace it.**

| Traditional AI | PAI Approach |
|----------------|--------------|
| Black box decisions | Transparent, file-based logic |
| Vendor lock-in | Completely portable |
| Forgets everything | Persistent memory |
| Generic responses | Personalized to you |
| Replaces thinking | Augments capability |

<br/>

## 📚 **Examples**

Coming soon! Each example will include:
- Complete file structure
- Configuration templates  
- Step-by-step setup
- Video walkthrough

### **Planned Examples**
- 📰 Daily Intelligence Briefing
- 💰 Expense Tracking & Analysis
- 📝 Content Creation Pipeline
- 🔬 Research Assistant
- 🏥 Health Monitoring
- 📚 Learning System

<br/>

## 🤝 **Contribute**

PAI is open source and welcomes contributions!

- 🐛 [Report Issues](https://github.com/danielmiessler/PAI/issues)
- 💡 [Suggest Features](https://github.com/danielmiessler/PAI/discussions)
- 🔧 [Submit PRs](https://github.com/danielmiessler/PAI/pulls)
- ⭐ Star the repo to show support!

<br/>

## 📄 **License**

PAI is MIT licensed. See [LICENSE](./LICENSE) for details.

<br/>

---

<div align="center">

### 🎓 **Remember**

> *"This is YOUR infrastructure. Every configuration, every tool, every workflow should serve your unique life and goals. You're not using AI—you're augmenting yourself with it."*

**by [Daniel Miessler](https://danielmiessler.com) • Follow along on [YouTube](https://www.youtube.com/@unsupervised-learning)**

</div>
