import json
from ollama import chat


system_prompt = """
You are a Reviewer Agent for a robot navigation system.

Your task is to analyze a simulation report and identify whether
the navigation logic has problems.

You must return ONLY a valid JSON object.

The JSON object must contain exactly these keys:

{
    "issue": string,
    "likely_cause": string,
    "recommendation": string,
    "needs_revision": boolean
}

Rules:

1. "issue" must describe the main problem found in the simulation report.
2. "likely_cause" must describe the most likely reason for the problem.
3. "recommendation" must explain how the navigation logic could be improved.
4. "needs_revision" must be true if the navigation logic should be revised,
   otherwise false.
5. Base every conclusion only on evidence contained in the simulation report.

6. Do not invent environmental obstacles, sensor problems, path-planning
   errors, collisions, or other causes unless they are explicitly shown
   in the report.

7. If the report only provides aggregate statistics and does not contain
   details of the failed scenarios, state that the exact cause cannot be
   determined from the available report.

8. If all scenarios pass, explain that no major issue was detected and set
   "needs_revision" to false.

9. Return JSON only.

10. Do not use Markdown code blocks.

11. Do not include explanations before or after the JSON object.
"""


def validate_reviewer_output(data):

    if not isinstance(data, dict):
        raise ValueError("Reviewer output must be a dictionary.")

    required_keys = {
        "issue",
        "likely_cause",
        "recommendation",
        "needs_revision"
    }

    if set(data.keys()) != required_keys:
        raise ValueError(
            "Reviewer output contains missing or extra keys."
        )

    if not isinstance(data["issue"], str):
        raise ValueError("issue must be a string.")

    if not isinstance(data["likely_cause"], str):
        raise ValueError("likely_cause must be a string.")

    if not isinstance(data["recommendation"], str):
        raise ValueError("recommendation must be a string.")

    if not isinstance(data["needs_revision"], bool):
        raise ValueError("needs_revision must be a boolean.")

    return True


def run_reviewer(simulation_report):

    if not isinstance(simulation_report, dict):
        raise ValueError("Simulation report must be a dictionary.")

    report_text = json.dumps(
        simulation_report,
        indent=4,
        ensure_ascii=False
    )

    prompt = f"""
Analyze the following robot navigation simulation report.

SIMULATION REPORT:
{report_text}

Identify the main issue, likely cause, and recommendation.

Do not guess the cause of a failure.

If failed-scenario details are not available, clearly state that
the exact cause cannot be determined from the report.

If the report shows that all scenarios passed successfully,
do not invent a problem.

Return the result using exactly this JSON structure:

{{
    "issue": "...",
    "likely_cause": "...",
    "recommendation": "...",
    "needs_revision": true
}}

Return JSON only.
"""

    response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
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
        raise ValueError(
            f"Reviewer did not return valid JSON: {error}"
        )

    validate_reviewer_output(result)

    return result