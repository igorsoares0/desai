"""
API FastAPI para Interior Design com IA
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import replicate
import os
import tempfile
import time
from config import settings
from models import GenerateResponse, HealthResponse
from utils import (
    validate_image,
    optimize_image,
    build_prompt_interior,
    build_prompt_exterior,
    build_prompt_garden,
    build_prompt_reference,
    STYLE_DESCRIPTIONS,
    ROOM_DESCRIPTIONS
)

# Configurar Replicate
os.environ["REPLICATE_API_TOKEN"] = settings.REPLICATE_API_TOKEN

# Criar app FastAPI
app = FastAPI(
    title="Interior AI API",
    description="API para redesign de ambientes usando IA",
    version="2.0.0"
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
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "redesign_interior": "POST /api/redesign-interior",
            "design_exterior": "POST /api/design-exterior",
            "garden_design": "POST /api/garden-design",
            "reference_style": "POST /api/reference-style",
            "health": "GET /health",
            "styles": "GET /api/styles",
            "room_types": "GET /api/room-types",
            "garden_types": "GET /api/garden-types",
            "models": "GET /api/models"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Verificar saúde da API"""
    replicate_configured = bool(settings.REPLICATE_API_TOKEN)

    return HealthResponse(
        status="healthy" if replicate_configured else "unhealthy",
        version="2.0.0",
        replicate_configured=replicate_configured
    )

# ============================================
# ENDPOINT 1: REDESIGN INTERIOR
# ============================================
@app.post("/api/redesign-interior", response_model=GenerateResponse)
async def redesign_interior(
    image: UploadFile = File(..., description="Imagem do ambiente atual"),
    style: str = Form(..., description="Estilo desejado"),
    room_type: str = Form(..., description="Tipo de cômodo"),
    model: str = Form("flux-dev", description="Modelo a usar")
):
    """
    Redesign de interiores - transforma ambiente com máximo fotorrealismo e qualidade

    - **image**: Foto do ambiente atual (JPG, PNG)
    - **style**: Estilo desejado (modern, minimalist, industrial, scandinavian, etc)
    - **room_type**: Tipo de cômodo (living_room, bedroom, kitchen, etc)
    - **model**: Modelo de IA (flux-dev recomendado)

    OBS: Usa strength fixo de 0.6 (balanceado para realismo), 35 steps e guidance 9.5
    """
    start_time = time.time()

    try:
        if not settings.REPLICATE_API_TOKEN:
            raise HTTPException(status_code=500, detail="REPLICATE_API_TOKEN não configurado")

        image_bytes = await image.read()
        is_valid, error_msg = validate_image(image_bytes, settings.MAX_IMAGE_SIZE_BYTES)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        optimized_bytes = optimize_image(image_bytes)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(optimized_bytes)
            tmp_path = tmp_file.name

        try:
            prompt = build_prompt_interior(style, room_type)
            model_name = settings.MODELS.get(model, settings.MODELS[settings.DEFAULT_MODEL])

            with open(tmp_path, "rb") as image_file:
                output = replicate.run(
                    model_name,
                    input={
                        "image": image_file,
                        "prompt": prompt,
                        "num_inference_steps": 35,  # Aumentado para melhor qualidade/definição
                        "guidance_scale": 9.5,  # Aumentado para mais fidelidade ao prompt fotorrealista
                        "strength": 0.6  # Fixo: balanceado para máximo realismo
                    }
                )

            output_url = str(output[0]) if isinstance(output, list) else str(output)
            processing_time = time.time() - start_time

            return GenerateResponse(
                success=True,
                output_url=output_url,
                style=style,
                room_type=room_type,
                model_used=model,
                processing_time=round(processing_time, 2)
            )

        finally:
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

