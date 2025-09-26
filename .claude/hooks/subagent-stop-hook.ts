#!/usr/bin/env bun

import { readFileSync, existsSync } from 'fs';

// Voice mappings for different agent types
const AGENT_VOICE_IDS: Record<string, string> = {
  researcher: 'AXdMgz6evoL7OPd7eU12',
  pentester: 'hmMWXCj9K7N5mCPcRkfC',
  engineer: 'kmSVBPu7loj4ayNinwWM',
  designer: 'ZF6FPAbjXT4488VcRRnw',
  architect: 'muZKMsIDGYtIkjjiUS82',
  writer: 'gfRt6Z3Z8aTbpLfexQ7N',
  assistant: 'jqcCZkN6Knx8BJ5TBdYR',  // Default assistant voice
  default: 'jqcCZkN6Knx8BJ5TBdYR'
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
    'completed your request',
    'the requested task'
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

async function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function findTaskResult(transcriptPath: string, maxAttempts: number = 10): Promise<{ result: string | null, agentType: string | null, userQuery: string | null }> {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    if (attempt > 0) {
      // Wait progressively longer between attempts
      await delay(100 * attempt);
    }

    if (!existsSync(transcriptPath)) {
      continue;
    }

    try {
      const transcript = readFileSync(transcriptPath, 'utf-8');
      const lines = transcript.trim().split('\n');

      // First, find the last user query
      let lastUserQuery = '';
      for (let i = lines.length - 1; i >= 0; i--) {
        try {
          const entry = JSON.parse(lines[i]);
          if (entry.type === 'user' && entry.message?.content) {
            // Extract text from user message
            const content = entry.message.content;
            if (typeof content === 'string') {
              lastUserQuery = content;
              break;
            } else if (Array.isArray(content)) {
              for (const item of content) {
                if (item.type === 'text' && item.text) {
                  lastUserQuery = item.text;
                  break;
                }
              }
              if (lastUserQuery) break;
            }
          }
        } catch (e) {
          // Skip invalid JSON
        }
      }

      // Search from the end of the transcript backwards for Task result
      for (let i = lines.length - 1; i >= 0; i--) {
        try {
          const entry = JSON.parse(lines[i]);

          // Look for assistant messages that contain Task tool_use
          if (entry.type === 'assistant' && entry.message?.content) {
            for (const content of entry.message.content) {
              if (content.type === 'tool_use' && content.name === 'Task') {
                // Found a Task invocation, now look for its result
                // The result should be in a subsequent user message
                for (let j = i + 1; j < lines.length; j++) {
                  const resultEntry = JSON.parse(lines[j]);
                  if (resultEntry.type === 'user' && resultEntry.message?.content) {
                    for (const resultContent of resultEntry.message.content) {
                      if (resultContent.type === 'tool_result' && resultContent.tool_use_id === content.id) {
                        // Found the matching Task result
                        const taskOutput = resultContent.content;

                        // Extract agent type from the input or output
                        let agentType = content.input?.subagent_type || 'default';
                        const agentMatch = taskOutput.match(/Sub-agent\s+(\w+)\s+completed/i);
                        if (agentMatch) {
                          agentType = agentMatch[1].toLowerCase();
                        }

                        return { result: taskOutput, agentType, userQuery: lastUserQuery };
                      }
                    }
                  }
                }
              }
            }
          }
        } catch (e) {
          // Invalid JSON line, skip
        }
      }
    } catch (e) {
      // Error reading file, will retry
    }
  }

  return { result: null, agentType: null, userQuery: null };
}

