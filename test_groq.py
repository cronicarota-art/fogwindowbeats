import os
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])
r = client.chat.completions.create(
    model="qwen/qwen3.6-27b",
    messages=[{"role": "user", "content": "Di hola en una palabra"}],
    max_tokens=50
)
print(f"OK: {r.choices[0].message.content}")