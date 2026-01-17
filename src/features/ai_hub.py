import os
import json
import time
import base64
import requests
import flet as ft


class AIHubView(ft.Column):
    def __init__(self):
        super().__init__()
        self.expand = True
        self._page = None

        self.config_path = os.path.join(os.getcwd(), "user_data", "providers.json")
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

        self.providers = self._load_config()

        self.provider_type = ft.Dropdown(
            label="Provider",
            options=[
                ft.dropdown.Option("OpenAI"),
                ft.dropdown.Option("Anthropic"),
                ft.dropdown.Option("OpenRouter"),
                ft.dropdown.Option("Groq"),
                ft.dropdown.Option("Together"),
                ft.dropdown.Option("Fireworks"),
                ft.dropdown.Option("Mistral"),
                ft.dropdown.Option("DeepSeek"),
                ft.dropdown.Option("xAI"),
                ft.dropdown.Option("Gemini (OpenAI Compatible)"),
                ft.dropdown.Option("OpenAI-Compatible"),
                ft.dropdown.Option("Perplexity"),
                ft.dropdown.Option("AnyScale"),
                ft.dropdown.Option("NVIDIA"),
                ft.dropdown.Option("Azure OpenAI"),
                ft.dropdown.Option("Replicate"),
                ft.dropdown.Option("Stability"),
                ft.dropdown.Option("Cohere"),
                ft.dropdown.Option("AI21"),
                ft.dropdown.Option("SambaNova"),
                ft.dropdown.Option("IBM watsonx"),
                ft.dropdown.Option("AWS Bedrock"),
                ft.dropdown.Option("Cloudflare Workers AI"),
                ft.dropdown.Option("HuggingFace"),
            ],
            value=self.providers.get("type", "OpenAI-Compatible"),
            width=200,
        )

        self.base_url = ft.TextField(
            label="Base URL",
            value=self.providers.get("base_url", "https://openrouter.ai/api/v1"),
            expand=True,
        )
        self.api_key = ft.TextField(
            label="API Key",
            value=self.providers.get("api_key", ""),
            password=True,
            can_reveal_password=True,
            expand=True,
        )

        self.model_dropdown = ft.Dropdown(label="Model", options=[], expand=True)
        self.model_search = ft.TextField(label="HF search keyword (optional)", expand=True)

        self.output_type = ft.Dropdown(
            label="Output Type",
            options=[
                ft.dropdown.Option("text"),
                ft.dropdown.Option("image"),
                ft.dropdown.Option("audio"),
                ft.dropdown.Option("video"),
            ],
            value="text",
            width=150,
        )

        self.custom_endpoint = ft.TextField(
            label="Custom Endpoint (optional)",
            hint_text="Full URL for non-standard APIs",
            expand=True,
        )
        self.save_ext = ft.TextField(label="Save as (ext)", value="png", width=120)
        self.fetch_models_btn = ft.ElevatedButton("Fetch Models", on_click=self.fetch_models)
        self.save_btn = ft.ElevatedButton("Save", on_click=self.save_config)

        self.prompt = ft.TextField(label="Prompt", multiline=True, min_lines=3, expand=True)
        self.response = ft.TextField(label="Output", multiline=True, min_lines=6, expand=True, read_only=True)

        self.generate_text_btn = ft.ElevatedButton("Generate Text", on_click=self.generate_text)
        self.generate_image_btn = ft.ElevatedButton("Generate Image", on_click=self.generate_image)
        self.open_folder_btn = ft.TextButton("Open Saved Folder", on_click=self.open_saved_folder)

        self.status = ft.Text("")

        self.provider_type.on_change = self._on_provider_change

        self.controls = [
            ft.Text("🌐 Universal AI Hub", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_400),
            ft.Row([self.provider_type, self.fetch_models_btn, self.save_btn], spacing=10),
            ft.Row([self.base_url, self.api_key], spacing=10),
            ft.Row([self.model_dropdown, self.output_type, self.save_ext], spacing=10),
            ft.Row([self.model_search], spacing=10),
            ft.Row([self.custom_endpoint], spacing=10),
            ft.Divider(),
            self.prompt,
            ft.Row([self.generate_text_btn, self.generate_image_btn, self.open_folder_btn], spacing=10),
            self.response,
            self.status,
        ]

        self._populate_models_from_cache()

    def did_mount(self):
        self._page = self.page
        if self._page:
            self.update()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            return {}
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_config(self, data):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _populate_models_from_cache(self):
        cached = self.providers.get("models", [])
        if cached:
            self.model_dropdown.options = [ft.dropdown.Option(m) for m in cached]
            if self.providers.get("model"):
                self.model_dropdown.value = self.providers.get("model")

    def save_config(self, e):
        self.providers.update({
            "type": self.provider_type.value,
            "base_url": self.base_url.value.strip(),
            "api_key": self.api_key.value.strip(),
            "model": self.model_dropdown.value,
            "output_type": self.output_type.value,
            "custom_endpoint": self.custom_endpoint.value.strip(),
            "save_ext": self.save_ext.value.strip(),
            "model_search": self.model_search.value.strip(),
        })
        self._save_config(self.providers)
        self.status.value = "✅ Saved configuration."
        self.update()

    def fetch_models(self, e):
        ptype = self.provider_type.value
        base = self.base_url.value.strip()
        key = self.api_key.value.strip()
        search = self.model_search.value.strip()

        self.status.value = "⏳ Fetching models..."
        self.update()

        try:
            if ptype != "HuggingFace":
                url = f"{base.rstrip('/')}/models"
                headers = {"Authorization": f"Bearer {key}"}
                res = requests.get(url, headers=headers, timeout=20)
                res.raise_for_status()
                data = res.json()
                models = [m.get("id") for m in data.get("data", []) if m.get("id")]
            else:
                # HuggingFace search (optional)
                if not search:
                    models = self.providers.get("models", [])
                else:
                    url = f"https://huggingface.co/api/models?search={search}&limit=50"
                    headers = {"Authorization": f"Bearer {key}"} if key else {}
                    res = requests.get(url, headers=headers, timeout=20)
                    res.raise_for_status()
                    data = res.json()
                    models = [m.get("modelId") for m in data if m.get("modelId")]

            self.model_dropdown.options = [ft.dropdown.Option(m) for m in models]
            if models:
                self.model_dropdown.value = models[0]
            self.providers["models"] = models
            self._save_config(self.providers)
            self.status.value = f"✅ Loaded {len(models)} models."
        except Exception as ex:
            self.status.value = f"❌ Model fetch failed: {ex}"
        self.update()

    def generate_text(self, e):
        ptype = self.provider_type.value
        base = self.base_url.value.strip()
        key = self.api_key.value.strip()
        model = self.model_dropdown.value
        prompt = self.prompt.value.strip()
        output_type = self.output_type.value
        custom_endpoint = self.custom_endpoint.value.strip()
        if not prompt:
            return

        if output_type != "text":
            self.response.value = "⚠️ Switch Output Type to 'text' for text generation."
            self.update()
            return

        self.response.value = "⏳ Generating..."
        self.update()

        try:
            if ptype != "HuggingFace":
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
                text = data["choices"][0]["message"]["content"]
            else:
                url = custom_endpoint or f"https://api-inference.huggingface.co/models/{model}"
                headers = {"Authorization": f"Bearer {key}"}
                res = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=60)
                res.raise_for_status()
                data = res.json()
                text = data[0].get("generated_text") if isinstance(data, list) else str(data)

            self.response.value = text
        except Exception as ex:
            self.response.value = f"❌ Error: {ex}"
        self.update()

    def generate_image(self, e):
        ptype = self.provider_type.value
        base = self.base_url.value.strip()
        key = self.api_key.value.strip()
        model = self.model_dropdown.value
        prompt = self.prompt.value.strip()
        output_type = self.output_type.value
        custom_endpoint = self.custom_endpoint.value.strip()
        ext = (self.save_ext.value.strip() or "png").lstrip(".")
        if not prompt:
            return

        if output_type not in ["image", "audio", "video"]:
            self.response.value = "⚠️ Set Output Type to image/audio/video for media generation."
            self.update()
            return

        self.response.value = "⏳ Generating image..."
        self.update()

        try:
            if ptype != "HuggingFace":
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
                        self.response.value = "❌ Provide Custom Endpoint for audio/video."
                        self.update()
                        return
                    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
                    payload = {"model": model, "prompt": prompt}
                    res = requests.post(custom_endpoint, headers=headers, json=payload, timeout=300)
                    res.raise_for_status()
                    out_bytes = res.content
            else:
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

            self.response.value = f"✅ File saved: {out_path}"
        except Exception as ex:
            self.response.value = f"❌ Error: {ex}"
        self.update()

    def open_saved_folder(self, e):
        out_dir = os.path.join(os.getcwd(), "user_data", "generated")
        os.makedirs(out_dir, exist_ok=True)
        try:
            os.startfile(out_dir)
        except Exception:
            pass

    def _on_provider_change(self, e):
        presets = {
            "OpenAI": "https://api.openai.com/v1",
            "Anthropic": "https://api.anthropic.com/v1",
            "OpenRouter": "https://openrouter.ai/api/v1",
            "Groq": "https://api.groq.com/openai/v1",
            "Together": "https://api.together.xyz/v1",
            "Fireworks": "https://api.fireworks.ai/inference/v1",
            "Mistral": "https://api.mistral.ai/v1",
            "DeepSeek": "https://api.deepseek.com/v1",
            "xAI": "https://api.x.ai/v1",
            "Gemini (OpenAI Compatible)": "https://generativelanguage.googleapis.com/v1beta/openai",
            "Perplexity": "https://api.perplexity.ai/v1",
            "AnyScale": "https://api.endpoints.anyscale.com/v1",
            "NVIDIA": "https://integrate.api.nvidia.com/v1",
            "Azure OpenAI": "https://YOUR-RESOURCE.openai.azure.com/openai/deployments",
            "Replicate": "https://api.replicate.com/v1",
            "Stability": "https://api.stability.ai/v1",
            "Cohere": "https://api.cohere.ai/v1",
            "AI21": "https://api.ai21.com/studio/v1",
            "SambaNova": "https://api.sambanova.ai/v1",
            "IBM watsonx": "https://us-south.ml.cloud.ibm.com",
            "AWS Bedrock": "https://bedrock-runtime.us-east-1.amazonaws.com",
            "Cloudflare Workers AI": "https://api.cloudflare.com/client/v4/accounts",
        }
        if self.provider_type.value in presets:
            self.base_url.value = presets[self.provider_type.value]
            self.update()
