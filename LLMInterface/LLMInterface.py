import requests
import json

MODEL = "deepseek-coder-v2:16b"

def send_class_to_llm(class_text: str, system_prompt: str, project_context: str = "", file_path: str = "") -> str:
    url = f"http://localhost:11434/api/generate"
    
    # Construct the prompt with file path if provided
    prompt = class_text
    if file_path:
        prompt = f"""FILE: {file_path}

{class_text}"""
    
    payload = {
        "model": MODEL,
        "prompt": prompt,
    }
    
    # Add project context to the system prompt if provided
    full_system_prompt = system_prompt
    if project_context:
        full_system_prompt = f"""{system_prompt}
---
PROJECT CONTEXT:
The following is the project's README that provides overall context:

{project_context}

"""
    
    payload["system"] = full_system_prompt

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
