# modal-ollama-qwen

Ollama on Modal (L4 GPU) serving **Qwen3.8 27B abliterated** (uncensored,
`huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF`, quant `UD-DW-Q4_K_M`,
16.6 GB) for security-research / bug-bounty work.

## Files

- `app.py` — Modal app, self-contained: L4 GPU, Ollama, persistent volume
  `ollama-models`, web server on :11434 (OpenAI-compatible). The model pull
  and the custom `uncensored` model happen inside `serve()` on first boot.
- `deploy.sh` — VPS deploy helper: installs Modal CLI, sets the token,
  runs `modal deploy`.

## Deploy (from the VPS)

```bash
bash deploy.sh <modal-token-id> <modal-token-secret>
```

## Use

```bash
# chat (OpenAI-compatible)
curl "$URL/v1/chat/completions" \
  -d '{"model":"uncensored","messages":[{"role":"user","content":"hello"}]}'

# list models
curl "$URL/api/tags"
```

## Notes

- First cold start downloads ~16.6 GB into the volume (one-time); later
  starts reuse it. The first request right after deploy may fail until the
  pull finishes — wait a few minutes, then retry.
- Modal 1.6.4 has no `Image.copy_local_file`, so no files are copied into
  the image; everything the server needs is in `app.py`.

## Cost

L4 ~$0.80/hr while the container runs; scales to zero when idle.
