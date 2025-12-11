import re
import statistics
import subprocess
import time


def run_wrk(url="http://127.0.0.1:5000/", duration="10s", connections="100"):
    print(f"Running wrk on {url} (Duration: {duration}, Connections: {connections})...")
    result = subprocess.run(
        ["wrk", "-d", duration, "-c", connections, "-t", "2", url],
        capture_output=True,
        text=True,
    )
    output = result.stdout
    # Parse requests/sec
    match = re.search(r"Requests/sec:\s+([\d\.]+)", output)
    if match:
        rps = float(match.group(1))
        print(f"Result: {rps} Requests/sec")
        return rps
    else:
        print("Failed to parse wrk output")
        print(output)
        return None


def main():
    runs = 5
    results = []

    print(f"Starting benchmark ({runs} runs)...")
    for i in range(runs):
        print(f"\nRun {i + 1}/{runs}")
        rps = run_wrk()
        if rps:
            results.append(rps)
        time.sleep(1)  # Cool down

    if results:
        avg_rps = statistics.mean(results)
        stdev_rps = statistics.stdev(results) if len(results) > 1 else 0
        print("\n" + "=" * 40)
        print("Benchmark Complete")
        print("=" * 40)
        print(f"Runs: {results}")
        print(f"Average RPS: {avg_rps:.2f}")
        print(f"Stdev RPS:   {stdev_rps:.2f}")
    else:
        print("No successful runs.")


if __name__ == "__main__":
    main()
