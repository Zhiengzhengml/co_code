import json
from ollama import chat


system_prompt = """
You are a Developer Agent for a robot navigation system.

Your task is to convert the validated navigation plan provided by
the Planner Agent into valid Python code.

The generated Python code must contain a main function called:

decide_next_move(state)

The state parameter is a dictionary containing:

{
    "goal_ahead": boolean,
    "goal_on_left": boolean,
    "goal_on_right": boolean,
    "front_blocked": boolean,
    "left_blocked": boolean,
    "right_blocked": boolean
}

At most one of goal_ahead, goal_on_left, goal_on_right is True.
If none is True, the goal direction is unknown.

The original navigation logic should be retained.

You may create helper functions such as:

decide_action(front_blocked, left_blocked, right_blocked, goal_direction)

However, other programs must only call:

decide_next_move(state)

The decide_next_move(state) function must return only one of:

FORWARD
LEFT
RIGHT
STOP

IMPORTANT DECISION ORDER:

1. FIRST check the goal flags.

2. If goal_ahead is True and front_blocked is False:
   return "FORWARD".

3. If goal_on_left is True and left_blocked is False:
   return "LEFT".

4. If goal_on_right is True and right_blocked is False:
   return "RIGHT".

5. ONLY when the goal direction is blocked or unknown,
   use this fallback order:

   FORWARD
   LEFT
   RIGHT

6. Never move into a blocked direction.

7. If front, left, and right are all blocked:
   return "STOP".

IMPORTANT:
Do NOT automatically return FORWARD just because the front is clear.
The goal direction must always be checked first.

Example:

If state is:

{
    "goal_ahead": False,
    "goal_on_left": True,
    "goal_on_right": False,
    "front_blocked": False,
    "left_blocked": False,
    "right_blocked": False
}

the result MUST be:

LEFT

It must NOT be FORWARD.

Return Python code only.
Do not use Markdown code blocks.
Do not include explanations before or after the code.
"""


def validate_code(code):

    if not isinstance(code, str):
        raise ValueError("Generated code must be a string.")

    if code.strip() == "":
        raise ValueError("Generated code cannot be empty.")

    try:
        compile(code, "navigation_logic.py", "exec")
    except SyntaxError as error:
        raise ValueError(f"Generated code is not valid Python: {error}")

    if "def decide_next_move" not in code:
        raise ValueError(
            "Generated code must contain a decide_next_move(state) function."
        )

    namespace = {}
    exec(code, namespace)

    if "decide_next_move" not in namespace:
        raise ValueError("decide_next_move function was not created.")

    decide_next_move = namespace["decide_next_move"]

    allowed_actions = {"FORWARD", "LEFT", "RIGHT", "STOP"}

    # Test 1: goal ahead, front clear → FORWARD
    state = {
        "goal_ahead": True,
        "goal_on_left": False,
        "goal_on_right": False,
        "front_blocked": False,
        "left_blocked": False,
        "right_blocked": False
    }
    result = decide_next_move(state)
    if result != "FORWARD":
        raise ValueError(
            "When the goal is ahead and the front is clear, "
            "the action must be FORWARD."
        )
    if result not in allowed_actions:
        raise ValueError("Invalid robot action.")

    # Test 2: goal left, left clear → LEFT
    state = {
        "goal_ahead": False,
        "goal_on_left": True,
        "goal_on_right": False,
        "front_blocked": False,
        "left_blocked": False,
        "right_blocked": False
    }
    result = decide_next_move(state)
    if result != "LEFT":
        raise ValueError(
            "When the goal is left and the left path is clear, "
            "the action must be LEFT."
        )
    if result not in allowed_actions:
        raise ValueError("Invalid robot action.")

    # Test 3: goal right, right clear → RIGHT
    state = {
        "goal_ahead": False,
        "goal_on_left": False,
        "goal_on_right": True,
        "front_blocked": False,
        "left_blocked": False,
        "right_blocked": False
    }
    result = decide_next_move(state)
    if result != "RIGHT":
        raise ValueError(
            "When the goal is right and the right path is clear, "
            "the action must be RIGHT."
        )
    if result not in allowed_actions:
        raise ValueError("Invalid robot action.")

    # Test 4: goal left but left blocked → fallback FORWARD
    state = {
        "goal_ahead": False,
        "goal_on_left": True,
        "goal_on_right": False,
        "front_blocked": False,
        "left_blocked": True,
        "right_blocked": False
    }
    result = decide_next_move(state)
    if result != "FORWARD":
        raise ValueError(
            "When the goal direction is blocked, "
            "the fallback order should start with FORWARD."
        )
    if result not in allowed_actions:
        raise ValueError("Invalid robot action.")

    # Test 5: all blocked → STOP
    state = {
        "goal_ahead": True,
        "goal_on_left": False,
        "goal_on_right": False,
        "front_blocked": True,
        "left_blocked": True,
        "right_blocked": True
    }
    result = decide_next_move(state)
    if result != "STOP":
        raise ValueError(
            "When all directions are blocked, "
            "the action must be STOP."
        )
    if result not in allowed_actions:
        raise ValueError("Invalid robot action.")

    return True


def run_developer(plan):

    if not isinstance(plan, dict):
        raise ValueError("Plan must be a dictionary.")

    plan_text = json.dumps(plan, indent=4)

    prompt = f"""
Create Python navigation code based on the following validated plan:

{plan_text}

The generated code must contain:

decide_next_move(state)

Other programs will use only this function.

Return Python code only.
"""

    response = chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    code = response["message"]["content"].strip()

    if code.startswith("```python"):
        code = code[9:]
    elif code.startswith("```"):
        code = code[3:]

    if code.endswith("```"):
        code = code[:-3]

    code = code.strip()

    validate_code(code)

    return code


def run_developer_revision(
    original_code,
    review_notes,
    benchmark_report,
    requirements,
    plan,
    output_file="navigation_logic_revised.py"
):
    # Check the original navigation code
    if not isinstance(original_code, str) or not original_code.strip():
        raise ValueError("Original navigation code must be a non-empty string.")

    # Convert structured information to text
    review_text = json.dumps(review_notes, indent=4, ensure_ascii=False)
    benchmark_text = json.dumps(benchmark_report, indent=4, ensure_ascii=False)
    requirements_text = json.dumps(requirements, indent=4, ensure_ascii=False)
    plan_text = json.dumps(plan, indent=4, ensure_ascii=False)

    # Build a revision prompt using the five inputs
    prompt = f"""
Revise the existing robot navigation code using the information below.

ORIGINAL NAVIGATION CODE:
{original_code}

REVIEW NOTES:
{review_text}

BENCHMARK REPORT:
{benchmark_text}

REQUIREMENTS:
{requirements_text}

VALIDATED PLAN:
{plan_text}

Instructions:
1. Preserve the original navigation rules unless the feedback
   identifies a necessary correction.
2. Address problems identified in the review notes.
3. Improve the navigation logic based on the benchmark report.
4. Follow the requirements and validated plan.
5. Keep the function decide_next_move(state).
6. Return only valid Python code, without explanations
   or Markdown code blocks.
"""

    # Ask the LLM to generate revised navigation logic
    response = chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    code = response["message"]["content"].strip()

    # Remove Markdown code fences if present
    if code.startswith("```python"):
        code = code[9:]
    elif code.startswith("```"):
        code = code[3:]

    if code.endswith("```"):
        code = code[:-3]

    code = code.strip()

    # Validate the revised code before saving
    validate_code(code)

    # Save the revised navigation logic as a new Python file
    from pathlib import Path

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(code, encoding="utf-8")

    return code
