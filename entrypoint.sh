#!/bin/sh
set -eu

# Configurable via environment
#MODEL="${MODEL:-gpt-oss:20b}"
MODEL="${MODEL:-llama3.1:8b}"

echo "Starting default command (ollama serve) and post-start setup..."

# Start the server (default command) in the background.
ollama serve &
main_pid=$!

# Ensure we clean up the background process on container stop
trap 'kill -TERM "$main_pid" 2>/dev/null || true; wait "$main_pid" 2>/dev/null || true' TERM INT

echo "Waiting for Ollama to be ready ..."
# Wait until the daemon responds; using the ollama CLI avoids curl/wget dependency
until ollama list >/dev/null 2>&1; do
  sleep 1
done
echo "Ollama is ready."

# Check if the model is already available; if not, pull with retries until success
if ! ollama list | grep -q "^${MODEL}[[:space:]]"; then
  echo "Pulling model ${MODEL} ..."
  until ollama pull "${MODEL}"; do
    echo "Pull failed, retrying in 5s..."
    sleep 5
  done
  echo "Model ${MODEL} is ready."
else
  echo "Model ${MODEL} already present."
fi

# Keep the server process in the foreground
wait "$main_pid"
