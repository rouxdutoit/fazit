# Starts llama.cpp's server for the local review. Listens on this computer only.
# Adjust $Runner and $Model if the files live elsewhere.
$Runner = "$env:USERPROFILE\llm\llama.cpp-b12633\llama-server.exe"
$Model  = "$env:USERPROFILE\llm\models\Qwen3.8-27B-UD-IQ4_XS.gguf"

& $Runner `
  --model $Model `
  --host 127.0.0.1 --port 8080 `
  --ctx-size 32768 --parallel 1 `
  --flash-attn on --cache-type-k q8_0 --cache-type-v q8_0 `
  --fit on `
  --reasoning on --reasoning-budget 8192 `
  --seed 42 `
  --no-webui
