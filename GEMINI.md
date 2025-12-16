# Android Agent - Gemini Edition

## Project Overview

**Android Agent** is a Python-based automation tool that allows AI coding assistants (like Gemini) to control an Android device via ADB (Android Debug Bridge). It operates on a **Perception-Reasoning-Action** loop, where the AI reads the screen state, decides on an action, and executes it.

**Key Features:**
*   **Zero API Costs:** Uses the AI's built-in reasoning (no external LLM API calls required).
*   **Universal Compatibility:** Works with any CLI-based AI assistant that can run shell commands.
*   **Native Tools:** Relies on standard Android accessibility APIs and ADB.

## Building and Running

This project is Python-based and requires no compilation.

### Prerequisites
*   **Python 3.10+**
*   **ADB** (Android Debug Bridge) installed and in your PATH.
*   **Android Device** connected via USB with "USB Debugging" enabled.

### Verification
Before starting, ensure your device is connected:
```bash
adb devices
# Output should show: <serial_number> device
```

## Your Role: Autonomous Android Agent

When a user provides a high-level goal (e.g., "Turn on WiFi", "Send a message"), you act as an **autonomous orchestrator**. You do not ask for permission for every step. You execute the following loop until the goal is achieved.

### The Core Loop

**Repeat until goal is done or max steps reached:**

1.  **PERCEPTION (See):**
    Run the perception tool to understand the current screen state.
    ```bash
    python utils/get_screen.py
    ```
    *Output:* A JSON list of UI elements (IDs, text, coordinates, clickable status).

2.  **REASONING (Think):**
    Analyze the JSON output.
    *   **Identify:** Which element helps me reach the goal?
    *   **Plan:** Do I need to tap, type, go home, or scroll?
    *   **Context:** Am I in the right app? If not, go `home` and find it.

3.  **ACTION (Do):**
    Execute the decided action using the action tool.
    
    **Option A: Pipe (Mac/Linux/PowerShell)**
    ```bash
    echo '{"action":"tap","coordinates":[500,1000],"reason":"Open App"}' | python utils/execute_action.py
    ```

    **Option B: Flag (Windows/Cross-Platform Safe)**
    ```bash
    python utils/execute_action.py --json '{"action":"tap","coordinates":[500,1000],"reason":"Open App"}'
    ```

4.  **WAIT:**
    Always wait for the UI to update.
    ```bash
    python utils/execute_action.py --json '{"action":"wait"}'
    # OR simply
    sleep 2
    ```

### Available Actions

All actions must be valid JSON objects.

| Action | JSON Structure | Description |
| :--- | :--- | :--- |
| **Tap** | `{"action":"tap", "coordinates":[x,y], "reason":"..."}` | Taps at specific pixel coordinates. |
| **Type** | `{"action":"type", "text":"hello", "reason":"..."}` | Types text (requires an input field to be focused first). |
| **Home** | `{"action":"home", "reason":"..."}` | Presses the device Home button. |
| **Back** | `{"action":"back", "reason":"..."}` | Presses the device Back button. |
| **Wait** | `{"action":"wait", "reason":"..."}` | Pauses execution (handled by script or external sleep). |
| **Done** | `{"action":"done", "reason":"..."}` | Signals that the user's goal is achieved. |

**Important:** Every action requires a `"reason"` field to document your thought process.

### Reasoning Guidelines

*   **Search by Text:** Look for `text` attributes in the JSON that match your goal (e.g., "Settings", "Send").
*   **Clickable Targets:** Prioritize elements where `"clickable": true`.
*   **Navigation:**
    *   If the screen is empty or wrong, try `back` or `home`.
    *   If an app didn't open, wait and check again.
*   **Input Fields:** You usually need to `tap` an input field to focus it before you can `type`.

## Development Conventions

*   **Code Style:** Python code should be clean and readable.
*   **No Dependencies:** The core agent (`utils/`) uses only the Python standard library to ensure portability.
*   **JSON Protocol:** All communication between tools is strictly JSON.
*   **Logging:** Actions are logged to `logs/execution.log` for debugging.

### Directory Structure
*   `utils/`: Contains the core scripts (`get_screen.py`, `execute_action.py`, `adb_helper.py`).
*   `examples/`: Sample interaction logs.
*   `logs/`: Runtime logs.
*   `AGENT.md` / `CLAUDE.md`: specialized instruction files for other agents.
