from pathlib import Path
import ollama


# Read brief.txt
brief_text = Path("brief.txt").read_text(encoding="utf-8")


prompt = f"""
Read the following software brief and convert it into clear software requirements.

Brief:
{brief_text}
"""


response = ollama.chat(
    model="qwen3:8b",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)


requirements = response["message"]["content"]

print(requirements)


# Save the Qwen output
Path("robot_requirements.txt").write_text(
    requirements,
    encoding="utf-8"
)