#!/usr/bin/env bash
# Voice Server Launcher Script

export HOME=/Users/daniel
export PATH=/Users/daniel/.bun/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
export PORT=8888

cd /Users/daniel/.claude/voice-server
exec /Users/daniel/.bun/bin/bun run server.ts