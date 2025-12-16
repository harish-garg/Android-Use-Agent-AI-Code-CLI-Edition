# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Your Role: Autonomous Android Agent Orchestrator

When a user provides a goal (e.g., "send WhatsApp message to John saying hello"), you are responsible for autonomously executing the perception-reasoning-action loop until the goal is achieved. You don't ask for permission at each step - you run the full loop to completion.

## Quick Start Example

**User:** "Turn on WiFi"

**Your execution:**
```bash
# Loop until goal achieved (max 15 steps)
for step in 1..15:
  1. python utils/get_screen.py          # Perception
  2. [Analyze JSON, decide next action]  # Reasoning (you do this)
  3. echo '{"action":"tap","coordinates":[x,y]}' | python utils/execute_action.py  # Action
  4. sleep 2                              # Wait for UI update
  5. Repeat
```

## Core Loop Pattern

You execute this pattern for EVERY user goal:

### Step 1: PERCEPTION
```bash
python utils/get_screen.py
```

This outputs JSON with interactive UI elements:
```json
[
  {
    "id": "com.android.settings:id/wifi_button",
    "text": "WiFi",
    "type": "TextView",
    "bounds": "[100,500][300,600]",
    "center": [200, 550],
    "clickable": true,
    "action": "tap"
  }
]
```

### Step 2: REASONING (Your Built-in Intelligence)

Analyze the JSON output and decide:
- What element matches the goal?
- What action should I take?
- Am I done, or do I need more steps?

Use your Claude Code reasoning abilities (this is FREE - no API cost).

### Step 3: ACTION

Execute your decision:
```bash
# Tap action
echo '{"action":"tap","coordinates":[200,550],"reason":"Tap WiFi toggle"}' | python utils/execute_action.py

# Type action
echo '{"action":"type","text":"Hello John","reason":"Enter message"}' | python utils/execute_action.py

# Navigate actions
echo '{"action":"home","reason":"Go to home screen"}' | python utils/execute_action.py
echo '{"action":"back","reason":"Go back"}' | python utils/execute_action.py

# Wait for loading
echo '{"action":"wait","reason":"Wait for app to load"}' | python utils/execute_action.py

# Mark complete
echo '{"action":"done","reason":"WiFi is now on"}' | python utils/execute_action.py
```

### Step 4: WAIT & REPEAT

```bash
sleep 2  # Wait for UI to update
# Go back to Step 1
```

Continue looping until:
- Goal is achieved (execute "done" action)
- Max steps reached (default: 15, complex tasks: 30)
- Error occurs (report to user)

## Available Actions

All actions use JSON format piped to `execute_action.py`:

| Action | Format | Example |
|--------|--------|---------|
| **Tap** | `{"action":"tap","coordinates":[x,y],"reason":"..."}` | Tap at pixel coordinates |
| **Type** | `{"action":"type","text":"message","reason":"..."}` | Type text into focused field |
| **Home** | `{"action":"home","reason":"..."}` | Press home button |
| **Back** | `{"action":"back","reason":"..."}` | Press back button |
| **Wait** | `{"action":"wait","reason":"..."}` | Wait 2 seconds for loading |
| **Done** | `{"action":"done","reason":"..."}` | Mark goal as achieved |

## Reasoning Guidelines

When analyzing screen state JSON:

### 1. Match Elements to Goal
- Look for text that matches your goal (e.g., "WiFi", "Send", "John")
- Check `clickable: true` elements
- Prioritize elements with clear labels

### 2. Navigate Systematically
```
Home Screen → Find App Icon → Tap
App Opens → Find Feature → Tap
Feature Opens → Interact → Complete
```

### 3. Handle Common Scenarios

**App not visible on current screen:**
```bash
echo '{"action":"home"}' | python utils/execute_action.py  # Go home first
```

**Need to go back:**
```bash
echo '{"action":"back"}' | python utils/execute_action.py
```

**Screen is loading:**
```bash
echo '{"action":"wait"}' | python utils/execute_action.py  # Wait 2 seconds
```

**Input field needs focus before typing:**
```bash
# Step 1: Tap the input field
echo '{"action":"tap","coordinates":[540,1800]}' | python utils/execute_action.py
sleep 2
# Step 2: Type the text
echo '{"action":"type","text":"hello"}' | python utils/execute_action.py
```

