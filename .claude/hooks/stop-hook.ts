#!/usr/bin/env bun

import { readFileSync } from 'fs';

// Simple voice mappings
const VOICES = {
  researcher: 'AXdMgz6evoL7OPd7eU12',
  pentester: 'hmMWXCj9K7N5mCPcRkfC', 
  engineer: 'kmSVBPu7loj4ayNinwWM',
  designer: 'ZF6FPAbjXT4488VcRRnw',
  architect: 'muZKMsIDGYtIkjjiUS82',
  writer: 'gfRt6Z3Z8aTbpLfexQ7N',
  kai: 'jqcCZkN6Knx8BJ5TBdYR'
};

// Removed summarizeTask function - no longer needed

async function main() {
  // Get input
  let input = '';
  const decoder = new TextDecoder();
  const reader = Bun.stdin.stream().getReader();
  
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      input += decoder.decode(value, { stream: true });
    }
  } catch (e) {
    process.exit(0);
  }

  if (!input) process.exit(0);
  
  let transcriptPath;
  try {
    const parsed = JSON.parse(input);
    transcriptPath = parsed.transcript_path;
  } catch (e) {
    process.exit(0);
  }

  if (!transcriptPath) process.exit(0);

  // Read the transcript
  let transcript;
  try {
    transcript = readFileSync(transcriptPath, 'utf-8');
  } catch (e) {
    process.exit(0);
  }

  // Parse the JSON lines to find what happened in this session
  const lines = transcript.trim().split('\n');

  // First, check if the LAST assistant message contains a Task tool or a COMPLETED line
  let isAgentTask = false;
  let taskResult = '';
  let agentType = '';

  // Find the last assistant message
  for (let i = lines.length - 1; i >= 0; i--) {
    try {
      const entry = JSON.parse(lines[i]);

      if (entry.type === 'assistant' && entry.message?.content) {
        // Check if this assistant message contains a Task tool_use
        let foundTask = false;
        for (const content of entry.message.content) {
          if (content.type === 'tool_use' && content.name === 'Task') {
            // This is an agent task - find its result
            foundTask = true;
            agentType = content.input?.subagent_type || '';

            // Find the corresponding tool_result
            for (let j = i + 1; j < lines.length; j++) {
              const resultEntry = JSON.parse(lines[j]);
              if (resultEntry.type === 'user' && resultEntry.message?.content) {
                for (const resultContent of resultEntry.message.content) {
                  if (resultContent.type === 'tool_result' && resultContent.tool_use_id === content.id) {
                    taskResult = resultContent.content;
                    isAgentTask = true;
                    break;
                  }
                }
              }
              if (taskResult) break;
            }
            break;
          }
        }

        // We found the last assistant message, stop looking
        break;
      }
    } catch (e) {
      // Skip invalid JSON
    }
  }

  // Generate the announcement
  let message = '';
  let voiceId = VOICES.kai; // Default to Kai's voice

  if (isAgentTask && taskResult) {
    // AGENT DID THE TASK - Look for their COMPLETED line
    const completedMatch = taskResult.match(/🎯\s*COMPLETED:\s*(.+?)$/im);

    if (completedMatch) {
      // Get exactly what the agent said after COMPLETED:
      let completedText = completedMatch[1].trim();

      // Remove markdown formatting
      completedText = completedText
        .replace(/\*+/g, '')  // Remove asterisks
        .replace(/\[AGENT:\w+\]\s*/i, '') // Remove agent tags
        .trim();

      // Send exactly what was in the agent's COMPLETED line
      message = completedText;
      voiceId = VOICES[agentType.toLowerCase()] || VOICES.kai;

      console.error(`🎯 AGENT COMPLETION: ${message}`);
    }

  } else {
    // I (KAI) DID THE TASK - Look for my COMPLETED line
    const lastResponse = lines[lines.length - 1];
    try {
      const entry = JSON.parse(lastResponse);
      if (entry.type === 'assistant' && entry.message?.content) {
        const content = entry.message.content.map(c => c.text || '').join(' ');

        // Look for the COMPLETED line and extract EXACTLY what's after the colon
        const completedMatch = content.match(/🎯\s*COMPLETED:\s*(.+?)$/im);

        if (completedMatch) {
          // Get the raw text after the colon
          let completedText = completedMatch[1].trim();

          // Remove any markdown formatting but keep the actual message
          completedText = completedText
            .replace(/\*+/g, '')  // Remove asterisks
            .trim();

          // Send exactly what was in the COMPLETED line
          message = completedText;

          console.error(`🎯 KAI COMPLETION: ${message}`);
        } else {
          // No COMPLETED line found - don't send anything
          console.error('⚠️ No COMPLETED line found');
        }
      }
    } catch (e) {
      console.error('⚠️ Error parsing response:', e);
    }
  }

  if (message) {
    // Send to voice server
    await fetch('http://localhost:8888/notify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: message,  // Changed from 'text' to 'message' to match server expectation
        voice_id: voiceId  // Changed from 'voiceId' to 'voice_id' to match server expectation
      })
    }).catch(() => {});
  }
}

main().catch(() => {});