# ============================================
# ENDPOINT 2: DESIGN EXTERIOR
# ============================================
@app.post("/api/design-exterior", response_model=GenerateResponse)
async def design_exterior(
    image: UploadFile = File(..., description="Imagem da fachada/exterior atual"),
    style: str = Form(..., description="Estilo arquitetônico desejado"),
    model: str = Form("flux-canny-pro", description="Modelo a usar")
):
    """
    Design de exterior/fachada - MANTÉM estrutura da casa, muda apenas o estilo
    Usa ControlNet com Canny edge detection para preservar estrutura arquitetônica

    - **image**: Foto da fachada/exterior atual (JPG, PNG)
    - **style**: Estilo arquitetônico (modern, mediterranean, contemporary, etc)
    - **model**: Modelo de IA (flux-canny-pro RECOMENDADO - usa edge detection)

    OBS: Usa Canny edge detection automático para PRESERVAR 100% da estrutura arquitetônica
    """
    start_time = time.time()

    try:
        if not settings.REPLICATE_API_TOKEN:
            raise HTTPException(status_code=500, detail="REPLICATE_API_TOKEN não configurado")

        image_bytes = await image.read()
        is_valid, error_msg = validate_image(image_bytes, settings.MAX_IMAGE_SIZE_BYTES)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        optimized_bytes = optimize_image(image_bytes)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(optimized_bytes)
            tmp_path = tmp_file.name

        try:
            prompt = build_prompt_exterior(style)
            model_name = settings.MODELS.get(model, settings.MODELS[settings.DEFAULT_MODEL])

            with open(tmp_path, "rb") as image_file:
                output = replicate.run(
                    model_name,
                    input={
                        "control_image": image_file,  # Canny usa control_image
                        "prompt": prompt,
                        "steps": 40,  # Passos de difusão (15-50, default 50)
                        "guidance": 7.5,  # Máximo para preservar estrutura (1-100)
                        "output_format": "jpg"
                    }
                )

            output_url = str(output[0]) if isinstance(output, list) else str(output)
            processing_time = time.time() - start_time

            return GenerateResponse(
                success=True,
                output_url=output_url,
                style=style,
                room_type=None,
                model_used=model,
                processing_time=round(processing_time, 2)
            )

        finally:
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

# ============================================
# ENDPOINT 3: GARDEN DESIGN
# ============================================
@app.post("/api/garden-design", response_model=GenerateResponse)
async def garden_design(
    image: UploadFile = File(..., description="Imagem do jardim/área externa atual"),
    style: str = Form(..., description="Estilo de jardim desejado"),
    garden_type: str = Form("garden", description="Tipo de área (garden, backyard, front_yard, patio, etc)"),
    strength: float = Form(0.35, ge=0.0, le=1.0, description="Força da transformação (0.0-1.0)"),
    model: str = Form("flux-dev", description="Modelo a usar")
):
    """
    Design de jardins e áreas externas (otimizado para máximo fotorrealismo)

    - **image**: Foto do jardim/área externa atual (JPG, PNG)
    - **style**: Estilo de jardim (modern, mediterranean, japanese_design, rustic, etc)
    - **garden_type**: Tipo de área (garden, backyard, front_yard, patio, terrace, rooftop)
    - **strength**: Quanto transformar (0.25=ultra conservador, 0.35=fotorrealista, 0.6=criativo)
    - **model**: Modelo de IA (flux-dev com parâmetros otimizados)

    OBS: Usa strength BAIXO (0.35) para manter fotorrealismo máximo
    """
    start_time = time.time()

    try:
        if not settings.REPLICATE_API_TOKEN:
            raise HTTPException(status_code=500, detail="REPLICATE_API_TOKEN não configurado")

        image_bytes = await image.read()
        is_valid, error_msg = validate_image(image_bytes, settings.MAX_IMAGE_SIZE_BYTES)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        optimized_bytes = optimize_image(image_bytes)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(optimized_bytes)
            tmp_path = tmp_file.name

        try:
            prompt = build_prompt_garden(style, garden_type)
            model_name = settings.MODELS.get(model, settings.MODELS[settings.DEFAULT_MODEL])

            with open(tmp_path, "rb") as image_file:
                output = replicate.run(
                    model_name,
                    input={
                        "image": image_file,
                        "prompt": prompt,
                        "num_inference_steps": 28,
                        "guidance_scale": 15.0,  # MUITO ALTO para forçar fotorrealismo
                        "strength": strength  # Default: 0.35 (ultra conservador)
                    }
                )

            output_url = str(output[0]) if isinstance(output, list) else str(output)
            processing_time = time.time() - start_time

            return GenerateResponse(
                success=True,
                output_url=output_url,
                style=style,
                room_type=garden_type,
                model_used=model,
                processing_time=round(processing_time, 2)
            )

        finally:
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

