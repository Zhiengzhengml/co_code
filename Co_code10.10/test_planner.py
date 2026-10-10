import json
from pathlib import Path

from planner_agent import run_planner


def test_planner():
    # Read the requirements produced by the Analyst Agent
    with open("artifacts/requirements.json", "r", encoding="utf-8") as f:
        requirements = json.load(f)

    # Call the Planner Agent
    plan = run_planner(requirements)

    # Assert: structure is correct
    assert isinstance(plan, dict), "plan must be a dict"
    assert set(plan.keys()) == {
        "strategy",
        "decisions",
        "stop_condition",
    }, "plan keys are incorrect"

    assert isinstance(plan["strategy"], str)
    assert plan["strategy"].strip() != ""

    assert isinstance(plan["decisions"], list)
    assert len(plan["decisions"]) > 0

    actions = set()
    for decision in plan["decisions"]:
        assert isinstance(decision, dict)
        assert set(decision.keys()) == {"condition", "action"}
        assert isinstance(decision["condition"], str)
        assert decision["action"] in {
            "FORWARD",
            "LEFT",
            "RIGHT",
            "STOP",
        }
        actions.add(decision["action"])

    assert actions == {
        "FORWARD",
        "LEFT",
        "RIGHT",
        "STOP",
    }, "plan must cover all four actions"

    assert isinstance(plan["stop_condition"], str)
    assert plan["stop_condition"].strip() != ""

    # Save to artifacts
    with open("artifacts/plan.json", "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=4)

    # Display after the test ends
    print("plan.json:")
    print(json.dumps(plan, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    test_planner()
    print("test_planner passed")