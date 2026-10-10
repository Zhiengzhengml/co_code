
import json
from pathlib import Path

from reviewer_agent import run_reviewer
from reviewer_benchmark_agent import run_benchmark_reviewer


ARTIFACTS = Path(__file__).resolve().parent / "artifacts"


def load_report(filename):
    path = ARTIFACTS / filename

    if not path.exists():
        raise FileNotFoundError(f"Missing report: {path}")

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_report(filename, data):
    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    with open(ARTIFACTS / filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main():

    # Step 1: Load B's real reports
    simulation_report = load_report(
        "simulation_report.json"
    )

    benchmark_report = load_report(
        "irsim_benchmark_report.json"
    )

    # Step 2: Check report consistency
    simulation_results = simulation_report["results"]
    benchmark_results = benchmark_report["results"]

    if simulation_report["total_scenarios"] != len(simulation_results):
        raise ValueError("Simulation scenario count mismatch.")

    if simulation_report["passed"] != sum(
        result["passed"] for result in simulation_results
    ):
        raise ValueError("Simulation passed count mismatch.")

    if benchmark_report["total_worlds"] != len(benchmark_results):
        raise ValueError("Benchmark world count mismatch.")

    if benchmark_report["goals_reached"] != sum(
        result["reached_goal"] for result in benchmark_results
    ):
        raise ValueError("Benchmark goal count mismatch.")

    print("Reports loaded and checked successfully.")

    # Step 3: Run the normal Reviewer
    print("\nRunning Reviewer Agent...")

    review_notes = run_reviewer(simulation_report)

    print(json.dumps(review_notes, indent=4))

    # Step 4: Run the Benchmark Reviewer
    print("\nRunning Benchmark Reviewer...")

    benchmark_review = run_benchmark_reviewer(
        benchmark_report
    )

    print(json.dumps(benchmark_review, indent=4))

    # Step 5: Check Reviewer decisions
    expected_revision = simulation_report["failed"] > 0

    if review_notes["needs_revision"] != expected_revision:
        raise ValueError(
            "Reviewer decision conflicts with simulation results."
        )

    expected_benchmark_revision = not all([
        benchmark_review["safety_passed"],
        benchmark_review["goal_completion_passed"],
        benchmark_review["efficiency_passed"]
    ])

    if benchmark_review["needs_revision"] != expected_benchmark_revision:
        raise ValueError(
            "Benchmark Reviewer decision is inconsistent."
        )

    # Step 6: Save review outputs
    save_report("review_notes.json", review_notes)

    save_report("benchmark_review.json", benchmark_review)

    print("\nBoth review reports saved successfully.")

    # Step 7: Decide whether revision is needed
    needs_revision = (
        review_notes["needs_revision"]
        or benchmark_review["needs_revision"]
    )

    if needs_revision:
        print("\nRevision is required.")
        print("Developer Revision should run next.")
    else:
        print("\nNo revision required.")
        print("Original navigation code meets current test criteria.")

    print("\nA+B integration test completed.")


if __name__ == "__main__":
    main()
