#!/usr/bin/env bun
/**
 * PAIVoice - Personal AI Voice notification server for macOS with native voices
 */

import { serve } from "bun";
import { spawn } from "child_process";
import { homedir } from "os";
import { join } from "path";
import { existsSync } from "fs";

// Load .env from user home directory (optional, for future use)
const envPath = join(homedir(), '.env');
if (existsSync(envPath)) {
  const envContent = await Bun.file(envPath).text();
  envContent.split('\n').forEach(line => {
    const [key, value] = line.split('=');
    if (key && value && !key.startsWith('#')) {
      process.env[key.trim()] = value.trim();
    }
  });
}

const PORT = parseInt(process.env.PORT || "8888");

// macOS Voice configuration
// Jamie (Premium) is Kai's voice - UK Male, professional and conversational
const DEFAULT_VOICE = "Jamie (Premium)";

// Sanitize input for shell commands
function sanitizeForShell(input: string): string {
  // Remove any characters that could be used for command injection
  // Allow only alphanumeric, spaces, and basic punctuation
  return input.replace(/[^a-zA-Z0-9\s.,!?\-']/g, '').trim().substring(0, 500);
}

// Validate and sanitize user input
function validateInput(input: any): { valid: boolean; error?: string } {
  if (!input || typeof input !== 'string') {
    return { valid: false, error: 'Invalid input type' };
  }
  
  // Limit message length
  if (input.length > 500) {
    return { valid: false, error: 'Message too long (max 500 characters)' };
  }
  
  // Check for potentially malicious patterns
  const dangerousPatterns = [
    /[;&|><`\$\(\)\{\}\[\]\\]/,  // Shell metacharacters
    /\.\.\//,  // Path traversal
    /<script/i,  // Script injection
  ];
  
  for (const pattern of dangerousPatterns) {
    if (pattern.test(input)) {
      return { valid: false, error: 'Invalid characters in input' };
    }
  }
  
  return { valid: true };
}

// Speak using native macOS say command
async function speak(text: string, voiceName: string | null = null, rate: number | null = null): Promise<void> {
  const voice = voiceName || DEFAULT_VOICE;
  const speechRate = rate || 175; // Default macOS rate is ~175 wpm

  return new Promise((resolve, reject) => {
    // Build args: if voice is null, don't include -v flag (uses system default)
    // Always include rate for speed control
    const args = [];
    if (voice) {
      args.push('-v', voice);
    }
    args.push('-r', speechRate.toString(), text);

    const proc = spawn('/usr/bin/say', args);

    proc.on('error', (error) => {
      console.error(`Error speaking with voice ${voice || 'system default'} at rate ${speechRate}:`, error);
      reject(error);
    });

    proc.on('exit', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`say command exited with code ${code}`));
      }
    });
  });
}

// Spawn a process safely
function spawnSafe(command: string, args: string[]): Promise<void> {
  return new Promise((resolve, reject) => {
    const proc = spawn(command, args);
    
    proc.on('error', (error) => {
      console.error(`Error spawning ${command}:`, error);
      reject(error);
    });
    
    proc.on('exit', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`${command} exited with code ${code}`));
      }
    });
  });
}

// Send macOS notification with voice
async function sendNotification(title: string, message: string, voiceEnabled = true, voiceName: string | null = null, rate: number | null = null) {
  // Validate inputs
  const titleValidation = validateInput(title);
  const messageValidation = validateInput(message);

  if (!titleValidation.valid) {
    throw new Error(`Invalid title: ${titleValidation.error}`);
  }

  if (!messageValidation.valid) {
    throw new Error(`Invalid message: ${messageValidation.error}`);
  }

  // Sanitize inputs for shell commands
  const safeTitle = sanitizeForShell(title);
  const safeMessage = sanitizeForShell(message);

  if (voiceEnabled) {
    try {
      await speak(safeMessage, voiceName, rate);
    } catch (error) {
      console.error("Failed to speak message:", error);
    }
  }

  // Use spawn for osascript with proper escaping
  try {
    const script = `display notification "${safeMessage}" with title "${safeTitle}" sound name ""`;
    await spawnSafe('/usr/bin/osascript', ['-e', script]);
  } catch (error) {
    console.error("Notification display error:", error);
  }
}

// Rate limiting
const requestCounts = new Map<string, { count: number; resetTime: number }>();
const RATE_LIMIT = 10; // 10 requests per minute
const RATE_WINDOW = 60000; // 1 minute in milliseconds

function checkRateLimit(ip: string): boolean {
  const now = Date.now();
  const record = requestCounts.get(ip);
  
  if (!record || now > record.resetTime) {
    requestCounts.set(ip, { count: 1, resetTime: now + RATE_WINDOW });
    return true;
  }
  
  if (record.count >= RATE_LIMIT) {
    return false;
  }
  
  record.count++;
  return true;
}

// Start HTTP server
const server = serve({
  port: PORT,
  async fetch(req) {
    const url = new URL(req.url);
    
    // Get client IP for rate limiting (localhost only)
    const clientIp = req.headers.get('x-forwarded-for') || 'localhost';
    
    // Restrict CORS to localhost only for security
    const corsHeaders = {
      "Access-Control-Allow-Origin": "http://localhost",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type"
    };
    
    if (req.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders, status: 204 });
    }
    
    // Check rate limit
    if (!checkRateLimit(clientIp)) {
      return new Response(
        JSON.stringify({ status: "error", message: "Rate limit exceeded" }),
        { 
          headers: { ...corsHeaders, "Content-Type": "application/json" },
          status: 429 
        }
      );
    }
    
    if (url.pathname === "/notify" && req.method === "POST") {
      try {
        const data = await req.json();
        const title = data.title || "PAI Notification";
        const message = data.message || "Task completed";
        const voiceEnabled = data.voice_enabled !== false;
        const voiceName = data.voice_name || data.voice_id || null; // Support both voice_name and legacy voice_id
        const rate = data.rate || null; // Speech rate in words per minute

        // Validate voice name if provided
        if (voiceName && typeof voiceName !== 'string') {
          throw new Error('Invalid voice_name');
        }

        // Validate rate if provided
        if (rate && (typeof rate !== 'number' || rate < 100 || rate > 500)) {
          throw new Error('Invalid rate: must be between 100-500 wpm');
        }

        console.log(`📨 Received notification: "${title}" - "${message}" (voice: ${voiceEnabled}, voiceName: ${voiceName}, rate: ${rate})`);

        await sendNotification(title, message, voiceEnabled, voiceName, rate);

        return new Response(
          JSON.stringify({ status: "success", message: "Notification sent" }),
          {
            headers: { ...corsHeaders, "Content-Type": "application/json" },
            status: 200
          }
        );
      } catch (error: any) {
        console.error("Notification error:", error);
        return new Response(
          JSON.stringify({ status: "error", message: error.message || "Internal server error" }),
          {
            headers: { ...corsHeaders, "Content-Type": "application/json" },
            status: error.message?.includes('Invalid') ? 400 : 500
          }
        );
      }
    }
    
    if (url.pathname === "/pai" && req.method === "POST") {
      try {
        const data = await req.json();
        const title = data.title || "PAI Assistant";
        const message = data.message || "Task completed";
        
        console.log(`🤖 PAI notification: "${title}" - "${message}"`);
        
        await sendNotification(title, message, true, null);
        
        return new Response(
          JSON.stringify({ status: "success", message: "PAI notification sent" }),
          { 
            headers: { ...corsHeaders, "Content-Type": "application/json" },
            status: 200 
          }
        );
      } catch (error: any) {
        console.error("PAI notification error:", error);
        return new Response(
          JSON.stringify({ status: "error", message: error.message || "Internal server error" }),
          { 
            headers: { ...corsHeaders, "Content-Type": "application/json" },
            status: error.message?.includes('Invalid') ? 400 : 500 
          }
        );
      }
    }
    
    if (url.pathname === "/health") {
      return new Response(
        JSON.stringify({ status: "healthy", port: PORT, voice_system: "macOS Native", default_voice: DEFAULT_VOICE || "System Default" }),
        {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
          status: 200
        }
      );
    }

    return new Response("PAIVoice Server - POST to /notify or /pai", {
      headers: corsHeaders,
      status: 200
    });
  },
});

console.log(`🚀 PAIVoice Server running on port ${PORT}`);
console.log(`🎙️  Using macOS native voices (default: ${DEFAULT_VOICE || "System Default - Highest Quality"})`);
console.log(`📡 POST to http://localhost:${PORT}/notify`);
console.log(`🔒 Security: CORS restricted to localhost, rate limiting enabled`);