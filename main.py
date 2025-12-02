"""
API FastAPI para Interior Design com IA
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import replicate
import os
import tempfile
import time
from config import settings
from models import GenerateResponse, HealthResponse
from utils import validate_image, optimize_image, build_prompt

# Configurar Replicate
os.environ["REPLICATE_API_TOKEN"] = settings.REPLICATE_API_TOKEN

# Criar app FastAPI
app = FastAPI(
    title="Interior AI API",
    description="API para redesign de ambientes usando IA",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=dict)
async def root():
    """Endpoint raiz"""
    return {
        "message": "Interior AI API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "generate": "POST /api/generate",
            "health": "GET /health"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Verificar saúde da API"""
    replicate_configured = bool(settings.REPLICATE_API_TOKEN)

    return HealthResponse(
        status="healthy" if replicate_configured else "unhealthy",
        version="1.0.0",
        replicate_configured=replicate_configured
    )

@app.post("/api/generate", response_model=GenerateResponse)
async def generate_design(
    image: UploadFile = File(..., description="Imagem do ambiente"),
    style: str = Form(..., description="Estilo desejado (modern, minimalist, etc)"),
    room_type: str = Form(..., description="Tipo de cômodo (living_room, bedroom, etc)"),
    strength: float = Form(0.7, ge=0.0, le=1.0, description="Força da transformação (0.0-1.0)"),
    model: str = Form("flux-dev", description="Modelo a usar")
):
    """
    Gera um novo design para o ambiente

    - **image**: Foto do ambiente atual (JPG, PNG)
    - **style**: Estilo desejado (modern, minimalist, industrial, etc)
    - **room_type**: Tipo de cômodo (living_room, bedroom, kitchen, etc)
    - **strength**: Quanto transformar (0.3=conservador, 0.7=balanceado, 0.9=criativo)
    - **model**: Modelo de IA (flux-schnell, flux-dev, sdxl)
    """
    start_time = time.time()

    try:
        # 1. Validar token Replicate
        if not settings.REPLICATE_API_TOKEN:
            raise HTTPException(
                status_code=500,
                detail="REPLICATE_API_TOKEN não configurado"
            )

        # 2. Ler imagem
        image_bytes = await image.read()

        # 3. Validar imagem
        is_valid, error_msg = validate_image(image_bytes, settings.MAX_IMAGE_SIZE_BYTES)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # 4. Otimizar imagem
        optimized_bytes = optimize_image(image_bytes)

        # 5. Salvar temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(optimized_bytes)
            tmp_path = tmp_file.name

        try:
            # 6. Construir prompt
            prompt = build_prompt(style, room_type)

            # 7. Selecionar modelo
            model_name = settings.MODELS.get(model, settings.MODELS[settings.DEFAULT_MODEL])

            # 8. Chamar Replicate
            with open(tmp_path, "rb") as image_file:
                output = replicate.run(
                    model_name,
                    input={
                        "image": image_file,
                        "prompt": prompt,
                        "num_inference_steps": 28,
                        "guidance_scale": 7.5,
                        "strength": strength
                    }
                )

            # 9. Processar resultado
            # O Replicate pode retornar FileOutput, lista de FileOutput, ou string
            if isinstance(output, list) and len(output) > 0:
                output_url = str(output[0])
            else:
                output_url = str(output)

            processing_time = time.time() - start_time

            # 10. Retornar resposta
            return GenerateResponse(
                success=True,
                output_url=output_url,
                style=style,
                room_type=room_type,
                model_used=model,
                processing_time=round(processing_time, 2)
            )

        finally:
            # Limpar arquivo temporário
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        return GenerateResponse(
            success=False,
            error=str(e),
            processing_time=round(processing_time, 2)
        )

@app.get("/api/styles")
async def get_styles():
    """Retorna lista de estilos disponíveis"""
    return {
        "styles": [
            {"id": "modern", "name": "Moderno", "description": "Linhas limpas e cores neutras"},
            {"id": "minimalist", "name": "Minimalista", "description": "Simples e despojado"},
            {"id": "industrial", "name": "Industrial", "description": "Tijolos expostos e metal"},
            {"id": "scandinavian", "name": "Escandinavo", "description": "Aconchegante e natural"},
            {"id": "bohemian", "name": "Boêmio", "description": "Colorido e eclético"},
            {"id": "rustic", "name": "Rústico", "description": "Madeira e tons quentes"},
            {"id": "contemporary", "name": "Contemporâneo", "description": "Sofisticado e elegante"},
            {"id": "traditional", "name": "Tradicional", "description": "Clássico e atemporal"},
            {"id": "coastal", "name": "Costeiro", "description": "Inspirado na praia"},
            {"id": "midcentury", "name": "Mid-Century", "description": "Retrô dos anos 50-60"}
        ]
    }

@app.get("/api/room-types")
async def get_room_types():
    """Retorna lista de tipos de cômodos disponíveis"""
    return {
        "room_types": [
            {"id": "living_room", "name": "Sala de Estar"},
            {"id": "bedroom", "name": "Quarto"},
            {"id": "kitchen", "name": "Cozinha"},
            {"id": "bathroom", "name": "Banheiro"},
            {"id": "office", "name": "Escritório"},
            {"id": "dining_room", "name": "Sala de Jantar"},
            {"id": "kids_room", "name": "Quarto Infantil"},
            {"id": "master_bedroom", "name": "Suíte Master"}
        ]
    }

@app.get("/api/models")
async def get_models():
    """Retorna lista de modelos disponíveis"""
    return {
        "models": [
            {
                "id": "flux-schnell",
                "name": "Flux Schnell",
                "description": "Rápido e eficiente",
                "speed": "10-15s",
                "cost": "$0.001"
            },
            {
                "id": "flux-dev",
                "name": "Flux Dev",
                "description": "Alta qualidade",
                "speed": "25-35s",
                "cost": "$0.003"
            },
            {
                "id": "sdxl",
                "name": "SDXL",
                "description": "Balanceado",
                "speed": "20-30s",
                "cost": "$0.002"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
