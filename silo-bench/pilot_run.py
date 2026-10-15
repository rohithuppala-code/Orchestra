"""ORCHESTRA Pilot Run: First end-to-end benchmark test."""
import json
import os
import time

from src.engine import init_case, run_round

print("=== ORCHESTRA Pilot: I-01_n2, P2P protocol, gemma4:e2b ===")
print()

task_file = "benchmarks/I-01_n2.json"
start = time.time()

print("Initializing case...")
case_dir = init_case(
    task_file=task_file,
    protocol="msg",
    max_rounds=10,
    workspace="workspace",
)
print(f"Case dir: {case_dir}")
print(f"Init time: {time.time()-start:.1f}s")
print()

# Run rounds
for r in range(10):
    round_start = time.time()
    print(f"Running round {r+1}...")
    done = run_round(case_dir)
    elapsed = time.time() - round_start
    print(f"  Round {r+1} done in {elapsed:.1f}s (total: {time.time()-start:.1f}s)")
    if done:
        print("  Case completed!")
        break
    print()

total = time.time() - start
print(f"\nTotal time: {total:.1f}s")

# Check results
results_file = os.path.join(case_dir, "results.json")
if os.path.exists(results_file):
    with open(results_file) as f:
        results = json.load(f)
    print(f"Success: {results['success']}")
    print(f"Metrics: {json.dumps(results['metrics'], indent=2)}")
    print(f"Submissions: {json.dumps(results['submissions'], indent=2)}")
    print(f"Ground truth: {results['ground_truth']}")
else:
    print("No results.json found (case may not have completed)")
    meta_file = os.path.join(case_dir, "metadata.json")
    with open(meta_file) as f:
        meta = json.load(f)
    print(f"Status: {meta['execution']['status']}")
    print(f"Current round: {meta['execution']['current_round']}")
