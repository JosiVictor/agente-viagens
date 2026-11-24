"""Configurações gerais do projeto (chave de API e modelo)."""
import os
from dotenv import load_dotenv
load_dotenv()  # lê o arquivo .env

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
REQUEST_TIMEOUT = 10 


def validar_config() -> None:
    if not GOOGLE_API_KEY:
        raise RuntimeError(
            "GOOGLE_API_KEY não encontrada. Copie .env.example para .env "
            "e preencha com sua chave do Google AI Studio."
        )
