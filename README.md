# Android Agent - AI CLI Edition

**Control your Android device using any AI coding assistant - zero API costs**

Adapted from [android-action-kernel](https://github.com/actionstatelabs/android-action-kernel) by Ethan Lim. The original used OpenAI's GPT-4o API ($0.01 per action). This version uses your AI coding assistant's built-in intelligence at no additional cost.

If you already subscribe to Claude Code, Gemini Code Assist, Cursor, or similar - you can use it for Android automation with zero marginal API costs.

[![Android Agent Demo](https://img.youtube.com/vi/MvVX1ZgyM8Y/maxresdefault.jpg)](https://www.youtube.com/watch?v=MvVX1ZgyM8Y)
*(Click the image above to watch the demo video)*

## How It Works

Your AI assistant reads instruction files (`AGENT.md` or `CLAUDE.md`) and autonomously executes a perception-reasoning-action loop until your goal is achieved:

1. **Perception** - Gets screen state: `python utils/get_screen.py`
2. **Reasoning** - AI decides next action (built-in intelligence)
3. **Action** - Executes: `echo '{"action":"tap",...}' | python utils/execute_action.py`
4. **Repeat** - Until complete

## Quick Start

### Prerequisites

- **Python 3.10+**
- **ADB (Android Debug Bridge)**
  - Windows: `choco install adb` or `winget install adb`
  - macOS: `brew install android-platform-tools`
  - Linux: `sudo apt-get install adb`
- **Android device** with USB debugging enabled
- **AI Coding Assistant**: [Claude Code](https://claude.ai/code), [Cursor](https://cursor.sh/), [Windsurf](https://codeium.com/windsurf), or similar

### Setup

```bash
# 1. Clone and navigate
cd android-agent

# 2. Connect device and verify
adb devices
# Should show: xxxxxxx device

# 3. Unlock device screen

# 4. Open your AI assistant in this folder and give it a goal
claude/gemini/codex

```

### Example Usage

In Claude Code (or your AI assistant):

```
"Turn on WiFi"
```

The AI will autonomously:
1. Read AGENT.md/CLAUDE.md
2. Navigate: Home → Settings → Network → WiFi toggle
3. Report: "WiFi turned on successfully"

**No per-step approval needed. Fully autonomous.**

## Example Goals

**Simple:**
- "Turn on WiFi"
- "Open Camera app"
- "Go to Settings"

**Messaging:**
- "Send WhatsApp message to John saying hello"

**Complex:**
- "Get latest image from WhatsApp, then open RTS Pro and submit as invoice"
- See `examples/logistics_flow.txt` for full trace

## Troubleshooting

**"No Android device connected"**
```bash
adb devices
# If "unauthorized" - accept USB debugging prompt on device
# If empty - check USB cable or enable USB debugging in Developer Options
```

**"Empty screen state"**
- Device screen must be unlocked
- Wait a few seconds if app is loading

**Actions not working**
- Ensure screen is on and unlocked
- Check logs: `cat logs/execution.log` (Windows: `type logs\execution.log`)
- Test manually: `adb shell input tap 540 960`


## Acknowledgments

- **[android-action-kernel](https://github.com/actionstatelabs/android-action-kernel)** by Ethan Lim - Original implementation
- **[agents.md](https://agents.md/)** - AI agent instruction standard
- **Android Accessibility API** - Provides UI tree for perception

---

**Works with Claude Code, Codex, Amp, Mistral Vibe, OpenCode, Gemini Code Assist, Cursor, Windsurf, and other CLI AI assistants**
