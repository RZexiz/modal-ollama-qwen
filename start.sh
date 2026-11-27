#!/bin/bash
# start.sh — runs inside the Modal container.
# Starts ollama serve, pulls the model into the persistent volume on first
# boot, creates the "uncensored" custom model, then keeps serve in foreground.
set -e
export OLLAMA_HOST=0.0.0.0:11434

ollama serve &
SERVE_PID=$!

# wait for the server to answer
for i in $(seq 1 90); do
  if ollama list >/dev/null 2>&1; then break; fi
  sleep 2
done

MODEL="hf.co/huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF:UD-DW-Q4_K_M"

if ! ollama list 2>/dev/null | grep -q "Huihui-Qwen3.8-27B-abliterated-GGUF"; then
  echo "pulling $MODEL ..."
  ollama pull "$MODEL"
else
  echo "model already in volume, skipping pull"
fi

if ! ollama list 2>/dev/null | grep -q "^uncensored "; then
  echo "creating custom model 'uncensored' ..."
  ollama create uncensored -f /root/Modelfile
else
  echo "custom model 'uncensored' already exists"
fi

echo "ready, serving on :11434"
wait $SERVE_PID
