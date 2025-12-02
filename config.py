"""
Configurações da aplicação
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Settings:
    # Replicate
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

    # Servidor
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))

    # Limites
    MAX_IMAGE_SIZE_MB = int(os.getenv("MAX_IMAGE_SIZE_MB", 10))
    MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024

    # CORS
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

    # Modelos disponíveis
    MODELS = {
        "flux-schnell": "black-forest-labs/flux-schnell",
        "flux-dev": "black-forest-labs/flux-dev",
        "sdxl": "stability-ai/sdxl"
    }

    # Modelo padrão (flux-dev conforme solicitado)
    DEFAULT_MODEL = "flux-dev"

settings = Settings()
