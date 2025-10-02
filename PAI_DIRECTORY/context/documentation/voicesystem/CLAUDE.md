#### Agent Voice Architecture

Each agent has a unique macOS Premium or Enhanced voice for the notification system, creating distinct personalities through natural-sounding neural TTS voices.

**Voice Mappings (macOS Native):**
- **Kai (Main Agent)**: Jamie (Premium) - UK Male - Professional, conversational
- **Researcher Agent**: Ava (Premium) - US Female - Analytical, highest quality
- **Designer Agent**: Isha (Premium) - Indian Female - Creative, distinct
- **Engineer Agent**: Tom (Enhanced) - US Male - Steady, professional
- **Writer Agent**: Samantha (Enhanced) - US Female - Articulate, warm
- **Pentester Agent**: Oliver (Enhanced) - UK Male - Technical, sharp
- **Architect Agent**: Serena (Premium) - UK Female - Strategic, sophisticated

**Voice Configuration:**
- All voices configured in `${PAI_DIR}/voice-server/voices.json`
- Uses macOS native Premium and Enhanced neural voices
- Zero API costs, complete privacy, 100% offline
- Customizable speech rates per agent (configured via rate_multiplier)
- Default speeds: Kai at 228 wpm (1.3x), agents at 236 wpm (1.35x)

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

**🚨 VOICE UPDATE CHECKLIST - CRITICAL REFERENCE**

When updating any agent voice, you MUST update ALL of these locations:

1. **Voice Configuration File**: `${PAI_DIR}/voice-server/voices.json`
   - Update `voice_name`: macOS voice (e.g., "Jamie (Premium)", "Ava (Premium)")
   - Adjust `rate_multiplier`: Speed multiplier (1.0 = normal, 1.3 = 30% faster)
   - Update `description`: Voice characteristics and personality match
   - Set `type`: "Premium" or "Enhanced"

2. **Agent Configuration File**: `${PAI_DIR}/agents/[agent-name].md`
   - Update `voiceId:` in frontmatter to match macOS voice name
   - Example: `voiceId: Ava (Premium)` or `voiceId: Tom (Enhanced)`

3. **Stop Hook**: `${PAI_DIR}/hooks/stop-hook.ts`
   - Update `VOICES` mapping to reference correct voice names from voices.json
   - Ensure agent name exists in voice mappings
   - Hook loads configuration from voices.json automatically

4. **Documentation**: `${PAI_DIR}/context/documentation/voice-system.md`
   - Update voice mappings table
   - Keep this documentation current with voice changes

**BEFORE CHANGING VOICES:**
1. Download the new voice from System Settings → Voice (Live Speech) → Manage Voices
2. Verify it's a Premium or Enhanced voice (not legacy/compact)
3. Test voice directly: `say -v "Voice Name (Premium)" "Test message"`

**VERIFICATION STEPS:**
1. Test agent with simple task to verify voice system works
2. Confirm voice sounds correct and matches intended agent personality
3. Verify speech rate is appropriate (not too fast/slow)
4. Check no errors in voice server output

**COMMON MISTAKES TO AVOID:**
- Using legacy voices instead of Premium/Enhanced (sounds robotic!)
- Forgetting to download the voice from System Settings first
- Not matching voice name exactly in voices.json (case-sensitive!)
- Setting rate_multiplier too high (>1.5x can be hard to understand)