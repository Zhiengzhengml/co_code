

## Create a function to run the simulation of the navigation logic.
## It should define a set of scenarios with different states (e.g., front_blocked, left_blocked, right_blocked), expected outputs (e.g., FORWARD, LEFT, RIGHT, STOP), and then run the decide_next_move function on each scenario.
## The function should collect the results, including whether the actual output matches the expected output, and return a report summarizing the results.
## The report must include the total number of scenarios, the number of passed and failed scenarios, and a success rate, which is the number of passed scenarios divided by the total number of scenarios.


## If this script is run directly, run the simulation function and save the simulation report to a JSON file.

## Create a function to run the simulation of the navigation logic.
## It should define a set of scenarios with different states (e.g., front_blocked, left_blocked, right_blocked), expected outputs (e.g., FORWARD, LEFT, RIGHT, STOP), and then run the decide_next_move function on each scenario.
## The function should collect the results, including whether the actual output matches the expected output, and return a report summarizing the results.
## The report must include the total number of scenarios, the number of passed and failed scenarios, and a success rate, which is the number of passed scenarios divided by the total number of scenarios.


## If this script is run directly, run the simulation function and save the simulation report to a JSON file.
import json
import importlib.util
from pathlib import Path


CASES = [
    # 1. goal ahead + front clear -> FORWARD
    (
        {"goal_ahead": True,  "goal_on_left": False, "goal_on_right": False,
         "front_blocked": False, "left_blocked": False, "right_blocked": False},
        "FORWARD",
    ),
    # 2. goal left + left clear -> LEFT
    (
        {"goal_ahead": False, "goal_on_left": True,  "goal_on_right": False,
         "front_blocked": False, "left_blocked": False, "right_blocked": False},
        "LEFT",
    ),
    # 3. goal right + right clear -> RIGHT
    (
        {"goal_ahead": False, "goal_on_left": False, "goal_on_right": True,
         "front_blocked": False, "left_blocked": False, "right_blocked": False},
        "RIGHT",
    ),
    # 4. goal ahead but front blocked, left clear -> LEFT (fallback)
    (
        {"goal_ahead": True,  "goal_on_left": False, "goal_on_right": False,
         "front_blocked": True,  "left_blocked": False, "right_blocked": False},
        "LEFT",
    ),
    # 5. goal ahead but front+left blocked, right clear -> RIGHT (fallback)
    (
        {"goal_ahead": True,  "goal_on_left": False, "goal_on_right": False,
         "front_blocked": True,  "left_blocked": True,  "right_blocked": False},
        "RIGHT",
    ),
    # 6. goal left but left blocked, front clear -> FORWARD (fallback)
    (
        {"goal_ahead": False, "goal_on_left": True,  "goal_on_right": False,
         "front_blocked": False, "left_blocked": True,  "right_blocked": False},
        "FORWARD",
    ),
    # 7. goal right but right blocked, front clear -> FORWARD (fallback)
    (
        {"goal_ahead": False, "goal_on_left": False, "goal_on_right": True,
         "front_blocked": False, "left_blocked": False, "right_blocked": True},
        "FORWARD",
    ),
    # 8. goal unknown (all goal flags False), front clear -> FORWARD
    (
        {"goal_ahead": False, "goal_on_left": False, "goal_on_right": False,
         "front_blocked": False, "left_blocked": False, "right_blocked": False},
        "FORWARD",
    ),
    # 9. all directions blocked -> STOP
    (
        {"goal_ahead": True,  "goal_on_left": False, "goal_on_right": False,
         "front_blocked": True,  "left_blocked": True,  "right_blocked": True},
        "STOP",
    ),
]

ALLOWED_ACTIONS = {"FORWARD", "LEFT", "RIGHT", "STOP"}



def load_navigation_logic():
    candidates = [
        Path("navigation_logic.py"),
        Path("generated/navigation_logic.py"),
    ]

    target = None
    for c in candidates:
        if c.exists():
            target = c
            break

    if target is None:
        raise FileNotFoundError(
            "Could not find navigation_logic.py (checked root and generated/)."
        )

    spec = importlib.util.spec_from_file_location("nav", target)
    nav = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nav)

    if not hasattr(nav, "decide_next_move"):
        raise AttributeError(
            f"{target} does not define decide_next_move(state)."
        )

    return nav.decide_next_move, str(target)


def run_simulation():
    decide = load_navigation_logic()[0]

    results = []
    passed = 0

    for state, expected in CASES:
        actual = decide(state)
        ok = (actual == expected)
        if ok:
            passed += 1

        results.append({
            "state": state,
            "expected": expected,
            "actual": actual,
            "passed": ok,
        })

    total = len(CASES)
    report = {
        "total_scenarios": total,
        "passed": passed,
        "failed": total - passed,
        "success_rate": passed / total if total > 0 else 0.0,
        "results": results,
    }
    return report

if __name__ == "__main__":
    decide, source = load_navigation_logic()
    print(f"Loaded navigation logic from: {source}")

    report = run_simulation()

    Path("artifacts").mkdir(exist_ok=True)
    out_path = Path("artifacts/simulation_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    print(json.dumps(report, indent=4))
    print(f"\nSimulation report saved to: {out_path}")