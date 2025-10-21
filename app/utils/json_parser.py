import json, re

def robust_json_loads(text: str):
    """Extrai e parseia a primeira lista JSON presente no texto."""
    try:
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if not match:
            raise ValueError("Nenhum array JSON detectado na resposta.")
        return json.loads(match.group(0))
    except Exception as e:
        raise ValueError(f"Falha ao parsear JSON da LLM: {e}\nTexto bruto:\n{text}")