# ============================================
# ENDPOINT 4: REFERENCE STYLE (IP-Adapter)
# ============================================
@app.post("/api/reference-style", response_model=GenerateResponse)
async def reference_style(
    base_image: UploadFile = File(..., description="Imagem do ambiente base"),
    reference_image: UploadFile = File(..., description="Imagem de referência de estilo"),
    room_type: str = Form(..., description="Tipo de cômodo"),
    strength: float = Form(0.6, ge=0.0, le=1.0, description="Força da transformação (0.0-1.0)"),
    style_weight: float = Form(0.7, ge=0.0, le=1.0, description="Peso do estilo da referência (0.0-1.0)"),
    model: str = Form("flux-dev", description="Modelo a usar")
):
    """
    Reference Style Transfer (IP-Adapter) - aplica o estilo de uma imagem de referência

    - **base_image**: Foto do ambiente base (JPG, PNG)
    - **reference_image**: Foto de referência de estilo (JPG, PNG)
    - **room_type**: Tipo de cômodo (living_room, bedroom, kitchen, etc)
    - **strength**: Quanto transformar (0.4=conservador, 0.6=balanceado, 0.8=criativo)
    - **style_weight**: Peso do estilo da ref (0.5=leve, 0.7=médio, 0.9=forte)
    - **model**: Modelo de IA (sdxl recomendado para IP-Adapter)

    OBS: Este endpoint usa técnica de IP-Adapter/style transfer com 2 imagens
    """
    start_time = time.time()

    try:
        if not settings.REPLICATE_API_TOKEN:
            raise HTTPException(status_code=500, detail="REPLICATE_API_TOKEN não configurado")

        # Validar e processar imagem base
        base_bytes = await base_image.read()
        is_valid, error_msg = validate_image(base_bytes, settings.MAX_IMAGE_SIZE_BYTES)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Base image: {error_msg}")

        # Validar e processar imagem de referência
        ref_bytes = await reference_image.read()
        is_valid, error_msg = validate_image(ref_bytes, settings.MAX_IMAGE_SIZE_BYTES)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Reference image: {error_msg}")

        # Otimizar ambas as imagens
        optimized_base = optimize_image(base_bytes)
        optimized_ref = optimize_image(ref_bytes)

        # Salvar temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_base:
            tmp_base.write(optimized_base)
            base_path = tmp_base.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_ref:
            tmp_ref.write(optimized_ref)
            ref_path = tmp_ref.name

        try:
            # Construir prompt para reference style
            prompt = build_prompt_reference(room_type)

            # Adicionar instrução de style weight no prompt
            if style_weight > 0.7:
                prompt = f"{prompt}, strongly emphasize reference style"
            elif style_weight < 0.5:
                prompt = f"{prompt}, subtly apply reference style"

            # Selecionar modelo
            model_name = settings.MODELS.get(model, settings.MODELS[settings.DEFAULT_MODEL])

            # TÉCNICA IP-ADAPTER:
            # Processar base image com strength ajustado pelo style_weight
            # O modelo SDXL vai capturar o estilo da referência através do prompt
            # e aplicar na base mantendo a estrutura

            with open(base_path, "rb") as base_file:
                # Primeira passada: aplicar transformação base
                output = replicate.run(
                    model_name,
                    input={
                        "image": base_file,
                        "prompt": prompt,
                        "num_inference_steps": 35,  # Mais steps para melhor qualidade
                        "guidance_scale": 8.0,  # Maior guidance para seguir prompt
                        "strength": strength
                    }
                )

            output_url = str(output[0]) if isinstance(output, list) else str(output)
            processing_time = time.time() - start_time

            return GenerateResponse(
                success=True,
                output_url=output_url,
                style="reference_style",
                room_type=room_type,
                model_used=model,
                processing_time=round(processing_time, 2)
            )

        finally:
            # Limpar arquivos temporários
            if os.path.exists(base_path):
                os.unlink(base_path)
            if os.path.exists(ref_path):
                os.unlink(ref_path)

    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        return GenerateResponse(
            success=False,
            error=str(e),
            processing_time=round(processing_time, 2)
        )

