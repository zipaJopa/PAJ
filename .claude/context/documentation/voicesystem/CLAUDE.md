#### Agent Voice Architecture

Each agent has a unique voice ID for the notification system, creating distinct personalities:

**Voice ID Mappings:**
- **Main Agent**: Configure your own voice ID - The primary orchestrator voice
- **Researcher Agent**: Configure your own voice ID - Information discovery voice
- **Designer Agent**: Configure your own voice ID - Designer voice
- **Engineer Agent**: Configure your own voice ID - Development voice
- **Writer Agent**: Configure your own voice ID - Content creation voice
- **Pentester Agent**: Configure your own voice ID - Security testing voice
- **Architect Agent**: Configure your own voice ID - Architecture and planning voice

**Voice Completion Format:**

**Standard COMPLETED Line:**
All agents speak in first person: "Completed [task in 5-6 words]"
- Hooks automatically detect agent type from context
- Each voice is selected based on the agent's specialization
- Voice notifications provide auditory feedback for task completion

**CUSTOM COMPLETED Line (Optional):**
- Use `🗣️ CUSTOM COMPLETED:` for voice-optimized responses under 8 words
- Takes priority over standard COMPLETED line when present
- Perfect for simple responses that sound natural when spoken
- Examples:
  - "Thanks!" → CUSTOM COMPLETED: "You're welcome!"
  - "2+2?" → CUSTOM COMPLETED: "Four"
  - "What time?" → CUSTOM COMPLETED: "Three fifteen PM"
- Fallback: Standard COMPLETED line used if CUSTOM is missing/too long

**🚨 VOICE ID UPDATE CHECKLIST - CRITICAL REFERENCE**

When updating any agent voice ID, you MUST update ALL of these locations:

1. **Agent Configuration File**: `agents/[agent-name].md`
   - Update `voiceId: [new-voice-id]` in frontmatter
   - Update voice ID reference in completion rules section

2. **Subagent Stop Hook**: `.claude/hooks/subagent-stop-hook.ts`
   - Update `AGENT_VOICE_IDS` mapping with new voice ID
   - Ensure agent name exists in `AGENT_NAMES` mapping
   - Verify agent type included in regex patterns for completion parsing

3. **Main Context Documentation**: `.claude/context/CLAUDE.md`
   - Update voice ID in "Agent Voice Architecture" section
   - Keep this checklist current with any new locations

4. **Voice Server Configuration**: (Location varies)
   - Voice notification server may cache voice mappings
   - Check notification server configuration files
   - Restart voice server if needed to reload configurations

5. **Test Scripts**: `.claude/hooks/tests/` (if they exist)
   - Update any test cases that reference specific voice IDs
   - Verify test suite passes with new voice configuration

**VERIFICATION STEPS:**
1. Test agent with simple task to verify voice system works
2. Check voice server logs for any errors with new voice ID
3. Confirm voice sounds correct and matches intended agent personality
4. Update this documentation if new locations are discovered

**COMMON MISTAKES TO AVOID:**
- Forgetting to update agent regex patterns in hook parsing
- Missing voice ID updates in agent configuration frontmatter
- Not restarting voice server after configuration changes
- Updating hook but not agent config (or vice versa)