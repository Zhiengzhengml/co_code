
import json
from ollama import chat


system_prompt = """
You are a Benchmark Reviewer Agent for robot navigation.

Analyze the IR-SIM benchmark report using measured evidence.

Do not claim a collision occurred solely because
collision_or_done is True; the flag may also indicate
other termination conditions.

Return ONLY a valid JSON object with exactly these keys:

{
    "issue": string,
    "likely_cause": string,
    "recommendation": string,
    "safety_passed": boolean,
    "goal_completion_passed": boolean,
    "efficiency_passed": boolean,
    "needs_revision": boolean
}

Rules:
1. Base conclusions only on the benchmark report.
2. Do not invent collision, sensor, or navigation failures.
3. The deterministic review provides the correct boolean values.
4. Preserve those boolean values exactly.
5. You may improve only the three text explanations.
6. Return JSON only, without Markdown or explanations.
"""


def validate_benchmark_reviewer_output(data):

    if not isinstance(data, dict):
        raise ValueError("Output must be a dictionary.")

    string_keys = {
        "issue",
        "likely_cause",
        "recommendation"
    }

    boolean_keys = {
        "safety_passed",
        "goal_completion_passed",
        "efficiency_passed",
        "needs_revision"
    }

    if set(data.keys()) != string_keys | boolean_keys:
        raise ValueError("Missing or extra output keys.")

    for key in string_keys:
        if not isinstance(data[key], str):
            raise ValueError(f"{key} must be a string.")

    for key in boolean_keys:
        if not isinstance(data[key], bool):
            raise ValueError(f"{key} must be a boolean.")

    return True


def build_deterministic_review(benchmark_report):

    if not isinstance(benchmark_report, dict):
        raise ValueError("Benchmark report must be a dictionary.")

    results = benchmark_report.get("results", [])
    success_rate = benchmark_report.get("success_rate", 0.0)
    inefficient_worlds = benchmark_report.get(
        "inefficient_success_worlds", 0
    )
    efficiency_rate = benchmark_report.get("efficiency_rate", 0.0)

    if not isinstance(results, list):
        raise ValueError("results must be a list.")

    if not all(isinstance(world, dict) for world in results):
        raise ValueError("Each world result must be a dictionary.")

    # Safety: no collision/termination before reaching the goal
    unsafe_behavior = any(
        world.get("collision_or_done", False)
        and not world.get("reached_goal", False)
        for world in results
    )

    safety_passed = not unsafe_behavior

    # Goal completion: all worlds must reach their goals
    goal_completion_passed = success_rate >= 1.0

    # Efficiency: all worlds must complete efficiently
    efficiency_passed = (
        inefficient_worlds == 0
        and efficiency_rate >= 1.0
    )

    needs_revision = not (
        safety_passed
        and goal_completion_passed
        and efficiency_passed
    )

    if not safety_passed:
        issue = "Unsafe benchmark behavior detected"
        likely_cause = (
            "At least one world terminated without reaching its goal."
        )
        recommendation = (
            "Inspect the failed world and improve navigation safety."
        )

    elif not goal_completion_passed:
        issue = "Goal completion failure"
        likely_cause = (
            "The robot did not reach the goal in every world."
        )
        recommendation = (
            "Review failed worlds and improve goal-directed navigation."
        )

    elif not efficiency_passed:
        issue = "Successful but inefficient navigation"
        likely_cause = (
            "Some successful runs exceeded the efficiency threshold."
        )
        recommendation = (
            "Improve navigation efficiency and reduce unnecessary steps."
        )

    else:
        issue = "No benchmark issue detected"
        likely_cause = "All measured benchmark criteria passed."
        recommendation = "No revision is currently required."

    return {
        "issue": issue,
        "likely_cause": likely_cause,
        "recommendation": recommendation,
        "safety_passed": safety_passed,
        "goal_completion_passed": goal_completion_passed,
        "efficiency_passed": efficiency_passed,
        "needs_revision": needs_revision
    }


def run_benchmark_reviewer(benchmark_report):

    deterministic_review = build_deterministic_review(
        benchmark_report
    )

    prompt = f"""
Analyze the following IR-SIM benchmark report:

{json.dumps(benchmark_report, indent=4)}

The deterministic review is:

{json.dumps(deterministic_review, indent=4)}

Return the seven required JSON fields.
Preserve the four boolean values exactly.
Do not invent reasons that are unsupported by the report.
"""

    response = chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    content = response["message"]["content"].strip()

    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]

    if content.endswith("```"):
        content = content[:-3]

    content = content.strip()

    try:
        result = json.loads(content)
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid Reviewer JSON: {error}")

    validate_benchmark_reviewer_output(result)

    # Measured data always overrides LLM boolean decisions
    for key in (
        "safety_passed",
        "goal_completion_passed",
        "efficiency_passed",
        "needs_revision"
    ):
        result[key] = deterministic_review[key]

    validate_benchmark_reviewer_output(result)

    return result