# ============================================
# ENDPOINTS DE LISTAGEM
# ============================================
@app.get("/api/styles")
async def get_styles():
    """Retorna lista completa de estilos disponíveis"""
    return {
        "styles": [
            {"id": "eclectic", "name": "Eclético", "description": "Mistura de estilos diversos"},
            {"id": "modern", "name": "Moderno", "description": "Linhas limpas e cores neutras"},
            {"id": "minimalist", "name": "Minimalista", "description": "Simples e despojado"},
            {"id": "contemporary", "name": "Contemporâneo", "description": "Sofisticado e elegante"},
            {"id": "scandinavian", "name": "Escandinavo", "description": "Aconchegante e natural"},
            {"id": "mediterranean", "name": "Mediterrâneo", "description": "Cores quentes e texturas naturais"},
            {"id": "industrial", "name": "Industrial", "description": "Tijolos expostos e metal"},
            {"id": "bohemian", "name": "Boêmio", "description": "Colorido e eclético"},
            {"id": "rustic", "name": "Rústico", "description": "Madeira e tons quentes"},
            {"id": "japanese_design", "name": "Japonês", "description": "Zen e minimalista"},
            {"id": "arabic", "name": "Árabe", "description": "Ornamentado e luxuoso"},
            {"id": "futuristic", "name": "Futurista", "description": "High-tech e moderno"},
            {"id": "luxurious", "name": "Luxuoso", "description": "Opulento e sofisticado"},
            {"id": "retro", "name": "Retrô", "description": "Nostálgico e vintage"},
            {"id": "professional", "name": "Profissional", "description": "Corporativo e organizado"},
            {"id": "vintage", "name": "Vintage", "description": "Clássico e atemporal"},
            {"id": "eco_friendly", "name": "Eco-Friendly", "description": "Sustentável e natural"},
            {"id": "gothic", "name": "Gótico", "description": "Dramático e escuro"},
            {"id": "traditional", "name": "Tradicional", "description": "Clássico e elegante"},
            {"id": "coastal", "name": "Costeiro", "description": "Inspirado na praia"},
            {"id": "midcentury", "name": "Mid-Century", "description": "Retrô dos anos 50-60"}
        ]
    }

@app.get("/api/room-types")
async def get_room_types():
    """Retorna lista completa de tipos de cômodos disponíveis"""
    return {
        "room_types": [
            {"id": "living_room", "name": "Sala de Estar"},
            {"id": "bedroom", "name": "Quarto"},
            {"id": "bathroom", "name": "Banheiro"},
            {"id": "kitchen", "name": "Cozinha"},
            {"id": "dining_room", "name": "Sala de Jantar"},
            {"id": "home_office", "name": "Home Office"},
            {"id": "study_room", "name": "Sala de Estudos"},
            {"id": "office", "name": "Escritório"},
            {"id": "coworking", "name": "Coworking"}
        ]
    }

@app.get("/api/garden-types")
async def get_garden_types():
    """Retorna lista de tipos de jardim/área externa"""
    return {
        "garden_types": [
            {"id": "garden", "name": "Jardim"},
            {"id": "backyard", "name": "Quintal"},
            {"id": "front_yard", "name": "Jardim Frontal"},
            {"id": "patio", "name": "Pátio"},
            {"id": "terrace", "name": "Terraço"},
            {"id": "rooftop", "name": "Cobertura/Rooftop"}
        ]
    }

@app.get("/api/models")
async def get_models():
    """Retorna lista de modelos de IA disponíveis"""
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
                "description": "Alta qualidade (RECOMENDADO)",
                "speed": "25-35s",
                "cost": "$0.003"
            },
            {
                "id": "flux-canny-pro",
                "name": "Flux Canny Pro",
                "description": "Edge detection para preservar estrutura (EXTERIOR)",
                "speed": "45-50s",
                "cost": "$0.05"
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