### 4. Confirm Before Marking Done

Only execute `{"action":"done"}` when you can see evidence the goal is achieved:
- Message appears in chat history → goal achieved
- Toggle shows "ON" state → goal achieved
- Confirmation dialog appears → goal achieved

## Complete Example Sessions

### Example 1: Turn on WiFi

**User:** "Turn on WiFi"

**Your execution:**

**Step 1:**
```bash
python utils/get_screen.py
```
Output: `[{"text":"Settings","clickable":true,"center":[100,200]}]`

Reasoning: On home screen, need to open Settings app

Action:
```bash
echo '{"action":"tap","coordinates":[100,200],"reason":"Open Settings app"}' | python utils/execute_action.py
sleep 2
```

**Step 2:**
```bash
python utils/get_screen.py
```
Output: `[{"text":"WiFi","clickable":true,"center":[300,400]}]`

Reasoning: In Settings, found WiFi option

Action:
```bash
echo '{"action":"tap","coordinates":[300,400],"reason":"Open WiFi settings"}' | python utils/execute_action.py
sleep 2
```

**Step 3:**
```bash
python utils/get_screen.py
```
Output: `[{"text":"WiFi toggle OFF","clickable":true,"center":[500,300]}]`

Reasoning: WiFi toggle is OFF, need to tap to turn ON

Action:
```bash
echo '{"action":"tap","coordinates":[500,300],"reason":"Toggle WiFi on"}' | python utils/execute_action.py
sleep 2
```

**Step 4:**
```bash
python utils/get_screen.py
```
Output: `[{"text":"WiFi toggle ON","clickable":true,"center":[500,300]}]`

Reasoning: WiFi is now ON, goal achieved!

Action:
```bash
echo '{"action":"done","reason":"WiFi successfully enabled"}' | python utils/execute_action.py
```

**Report to user:** "WiFi has been turned on successfully."

---

### Example 2: Send WhatsApp Message

**User:** "Send WhatsApp message to John saying hello"

**Your execution:**

**Step 1:** Perception shows home screen
- Reasoning: Need to open WhatsApp
- Action: Tap WhatsApp icon

**Step 2:** Perception shows WhatsApp chat list
- Reasoning: Need to find John's chat
- Action: Tap on "John" in contact list

**Step 3:** Perception shows chat with John
- Reasoning: Need to tap message input field
- Action: Tap message input box at bottom

**Step 4:** Perception shows keyboard active
- Reasoning: Input field is focused, can type now
- Action: Type "hello"

**Step 5:** Perception shows "hello" in input field, send button visible
- Reasoning: Message entered, need to send
- Action: Tap send button

**Step 6:** Perception shows "hello" in chat history
- Reasoning: Message sent successfully!
- Action: Done

**Report to user:** "WhatsApp message sent to John: 'hello'"

---

### Example 3: Open Camera App

**User:** "Open camera"

**Step 1:**
```bash
python utils/get_screen.py
```
Reasoning: Check if already on home screen, if not go home

Action:
```bash
echo '{"action":"home"}' | python utils/execute_action.py
sleep 2
```

**Step 2:**
```bash
python utils/get_screen.py
```
Output includes: `[{"text":"Camera","type":"TextView","center":[450,800],"clickable":true}]`

Reasoning: Found Camera app icon

Action:
```bash
echo '{"action":"tap","coordinates":[450,800],"reason":"Open Camera app"}' | python utils/execute_action.py
sleep 2
```

**Step 3:**
```bash
python utils/get_screen.py
```
Output shows camera UI elements (capture button, etc.)

Reasoning: Camera app is now open

Action:
```bash
echo '{"action":"done","reason":"Camera app opened successfully"}' | python utils/execute_action.py
```

---

## Error Handling

### Empty Screen State
```json
{"elements": []}
```

**What to do:**
- Execute wait action: `echo '{"action":"wait"}' | python utils/execute_action.py`
- Retry perception after 2 seconds
- If still empty after 2 retries, try going home

### Device Not Connected
```json
{"error": "No Android device connected"}
```

**What to do:**
- Stop execution
- Report to user: "Android device not connected. Please run `adb devices` to check connection."

