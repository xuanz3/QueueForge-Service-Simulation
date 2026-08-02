#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cmake = (root / "engines/simulation-cpp/CMakeLists.txt").read_text(encoding="utf-8")
dockerfile = (root / "engines/simulation-cpp/Dockerfile").read_text(encoding="utf-8")

for item in ["-static-libgcc", "-static-libstdc++"]:
    if item not in cmake:
        raise SystemExit(f"Missing C++ runtime link option: {item}")

runtime_check = "RUN /usr/local/bin/queueforge-sim --health"
if runtime_check not in dockerfile:
    raise SystemExit("Final C++ Docker stage does not execute the runtime health check.")

print("C++ runtime compatibility verification passed.")
