"""Opt-in model adapters. Ollama is local by default; cloud-compatible mode is explicit."""
from __future__ import annotations
import json, os
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

class ProviderError(RuntimeError): pass

def generate(prompt: str) -> dict:
    provider=os.getenv("ZERO_BURN_PROVIDER","").strip().lower()
    if not provider:
        raise ProviderError("No provider configured. Set ZERO_BURN_PROVIDER=ollama to opt in.")
    timeout=max(1,min(int(os.getenv("ZERO_BURN_PROVIDER_TIMEOUT","60")),180))
    if provider=="ollama":
        base=os.getenv("OLLAMA_BASE_URL","http://127.0.0.1:11434").rstrip("/")
        model=os.getenv("OLLAMA_MODEL","qwen2.5-coder:7b")
        payload={"model":model,"prompt":prompt,"stream":False}
        url=base+"/api/generate"
        headers={"Content-Type":"application/json"}
    elif provider=="openai-compatible":
        # This may incur charges. The user must explicitly enable it and supply a base URL/key.
        base=os.getenv("OPENAI_COMPATIBLE_BASE_URL","").rstrip("/")
        model=os.getenv("OPENAI_COMPATIBLE_MODEL","")
        key=os.getenv("OPENAI_COMPATIBLE_API_KEY","")
        if not base or not model or not key:
            raise ProviderError("Cloud provider requires base URL, model, and API key environment variables.")
        url=base+"/chat/completions"
        payload={"model":model,"messages":[{"role":"user","content":prompt}],"stream":False}
        headers={"Content-Type":"application/json","Authorization":"Bearer "+key}
    else:
        raise ProviderError("Unsupported provider. Supported: ollama, openai-compatible.")
    req=Request(url,data=json.dumps(payload).encode(),headers=headers,method="POST")
    try:
        with urlopen(req,timeout=timeout) as response:
            data=json.loads(response.read(2_000_000).decode("utf-8"))
    except (URLError,HTTPError,TimeoutError,ValueError) as exc:
        raise ProviderError(f"Provider request failed: {type(exc).__name__}") from exc
    if provider=="ollama":
        answer=data.get("response","")
        usage={"prompt_tokens":data.get("prompt_eval_count"),"completion_tokens":data.get("eval_count")}
    else:
        choices=data.get("choices") or []
        answer=(choices[0].get("message") or {}).get("content","") if choices else ""
        usage=data.get("usage",{})
    if not isinstance(answer,str) or not answer.strip():
        raise ProviderError("Provider returned an empty or invalid answer.")
    return {"provider":provider,"model":model,"text":answer,
            "usage":usage,"cost_usd":None,
            "notice":"Provider-reported token usage is informational; cost is not estimated unless the provider supplies authoritative pricing."}
