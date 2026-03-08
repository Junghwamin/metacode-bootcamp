"""ch9-17 solution_code execution test."""
import json
import subprocess
import sys
import os
import re
import tempfile
import pytest

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT, "data", "problems")


def patch_gui(code):
    """GUI 호출을 비활성화한다."""
    if "matplotlib" in code or "plt" in code:
        code = "import matplotlib\nmatplotlib.use('Agg')\n" + code
    lines = code.split("\n")
    out = []
    for line in lines:
        s = line.strip()
        if s in ("fig.show()", "plt.show()"):
            out.append(line.replace(s, "pass"))
        else:
            out.append(line)
    return "\n".join(out)


def run_sol(code, stdin_data=None, timeout=10):
    """solution_code를 subprocess로 실행한다."""
    code = patch_gui(code)
    fd, tmpfile = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(code)
        result = subprocess.run(
            [sys.executable, tmpfile],
            capture_output=True, text=True, timeout=timeout,
            stdin=subprocess.PIPE, input=stdin_data, cwd=PROJECT,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except Exception as e:
        return -1, "", str(e)
    finally:
        try:
            os.unlink(tmpfile)
        except OSError:
            pass


def load_all():
    """ch9-17 문제를 로드한다."""
    params = []
    for ch in range(9, 18):
        fp = os.path.join(DATA_DIR, "chapter%d_problems.json" % ch)
        if not os.path.exists(fp):
            continue
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)
        for prob in data.get("problems", []):
            params.append(pytest.param(prob, id=prob["problem_id"]))
    return params


@pytest.mark.parametrize("prob", load_all())
def test_solution_runs(prob):
    """solution_code가 에러 없이 실행되는지 테스트한다."""
    code = prob["solution_code"]
    gr = prob.get("grading", {})

    stdin_data = None
    ti = gr.get("test_input", prob.get("test_input", []))
    if isinstance(ti, list) and ti:
        stdin_data = "\n".join(str(x) for x in ti) + "\n"
    elif isinstance(ti, str) and ti:
        stdin_data = ti + "\n"

    rc, out, err = run_sol(code, stdin_data)
    if rc != 0:
        last_err = err.strip().splitlines()[-1] if err.strip() else "unknown"
        pytest.fail(f"Execution error: {last_err}")
