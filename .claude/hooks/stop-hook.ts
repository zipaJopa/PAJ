#!/usr/bin/env bun

import { readFileSync } from 'fs';

/**
 * Generate 3-word tab title from user prompt
 */
function generateTabTitle(prompt: string): string {
  // Clean the prompt and extract meaningful words
  const cleanPrompt = prompt.replace(/[^\w\s]/g, ' ').trim();
  const words = cleanPrompt.split(/\s+/).filter(word =>
    word.length > 2 &&
    !['the', 'and', 'but', 'for', 'are', 'with', 'his', 'her', 'this', 'that', 'you', 'can', 'will', 'have', 'been', 'your', 'from', 'they', 'were', 'said', 'what', 'them', 'just', 'told', 'how', 'does', 'into', 'about'].includes(word.toLowerCase())
  );

  const lowerPrompt = prompt.toLowerCase();

  // Find action verb if present
  const actionVerbs = ['test', 'rename', 'fix', 'debug', 'research', 'write', 'create', 'make', 'build', 'implement', 'analyze', 'review', 'update', 'modify', 'generate', 'develop', 'design', 'deploy', 'configure', 'setup', 'install', 'remove', 'delete', 'add', 'check', 'verify', 'validate', 'optimize', 'refactor', 'enhance', 'improve', 'send', 'email', 'help'];

  let titleWords = [];

  // Check for action verb
  for (const verb of actionVerbs) {
    if (lowerPrompt.includes(verb)) {
      titleWords.push(verb.charAt(0).toUpperCase() + verb.slice(1));
      break;
    }
  }

  // Add most meaningful remaining words
  const remainingWords = words
    .filter(word => !actionVerbs.includes(word.toLowerCase()))
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase());

  // Fill up to 3 words total
  for (const word of remainingWords) {
    if (titleWords.length < 3) {
      titleWords.push(word);
    } else {
      break;
    }
  }

  // If we don't have enough words, add generic ones
  if (titleWords.length === 0) {
    titleWords.push('Assistant');
  }
  if (titleWords.length === 1) {
    titleWords.push('Task');
  }
  if (titleWords.length === 2) {
    titleWords.push('Complete');
  }

  return titleWords.slice(0, 3).join(' ');
}

/**
 * Set Kitty terminal tab title
 */
function setKittyTabTitle(title: string): void {
  // Use OSC escape sequence to set tab/window title with checkmark
  process.stdout.write(`\x1b]0;✓ ${title}\x07`);
}

// Simple voice mappings
const VOICES = {
  researcher: 'AXdMgz6evoL7OPd7eU12',
  pentester: 'hmMWXCj9K7N5mCPcRkfC',
  engineer: 'kmSVBPu7loj4ayNinwWM',
  designer: 'ZF6FPAbjXT4488VcRRnw',
  architect: 'muZKMsIDGYtIkjjiUS82',
  writer: 'gfRt6Z3Z8aTbpLfexQ7N',
  assistant: 'jqcCZkN6Knx8BJ5TBdYR'  // Default assistant voice
};

