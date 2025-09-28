# UFC Context System Documentation

## Overview

The Universal Flexible Context (UFC) system is PAI's intelligent context management framework. It provides semantic understanding of user intent and dynamically loads relevant context files and agents, making AI interactions more aware and capable.

## Core Concepts

### Semantic Understanding

Unlike traditional keyword matching, UFC understands the **meaning** behind user requests:

- "Help me with my site" → Understands this means website context
- "What's new with AI" → Recognizes research intent
- "Fix this bug" → Identifies engineering context needed

### Dynamic Loading

Context and agents are loaded on-demand based on:
1. User intent analysis
2. Current conversation context
3. Project-specific requirements
4. Task complexity

## How UFC Works

### 1. Intent Recognition Pipeline

```
User Input → Semantic Analysis → Pattern Matching → Context Selection → Loading
```

**Example Flow:**
```yaml
User: "I need to update my blog with AI research"
↓
Semantic Analysis: [blog, update, AI, research]
↓
Pattern Match: 
  - "blog" → Website context
  - "research" → Research agent
↓
Context Load:
  - ${PAI_DIR}/context/projects/website/CLAUDE.md
  - Agent: researcher
```

### 2. Context Loading Rules

Context files are loaded based on semantic triggers defined in the hook system:

```javascript
// Example context rule
{
  trigger: {
    semantic: ["website", "blog", "site", "homepage"],
    phrases: ["update my site", "fix navigation", "publish article"]
  },
  action: {
    loadContext: ["${PAI_DIR}/context/projects/website/CLAUDE.md"],
    agent: null
  }
}
```

## Configuration

### Context File Structure

Context files use Markdown with special directives:

```markdown
# Context Name

## Purpose
Brief description of this context

## Knowledge Base
Domain-specific information...

## Instructions
Special instructions for the AI...

## Available Commands
- command1: Description
- command2: Description
```

### Creating Context Files

1. **Global Context**: `${PAI_DIR}/context/CLAUDE.md`
   - Loaded for all conversations
   - Contains system-wide settings

2. **Project Context**: `${PAI_DIR}/context/projects/*/CLAUDE.md`
   - Project-specific knowledge
   - Loaded based on intent

3. **Domain Context**: `${PAI_DIR}/context/domains/*/CLAUDE.md`
   - Specialized domain knowledge
   - Technical references

## Context Categories

### 1. Website & Blog Context
**Triggers**: website, blog, site, homepage, navigation
**Files**: 
- `${PAI_DIR}/context/projects/website/CLAUDE.md`
- `${PAI_DIR}/context/projects/website/content/CLAUDE.md`

### 2. Research Context
**Triggers**: research, investigate, find information, latest news
**Agent**: researcher
**Behavior**: Launches research agent for web searches

### 3. Security Context
**Triggers**: security, vulnerabilities, pentesting, audit
**Agent**: pentester
**Behavior**: Launches security testing agent

### 4. Engineering Context
**Triggers**: code, debug, implement, fix bug
**Agent**: engineer
**Behavior**: Launches engineering agent

### 5. Financial Context
**Triggers**: expenses, bills, budget, spending
**Files**:
- `${PAI_DIR}/context/life/expenses.md`
- `${PAI_DIR}/context/life/finances/`

### 6. Health Context
**Triggers**: health, fitness, medical, wellness
**Files**: `${HOME}/Projects/Life/Health/CLAUDE.md`

## Agent System Integration

UFC can automatically launch specialized agents:

```yaml
Available Agents:
- general-purpose: Default for complex tasks
- researcher: Web research and information gathering
- engineer: Software development
- designer: UI/UX and visual design
- pentester: Security testing
- architect: System design and specs
- writer: Content creation
```

### Agent Selection Logic

```python
def select_agent(intent):
    if "research" in intent:
        return "researcher"
    elif "security" in intent:
        return "pentester"
    elif "code" in intent:
        return "engineer"
    elif "design" in intent:
        return "designer"
    else:
        return "general-purpose"
```

## Dynamic Requirements Loading

The UFC system uses a special hook (`user-prompt-submit-hook`) to load requirements:

### Loading Process

1. **Hook Activation**: Triggered before prompt processing
2. **Intent Analysis**: Semantic understanding of user request
3. **Context Selection**: Matching against defined patterns
4. **File Loading**: Reading selected context files
5. **Agent Launch**: Starting specialized agents if needed

