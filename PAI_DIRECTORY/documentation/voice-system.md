# PAI Voice System Documentation

## Overview
The PAI Voice System provides text-to-speech capabilities for Kai and all agents using ElevenLabs voices. The system uses a unified stop-hook approach where completion messages are read aloud using different voice IDs for Kai and each specialized agent.

## Architecture Overview

### Core Components

1. **Voice Server** (`${PAI_DIR}/voice-server/server.ts`)
   - Bun-based HTTP server running on port 8888
   - Handles text-to-speech requests via ElevenLabs API
   - Falls back to macOS 'say' command if ElevenLabs not configured
   - Provides notification display alongside voice output

2. **Stop Hook** (`${PAI_DIR}/hooks/stop-hook.ts`)
   - Triggers after every Claude Code response
   - Parses completion messages from transcripts
   - Extracts text from COMPLETED lines
   - Sends appropriate voice requests to the voice server
   - Handles both Kai's direct work and agent completions

3. **Agent Configurations** (`${PAI_DIR}/agents/*.md`)
   - Each agent has a unique voice ID for distinct personality
   - Voice IDs defined in agent configurations
   - No special formatting required in agent outputs

## How It Works

### Complete System Flow

1. **Task Execution**
   - User requests a task
   - Either Kai handles it directly or delegates to an agent

2. **Completion Format**
   - All responses must end with: `🎯 COMPLETED: [description of what was done]`
   - This line is mandatory for voice output to trigger
   - Description should be 5-6 words summarizing the accomplishment

3. **Stop Hook Processing**
   - Hook reads the transcript after each response
   - Searches for the COMPLETED line in the output
   - Extracts the exact text after "COMPLETED:"
   - Determines if it was Kai or an agent who completed the task

4. **Voice Selection**
   - For Kai's completions: Uses Kai's voice ID (jqcCZkN6Knx8BJ5TBdYR)
   - For agent completions: Uses the agent's specific voice ID

5. **Voice Generation**
   - Stop hook sends POST request to voice server at localhost:8888
   - Request includes the completion message and appropriate voice ID
   - Server generates audio using ElevenLabs API
   - Audio plays through system speakers

## Voice ID Mappings

| Entity | Voice ID | Description |
|--------|----------|-------------|
| Kai | jqcCZkN6Knx8BJ5TBdYR | Main orchestrator and assistant |
| Researcher | AXdMgz6evoL7OPd7eU12 | Information discovery specialist |
| Pentester | hmMWXCj9K7N5mCPcRkfC | Security testing specialist |
| Engineer | kmSVBPu7loj4ayNinwWM | Development specialist |
| Designer | ZF6FPAbjXT4488VcRRnw | Design specialist |
| Architect | muZKMsIDGYtIkjjiUS82 | System architecture specialist |
| Writer | gfRt6Z3Z8aTbpLfexQ7N | Content creation specialist |

## Server Configuration

### Environment Variables (in ${PAI_DIR}/.env)
```bash
ELEVENLABS_API_KEY="your_api_key_here"
ELEVENLABS_VOICE_ID="jqcCZkN6Knx8BJ5TBdYR"  # Default voice ID (Kai)
PORT="8888"
```

### Server API

#### POST /notify
Main endpoint for voice notifications.

**Request Format:**
```json
{
  "message": "Text to speak",
  "voice_id": "voice_id_here",
  "title": "Optional notification title",
  "voice_enabled": true
}
```

**Field Requirements:**
- `message` (required): The text to be spoken
- `voice_id` (optional): ElevenLabs voice ID to use
- `title` (optional): Visual notification title
- `voice_enabled` (optional): Set to false to skip voice output

#### GET /health
Returns server health status and configuration.

### Starting the Voice Server

**Automatic Start:**
```bash
cd ${PAI_DIR}/voice-server
./start.sh
```

**Manual Start:**
```bash
bun ${PAI_DIR}/voice-server/server.ts
```

**Verify Server Running:**
```bash
curl http://localhost:8888/health
```

## Stop Hook Implementation

### Current Working Implementation
The stop hook (`${PAI_DIR}/hooks/stop-hook.ts`) processes completion messages with this logic:

1. **Parse Transcript**: Reads Claude Code conversation transcript
2. **Find Completions**: Looks for Task tool usage (agents) or COMPLETED lines (Kai)
3. **Extract Message**: Gets the exact text after "COMPLETED:"
4. **Select Voice**: Chooses appropriate voice ID based on who completed the task
5. **Send to Server**: POSTs to voice server with correct field names

### Critical Field Names
The voice server expects these exact field names:
- `message` - The text to speak (NOT `text`)
- `voice_id` - The ElevenLabs voice ID (NOT `voiceId`)

## Claude Code Hook Configuration

