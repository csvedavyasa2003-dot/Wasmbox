"""Run while app.py is running:  python test_suite.py
Prints a results table and writes test_report.md (paste into your report)."""
import statistics, time
import requests

BASE = "http://127.0.0.1:5000"


def run(code):
    t = time.perf_counter()
    r = requests.post(f"{BASE}/run", json={"code": code}, timeout=30)
    d = r.json()
    d["wall_ms"] = round((time.perf_counter() - t) * 1000, 1)
    return d


# (name, category, code, expectation text, check function)
TESTS = [
    ("Happy path", "E2E", 'print("hello-from-plugin")',
     "stdout returned", lambda d: d["status"] == "ok" and "hello-from-plugin" in d["stdout"]),
    ("Read /etc/passwd", "Security", 'print(open("/etc/passwd").read())',
     "blocked, no file contents", lambda d: "root:" not in d["stdout"] and d["status"] != "timeout"),
    ("Read host home dir", "Security", 'import os\nprint(os.listdir("/"))',
     "only sandbox dirs visible", lambda d: "home" not in d["stdout"] and "etc" not in d["stdout"]),
    ("Write to filesystem", "Security", 'open("/hacked.txt","w").write("x")\nprint("WROTE")',
     "write denied", lambda d: "WROTE" not in d["stdout"]),
    ("External socket", "Security",
     'import socket\ns=socket.socket()\ns.connect(("8.8.8.8",53))\nprint("CONNECTED")',
     "connection denied", lambda d: "CONNECTED" not in d["stdout"]),
    ("Infinite loop", "Resource", "while True:\n    pass",
     "killed by timeout", lambda d: d["status"] == "timeout"),
    ("Memory bomb", "Resource",
     'x=[]\ntry:\n    while True: x.append("A"*1000000)\nexcept MemoryError:\n    print("CONTAINED")',
     "MemoryError or kill, host survives", lambda d: "CONTAINED" in d["stdout"] or d["status"] in ("timeout", "error")),
    ("Syntax error", "E2E", "def broken(:\n    pass",
     "clean error returned", lambda d: d["status"] == "error" and "SyntaxError" in d["stderr"]),
    ("Empty code", "E2E", "   ",
     "clean error returned", lambda d: d["status"] == "error"),
]

rows, passed = [], 0
for name, cat, code, expect, check in TESTS:
    d = run(code)
    ok = bool(check(d))
    passed += ok
    rows.append((name, cat, expect, f'{d["status"]} ({d["ms"]} ms)', "PASS" if ok else "FAIL"))
    print(f'{"PASS" if ok else "FAIL":5} {name:22} {d["status"]:8} {d["ms"]} ms')

# Server must still be healthy after all the attacks
alive = run('print("still-alive")')["stdout"].strip() == "still-alive"
rows.append(("Host healthy after attacks", "Resilience", "server still works", "yes" if alive else "no",
             "PASS" if alive else "FAIL"))
passed += alive

# Performance: first (cold) vs 30 warm runs
print("\nPerformance (30 runs)...")
times = sorted(run('print("ok")')["ms"] for _ in range(30))
avg, p95, mx, mn = statistics.mean(times), times[int(len(times) * 0.95) - 1], times[-1], times[0]
print(f"avg {avg:.1f} ms | min {mn} | p95 {p95} | max {mx}")

total = len(rows)
md = ["# WasmBox Test Report", "", f"**Result: {passed}/{total} tests passed**", "",
      "| # | Test | Category | Expected | Actual | Result |", "|---|------|----------|----------|--------|--------|"]
for i, r in enumerate(rows, 1):
    md.append(f"| {i} | {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} |")
md += ["", "## Performance (30 runs of a hello-world plugin)", "",
       f"- Average: {avg:.1f} ms", f"- Min: {mn} ms", f"- p95: {p95} ms", f"- Max: {mx} ms", ""]
open("test_report.md", "w").write("\n".join(md))
print(f"\n{passed}/{total} passed. Report saved to test_report.md")