import requests
import json

MODEL = "mistral"

def send_class_to_llm(class_text: str, system_prompt: str) -> str:
    url = f"http://localhost:11434/api/generate"
    payload = {
        "model": MODEL,
        "prompt": class_text,
    }
    payload["system"] = system_prompt

    response = requests.post(url, json=payload, stream=True)
    response.raise_for_status()
    result_text = ""
    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode("utf-8"))
                if "response" in data:
                    result_text += data["response"]
                if data.get("done"):
                    break
            except Exception:
                continue
    return result_text.strip()
