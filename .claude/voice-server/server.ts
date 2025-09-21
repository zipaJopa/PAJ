#!/usr/bin/env bun
/**
 * PAIVoice - Personal AI Voice notification server for macOS with ElevenLabs
 */

import { serve } from "bun";
import { spawn } from "child_process";
import { writeFile, unlink } from "fs/promises";
import { tmpdir } from "os";
import { join } from "path";
import { homedir } from "os";
import { existsSync } from "fs";

// Load .env from user home directory
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

// ElevenLabs configuration - MUST be set in ~/.env
const ELEVENLABS_API_KEY = process.env.ELEVENLABS_API_KEY;
const ELEVENLABS_VOICE_ID = process.env.ELEVENLABS_VOICE_ID || process.env.DEFAULT_VOICE_ID || "jqcCZkN6Knx8BJ5TBdYR";

if (!ELEVENLABS_API_KEY) {
  console.error("⚠️  Warning: ELEVENLABS_API_KEY not found in ~/.env");
  console.error("   Voice features will fall back to macOS 'say' command");
  console.error("   To enable ElevenLabs voices, add to ~/.env:");
  console.error("   ELEVENLABS_API_KEY=your_api_key_here");
}

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

// Generate voice using ElevenLabs
async function generateVoice(text: string, voiceId: string | null = null): Promise<string | null> {
  // If no API key, return null to trigger fallback
  if (!ELEVENLABS_API_KEY) {
    return null;
  }
  
  const voiceToUse = voiceId || ELEVENLABS_VOICE_ID;
  
  try {
    const response = await fetch(
      `https://api.elevenlabs.io/v1/text-to-speech/${voiceToUse}`,
      {
        method: "POST",
        headers: {
          "Accept": "audio/mpeg",
          "Content-Type": "application/json",
          "xi-api-key": ELEVENLABS_API_KEY
        },
        body: JSON.stringify({
          text,
          model_id: "eleven_turbo_v2_5",
          voice_settings: {
            stability: 0.75,
            similarity_boost: 0.75,
            style: 0.5,
            use_speaker_boost: true
          }
        })
      }
    );

    if (!response.ok) {
      console.error(`ElevenLabs API error: ${response.status}`);
      return null;
    }

    const audioBuffer = await response.arrayBuffer();
    const tempFile = join(tmpdir(), `kainotify-${Date.now()}.mp3`);
    await writeFile(tempFile, Buffer.from(audioBuffer));
    
    return tempFile;
  } catch (error) {
    console.error("ElevenLabs error:", error);
    return null;
  }
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
async function sendNotification(title: string, message: string, voiceEnabled = true, voiceId: string | null = null) {
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
    const audioFile = await generateVoice(safeMessage, voiceId);
    
    if (audioFile) {
      // Use spawn for safer audio playback
      try {
        await spawnSafe('/usr/bin/afplay', [audioFile]);
        await unlink(audioFile).catch(() => {});
      } catch (error) {
        console.error("Failed to play ElevenLabs audio:", error);
        // Fallback to say command
        try {
          await spawnSafe('/usr/bin/say', [safeMessage]);
        } catch (e) {
          console.error("Failed to speak message:", e);
        }
      }
    } else {
      // Use spawn for say command
      try {
        await spawnSafe('say', [safeMessage]);
      } catch (error) {
        console.error("Say command error:", error);
      }
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
        const voiceId = data.voice_id || null;
        
        // Validate voice ID if provided
        if (voiceId && typeof voiceId !== 'string') {
          throw new Error('Invalid voice_id');
        }
        
        console.log(`📨 Received notification: "${title}" - "${message}" (voice: ${voiceEnabled}, voiceId: ${voiceId})`);
        
        await sendNotification(title, message, voiceEnabled, voiceId);
        
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
        JSON.stringify({ status: "healthy", port: PORT, elevenlabs: !!ELEVENLABS_API_KEY }),
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
if (ELEVENLABS_API_KEY) {
  console.log(`🎙️  Using ElevenLabs voice: ${ELEVENLABS_VOICE_ID}`);
} else {
  console.log(`🎙️  Using macOS 'say' command (no ElevenLabs API key)`);
}
console.log(`📡 POST to http://localhost:${PORT}/notify`);
console.log(`🔒 Security: CORS restricted to localhost, rate limiting enabled`);