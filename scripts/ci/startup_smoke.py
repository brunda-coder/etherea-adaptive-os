from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    data_dir = Path(env.get("ETHEREA_DATA_DIR", root / "selftest"))
    env["ETHEREA_DATA_DIR"] = str(data_dir)
    env.setdefault("QT_QPA_PLATFORM", "offscreen")

    data_dir.mkdir(parents=True, exist_ok=True)

    cmd = [sys.executable, "etherea_launcher.py", "--self-test"]
    result = subprocess.run(cmd, cwd=root, env=env, check=False)
    marker = data_dir / "self_test_ok.txt"
    if result.returncode != 0 or not marker.exists():
        print("Startup smoke test failed.", file=sys.stderr)
        return 1

    if env.get("ETHEREA_PROFILE_STARTUP") == "1":
        log_path = data_dir / "logs" / "etherea.log"
        if log_path.exists():
            lines = log_path.read_text(encoding="utf-8").splitlines()
            for line in reversed(lines):
                if "Startup profile:" in line:
                    print(line)
                    break

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
