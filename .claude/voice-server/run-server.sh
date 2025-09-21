#!/usr/bin/env bash
# Voice Server Launcher Script

# Use current user's HOME if not set
export HOME="${HOME:-$(eval echo ~$USER)}"
export PATH="$HOME/.bun/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export PORT=8888

# Use PAI_HOME if set, otherwise default to HOME
PAI_HOME="${PAI_HOME:-$HOME}"

cd "${PAI_HOME}/.claude/voice-server"
exec "$HOME/.bun/bin/bun" run server.ts