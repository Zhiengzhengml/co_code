from reviewer_agent import run_reviewer


simulation_report = {
    "total_scenarios": 10,
    "passed_scenarios": 10,
    "failed_scenarios": 0,
    "success_rate": 1.0
}


result = run_reviewer(simulation_report)

print(result)