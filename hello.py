"""Minimal web_server control test: same Popen+return pattern as app.py,
but serving a trivial static HTTP server instead of ollama. If this
endpoint answers and qwen-uncensored does not, the problem is ollama-side;
if this also hangs, the problem is the web_server pattern / account / region.
"""

import subprocess

import modal

app = modal.App("hello-test")


@app.function()
@modal.web_server(port=8000, startup_timeout=60)
def serve():
    subprocess.Popen(["python3", "-m", "http.server", "8000"])
    return
