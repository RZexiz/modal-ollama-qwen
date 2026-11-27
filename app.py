"""Ollama on Modal (L4) serving Qwen3.8 27B abliterated (uncensored).

Deploy: modal deploy app.py
Endpoint: OpenAI-compatible via Ollama, e.g.
  curl $URL/v1/chat/completions -d '{"model":"uncensored","messages":[{"role":"user","content":"hello"}]}'
  curl $URL/api/tags

Costs: L4 ~$0.80/hr while the container runs; scales to zero when idle.
First cold start downloads ~16.6 GB into the persistent volume, then reuses it.
"""

import modal

MODEL = "hf.co/huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF:UD-DW-Q4_K_M"

image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("curl")
    .run_commands("curl -fsSL https://ollama.com/install.sh | sh")
    .copy_local_file("start.sh", "/root/start.sh")
    .copy_local_file("Modelfile", "/root/Modelfile")
    .run_commands("chmod +x /root/start.sh")
)

vol = modal.Volume.from_name("ollama-models", create_if_missing=True)

app = modal.App("qwen-uncensored")


@app.function(
    gpu="L4",
    image=image,
    volumes={"/root/.ollama": vol},
    timeout=3600,
)
@modal.web_server(port=11434, startup_timeout=1200)
def serve():
    import subprocess

    subprocess.run(["/root/start.sh"], check=True)
