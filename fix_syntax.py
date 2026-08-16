from pathlib import Path

filepath = Path("C:/LofiZen/scripts/pipeline.py")
content = filepath.read_text(encoding="utf-8")

old = 'community_text = f"Nuevo video disponible! {metadata[\\"titulo\\"]} - Escuchalo ahora en FogWindowBeats. Link en el canal. #lofi #estudiar #concentracion"'
new = 'titulo_community = metadata.get("titulo", "nuevo lofi")\n        community_text = f"Nuevo video disponible! {titulo_community} - Escuchalo ahora en FogWindowBeats. Link en el canal. #lofi #estudiar #concentracion"'

if old in content:
    content = content.replace(old, new)
    filepath.write_text(content, encoding="utf-8")
    print("Fix aplicado")
else:
    idx = content.find("community_text")
    print(f"Contexto: {repr(content[max(0,idx-10):idx+150])}")