### Example Hook Implementation

```bash
#!/bin/bash
# user-prompt-submit-hook

# Analyze user prompt
INTENT=$(analyze_intent "$USER_PROMPT")

# Load appropriate context
case "$INTENT" in
  "website")
    load_context "${PAI_DIR}/context/projects/website/CLAUDE.md"
    ;;
  "research")
    launch_agent "researcher"
    ;;
  "security")
    launch_agent "pentester"
    ;;
esac
```

## Best Practices

### 1. Context File Guidelines

- **Keep it focused**: One domain per context file
- **Use clear headers**: Structure with markdown headers
- **Include examples**: Provide usage examples
- **Update regularly**: Keep context current

### 2. Semantic Triggers

- **Be comprehensive**: Include synonyms and variations
- **Test patterns**: Verify trigger accuracy
- **Avoid conflicts**: Ensure clear disambiguation

### 3. Performance Optimization

- **Lazy loading**: Load only what's needed
- **Cache frequently used**: Store common contexts
- **Batch operations**: Load related contexts together

## Advanced Features

### Context Inheritance

Contexts can inherit from others:

```markdown
# Child Context
extends: ${PAI_DIR}/context/base/CLAUDE.md

## Additional Knowledge
...
```

### Conditional Loading

Load context based on conditions:

```yaml
condition:
  - file_exists: "package.json"
  - directory: "src/"
then:
  load: "${PAI_DIR}/context/javascript/CLAUDE.md"
```

### Context Variables

Use variables in context files:

```markdown
## Project Path
${PROJECT_PATH}

## Current User
${USER}

## Date
${DATE}
```

## Troubleshooting

### Context Not Loading

1. **Check triggers**: Verify semantic triggers match
2. **File paths**: Ensure context files exist
3. **Permissions**: Check file read permissions
4. **Hook execution**: Verify hooks are running

### Debug Mode

Enable debug logging:

```bash
export UFC_DEBUG=true
```

View debug output:
```bash
tail -f ${HOME}/Library/Logs/ufc-debug.log
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Context not found | Check file path in hook |
| Wrong agent selected | Review semantic triggers |
| Slow loading | Optimize context file size |
| Duplicate loading | Check for circular references |

## API Reference

### Context Loading Functions

```javascript
// Load single context
loadContext(filePath: string): void

// Load multiple contexts
loadContexts(filePaths: string[]): void

// Launch agent with context
launchAgent(agentType: string, context?: string): void
```

### Hook Interface

```typescript
interface UFCHook {
  trigger: {
    semantic: string[];
    phrases: string[];
  };
  action: {
    loadContext?: string[];
    launchAgent?: string;
    execute?: string;
  };
}
```

## Examples

### Example 1: Website Update

```bash
User: "I need to update my blog with the latest AI news"

UFC Analysis:
- Triggers: ["blog", "update", "AI", "news"]
- Contexts: website, research
- Actions:
  1. Load website context
  2. Launch researcher agent
  3. Combine results
```

### Example 2: Security Audit

```bash
User: "Check my server for vulnerabilities"

UFC Analysis:
- Triggers: ["check", "server", "vulnerabilities"]
- Context: security
- Actions:
  1. Launch pentester agent
  2. Load security context
  3. Execute security scan
```

### Example 3: Financial Analysis

```bash
User: "How much did I spend on utilities last month?"

UFC Analysis:
- Triggers: ["spend", "utilities", "last month"]
- Context: financial
- Actions:
  1. Load expense context
  2. Parse financial data
  3. Calculate utilities total
```

## Future Enhancements

### Planned Features

1. **Machine Learning Integration**: Learn from usage patterns
2. **Context Versioning**: Track context changes
3. **Multi-language Support**: Context in multiple languages
4. **Cloud Sync**: Synchronize contexts across devices
5. **Plugin System**: Third-party context providers

### Experimental Features

- **Auto-context Generation**: Create contexts from documentation
- **Context Compression**: Optimize large contexts
- **Predictive Loading**: Pre-load likely contexts
- **Context Sharing**: Share contexts between users

---

*UFC System Version 1.0.0*
*Last Updated: [Current Date]*