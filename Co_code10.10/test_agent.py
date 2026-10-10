
### Create a system prompt that instructs the Test Agent to generate pytest-style tests for the decide_next_move function, 
# based on the requirements and plan provided. 
# The prompt should specify the expected input structure and required test coverage, 
# while also enforcing constraints on the output format.


## Write a function to validate the generated test code. 
# It should check that the code is a non-empty string, does not contain markdown fences, 
# Also check that the test code includes all the necessary keywords like the import statements and test assertions.


## Write a function to run the Test Agent. 
# It should take in requirements and a plan, send them to the Test Agent.
# Thefunction must return the generated test code after validation.
import json
import re
from ollama import chat


SYSTEM_PROMPT = """
You are a Test Agent for a robot navigation system.

Your task is to generate pytest-style tests for a Python function called:

    decide_next_move(state)

The state parameter is a dictionary with exactly these keys:

{
    "goal_ahead": bool,
    "goal_on_left": bool,
    "goal_on_right": bool,
    "front_blocked": bool,
    "left_blocked": bool,
    "right_blocked": bool
}

At most one of goal_ahead, goal_on_left, goal_on_right is True.
If none is True, the goal direction is unknown.

decide_next_move(state) must return exactly one of these strings:

    "FORWARD"
    "LEFT"
    "RIGHT"
    "STOP"

Decision rules:
1. If goal_ahead is True and front_blocked is False -> "FORWARD".
2. If goal_on_left is True and left_blocked is False -> "LEFT".
3. If goal_on_right is True and right_blocked is False -> "RIGHT".
4. If the goal direction is blocked or unknown, use fallback order:
   FORWARD, LEFT, RIGHT.
5. Never move into a blocked direction.
6. If all three directions are blocked -> "STOP".

You must generate tests covering ALL of the following scenarios:

1. goal ahead, front clear -> FORWARD
2. goal left, left clear -> LEFT
3. goal right, right clear -> RIGHT
4. goal ahead but front blocked, left clear -> LEFT (fallback)
5. goal ahead but front and left blocked, right clear -> RIGHT (fallback)
6. goal left but left blocked, front clear -> FORWARD (fallback)
7. goal right but right blocked, front clear -> FORWARD (fallback)
8. goal unknown (all goal flags False), front clear -> FORWARD
9. all three directions blocked -> STOP

Strict output rules:
- Return ONLY Python code.
- Do NOT use Markdown code fences (no ```python, no ```).
- Do NOT include explanations before or after the code.
- The code must be valid Python 3.
- The code must import the function as:
      from navigation_logic import decide_next_move
- Every test function must start with "test_".
- Use assert statements.
- Do not use pytest fixtures, only plain assert.
"""


def validate_test_code(code):
    """
    检查 LLM 生成的测试代码是否合规。
    """
    if not isinstance(code, str):
        raise ValueError("Test code must be a string.")

    if code.strip() == "":
        raise ValueError("Test code cannot be empty.")

    if "```" in code:
        raise ValueError("Test code must not contain Markdown code fences.")

    required_keywords = [
        "import",
        "decide_next_move",
        "def test_",
        "assert",
    ]
    for kw in required_keywords:
        if kw not in code:
            raise ValueError(f"Test code is missing required keyword: {kw!r}")

    try:
        compile(code, "generated_tests.py", "exec")
    except SyntaxError as e:
        raise ValueError(f"Test code is not valid Python: {e}")

    return True


def _strip_code_fences(text):
    """
    去掉 LLM 可能添加的 Markdown 代码围栏。
    """
    text = text.strip()

    # ```python ... ```
    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1:]
        else:
            text = ""

    # 去掉结尾围栏
    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


def run_test_agent(requirements, plan):
    """
    根据 requirements 和 plan 生成 pytest 测试代码。
    返回经过验证的测试代码字符串。
    """
    if not isinstance(requirements, dict):
        raise ValueError("requirements must be a dictionary.")

    if not isinstance(plan, dict):
        raise ValueError("plan must be a dictionary.")

    requirements_text = json.dumps(requirements, indent=4, ensure_ascii=False)
    plan_text = json.dumps(plan, indent=4, ensure_ascii=False)

    prompt = f"""
Generate a single Python file containing pytest-style tests
for decide_next_move(state).

VALIDATED REQUIREMENTS:
{requirements_text}

VALIDATED PLAN:
{plan_text}

Cover all nine scenarios listed in the system prompt.

Return only the Python code, no Markdown fences, no explanations.
"""

    response = chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )

    raw = response["message"]["content"]
    code = _strip_code_fences(raw)

    validate_test_code(code)
    return code


if __name__ == "__main__":
    from pathlib import Path

    req_path = Path("artifacts/requirements.json")
    plan_path = Path("artifacts/plan.json")

    if not req_path.exists() or not plan_path.exists():
        raise FileNotFoundError(
            "Please run Analyst and Planner agents first to produce "
            "artifacts/requirements.json and artifacts/plan.json."
        )

    # 用 utf-8-sig 兼容 Windows PowerShell 写的带 BOM 的 JSON
    with open(req_path, "r", encoding="utf-8-sig") as f:
        requirements = json.load(f)
    with open(plan_path, "r", encoding="utf-8-sig") as f:
        plan = json.load(f)

    code = run_test_agent(requirements, plan)

    out_path = Path("test_generated_navigation_logic.py")
    out_path.write_text(code, encoding="utf-8")

    print("Generated test code saved to:", out_path)
    print()
    print(code)