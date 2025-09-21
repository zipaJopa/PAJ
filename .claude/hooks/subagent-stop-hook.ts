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
  kai: 'jqcCZkN6Knx8BJ5TBdYR',
  default: 'jqcCZkN6Knx8BJ5TBdYR'
};

async function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function findTaskResult(transcriptPath: string, maxAttempts: number = 10): Promise<{ result: string | null, agentType: string | null }> {
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
      
      // Search from the end of the transcript backwards
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
                        
                        // Extract agent type from the output
                        let agentType = 'default';
                        const agentMatch = taskOutput.match(/Sub-agent\s+(\w+)\s+completed/i);
                        if (agentMatch) {
                          agentType = agentMatch[1].toLowerCase();
                        }
                        
                        return { result: taskOutput, agentType };
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
  
  return { result: null, agentType: null };
}

function extractCompletionMessage(taskOutput: string): { message: string | null, agentType: string | null } {
  console.error('🔍 DEBUG - Extracting from task output, length:', taskOutput.length);
  console.error('🔍 DEBUG - First 200 chars:', taskOutput.substring(0, 200));
  console.error('🔍 DEBUG - Last 200 chars:', taskOutput.substring(taskOutput.length - 200));
  
  // Look for the COMPLETED section in the agent's output
  // Priority is given to [AGENT:type] format
  const agentPatterns = [
    /🎯\s*COMPLETED:\s*\[AGENT:(\w+)\]\s*I\s+completed\s+(.+?)(?:\n|$)/is,
    /COMPLETED:\s*\[AGENT:(\w+)\]\s*I\s+completed\s+(.+?)(?:\n|$)/is,
    /\[AGENT:(\w+)\]\s*I\s+completed\s+(.+?)(?:\.|!|\n|$)/is,
    // New pattern for our current format
    /🎯.*COMPLETED.*\[AGENT:(\w+)\]\s*I\s+completed\s+(.+?)(?:\n|$)/is
  ];
  
  // First try to match agent-specific patterns
  for (const pattern of agentPatterns) {
    const match = taskOutput.match(pattern);
    if (match && match[1] && match[2]) {
      const agentType = match[1].toLowerCase();
      let message = match[2].trim();
      
      // Clean up the message
      message = message.replace(/\*+/g, '');
      message = message.replace(/\s+/g, ' ');
      
      // Prepend agent name for spoken message
      const agentName = agentType.charAt(0).toUpperCase() + agentType.slice(1);
      const fullMessage = `${agentName} completed ${message}`;
      
      console.error(`✅ FOUND AGENT MATCH: [${agentType}] ${fullMessage}`);
      
      // Return agent type and message
      return { message: fullMessage, agentType };
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
      message = message.replace(/^(the\s+)?requested\s+task$/i, '');
      message = message.replace(/\*+/g, '');
      message = message.replace(/\s+/g, ' ');
      
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
  const { result: taskOutput, agentType } = await findTaskResult(transcriptPath);
  
  if (!taskOutput) {
    console.log('No Task result found in transcript after waiting');
    process.exit(0);
  }
  
  // Extract the completion message and agent type
  const { message: completionMessage, agentType: extractedAgentType } = extractCompletionMessage(taskOutput);
  
  if (!completionMessage) {
    console.log('No specific completion message found in Task output');
    process.exit(0);
  }
  
  // Use extracted agent type if available, otherwise use the one from task analysis
  const finalAgentType = extractedAgentType || agentType || 'default';
  
  // Prepare the notification
  const fullMessage = completionMessage; // Message is already prepared with agent name
  const agentName = finalAgentType.charAt(0).toUpperCase() + finalAgentType.slice(1);
  
  // Send to notification server
  try {
    await fetch('http://localhost:8888/notify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: `${agentName} Agent`,
        message: fullMessage,
        voice_enabled: true,
        agent_type: finalAgentType,
        voice_id: AGENT_VOICE_IDS[finalAgentType] || AGENT_VOICE_IDS.default
      })
    });
    
    console.log(`✅ Sent: [${agentName}] ${fullMessage}`);
  } catch (e) {
    console.error('Failed to send notification:', e);
  }
}

main().catch(console.error);