function extractCompletionMessage(taskOutput: string, userQuery: string | null): { message: string | null, agentType: string | null } {
  console.error('🔍 DEBUG - Extracting from task output, length:', taskOutput.length);
  console.error('🔍 DEBUG - First 200 chars:', taskOutput.substring(0, 200));
  console.error('🔍 DEBUG - Last 200 chars:', taskOutput.substring(taskOutput.length - 200));

  // First, check for CUSTOM COMPLETED line (voice-optimized)
  const customCompletedMatch = taskOutput.match(/🗣️\s*CUSTOM\s+COMPLETED:\s*(.+?)(?:\n|$)/im);

  if (customCompletedMatch) {
    // Get the custom voice response
    let customText = customCompletedMatch[1].trim()
      .replace(/\[.*?\]/g, '') // Remove bracketed text like [Optional: ...]
      .replace(/\*+/g, '') // Remove asterisks
      .replace(/\[AGENT:\w+\]\s*/i, '') // Remove agent tags
      .trim();

    // Use custom completed if it's under 8 words
    const wordCount = customText.split(/\s+/).length;
    if (customText && wordCount <= 8) {
      // Try to extract agent type from context
      let agentType = null;
      const agentMatch = taskOutput.match(/\[AGENT:(\w+)\]/i);
      if (agentMatch) {
        agentType = agentMatch[1].toLowerCase();
      }

      console.error(`🗣️ FOUND CUSTOM COMPLETED: ${customText}`);
      return { message: customText, agentType };
    }
  }

  // Look for the COMPLETED section in the agent's output
  // Priority is given to [AGENT:type] format
  const agentPatterns = [
    /🎯\s*COMPLETED:\s*\[AGENT:(\w+)\]\s*(.+?)(?:\n|$)/is,
    /COMPLETED:\s*\[AGENT:(\w+)\]\s*(.+?)(?:\n|$)/is,
    /\[AGENT:(\w+)\]\s*I\s+completed\s+(.+?)(?:\.|!|\n|$)/is,
    // New pattern for our current format
    /🎯.*COMPLETED.*\[AGENT:(\w+)\]\s*I\s+completed\s+(.+?)(?:\n|$)/is
  ];

  // First try to match agent-specific patterns
  for (const pattern of agentPatterns) {
    const match = taskOutput.match(pattern);
    if (match && match[1]) {
      const agentType = match[1].toLowerCase();
      let message = match[2] || (match[0].split('COMPLETED:')[1] || '').trim();

      // Clean up the message
      message = message
        .replace(/\*+/g, '')
        .replace(/\[AGENT:\w+\]\s*/i, '')
        .replace(/\s+/g, ' ')
        .trim();

      // Use intelligent response if we have the user query
      if (userQuery) {
        message = generateIntelligentResponse(userQuery, taskOutput, message);
      }

      console.error(`✅ FOUND AGENT MATCH: [${agentType}] ${message}`);

      // Return agent type and message
      return { message, agentType };
    }
  }

  // Fall back to generic patterns
  const genericPatterns = [
    /🎯\s*COMPLETED:\s*(.+?)(?:\n|$)/i,
    /COMPLETED:\s*(.+?)(?:\n|$)/i,
    /Sub-agent\s+\w+\s+completed\s+(.+?)(?:\.|!|\n|$)/i,
    /Agent\s+completed\s+(.+?)(?:\.|!|\n|$)/i
  ];

  for (const pattern of genericPatterns) {
    const match = taskOutput.match(pattern);
    if (match && match[1]) {
      let message = match[1].trim();

      // Clean up the message
      message = message
        .replace(/^(the\s+)?requested\s+task$/i, '')
        .replace(/\*+/g, '')
        .replace(/\[AGENT:\w+\]\s*/i, '')
        .replace(/\s+/g, ' ')
        .trim();

      // Use intelligent response if we have the user query
      if (userQuery && message) {
        message = generateIntelligentResponse(userQuery, taskOutput, message);
      }

      // Only return if it's not a generic message
      if (message &&
          !message.match(/^(the\s+)?requested\s+task$/i) &&
          !message.match(/^task$/i) &&
          message.length > 5) {
        return { message, agentType: null };
      }
    }
  }

  return { message: null, agentType: null };
}

async function main() {
  console.error('🔍 SubagentStop hook started');
  // Read input from stdin with timeout
  let input = '';
  try {
    const decoder = new TextDecoder();
    const reader = Bun.stdin.stream().getReader();

    const timeoutPromise = new Promise<void>((resolve) => {
      setTimeout(() => resolve(), 500);
    });

    const readPromise = (async () => {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        input += decoder.decode(value, { stream: true });
      }
    })();

    await Promise.race([readPromise, timeoutPromise]);
  } catch (e) {
    console.error('Failed to read input:', e);
    process.exit(0);
  }

  if (!input) {
    console.log('No input received');
    process.exit(0);
  }

  let transcriptPath: string;
  try {
    const parsed = JSON.parse(input);
    transcriptPath = parsed.transcript_path;
  } catch (e) {
    console.error('Invalid input JSON:', e);
    process.exit(0);
  }

  if (!transcriptPath) {
    console.log('No transcript path provided');
    process.exit(0);
  }

  // Wait for and find the Task result
  const { result: taskOutput, agentType, userQuery } = await findTaskResult(transcriptPath);

  if (!taskOutput) {
    console.log('No Task result found in transcript after waiting');
    process.exit(0);
  }

  // Extract the completion message and agent type
  const { message: completionMessage, agentType: extractedAgentType } = extractCompletionMessage(taskOutput, userQuery);

  if (!completionMessage) {
    console.log('No specific completion message found in Task output');
    process.exit(0);
  }

  // Use extracted agent type if available, otherwise use the one from task analysis
  const finalAgentType = extractedAgentType || agentType || 'default';
  const agentName = finalAgentType.charAt(0).toUpperCase() + finalAgentType.slice(1);

  // Send to notification server
  try {
    await fetch('http://localhost:8888/notify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: `${agentName} Agent`,
        message: completionMessage,
        voice_enabled: true,
        agent_type: finalAgentType,
        voice_id: AGENT_VOICE_IDS[finalAgentType] || AGENT_VOICE_IDS.default
      })
    });

    console.log(`✅ Sent: [${agentName}] ${completionMessage}`);
  } catch (e) {
    console.error('Failed to send notification:', e);
  }
}

main().catch(console.error);