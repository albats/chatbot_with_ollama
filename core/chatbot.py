from __future__ import annotations

import os
from typing import Any, Iterable, List, Mapping

try:
    from ollama import Client, ResponseError
except ImportError as import_error:
    Client = None
    ResponseError = Exception
    OLLAMA_IMPORT_ERROR = import_error
else:
    OLLAMA_IMPORT_ERROR = None

DEFAULT_MODEL = "gemma3:1b"
DEFAULT_HOST = "http://localhost:11434"


class OllamaConnectionError(RuntimeError):
    pass


class OllamaModelNotAvailableError(RuntimeError):
    pass


class OllamaGenerationError(RuntimeError):
    pass


class ThematicChatbot:
    def __init__(self, model: str = DEFAULT_MODEL, host: str | None = None) -> None:
        self.model = model
        self.host = host or os.getenv("OLLAMA_HOST", DEFAULT_HOST)
        if OLLAMA_IMPORT_ERROR is not None or Client is None:
            raise OllamaConnectionError(
                "No se pudo importar la librería ollama. Instala dependencias con: pip install -r requirements.txt"
            ) from OLLAMA_IMPORT_ERROR
        self.client = Client(host=self.host)

    def ensure_ready(self) -> None:
        try:
            model_names = self._get_local_model_names()
        except Exception as exc:
            raise OllamaConnectionError(
                "No se pudo conectar con Ollama en el equipo local. Verifica que el servicio esté activo con: ollama serve"
            ) from exc

        if self.model not in model_names:
            available = ", ".join(sorted(model_names)) if model_names else "ningún modelo local detectado"
            raise OllamaModelNotAvailableError(
                f"El modelo requerido '{self.model}' no está disponible localmente. Modelos detectados: {available}. "
                f"Descárgalo previamente con: ollama pull {self.model}"
            )

    def generate_response(self, messages: List[Mapping[str, str]]) -> str:
        try:
            response = self.client.chat(
                model=self.model,
                messages=list(messages),
                stream=False,
                options={
                    "temperature": 0.35,
                    "top_p": 0.9,
                    "num_ctx": 4096,
                },
            )
            content = self._extract_response_content(response)
        except ResponseError as exc:
            raise OllamaGenerationError(f"Ollama devolvió un error al generar la respuesta: {exc}") from exc
        except Exception as exc:
            raise OllamaGenerationError(
                "No se pudo generar la respuesta. Revisa que Ollama siga activo y que el modelo esté cargado correctamente."
            ) from exc

        if not content.strip():
            raise OllamaGenerationError("El modelo respondió sin contenido. Intenta reformular el mensaje.")
        return content.strip()

    def _get_local_model_names(self) -> set[str]:
        response = self.client.list()
        models = self._extract_models(response)
        names: set[str] = set()
        for model in models:
            name = self._read_model_name(model)
            if name:
                names.add(name)
        return names

    @staticmethod
    def _extract_models(response: Any) -> Iterable[Any]:
        if isinstance(response, Mapping):
            return response.get("models", [])
        return getattr(response, "models", []) or []

    @staticmethod
    def _read_model_name(model: Any) -> str | None:
        if isinstance(model, Mapping):
            return model.get("model") or model.get("name")
        return getattr(model, "model", None) or getattr(model, "name", None)

    @staticmethod
    def _extract_response_content(response: Any) -> str:
        if isinstance(response, Mapping):
            message = response.get("message", {})
            if isinstance(message, Mapping):
                return str(message.get("content", ""))
            return str(getattr(message, "content", ""))

        message = getattr(response, "message", None)
        if isinstance(message, Mapping):
            return str(message.get("content", ""))
        return str(getattr(message, "content", ""))
