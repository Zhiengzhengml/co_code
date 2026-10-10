
from pathlib import Path
from developer_agent import (
    run_developer_revision,
    validate_code
)

# 1. Read the original navigation code
original_code = Path(
    "navigation_logic.py"
).read_text(encoding="utf-8")


# 2. Simulated Reviewer feedback
review_notes = {
    "issue": "One benchmark world failed",
    "likely_cause": (
        "The exact cause cannot be determined "
        "without detailed navigation logs."
    ),
    "recommendation": (
        "Improve navigation reliability while "
        "preserving goal priority and obstacle avoidance."
    ),
    "needs_revision": True
}


# 3. Simulated Benchmark report
benchmark_report = {
    "total_worlds": 4,
    "goals_reached": 3,
    "success_rate": 0.75,
    "efficient_worlds": 2,
    "inefficient_success_worlds": 1,
    "failed_worlds": 1,
    "efficiency_rate": 0.5
}


# 4. Requirements
requirements = {
    "goal": "Navigate safely toward the target",
    "allowed_actions": [
        "FORWARD",
        "LEFT",
        "RIGHT",
        "STOP"
    ],
    "safe_stop": True,
    "avoid_obstacles": True
}


# 5. Navigation plan
plan = {
    "strategy": (
        "Prioritize the goal direction when it is clear. "
        "Otherwise use FORWARD, LEFT, RIGHT as fallback. "
        "STOP if all directions are blocked."
    ),
    "decisions": [
        {
            "condition": "Goal ahead and front clear",
            "action": "FORWARD"
        },
        {
            "condition": "Goal left and left clear",
            "action": "LEFT"
        },
        {
            "condition": "Goal right and right clear",
            "action": "RIGHT"
        },
        {
            "condition": "All directions blocked",
            "action": "STOP"
        }
    ],
    "stop_condition": "All directions blocked"
}


# 6. Run Developer Revision
print("Starting Developer Revision...")

revised_code = run_developer_revision(
    original_code=original_code,
    review_notes=review_notes,
    benchmark_report=benchmark_report,
    requirements=requirements,
    plan=plan
)


# 7. Validate the revised code
validate_code(revised_code)

print("Revised code validation passed.")


# 8. Check the output file
output_path = Path("navigation_logic_revised.py")

if output_path.exists():
    print("Revised navigation file created successfully.")
    print("File:", output_path)
else:
    raise FileNotFoundError(
        "Revised navigation file was not created."
    )

print("Developer Revision test completed.")
