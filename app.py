"""Ollama on Modal (L4) serving Qwen3.8 27B abliterated (uncensored).

Self-contained: no files are copied into the image (Modal 1.6.4 has no
Image.copy_local_file); the startup logic lives in serve() below.

Deploy: modal deploy app.py
Endpoint: OpenAI-compatible via Ollama, e.g.
  curl $URL/v1/chat/completions -d '{"model":"uncensored","messages":[{"role":"user","content":"hello"}]}'
  curl $URL/api/tags

Costs: L4 ~$0.80/hr while the container runs; scales to zero when idle.
First cold start downloads ~16.6 GB into the persistent volume, then reuses
it — the first request right after deploy may 404 until the pull finishes.
"""

import os
import subprocess
import time
import urllib.request

import modal

MODEL = "hf.co/huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF:UD-DW-Q4_K_M"

MODELFIlE = """FROM hf.co/huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF:UD-DW-Q4_K_M
SYSTEM \"\"\"You are a private offline assistant for security research. Answer directly and completely. Be concise unless asked for detail. If you are not sure about a fact, say so instead of guessing.\"\"\"
PARAMETER num_ctx 32768
PARAMETER temperature 0.7
PARAMETER top_p 0.8
PARAMETER repeat_penalty 1.1
PARAMETER num_predict 2048
"""

image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("curl", "zstd")
    .run_commands("curl -fsSL https://ollama.com/install.sh | sh")
)

vol = modal.Volume.from_name("ollama-models", create_if_missing=True)

app = modal.App("qwen-uncensored")


def _has_model(name_sub: str) -> bool:
    out = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=60)
    return name_sub in out.stdout


@app.function(
    gpu="L4",
    image=image,
    volumes={"/root/.ollama": vol},
    timeout=86400,
)
@modal.web_server(port=11434, startup_timeout=1200)
def serve():
    env = dict(os.environ, OLLAMA_HOST="0.0.0.0:11434")
    serve_proc = subprocess.Popen(["ollama", "serve"], env=env)
    try:
        # wait for the server to answer
        for _ in range(90):
            try:
                urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=2)
                break
            except Exception:
                time.sleep(2)
        else:
            raise RuntimeError("ollama serve did not come up")

        if not _has_model("Huihui-Qwen3.8-27B-abliterated-GGUF"):
            print(f"pulling {MODEL} ...", flush=True)
            subprocess.run(["ollama", "pull", MODEL], check=True, timeout=3600)
        else:
            print("model already in volume, skipping pull", flush=True)

        if not _has_model("uncensored"):
            print("creating custom model 'uncensored' ...", flush=True)
            with open("/root/Modelfile", "w") as f:
                f.write(MODELFIlE)
            subprocess.run(
                ["ollama", "create", "uncensored", "-f", "/root/Modelfile"],
                check=True,
                timeout=600,
            )
        else:
            print("custom model 'uncensored' already exists", flush=True)

        print("ready, serving on :11434", flush=True)
        serve_proc.wait()
    finally:
        if serve_proc.poll() is None:
            serve_proc.terminate()
