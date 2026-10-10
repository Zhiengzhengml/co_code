import json
from pathlib import Path

from analyst_agent import run_analyst


def test_analyst():
    # Read the original brief
    brief_text = Path("brief.txt").read_text(encoding="utf-8")

    # Call the Analyst Agent
    requirements = run_analyst(brief_text)

    # Assert: structure is correct
    assert isinstance(requirements, dict), "requirements must be a dict"
    assert set(requirements.keys()) == {
        "goal",
        "allowed_actions",
        "safe_stop",
        "avoid_obstacles",
    }, "requirements keys are incorrect"

    assert isinstance(requirements["goal"], str)
    assert requirements["goal"].strip() != ""

    assert isinstance(requirements["allowed_actions"], list)
    assert set(requirements["allowed_actions"]) == {
        "FORWARD",
        "LEFT",
        "RIGHT",
        "STOP",
    }

    assert isinstance(requirements["safe_stop"], bool)
    assert isinstance(requirements["avoid_obstacles"], bool)

    # Save to artifacts
    Path("artifacts").mkdir(exist_ok=True)
    with open("artifacts/requirements.json", "w", encoding="utf-8") as f:
        json.dump(requirements, f, indent=4)

    # Display after the test ends
    print("requirements.json:")
    print(json.dumps(requirements, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    test_analyst()
    print("test_analyst passed")