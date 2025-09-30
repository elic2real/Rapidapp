import os
import time
import subprocess

RUNNER_COUNT = int(os.environ.get("RSD_RUNNER_COUNT", "2"))
VARIANT_CONFIGS = [{"name": f"runner_{i}", "variant": i} for i in range(RUNNER_COUNT)]

def schedule_runners():
    procs = []
    for cfg in VARIANT_CONFIGS:
        proc = subprocess.Popen([
            "python", "-m", "zdf.services.rsd.runner.observer",
            "--variant", str(cfg["variant"])
        ])
        procs.append(proc)
    for proc in procs:
        proc.wait()

if __name__ == "__main__":
    schedule_runners()