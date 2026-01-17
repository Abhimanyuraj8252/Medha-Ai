import os
import json
import time
import base64
import requests

OPENAI_COMPAT_PROVIDERS = {
    "OpenAI",
    "OpenRouter",
    "Groq",
    "Together",
    "Fireworks",
    "Mistral",
    "DeepSeek",
    "xAI",
    "Gemini (OpenAI Compatible)",
    "OpenAI-Compatible",
    "Perplexity",
    "AnyScale",
    "NVIDIA",
    "Azure OpenAI",
}


def load_config():
    config_path = os.path.join(os.getcwd(), "user_data", "providers.json")
    if not os.path.exists(config_path):
        return {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def generate_text(prompt, model_override=None):
    cfg = load_config()
    ptype = cfg.get("type", "OpenAI-Compatible")
    base = (cfg.get("base_url") or "").strip()
    key = (cfg.get("api_key") or "").strip()
    model = model_override or cfg.get("model")
    custom_endpoint = (cfg.get("custom_endpoint") or "").strip()

    if not prompt:
        return "Prompt is empty."

    if ptype == "Azure OpenAI":
        url = custom_endpoint or f"{base.rstrip('/')}/{model}/chat/completions?api-version=2024-02-15-preview"
        headers = {"api-key": key, "Content-Type": "application/json"}
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        }
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        res.raise_for_status()
        data = res.json()
        return data["choices"][0]["message"]["content"]

    if ptype in OPENAI_COMPAT_PROVIDERS:
        url = custom_endpoint or f"{base.rstrip('/')}/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        }
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        res.raise_for_status()
        data = res.json()
        return data["choices"][0]["message"]["content"]

    # HuggingFace
    url = custom_endpoint or f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {key}"}
    res = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=60)
    res.raise_for_status()
    data = res.json()
    return data[0].get("generated_text") if isinstance(data, list) else str(data)


def generate_media(prompt, output_type="image", model_override=None):
    cfg = load_config()
    ptype = cfg.get("type", "OpenAI-Compatible")
    base = (cfg.get("base_url") or "").strip()
    key = (cfg.get("api_key") or "").strip()
    model = model_override or cfg.get("model")
    custom_endpoint = (cfg.get("custom_endpoint") or "").strip()
    ext = (cfg.get("save_ext") or "png").lstrip(".")

    if output_type not in ["image", "audio", "video"]:
        return None, "Unsupported output type"
    if not prompt:
        return None, "Prompt is empty"

    if ptype == "Azure OpenAI":
        if output_type != "image":
            return None, "Azure OpenAI media only supports images via DALL-E"
        url = custom_endpoint or f"{base.rstrip('/')}/{model}/images/generations?api-version=2024-02-15-preview"
        headers = {"api-key": key, "Content-Type": "application/json"}
        payload = {"prompt": prompt}
        res = requests.post(url, headers=headers, json=payload, timeout=120)
        res.raise_for_status()
        data = res.json()
        image_url = data["data"][0].get("url")
        if image_url:
            out_bytes = requests.get(image_url, timeout=60).content
        else:
            b64 = data["data"][0].get("b64_json")
            out_bytes = base64.b64decode(b64)

    elif ptype in OPENAI_COMPAT_PROVIDERS:
        if output_type == "image":
            url = custom_endpoint or f"{base.rstrip('/')}/images/generations"
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            payload = {"model": model, "prompt": prompt}
            res = requests.post(url, headers=headers, json=payload, timeout=120)
            res.raise_for_status()
            data = res.json()
            image_url = data["data"][0].get("url")
            if image_url:
                out_bytes = requests.get(image_url, timeout=60).content
            else:
                b64 = data["data"][0].get("b64_json")
                out_bytes = base64.b64decode(b64)
        else:
            if not custom_endpoint:
                return None, "Custom endpoint required for audio/video"
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            payload = {"model": model, "prompt": prompt}
            res = requests.post(custom_endpoint, headers=headers, json=payload, timeout=300)
            res.raise_for_status()
            out_bytes = res.content
    else:
        # HuggingFace
        url = custom_endpoint or f"https://api-inference.huggingface.co/models/{model}"
        headers = {"Authorization": f"Bearer {key}"}
        res = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=120)
        res.raise_for_status()
        out_bytes = res.content

    out_dir = os.path.join(os.getcwd(), "user_data", "generated")
    os.makedirs(out_dir, exist_ok=True)
    filename = f"gen_{int(time.time())}.{ext}"
    out_path = os.path.join(out_dir, filename)
    with open(out_path, "wb") as f:
        f.write(out_bytes)
    return out_path, None