// Intelligent response generator - prioritizes custom COMPLETED messages
function generateIntelligentResponse(userQuery: string, assistantResponse: string, completedLine: string): string {
  // Clean the completed line
  const cleanCompleted = completedLine
    .replace(/\*+/g, '')
    .replace(/\[AGENT:\w+\]\s*/i, '')
    .trim();

  // If the completed line has meaningful custom content (not generic), use it
  const genericPhrases = [
    'completed successfully',
    'task completed',
    'done successfully',
    'finished successfully',
    'completed the task',
    'completed your request'
  ];

  const isGenericCompleted = genericPhrases.some(phrase =>
    cleanCompleted.toLowerCase() === phrase ||
    cleanCompleted.toLowerCase() === `${phrase}.`
  );

  // If we have a custom, non-generic completed message, prefer it
  if (!isGenericCompleted && cleanCompleted.length > 10) {
    return cleanCompleted;
  }

  // Extract key information from the full response
  const responseLC = assistantResponse.toLowerCase();
  const queryLC = userQuery.toLowerCase();

  // Only apply shortcuts for very specific simple cases

  // Simple thanks acknowledgment - high priority
  if (queryLC.match(/^(thank|thanks|awesome|great|good job|well done)[\s!?.]*$/i)) {
    return "You're welcome!";
  }

  // Simple math calculations - ONLY if it's just a calculation
  if (queryLC.match(/^\s*\d+\s*[\+\-\*\/]\s*\d+\s*\??$/)) {
    const resultMatch = assistantResponse.match(/=\s*(-?\d+(?:\.\d+)?)|(?:equals?|is)\s+(-?\d+(?:\.\d+)?)/i);
    if (resultMatch) {
      return resultMatch[1] || resultMatch[2];
    }
  }

  // Very simple yes/no - ONLY if the query is extremely simple
  if (queryLC.match(/^(is|are|was|were)\s+\w+\s+\w+\??$/i)) {
    if (cleanCompleted.toLowerCase() === 'yes' || cleanCompleted.toLowerCase() === 'no') {
      return cleanCompleted;
    }
  }

  // Simple time query - ONLY if asking for just the time
  if (queryLC.match(/^what\s+time\s+is\s+it\??$/i)) {
    const timeMatch = assistantResponse.match(/\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?/i);
    if (timeMatch) {
      return timeMatch[0];
    }
  }

  // For all other cases, use the actual completed message
  // This ensures custom messages are preserved
  return cleanCompleted;
}

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

  // Get the last user query for context
  let lastUserQuery = '';
  for (let i = lines.length - 1; i >= 0; i--) {
    try {
      const entry = JSON.parse(lines[i]);
      if (entry.type === 'user' && entry.message?.content) {
        // Extract text from user message
        const content = entry.message.content;
        if (typeof content === 'string') {
          lastUserQuery = content;
        } else if (Array.isArray(content)) {
          for (const item of content) {
            if (item.type === 'text' && item.text) {
              lastUserQuery = item.text;
              break;
            }
          }
        }
        if (lastUserQuery) break;
      }
    } catch (e) {
      // Skip invalid JSON
    }
  }

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
  let voiceId = VOICES.assistant; // Default to assistant's voice

  if (isAgentTask && taskResult) {
    // AGENT DID THE TASK - Look for their CUSTOM COMPLETED or COMPLETED line

    // First, try to find CUSTOM COMPLETED line
    const customCompletedMatch = taskResult.match(/🗣️\s*CUSTOM\s+COMPLETED:\s*(.+?)(?:\n|$)/im);

    if (customCompletedMatch) {
      // Get the custom voice response
      let customText = customCompletedMatch[1].trim()
        .replace(/\[.*?\]/g, '') // Remove bracketed text
        .replace(/\*+/g, '') // Remove asterisks
        .replace(/\[AGENT:\w+\]\s*/i, '') // Remove agent tags
        .trim();

      // Use custom completed if it's under 8 words
      const wordCount = customText.split(/\s+/).length;
      if (customText && wordCount <= 8) {
        message = customText;
        voiceId = VOICES[agentType.toLowerCase()] || VOICES.assistant;
        console.error(`🗣️ AGENT CUSTOM VOICE: ${message}`);
      } else {
        // Custom completed too long, fall back to regular COMPLETED
        const completedMatch = taskResult.match(/🎯\s*COMPLETED:\s*(.+?)$/im);
        if (completedMatch) {
          let completedText = completedMatch[1].trim()
            .replace(/\*+/g, '')
            .replace(/\[AGENT:\w+\]\s*/i, '')
            .trim();
          message = generateIntelligentResponse(lastUserQuery, taskResult, completedText);
          voiceId = VOICES[agentType.toLowerCase()] || VOICES.assistant;
          console.error(`🎯 AGENT FALLBACK (custom too long): ${message}`);
        }
      }
    } else {
      // No CUSTOM COMPLETED, look for regular COMPLETED line
      const completedMatch = taskResult.match(/🎯\s*COMPLETED:\s*(.+?)$/im);

      if (completedMatch) {
        // Get exactly what the agent said after COMPLETED:
        let completedText = completedMatch[1].trim();

        // Remove markdown formatting
        completedText = completedText
          .replace(/\*+/g, '')  // Remove asterisks
          .replace(/\[AGENT:\w+\]\s*/i, '') // Remove agent tags
          .trim();

        // Generate intelligent response for agent tasks
        message = generateIntelligentResponse(lastUserQuery, taskResult, completedText);
        voiceId = VOICES[agentType.toLowerCase()] || VOICES.assistant;

        console.error(`🎯 AGENT INTELLIGENT: ${message}`);
      }
    }

  } else {
    // I (ASSISTANT) DID THE TASK - Look for my CUSTOM COMPLETED or COMPLETED line
    const lastResponse = lines[lines.length - 1];
    try {
      const entry = JSON.parse(lastResponse);
      if (entry.type === 'assistant' && entry.message?.content) {
        const content = entry.message.content.map(c => c.text || '').join(' ');

        // First, look for CUSTOM COMPLETED line (voice-optimized)
        const customCompletedMatch = content.match(/🗣️\s*CUSTOM\s+COMPLETED:\s*(.+?)(?:\n|$)/im);

        if (customCompletedMatch) {
          // Get the custom voice response
          let customText = customCompletedMatch[1].trim()
            .replace(/\[.*?\]/g, '') // Remove bracketed text like [Optional: ...]
            .replace(/\*+/g, '') // Remove asterisks
            .trim();

          // Use custom completed if it's under 8 words
          const wordCount = customText.split(/\s+/).length;
          if (customText && wordCount <= 8) {
            message = customText;
            console.error(`🗣️ CUSTOM VOICE: ${message}`);
          } else {
            // Custom completed too long, fall back to regular COMPLETED
            const completedMatch = content.match(/🎯\s*COMPLETED:\s*(.+?)(?:\n|$)/im);
            if (completedMatch) {
              let completedText = completedMatch[1].trim();
              message = generateIntelligentResponse(lastUserQuery, content, completedText);
              console.error(`🎯 ASSISTANT FALLBACK (custom too long): ${message}`);
            }
          }
        } else {
          // No CUSTOM COMPLETED, look for regular COMPLETED line
          const completedMatch = content.match(/🎯\s*COMPLETED:\s*(.+?)(?:\n|$)/im);

          if (completedMatch) {
            // Get the raw text after the colon
            let completedText = completedMatch[1].trim();

            // Generate intelligent response
            message = generateIntelligentResponse(lastUserQuery, content, completedText);

            console.error(`🎯 ASSISTANT INTELLIGENT: ${message}`);
          } else {
            // No COMPLETED line found - don't send anything
            console.error('⚠️ No COMPLETED line found');
          }
        }
      }
    } catch (e) {
      console.error('⚠️ Error parsing response:', e);
    }
  }

  // Set the Kitty tab title based on the user query
  if (lastUserQuery) {
    const tabTitle = generateTabTitle(lastUserQuery);
    setKittyTabTitle(tabTitle);
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