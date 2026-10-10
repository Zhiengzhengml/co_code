import json
import os
import subprocess
import sys



## Import all the necessary functions from other modules to run the entire pipeline.
import logging
from pathlib import Path
from datetime import datetime
from analyst_agent import run_analyst
from planner_agent import run_planner
from developer_agent import run_developer, run_developer_revision
from reviewer_agent import run_reviewer
from reviewer_benchmark_agent import run_benchmark_reviewer
from runner import run_simulation

try:
    from test_agent import run_test_agent
    TEST_AGENT_AVAILABLE = True
except ImportError:
    TEST_AGENT_AVAILABLE = False

## Write a main function to run the entire pipeline.
## It should create necessary directories, or check that it exists, 
# Then run each agent in sequence, save their outputs to files, and log events.
# Logging events should include the name of the agent and the action taken, such as "Analyst Agent created requirements.json".




def setup_logger():
    logger = logging.getLogger("pipeline")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []

    file_handler = logging.FileHandler("trace.log", mode="w", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("%(message)s"))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def ensure_directories(logger):
    for directory in ("artifacts", "generated"):
        path = Path(directory)
        if path.exists():
            logger.info(f"Directory already exists: {directory}/")
        else:
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directory created: {directory}/")


def save_json(data, filepath, logger, agent_name):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    logger.info(f"{agent_name} created {path.name}")


def load_json(filepath, logger):
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {filepath}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    logger.info(f"Loaded {path.name}")
    return data


def step_load_brief(logger):
    logger.info("=" * 60)
    logger.info("STEP 1: Loading requirements brief")
    logger.info("=" * 60)

    brief_path = Path("brief.txt")

    if not brief_path.exists():
        default_brief = (
            "The robot must navigate from its start position to a target goal. "
            "It can move FORWARD, turn LEFT, turn RIGHT, or STOP. "
            "The robot must avoid obstacles and prioritise movement toward the goal. "
            "If all directions are blocked, the robot must STOP."
        )
        brief_path.write_text(default_brief, encoding="utf-8")
        logger.info("brief.txt not found -> created default brief.txt")
    else:
        logger.info("Loaded existing brief.txt")

    brief_text = brief_path.read_text(encoding="utf-8")
    logger.info(f"Brief length: {len(brief_text)} characters")
    return brief_text


def step_analyst(logger, brief_text):
    logger.info("=" * 60)
    logger.info("STEP 2: Running Analyst Agent")
    logger.info("=" * 60)

    requirements = run_analyst(brief_text)

    save_json(requirements, "artifacts/requirements.json",
              logger, "Analyst Agent")
    return requirements


def step_planner(logger, requirements):
    logger.info("=" * 60)
    logger.info("STEP 3: Running Planner Agent")
    logger.info("=" * 60)

    plan = run_planner(requirements)

    save_json(plan, "artifacts/plan.json", logger, "Planner Agent")
    return plan


def step_developer(logger, plan):
    logger.info("=" * 60)
    logger.info("STEP 4: Running Developer Agent")
    logger.info("=" * 60)

    code = run_developer(plan)

    Path("navigation_logic.py").write_text(code, encoding="utf-8")
    logger.info("Developer Agent created navigation_logic.py")

    Path("generated").mkdir(exist_ok=True)
    Path("generated/navigation_logic.py").write_text(code, encoding="utf-8")
    logger.info("Developer Agent created generated/navigation_logic.py")

    return code


def step_test_agent(logger, requirements, plan):
    logger.info("=" * 60)
    logger.info("STEP 5: Running Test Agent")
    logger.info("=" * 60)

    if not TEST_AGENT_AVAILABLE:
        logger.warning("Test Agent not available - skipping this step")
        return None

    test_code = run_test_agent(requirements, plan)

    Path("test_generated_navigation_logic.py").write_text(
        test_code, encoding="utf-8"
    )
    logger.info("Test Agent created test_generated_navigation_logic.py")
    return test_code


def step_simulation(logger):
    logger.info("=" * 60)
    logger.info("STEP 6: Running Simulation")
    logger.info("=" * 60)

    report = run_simulation()

    save_json(report, "artifacts/simulation_report.json",
              logger, "Simulation Runner")

    logger.info(
        f"Simulation summary: {report['passed']}/{report['total_scenarios']} "
        f"passed (success rate = {report['success_rate']:.2%})"
    )
    return report


def step_reviewer(logger, simulation_report):
    logger.info("=" * 60)
    logger.info("STEP 7: Running Reviewer Agent")
    logger.info("=" * 60)

    review_notes = run_reviewer(simulation_report)

    save_json(review_notes, "artifacts/review_notes.json",
              logger, "Reviewer Agent")

    logger.info(f"Reviewer needs_revision = {review_notes['needs_revision']}")
    return review_notes


