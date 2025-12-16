#!/usr/bin/env python3
"""
Execute Action - Action Module

Executes a single action on the Android device via ADB.
This is the "action" step of the agent loop.

Usage:
    echo '{"action":"tap","coordinates":[540,1200]}' | python execute_action.py
    python execute_action.py --json '{"action":"home"}'
"""

import sys
import os
import json
import argparse
import time
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import adb_helper


LOG_FILE = "logs/execution.log"


def log_action(action_type: str, details: str, status: str):
    """
    Log action execution to file.

    Args:
        action_type: Type of action (tap, type, home, etc.)
        details: Action details (coordinates, text, etc.)
        status: SUCCESS or ERROR
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] ACTION: {action_type}({details}) -> {status}\n"

    try:
        os.makedirs("logs", exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except:
        pass  # Don't fail action execution due to logging errors


def validate_action(action: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate action JSON format.

    Args:
        action: Action dictionary

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(action, dict):
        return False, "Action must be a JSON object"

    if "action" not in action:
        return False, "Missing 'action' field"

    action_type = action["action"]
    valid_actions = ["tap", "type", "home", "back", "wait", "done"]

    if action_type not in valid_actions:
        return False, f"Invalid action type '{action_type}'. Must be one of: {valid_actions}"

    # Validate action-specific fields
    if action_type == "tap":
        if "coordinates" not in action:
            return False, "tap action requires 'coordinates' field"
        coords = action["coordinates"]
        if not isinstance(coords, list) or len(coords) != 2:
            return False, "coordinates must be [x, y] array"
        if not all(isinstance(c, (int, float)) for c in coords):
            return False, "coordinates must be numeric"

    elif action_type == "type":
        if "text" not in action:
            return False, "type action requires 'text' field"
        if not isinstance(action["text"], str):
            return False, "text must be a string"

    return True, ""


def execute_action(action: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a single action on the Android device.

    Args:
        action: Action dictionary with format:
            {"action": "tap", "coordinates": [x, y], "reason": "..."}
            {"action": "type", "text": "Hello", "reason": "..."}
            {"action": "home", "reason": "..."}
            {"action": "back", "reason": "..."}
            {"action": "wait", "reason": "..."}
            {"action": "done", "reason": "..."}

    Returns:
        Result dictionary:
            {"status": "success", "action": "tap", "message": "..."}
            {"status": "error", "message": "..."}
    """
    # Validate action format
    is_valid, error_msg = validate_action(action)
    if not is_valid:
        return {"status": "error", "message": error_msg}

    # Check device connection (except for done/wait)
    action_type = action["action"]
    if action_type not in ["done", "wait"]:
        if not adb_helper.check_device_connected():
            return {
                "status": "error",
                "message": "No Android device connected"
            }

    # Execute action
    try:
        if action_type == "tap":
            x, y = action["coordinates"]
            x, y = int(x), int(y)

            stdout, stderr, code = adb_helper.run_adb([
                "shell", "input", "tap", str(x), str(y)
            ])

            if code != 0:
                log_action("tap", f"{x},{y}", f"ERROR: {stderr}")
                return {
                    "status": "error",
                    "message": f"Tap failed: {stderr}"
                }

            log_action("tap", f"{x},{y}", "SUCCESS")
            return {
                "status": "success",
                "action": "tap",
                "message": f"Tapped at ({x}, {y})"
            }

        elif action_type == "type":
            text = action["text"]
            # ADB requires spaces to be encoded as %s
            encoded_text = text.replace(" ", "%s")

            stdout, stderr, code = adb_helper.run_adb([
                "shell", "input", "text", encoded_text
            ])

            if code != 0:
                log_action("type", text, f"ERROR: {stderr}")
                return {
                    "status": "error",
                    "message": f"Type failed: {stderr}"
                }

            log_action("type", text, "SUCCESS")
            return {
                "status": "success",
                "action": "type",
                "message": f"Typed: {text}"
            }

        elif action_type == "home":
            stdout, stderr, code = adb_helper.run_adb([
                "shell", "input", "keyevent", "KEYCODE_HOME"  # FIX: was KEYWORDS_HOME
            ])

            if code != 0:
                log_action("home", "", f"ERROR: {stderr}")
                return {
                    "status": "error",
                    "message": f"Home failed: {stderr}"
                }

            log_action("home", "", "SUCCESS")
            return {
                "status": "success",
                "action": "home",
                "message": "Pressed Home button"
            }

        elif action_type == "back":
            stdout, stderr, code = adb_helper.run_adb([
                "shell", "input", "keyevent", "KEYCODE_BACK"  # FIX: was KEYWORDS_BACK
            ])

            if code != 0:
                log_action("back", "", f"ERROR: {stderr}")
                return {
                    "status": "error",
                    "message": f"Back failed: {stderr}"
                }

            log_action("back", "", "SUCCESS")
            return {
                "status": "success",
                "action": "back",
                "message": "Pressed Back button"
            }

        elif action_type == "wait":
            time.sleep(2)
            log_action("wait", "2s", "SUCCESS")
            return {
                "status": "success",
                "action": "wait",
                "message": "Waited 2 seconds"
            }

        elif action_type == "done":
            log_action("done", "", "SUCCESS")
            return {
                "status": "success",
                "action": "done",
                "message": "Goal achieved - task complete"
            }

    except Exception as e:
        log_action(action_type, "", f"ERROR: {str(e)}")
        return {
            "status": "error",
            "message": f"Execution error: {str(e)}"
        }


def main():
    parser = argparse.ArgumentParser(
        description="Execute a single action on Android device"
    )
    parser.add_argument(
        "--json",
        type=str,
        help="Action JSON string (alternative to stdin)"
    )
    args = parser.parse_args()

    # Get action JSON from --json flag or stdin
    if args.json:
        action_json = args.json
    else:
        action_json = sys.stdin.read().strip()

    if not action_json:
        print(json.dumps({
            "status": "error",
            "message": "No action provided. Use --json flag or pipe JSON via stdin"
        }))
        sys.exit(1)

    # Parse JSON
    try:
        action = json.loads(action_json)
    except json.JSONDecodeError as e:
        print(json.dumps({
            "status": "error",
            "message": f"Invalid JSON: {str(e)}"
        }))
        sys.exit(1)

    # Execute action
    result = execute_action(action)

    # Output result
    print(json.dumps(result, indent=2))

    # Exit with appropriate code
    if result["status"] == "error":
        sys.exit(3)
    elif result.get("action") == "done":
        sys.exit(0)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