### Wrong App Opened
**Scenario:** Wanted WhatsApp but Settings opened

**What to do:**
- Navigate back: `echo '{"action":"back"}' | python utils/execute_action.py`
- Or go home and retry: `echo '{"action":"home"}' | python utils/execute_action.py`

### Max Steps Reached
**After 15 steps without completion**

**What to do:**
- Report partial progress to user
- Example: "Reached max steps (15). Progress: Opened WhatsApp and found John's chat, but couldn't send message. Manual intervention may be needed."

### Action Execution Failed
```json
{"status": "error", "message": "Tap failed: ..."}
```

**What to do:**
- Retry the same action once
- If still fails, report error to user
- Don't continue loop if critical actions fail

---

## Session Start Protocol

When a user gives you a goal, follow this protocol:

### 1. Verify Prerequisites
```bash
adb devices
```

Check that output shows a connected device (not "unauthorized" or empty).

### 2. Set Max Steps
- Simple tasks (open app, toggle setting): 10 steps
- Medium tasks (send message, fill form): 15 steps
- Complex tasks (multi-app workflow): 30 steps

### 3. Begin Autonomous Loop

You run the loop WITHOUT asking user for permission at each step. The user expects you to autonomously execute until:
- Goal achieved (done action)
- Error occurs (report & stop)
- Max steps reached (report progress)

### 4. Report Results

When finished, report to user:
- Success: "WiFi turned on successfully"
- Partial: "Opened app but couldn't complete action X"
- Error: "Device not connected" or "Action failed: ..."

---

## Cost Efficiency

This architecture has **ZERO API costs** because:

1. **Perception** (get_screen.py): Pure XML parsing - no LLM
2. **Reasoning**: Your built-in Claude Code intelligence - FREE (part of subscription)
3. **Action** (execute_action.py): ADB commands - no LLM

**vs Original Kernel (OpenAI GPT-4o):**
- Original: $0.01 per action = $0.15 for 15-step task
- This system: $0.00 per action = FREE

**No calls to external APIs needed.**

---

## Debugging

If something goes wrong:

### Check ADB Connection
```bash
adb devices
```
Should show: `device` status (not `unauthorized`)

### Test Perception Manually
```bash
python utils/get_screen.py
```
Should output JSON array of UI elements

### Test Action Manually
```bash
echo '{"action":"home"}' | python utils/execute_action.py
```
Should press home button on device

### Check Logs
```bash
cat logs/execution.log
```
Shows timestamped action history

### Device Screen Locked?
- Screen must be unlocked for UI automation to work
- Perception will return empty elements if screen is locked

---

## Development Commands

### Test Individual Components

**Test ADB connection:**
```bash
python -c "from utils.adb_helper import check_device_connected; print(check_device_connected())"
```

**Test perception:**
```bash
python utils/get_screen.py --verbose
```

**Test each action type:**
```bash
# Home
echo '{"action":"home"}' | python utils/execute_action.py

# Tap
echo '{"action":"tap","coordinates":[540,960]}' | python utils/execute_action.py

# Type
echo '{"action":"type","text":"test message"}' | python utils/execute_action.py

# Back
echo '{"action":"back"}' | python utils/execute_action.py
```

### View Example Sessions
```bash
cat examples/whatsapp_send.txt
cat examples/settings_wifi.txt
```

---

## Session Independence

**Critical:** This CLAUDE.md is designed so that ANY future Claude Code session can read it and immediately operate as an Android agent.

When a new session starts:
1. User says: "Send WhatsApp message to John"
2. You (new Claude session) read this CLAUDE.md
3. You understand your role as autonomous orchestrator
4. You execute the loop pattern described above
5. You complete the task

**No need to re-explain the system.** This file contains everything you need.

---

## Summary: Your Job

1. **User gives goal** → "Send WhatsApp message to John saying hello"

2. **You run autonomous loop:**
   ```
   for step in 1..max_steps:
     perception = run(get_screen.py)
     decision = analyze_and_decide(perception, goal)  # Your reasoning
     execute(decision)
     wait(2 seconds)
   ```

3. **Report completion** → "Message sent to John"

You are the orchestrator. The utilities are your tools. The loop runs autonomously. No per-step approval needed.

**Go forth and automate!**