### Settings Setup (`${PAI_DIR}/settings.json`)
```json
{
  "hooks": {
    "stop": [
      {
        "command": "bun ${PAI_DIR}/hooks/stop-hook.ts"
      }
    ]
  }
}
```

## Response Format Requirements

### Mandatory Structure
Every response from Kai and agents MUST include:

```
🎯 COMPLETED: [5-6 word description of what was done]
```

**Examples:**
- `🎯 COMPLETED: Fixed voice output field mismatch`
- `🎯 COMPLETED: Completed security scan of network`
- `🎯 COMPLETED: Generated design mockups for homepage`

### Why This Format Is Critical
- The stop hook specifically looks for the 🎯 COMPLETED pattern
- Without this line, voice output will not trigger
- The text after COMPLETED: is spoken exactly as written
- Keep descriptions concise (5-6 words) for natural speech

## Troubleshooting

### Voice Not Speaking

1. **Check COMPLETED Line**
   - Ensure response includes `🎯 COMPLETED:` line
   - Verify there's text after the colon
   - Check for proper formatting

2. **Verify Voice Server Running**
   ```bash
   curl -X POST http://localhost:8888/notify \
     -H "Content-Type: application/json" \
     -d '{"message": "Test", "voice_id": "jqcCZkN6Knx8BJ5TBdYR"}'
   ```

3. **Check Field Names**
   - Stop hook must send `message` not `text`
   - Stop hook must send `voice_id` not `voiceId`

4. **Review Stop Hook**
   - Verify hook is executable: `ls -la ${PAI_DIR}/hooks/stop-hook.ts`
   - Check hook is configured in settings.json
   - Review hook logs for errors

### Wrong Voice Playing

1. **Verify Voice ID**
   - Check agent's voice ID in the VOICES mapping
   - Ensure voice ID is valid ElevenLabs ID
   - Test voice directly with curl command

2. **Check Agent Detection**
   - Stop hook should detect agent type from Task tool usage
   - Verify agent type matches voice mapping

### Server Issues

1. **Port Conflict**
   ```bash
   lsof -i :8888
   ```

2. **API Key Issues**
   - Verify ELEVENLABS_API_KEY in ${PAI_DIR}/.env
   - Check API key is valid and has credits
   - Server falls back to 'say' command if API fails

## Testing the System

### Test Voice Server Directly
```bash
# Test with Kai's voice
curl -X POST http://localhost:8888/notify \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Testing Kai voice output",
    "voice_id": "jqcCZkN6Knx8BJ5TBdYR"
  }'

# Test with Agent voice
curl -X POST http://localhost:8888/notify \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Testing engineer voice",
    "voice_id": "kmSVBPu7loj4ayNinwWM"
  }'
```

### Test Complete Flow
1. Ask Kai to complete a simple task
2. Verify the response includes `🎯 COMPLETED:` line
3. Listen for voice output with appropriate voice
4. Check server logs for any errors

## Common Issues and Solutions

### "Task completed" Instead of Actual Message
**Problem**: Voice says generic "task completed" instead of the actual completion description.

**Cause**: Field name mismatch between stop hook and voice server.

**Solution**: Ensure stop hook sends:
- `message` (not `text`)
- `voice_id` (not `voiceId`)

### No Voice Output
**Problem**: Task completes but no voice is heard.

**Common Causes**:
1. Missing `🎯 COMPLETED:` line in response
2. Voice server not running
3. Stop hook not configured
4. ElevenLabs API issues

**Solutions**:
1. Verify response format includes COMPLETED line
2. Start voice server: `cd ${PAI_DIR}/voice-server && ./start.sh`
3. Check settings.json has stop hook configured
4. Test with fallback 'say' command by removing API key temporarily

### Voice Cuts Off
**Problem**: Voice output is truncated or cut off.

**Cause**: Message too long or contains special characters.

**Solution**: Keep COMPLETED descriptions concise (5-6 words) and avoid special characters.

## Maintenance

### Adding New Agents
1. Add voice ID to VOICES mapping in stop-hook.ts
2. Ensure agent outputs proper COMPLETED format
3. Test with agent invocation

### Updating Voice IDs
1. Edit VOICES constant in stop-hook.ts
2. Update this documentation
3. Restart any running sessions

### Server Logs
Monitor server output for:
- Successful voice generation
- API errors or rate limits
- Fallback to 'say' command
- Request/response debugging

## Security Considerations

- Voice server only accepts connections from localhost
- Rate limiting prevents abuse (10 requests/minute)
- Input sanitization prevents command injection
- API keys stored in environment variables, not code

## System Benefits

- **Unified Experience**: Consistent voice output across all interactions
- **Distinct Personalities**: Each agent has unique voice identity
- **Reliable Triggering**: COMPLETED format ensures consistent behavior
- **Fallback Support**: Works without ElevenLabs using macOS 'say'
- **Simple Integration**: Minimal configuration required