def step_irsim_benchmark(logger):
    logger.info("=" * 60)
    logger.info("STEP 8: Running IR-SIM benchmark")
    logger.info("=" * 60)

    benchmark_script = Path("benchmark_irsim.py")

    if benchmark_script.exists():
        logger.info("Launching benchmark_irsim.py ...")
        result = subprocess.run(
            [sys.executable, "benchmark_irsim.py"],
            capture_output=True, text=True, encoding="utf-8"
        )
        for line in (result.stdout or "").strip().splitlines():
            logger.info(f"  [benchmark] {line}")
        for line in (result.stderr or "").strip().splitlines():
            logger.warning(f"  [benchmark stderr] {line}")

        if result.returncode != 0:
            raise RuntimeError(
                f"benchmark_irsim.py failed (exit {result.returncode})"
            )
    else:
        logger.warning(
            "benchmark_irsim.py not found - creating placeholder report"
        )
        placeholder = {
            "total_worlds": 4,
            "goals_reached": 0,
            "success_rate": 0.0,
            "efficient_worlds": 0,
            "inefficient_success_worlds": 0,
            "failed_worlds": 4,
            "efficiency_rate": 0.0,
            "average_steps_taken": 0,
            "results": [
                {"world": w, "reached_goal": False,
                 "collision_or_done": False, "steps_taken": 0}
                for w in ("easy", "medium", "difficult", "custom")
            ],
        }
        save_json(placeholder, "artifacts/irsim_benchmark_report.json",
                  logger, "IR-SIM Benchmark")

    benchmark_report = load_json(
        "artifacts/irsim_benchmark_report.json", logger
    )
    return benchmark_report


def step_benchmark_reviewer(logger, benchmark_report):
    logger.info("=" * 60)
    logger.info("STEP 9: Running Benchmark Reviewer")
    logger.info("=" * 60)

    benchmark_review = run_benchmark_reviewer(benchmark_report)

    save_json(benchmark_review, "artifacts/benchmark_review.json",
              logger, "Benchmark Reviewer")

    logger.info(
        f"Benchmark Reviewer needs_revision = "
        f"{benchmark_review['needs_revision']}"
    )
    return benchmark_review


def step_developer_revision(logger, requirements, plan,
                            review_notes, benchmark_report,
                            benchmark_review):
    logger.info("=" * 60)
    logger.info("STEP 10: Checking whether revision is required")
    logger.info("=" * 60)

    needs_revision = (
        review_notes.get("needs_revision", False)
        or benchmark_review.get("needs_revision", False)
    )

    if not needs_revision:
        logger.info("No revision required - navigation logic passed all checks")
        return None

    logger.info("Revision required - launching Developer Revision")

    original_code = Path("navigation_logic.py").read_text(encoding="utf-8")

    revised_code = run_developer_revision(
        original_code=original_code,
        review_notes=review_notes,
        benchmark_report=benchmark_report,
        requirements=requirements,
        plan=plan,
        output_file="navigation_logic_revised.py",
    )

    Path("generated").mkdir(exist_ok=True)
    Path("generated/navigation_logic_revised.py").write_text(
        revised_code, encoding="utf-8"
    )
    logger.info("Developer Revision created navigation_logic_revised.py")
    logger.info(
        "Developer Revision created generated/navigation_logic_revised.py"
    )
    return revised_code


def main():
    logger = setup_logger()

    logger.info("=" * 60)
    logger.info("ROBOT NAVIGATION PIPELINE - START")
    logger.info(f"Started at: {datetime.now().isoformat(timespec='seconds')}")
    logger.info("=" * 60)

    try:
        ensure_directories(logger)

        brief_text        = step_load_brief(logger)
        requirements      = step_analyst(logger, brief_text)
        plan              = step_planner(logger, requirements)
        step_developer(logger, plan)
        step_test_agent(logger, requirements, plan)
        simulation_report = step_simulation(logger)
        review_notes      = step_reviewer(logger, simulation_report)
        benchmark_report  = step_irsim_benchmark(logger)
        benchmark_review  = step_benchmark_reviewer(logger, benchmark_report)
        step_developer_revision(
            logger, requirements, plan,
            review_notes, benchmark_report, benchmark_review
        )

        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info(f"Finished at: {datetime.now().isoformat(timespec='seconds')}")
        logger.info("=" * 60)
        return 0

    except Exception as exc:
        logger.error("=" * 60)
        logger.error(f"PIPELINE FAILED: {exc}")
        logger.error(f"Failed at: {datetime.now().isoformat(timespec='seconds')}")
        logger.error("=" * 60)

        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())