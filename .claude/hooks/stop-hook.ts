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

function summarizeTask(description: string, content: string): string {
  // Look at the task description and content to create a 6-word summary
  const words = [];
  
  // Extract key terms from description
  if (description) {
    const descWords = description.toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(w => w.length > 2 && !['the', 'and', 'for', 'with', 'task', 'test'].includes(w));
    words.push(...descWords.slice(0, 3));
  }
  
  // Extract key terms from content
  if (content) {
    const contentWords = content.toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(w => w.length > 3 && !['completed', 'task', 'test', 'analysis', 'system'].includes(w));
    words.push(...contentWords.slice(0, 3));
  }
  
  // Take first 6 unique words
  const uniqueWords = [...new Set(words)].slice(0, 6);
  return uniqueWords.join(' ');
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

  // Parse the JSON lines to find the last Task tool usage
  const lines = transcript.trim().split('\n');
  let taskDescription = '';
  let taskResult = '';
  let agentType = '';
  
  // Look for Task tool usage and result
  for (let i = lines.length - 1; i >= 0; i--) {
    try {
      const entry = JSON.parse(lines[i]);
      
      // Look for Task tool_use
      if (entry.type === 'assistant' && entry.message?.content) {
        for (const content of entry.message.content) {
          if (content.type === 'tool_use' && content.name === 'Task') {
            taskDescription = content.input?.description || '';
            agentType = content.input?.subagent_type || '';
            
            // Find the corresponding tool_result
            for (let j = i + 1; j < lines.length; j++) {
              const resultEntry = JSON.parse(lines[j]);
              if (resultEntry.type === 'user' && resultEntry.message?.content) {
                for (const resultContent of resultEntry.message.content) {
                  if (resultContent.type === 'tool_result' && resultContent.tool_use_id === content.id) {
                    taskResult = resultContent.content;
                    break;
                  }
                }
              }
              if (taskResult) break;
            }
            break;
          }
        }
      }
      if (taskDescription && taskResult) break;
    } catch (e) {
      // Skip invalid JSON
    }
  }

  // Generate the announcement
  let message = '';
  let voiceId = VOICES.kai; // Default to Kai's voice
  
  if (agentType && taskResult) {
    // AGENT DID THE TASK - Look for [AGENT:type] I completed something
    const agentMatch = taskResult.match(/\[AGENT:(\w+)\]\s*I\s+completed\s+(.+?)(?:\n|$)/is);
    
    if (agentMatch) {
      const agentType = agentMatch[1].toLowerCase();
      let completedText = agentMatch[2].trim();
      
      // Clean up but keep the full completion message
      completedText = completedText.replace(/[^\w\s+]/g, ' ').replace(/\s+/g, ' ').trim();
      
      const agentName = agentType.charAt(0).toUpperCase() + agentType.slice(1);
      message = `${agentName} completed ${completedText}`;
      voiceId = VOICES[agentType] || VOICES.kai;
      
      console.error(`🎯 AGENT COMPLETION: ${message}`);
    } else {
      // Fallback to old method if no proper completion found
      const summary = summarizeTask(taskDescription, taskResult);
      const agentName = agentType.charAt(0).toUpperCase() + agentType.slice(1);
      message = `${agentName} completed ${summary}`;
      voiceId = VOICES[agentType] || VOICES.kai;
      
      console.error(`🎯 AGENT COMPLETION (fallback): ${message}`);
    }
    
  } else {
    // I (KAI) DID THE TASK - Look for my COMPLETED line
    const lastResponse = lines[lines.length - 1];
    try {
      const entry = JSON.parse(lastResponse);
      if (entry.type === 'assistant' && entry.message?.content) {
        const content = entry.message.content.map(c => c.text || '').join(' ');
        
        console.error(`🔍 KAI CONTENT: "${content.substring(0, 200)}..."`);
        
        // Look for the COMPLETED line - multiple patterns
        const completedPatterns = [
          /🎯\s*COMPLETED:\s*(.+?)(?:\n|$)/i,
          /\*\*🎯\s*COMPLETED:\*\*\s*(.+?)(?:\n|$)/i,
          /COMPLETED:\s*(.+?)(?:\n|$)/i
        ];
        
        let completedMatch = null;
        for (const pattern of completedPatterns) {
          completedMatch = content.match(pattern);
          if (completedMatch) break;
        }
        
        if (completedMatch) {
          let completedText = completedMatch[1].trim();
          
          // The COMPLETED line is already a perfect summary - use it entirely
          // Just clean up any weird characters but keep the full message
          completedText = completedText.replace(/[^\w\s+]/g, ' ').replace(/\s+/g, ' ').trim();
          
          message = completedText;
          
          console.error(`🎯 KAI COMPLETION: ${message}`);
        } else {
          message = 'Kai completed task';
        }
      }
    } catch (e) {
      message = 'Kai completed task';
    }
  }

  if (message) {
    // Send to voice server
    await fetch('http://localhost:8888/notify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: message,
        voice_id: voiceId,
        voice_enabled: true
      })
    }).catch(() => {});
  }
}

main().catch(() => {});