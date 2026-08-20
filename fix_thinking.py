from pathlib import Path

filepath = Path("C:/LofiZen/scripts/pipeline.py")
content = filepath.read_text(encoding="utf-8")

# Fix 1: agregar thinking=False y extraccion defensiva de JSON en generate_metadata_largo
old = '''    r = client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=2000
    )
    return json.loads(r.choices[0].message.content, strict=False)

def generate_metadata_short'''

new = '''    r = client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=2000,
        reasoning_effort="none"
    )
    raw = r.choices[0].message.content
    import re as _re
    raw = _re.sub(r"<think>.*?</think>", "", raw, flags=_re.DOTALL).strip()
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start >= 0 and end > start:
        raw = raw[start:end]
    return json.loads(raw, strict=False)

def generate_metadata_short'''

if old in content:
    content = content.replace(old, new)
    print("Fix largo OK")
else:
    print("ERROR largo no encontrado")

# Fix 2: mismo fix para generate_metadata_short
old2 = '''    r = client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=600
    )
    return json.loads(r.choices[0].message.content, strict=False)'''

new2 = '''    r = client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=600,
        reasoning_effort="none"
    )
    raw = r.choices[0].message.content
    import re as _re
    raw = _re.sub(r"<think>.*?</think>", "", raw, flags=_re.DOTALL).strip()
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start >= 0 and end > start:
        raw = raw[start:end]
    return json.loads(raw, strict=False)'''

if old2 in content:
    content = content.replace(old2, new2)
    print("Fix short OK")
else:
    print("ERROR short no encontrado")

filepath.write_text(content, encoding="utf-8")