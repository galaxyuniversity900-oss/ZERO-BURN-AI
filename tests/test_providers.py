import os
import pytest
from zeroburn.providers import generate, ProviderError

def test_provider_disabled_by_default(monkeypatch):
    monkeypatch.delenv("ZERO_BURN_PROVIDER",raising=False)
    with pytest.raises(ProviderError,match="No provider configured"):
        generate("hello")

def test_unknown_provider_rejected(monkeypatch):
    monkeypatch.setenv("ZERO_BURN_PROVIDER","mystery")
    with pytest.raises(ProviderError,match="Unsupported provider"):
        generate("hello")

def test_cloud_provider_requires_credentials(monkeypatch):
    monkeypatch.setenv("ZERO_BURN_PROVIDER","openai-compatible")
    for key in ("OPENAI_COMPATIBLE_BASE_URL","OPENAI_COMPATIBLE_MODEL","OPENAI_COMPATIBLE_API_KEY"):
        monkeypatch.delenv(key,raising=False)
    with pytest.raises(ProviderError,match="requires base URL"):
        generate("hello")
