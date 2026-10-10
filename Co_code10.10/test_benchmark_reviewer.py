
from reviewer_benchmark_agent import (
    build_deterministic_review,
    run_benchmark_reviewer
)

benchmark_report = {
    "total_worlds": 4,
    "goals_reached": 3,
    "success_rate": 0.75,
    "efficient_worlds": 2,
    "inefficient_success_worlds": 1,
    "failed_worlds": 1,
    "efficiency_rate": 0.5,
    "average_steps_taken": 190,
    "results": [
        {
            "world": "easy",
            "reached_goal": True,
            "collision_or_done": False
        },
        {
            "world": "medium",
            "reached_goal": True,
            "collision_or_done": False
        },
        {
            "world": "hard",
            "reached_goal": False,
            "collision_or_done": True
        },
        {
            "world": "custom",
            "reached_goal": True,
            "collision_or_done": False
        }
    ]
}

print("Deterministic review:")
review = build_deterministic_review(benchmark_report)
print(review)

assert review["safety_passed"] is False
assert review["goal_completion_passed"] is False
assert review["efficiency_passed"] is False
assert review["needs_revision"] is True

print("\nLLM Benchmark review:")
result = run_benchmark_reviewer(benchmark_report)
print(result)

assert result["safety_passed"] is False
assert result["goal_completion_passed"] is False
assert result["efficiency_passed"] is False
assert result["needs_revision"] is True

print("\nAll benchmark reviewer checks passed.")
