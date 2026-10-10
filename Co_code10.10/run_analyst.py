import json
from pathlib import Path

from analyst_agent import run_analyst


# Read the brief text


brief_text = Path("brief.txt").read_text(encoding="utf-8")


# Call the Analyst Agent
requirements = run_analyst(brief_text)


# Create the artifacts folder if it does not exist
Path("artifacts").mkdir(exist_ok=True)


# Save the validated requirements
with open("artifacts/requirements.json", "w", encoding="utf-8") as file:
    json.dump(requirements, file, indent=4)


print("Requirements saved to artifacts/requirements.json")