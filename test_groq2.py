import os, json, re
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])
r = client.chat.completions.create(
    model="qwen/qwen3.6-27b",
    messages=[{"role": "user", "content": "Genera JSON con clave 'titulo' valor 'Lofi para estudiar' y clave 'tags' lista de 3 strings"}],
    response_format={"type": "json_object"},
    max_tokens=200,
    reasoning_effort="none"
)
raw = r.choices[0].message.content
raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
start = raw.find("{")
end = raw.rfind("}") + 1
if start >= 0 and end > start:
    raw = raw[start:end]
data = json.loads(raw)
print(f"OK: {data}")