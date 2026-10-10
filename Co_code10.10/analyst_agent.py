import json
import ollama


SYSTEM_PROMPT = """
You are a requirements engineer working on a robot navigation project.
Your job is to read a human-written brief and turn it into a JSON object
that the rest of the system can use.

From the brief, work out four things:
- goal: one short sentence describing what the robot is trying to do.
- allowed_actions: the moves the robot can make. Only these four exist:
  FORWARD, LEFT, RIGHT, STOP.
- safe_stop: true if the robot should stop when no safe move is available,
  false otherwise.
- avoid_obstacles: true if the robot must avoid obstacles in its path,
  false otherwise.

Rules you must follow:
- Do not invent or rename any action. Only FORWARD, LEFT, RIGHT, STOP.
- goal must be a string.
- allowed_actions must be a list of strings.
- safe_stop and avoid_obstacles must be real booleans (true / false),
  not the strings "true" or "false".
- All four keys must be present. No extra keys, no missing keys.
- Return only the JSON object. No markdown, no code fences, no explanation.

Use exactly this structure:
{
    "goal": "string",
    "allowed_actions": ["FORWARD", "LEFT", "RIGHT", "STOP"],
    "safe_stop": true,
    "avoid_obstacles": true
}
"""


def validate_requirements(data):
    required_keys = {
        "goal",
        "allowed_actions",
        "safe_stop",
        "avoid_obstacles"
    }

    allowed_actions = {
        "FORWARD",
        "LEFT",
        "RIGHT",
        "STOP"
    }

    # Check that the result is a dictionary
    if not isinstance(data, dict):
        raise ValueError("Requirements must be a dictionary.")

    # Check that there are no missing or extra keys
    if set(data.keys()) != required_keys:
        raise ValueError("Requirements contain missing or extra keys.")

    # Check goal
    if not isinstance(data["goal"], str):
        raise ValueError("goal must be a string.")

    # Check allowed_actions
    if not isinstance(data["allowed_actions"], list):
        raise ValueError("allowed_actions must be a list.")

    # Check every action
    for action in data["allowed_actions"]:
        if not isinstance(action, str):
            raise ValueError("Every action must be a string.")

        if action not in allowed_actions:
            raise ValueError(f"Invalid action: {action}")

    # Check booleans
    if not isinstance(data["safe_stop"], bool):
        raise ValueError("safe_stop must be a boolean.")

    if not isinstance(data["avoid_obstacles"], bool):
        raise ValueError("avoid_obstacles must be a boolean.")

    return True


def run_analyst(brief_text):
    response = ollama.chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": brief_text
            }
        ]
    )

    json_text = response["message"]["content"]

    try:
        requirements = json.loads(json_text)
    except json.JSONDecodeError:
        raise ValueError("Qwen did not return valid JSON.")

    validate_requirements(requirements)

    return requirements