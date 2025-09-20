#!/usr/bin/env bun
/**
 * PAIVoice - Personal AI Voice notification server for macOS with ElevenLabs
 */

import { serve } from "bun";
import { exec } from "child_process";
import { promisify } from "util";
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

const execAsync = promisify(exec);
const PORT = parseInt(process.env.PORT || "8888");

// ElevenLabs configuration - MUST be set in ~/.env
const ELEVENLABS_API_KEY = process.env.ELEVENLABS_API_KEY;
const ELEVENLABS_VOICE_ID = process.env.ELEVENLABS_VOICE_ID || "jqcCZkN6Knx8BJ5TBdYR";

if (!ELEVENLABS_API_KEY) {
  console.error("⚠️  Warning: ELEVENLABS_API_KEY not found in ~/.env");
  console.error("   Voice features will fall back to macOS 'say' command");
  console.error("   To enable ElevenLabs voices, add to ~/.env:");
  console.error("   ELEVENLABS_API_KEY=your_api_key_here");
}

// Generate voice using ElevenLabs
async function generateVoice(text, voiceId = null) {
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

// Send macOS notification with voice
async function sendNotification(title, message, voiceEnabled = true, voiceId = null) {
  if (voiceEnabled) {
    const audioFile = await generateVoice(message, voiceId);
    
    if (audioFile) {
      execAsync(`afplay "${audioFile}"`).then(() => {
        unlink(audioFile).catch(() => {});
      }).catch(() => {
        console.error("Failed to play ElevenLabs audio");
        execAsync(`say "${message}"`).catch(() => {});
      });
    } else {
      execAsync(`say "${message}"`).catch(() => {
        console.error("Failed to speak message");
      });
    }
  }
  
  const escapedMessage = message.replace(/'/g, "'\\''").replace(/"/g, '\\"');
  const escapedTitle = title.replace(/'/g, "'\\''").replace(/"/g, '\\"');
  const script = `display notification "${escapedMessage}" with title "${escapedTitle}" sound name ""`;
  await execAsync(`osascript -e '${script}'`);
}

// Start HTTP server
const server = serve({
  port: PORT,
  async fetch(req) {
    const url = new URL(req.url);
    
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type"
    };
    
    if (req.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders, status: 204 });
    }
    
    if (url.pathname === "/notify" && req.method === "POST") {
      try {
        const data = await req.json();
        const title = data.title || "PAI Notification";
        const message = data.message || "Task completed";
        const voiceEnabled = data.voice_enabled !== false;
        const voiceId = data.voice_id || null;
        
        console.log(`📨 Received notification: "${title}" - "${message}" (voice: ${voiceEnabled}, voiceId: ${voiceId}`);
        
        await sendNotification(title, message, voiceEnabled, voiceId);
        
        return new Response(
          JSON.stringify({ status: "success", message: "Notification sent" }),
          { 
            headers: { ...corsHeaders, "Content-Type": "application/json" },
            status: 200 
          }
        );
      } catch (error) {
        return new Response(
          JSON.stringify({ status: "error", message: error.message }),
          { 
            headers: { ...corsHeaders, "Content-Type": "application/json" },
            status: 500 
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
        
        await sendNotification(title, message, true);
        
        return new Response(
          JSON.stringify({ status: "success", message: "PAI notification sent" }),
          { 
            headers: { ...corsHeaders, "Content-Type": "application/json" },
            status: 200 
          }
        );
      } catch (error) {
        return new Response(
          JSON.stringify({ status: "error", message: error.message }),
          { 
            headers: { ...corsHeaders, "Content-Type": "application/json" },
            status: 500 
          }
        );
      }
    }
    
    if (url.pathname === "/health") {
      return new Response(
        JSON.stringify({ status: "healthy", port: PORT }),
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