# Guia Completo - API FastAPI para Interior Design com IA

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Configuração do Ambiente](#configuração-do-ambiente)
4. [Entendendo a API Replicate](#entendendo-a-api-replicate)
5. [Implementação da API FastAPI](#implementação-da-api-fastapi)
6. [Fluxo Completo de Uso](#fluxo-completo-de-uso)
7. [Testes e Desenvolvimento](#testes-e-desenvolvimento)
8. [Deploy em Produção](#deploy-em-produção)
9. [Otimizações e Boas Práticas](#otimizações-e-boas-práticas)
10. [Troubleshooting](#troubleshooting)

---

## Visão Geral

Esta API permite que aplicativos Android enviem fotos de ambientes e recebam redesigns gerados por IA usando modelos de machine learning da Replicate.

### Tecnologias Utilizadas

- **FastAPI**: Framework Python para criar a API REST
- **Replicate**: Plataforma de ML para rodar modelos de IA
- **Flux/SDXL**: Modelos de geração de imagens
- **Python 3.10+**: Linguagem base

### Fluxo Geral

```
App Android → API FastAPI → Replicate → Modelo de IA → Imagem Gerada → App Android
```

---

## Arquitetura do Sistema

### Diagrama de Fluxo

```
┌─────────────────┐
│  App Android    │
│  (Cliente)      │
└────────┬────────┘
         │ 1. POST /api/generate
         │    - image (file)
         │    - style (string)
         │    - room_type (string)
         ▼
┌─────────────────────────┐
│   API FastAPI           │
│   (Servidor Python)     │
│                         │
│  1. Recebe imagem       │
│  2. Valida dados        │
│  3. Salva temporário    │
│  4. Monta prompt        │
└────────┬────────────────┘
         │ 5. Chama Replicate
         ▼
┌─────────────────────────┐
│   Replicate API         │
│   (Serviço Externo)     │
│                         │
│  1. Upload da imagem    │
│  2. Processa com IA     │
│  3. Gera nova imagem    │
└────────┬────────────────┘
         │ 6. Retorna URL
         ▼
┌─────────────────────────┐
│   API FastAPI           │
│                         │
│  7. Retorna resposta    │
│     JSON com URL        │
└────────┬────────────────┘
         │ 8. Response
         ▼
┌─────────────────┐
│  App Android    │
│                 │
│  9. Baixa img   │
│  10. Salva local│
└─────────────────┘
```

---

## Configuração do Ambiente

### 1. Pré-requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)
- Conta na Replicate (https://replicate.com)

### 2. Criar Conta na Replicate

1. Acesse https://replicate.com
2. Crie uma conta (pode usar GitHub)
3. Vá em Account Settings → API Tokens
4. Copie seu token (formato: `r8_...`)

### 3. Setup do Projeto

```bash
# Criar diretório do projeto
mkdir interior-ai-api
cd interior-ai-api

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Criar arquivo requirements.txt
cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
replicate==0.22.0
python-dotenv==1.0.0
Pillow==10.1.0
EOF

# Instalar dependências
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

```bash
# Criar arquivo .env
cat > .env << EOF
REPLICATE_API_TOKEN=r8_seu_token_aqui
PORT=8000
HOST=0.0.0.0
MAX_IMAGE_SIZE_MB=10
ALLOWED_ORIGINS=*
EOF
```

---

## Entendendo a API Replicate

### Como Funciona a Replicate

A Replicate é uma plataforma que hospeda modelos de machine learning. Você envia dados (imagens, texto) e recebe resultados processados.

### Fluxo de Uso da Replicate

```python
# 1. Importar biblioteca
import replicate

# 2. Autenticar (usando variável de ambiente)
import os
os.environ["REPLICATE_API_TOKEN"] = "r8_seu_token"

# 3. Executar modelo
output = replicate.run(
    "nome-do-modelo",
    input={
        "parametro1": "valor1",
        "parametro2": "valor2"
    }
)

# 4. Receber resultado (geralmente uma URL)
image_url = output[0]
```

### Modelos Disponíveis para Interior Design

#### 1. Flux Schnell (Recomendado para MVP)

```python
model = "black-forest-labs/flux-schnell"

# Características:
# - Velocidade: ~10-15 segundos
# - Custo: ~$0.001 por geração
# - Qualidade: Boa
# - Ideal para: Protótipos e testes
```

#### 2. Flux Dev (Melhor Qualidade)

```python
model = "black-forest-labs/flux-dev"

# Características:
# - Velocidade: ~25-35 segundos
# - Custo: ~$0.003 por geração
# - Qualidade: Excelente
# - Ideal para: Produção
```

#### 3. SDXL (Alternativa)

```python
model = "stability-ai/sdxl"

# Características:
# - Velocidade: ~20-30 segundos
# - Custo: ~$0.002 por geração
# - Qualidade: Muito boa
# - Ideal para: Equilíbrio custo/qualidade
```

### Parâmetros Importantes

```python
input = {
    # Imagem de entrada (obrigatório)
    "image": open("foto.jpg", "rb"),
    
    # Prompt de texto (obrigatório)
    "prompt": "modern living room, minimalist, photorealistic",
    
    # Quantos passos de processamento (mais = melhor qualidade)
    "num_inference_steps": 28,  # Padrão: 28, Range: 1-50
    
    # Força da transformação
    "strength": 0.7,  # Range: 0.0-1.0
    # 0.3 = mantém 70% da imagem original (conservador)
    # 0.5 = 50/50 (balanceado)
    # 0.7 = transforma 70% (criativo) ← RECOMENDADO
    # 0.9 = quase completamente novo (muito criativo)
    
    # Guidance scale (quanto seguir o prompt)
    "guidance_scale": 7.5,  # Range: 1-20
    # Valores baixos (3-5): mais criativo, menos fiel ao prompt
    # Valores médios (7-8): balanceado ← RECOMENDADO
    # Valores altos (10-15): muito fiel ao prompt, menos criativo
}
```

### Tipos de Execução

#### Método 1: Síncrono (Mais Simples)

```python
# Aguarda até finalizar e retorna resultado
output = replicate.run(
    "black-forest-labs/flux-schnell",
    input={
        "image": image_file,
        "prompt": "modern living room"
    }
)
# Bloqueia a execução por ~10-30 segundos
```

#### Método 2: Assíncrono (Mais Avançado)

```python
# Cria uma "prediction" e retorna ID imediatamente
prediction = replicate.predictions.create(
    version="model-version-id",
    input={
        "image": image_url,
        "prompt": "modern living room"
    }
)

# Verificar status depois
prediction.reload()
if prediction.status == "succeeded":
    output = prediction.output
```

---

## Implementação da API FastAPI

### Estrutura de Arquivos

```
interior-ai-api/
├── venv/
├── .env
├── .gitignore
├── requirements.txt
├── main.py
├── models.py
├── config.py
└── utils.py
```

### 1. config.py - Configurações

```python
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
    
    # Modelo padrão
    DEFAULT_MODEL = "flux-schnell"

settings = Settings()
```

### 2. models.py - Modelos de Dados

```python
"""
Modelos Pydantic para validação de dados
"""
from pydantic import BaseModel, Field
from typing import Optional

class GenerateRequest(BaseModel):
    """Modelo para requisição de geração"""
    style: str = Field(..., description="Estilo do design")
    room_type: str = Field(..., description="Tipo de cômodo")
    strength: Optional[float] = Field(0.7, ge=0.0, le=1.0, description="Força da transformação")
    model: Optional[str] = Field("flux-schnell", description="Modelo a usar")

class GenerateResponse(BaseModel):
    """Modelo para resposta de geração"""
    success: bool
    output_url: Optional[str] = None
    style: Optional[str] = None
    room_type: Optional[str] = None
    model_used: Optional[str] = None
    processing_time: Optional[float] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    """Modelo para health check"""
    status: str
    version: str
    replicate_configured: bool
```

### 3. utils.py - Funções Utilitárias

```python
"""
Funções auxiliares
"""
from PIL import Image
import io
import os

def validate_image(image_bytes: bytes, max_size_bytes: int) -> tuple[bool, str]:
    """
    Valida se a imagem é válida e não excede o tamanho máximo
    
    Args:
        image_bytes: Bytes da imagem
        max_size_bytes: Tamanho máximo permitido em bytes
        
    Returns:
        (is_valid, error_message)
    """
    # Verificar tamanho
    if len(image_bytes) > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        return False, f"Imagem muito grande. Máximo permitido: {max_mb}MB"
    
    # Verificar se é uma imagem válida
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
        return True, ""
    except Exception as e:
        return False, f"Arquivo inválido: {str(e)}"

def optimize_image(image_bytes: bytes, max_dimension: int = 1024) -> bytes:
    """
    Otimiza a imagem redimensionando se necessário
    
    Args:
        image_bytes: Bytes da imagem original
        max_dimension: Dimensão máxima (largura ou altura)
        
    Returns:
        Bytes da imagem otimizada
    """
    img = Image.open(io.BytesIO(image_bytes))
    
    # Converter RGBA para RGB se necessário
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    # Redimensionar se necessário
    if max(img.size) > max_dimension:
        img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
    
    # Salvar otimizado
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=90, optimize=True)
    output.seek(0)
    
    return output.read()

def build_prompt(style: str, room_type: str) -> str:
    """
    Constrói o prompt otimizado para geração
    
    Args:
        style: Estilo selecionado
        room_type: Tipo de cômodo
        
    Returns:
        Prompt formatado
    """
    style_descriptions = {
        "modern": "modern, clean lines, neutral colors, contemporary furniture",
        "minimalist": "minimalist, simple, white and wood tones, uncluttered",
        "industrial": "industrial style, exposed brick, metal fixtures, concrete",
        "scandinavian": "scandinavian, cozy, natural materials, bright and airy",
        "bohemian": "bohemian, colorful, eclectic, plants, textured fabrics",
        "rustic": "rustic, wooden elements, warm tones, natural textures",
        "contemporary": "contemporary, sleek, sophisticated, mixed materials",
        "traditional": "traditional, classic, elegant, rich colors",
        "coastal": "coastal, beach inspired, light colors, natural light",
        "midcentury": "mid-century modern, retro, clean lines, organic shapes"
    }
    
    room_descriptions = {
        "living_room": "living room",
        "bedroom": "bedroom",
        "kitchen": "kitchen",
        "bathroom": "bathroom",
        "office": "home office",
        "dining_room": "dining room",
        "kids_room": "kids room",
        "master_bedroom": "master bedroom"
    }
    
    style_desc = style_descriptions.get(style.lower(), "modern")
    room_desc = room_descriptions.get(room_type.lower(), "living room")
    
    prompt = f"{style_desc} {room_desc}, professional interior design, photorealistic, high quality, architectural photography, well lit, 8k resolution"
    
    return prompt
```

### 4. main.py - Aplicação Principal

```python
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
    model: str = Form("flux-schnell", description="Modelo a usar")
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
            if isinstance(output, list) and len(output) > 0:
                output_url = output[0]
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
```

### 5. .gitignore

```
# Python
venv/
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
dist/
*.egg-info/

# Ambiente
.env
.env.local

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Temporários
*.log
tmp/
temp/
```

---

## Fluxo Completo de Uso

### Passo a Passo Detalhado

#### 1. Cliente Envia Requisição

```http
POST http://localhost:8000/api/generate
Content-Type: multipart/form-data

--boundary
Content-Disposition: form-data; name="image"; filename="living_room.jpg"
Content-Type: image/jpeg

[binary data]
--boundary
Content-Disposition: form-data; name="style"

modern
--boundary
Content-Disposition: form-data; name="room_type"

living_room
--boundary
Content-Disposition: form-data; name="strength"

0.7
--boundary--
```

#### 2. API Processa Requisição

```python
# FastAPI recebe dados
image_bytes = await image.read()  # Bytes da imagem

# Valida tamanho e formato
is_valid, error = validate_image(image_bytes, max_size)

# Otimiza imagem (resize se necessário)
optimized = optimize_image(image_bytes)

# Salva temporariamente
temp_file = save_to_temp(optimized)
```

#### 3. API Monta Prompt

```python
# Entrada do usuário
style = "modern"
room_type = "living_room"

# Função build_prompt() cria:
prompt = "modern, clean lines, neutral colors, contemporary furniture living room, professional interior design, photorealistic, high quality, architectural photography, well lit, 8k resolution"
```

#### 4. API Chama Replicate

```python
# Abre arquivo temporário
with open(temp_file, "rb") as f:
    # Envia para Replicate
    output = replicate.run(
        "black-forest-labs/flux-schnell",
        input={
            "image": f,
            "prompt": prompt,
            "strength": 0.7,
            "guidance_scale": 7.5,
            "num_inference_steps": 28
        }
    )

# Aguarda processamento (~10-30 segundos)
# Replicate processa e retorna URL
```

#### 5. Replicate Processa

```
Replicate Backend:
1. Recebe imagem + prompt
2. Carrega modelo (Flux Schnell)
3. Processa imagem através da rede neural
4. Aplica transformações baseadas no prompt
5. Gera nova imagem
6. Hospeda imagem em CDN
7. Retorna URL pública
```

#### 6. API Retorna Resposta

```json
{
  "success": true,
  "output_url": "https://replicate.delivery/pbxt/abc123.jpg",
  "style": "modern",
  "room_type": "living_room",
  "model_used": "flux-schnell",
  "processing_time": 12.34
}
```

#### 7. Cliente Baixa Imagem

```kotlin
// Android baixa a imagem
val url = response.output_url
val bitmap = downloadImage(url)

// Salva localmente
saveToInternalStorage(bitmap)
```

### Diagrama de Sequência Completo

```
Cliente          API FastAPI         Replicate         CDN
  |                  |                    |              |
  |-- POST image --->|                    |              |
  |                  |--- validate ------>|              |
  |                  |                    |              |
  |                  |--- optimize ------>|              |
  |                  |                    |              |
  |                  |--- build prompt -->|              |
  |                  |                    |              |
  |                  |--- replicate.run ->|              |
  |                  |                    |              |
  |                  |                    |-- process -->|
  |                  |                    |   (10-30s)   |
  |                  |                    |              |
  |                  |                    |<-- upload ---|
  |                  |                    |              |
  |                  |<-- return URL -----|              |
  |                  |                    |              |
  |<-- JSON resp ----|                    |              |
  |                  |                    |              |
  |---------------- GET image URL ----------------->|
  |<--------------- image binary ------------------|
  |                  |                    |              |
```

---

## Testes e Desenvolvimento

### 1. Testar Localmente

```bash
# Ativar ambiente virtual
source venv/bin/activate  # ou venv\Scripts\activate no Windows

# Rodar servidor
python main.py

# Ou com uvicorn diretamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Testar com cURL

```bash
# Health check
curl http://localhost:8000/health

# Listar estilos
curl http://localhost:8000/api/styles

# Gerar design
curl -X POST http://localhost:8000/api/generate \
  -F "image=@/path/to/image.jpg" \
  -F "style=modern" \
  -F "room_type=living_room" \
  -F "strength=0.7"
```

### 3. Testar com Postman

1. Abra Postman
2. Crie requisição POST para `http://localhost:8000/api/generate`
3. Em Body, selecione `form-data`
4. Adicione campos:
   - `image` (tipo: File) - selecione uma imagem
   - `style` (tipo: Text) - ex: "modern"
   - `room_type` (tipo: Text) - ex: "living_room"
   - `strength` (tipo: Text) - ex: "0.7"
5. Clique em Send

### 4. Testar com Python Script

```python
# test_api.py
import requests

# Endpoint
url = "http://localhost:8000/api/generate"

# Preparar dados
files = {
    'image': open('test_image.jpg', 'rb')
}
data = {
    'style': 'modern',
    'room_type': 'living_room',
    'strength': 0.7
}

# Fazer requisição
response = requests.post(url, files=files, data=data)

# Ver resultado
print(response.json())
```

### 5. Expor API para Teste no Android

#### Opção A: ngrok (Recomendado)

```bash
# Instalar ngrok
# https://ngrok.com/download

# Rodar API
python main.py

# Em outro terminal, expor porta
ngrok http 8000

# Vai retornar algo como:
# Forwarding: https://abc123.ngrok.io -> http://localhost:8000

# Use essa URL no Android
```

#### Opção B: Mesma Rede WiFi

```bash
# Descobrir IP local
# Windows:
ipconfig

# Linux/Mac:
ifconfig

# Exemplo de IP: 192.168.1.100

# Rodar API permitindo acesso externo
python main.py  # Já configurado com host=0.0.0.0

# No Android, use:
# http://192.168.1.100:8000
```

---

## Deploy em Produção

### Opção 1: Railway (Mais Fácil)

```bash
# 1. Criar conta em railway.app
# 2. Instalar CLI
npm i -g @railway/cli

# 3. Login
railway login

# 4. Inicializar projeto
railway init

# 5. Adicionar variáveis de ambiente
railway variables set REPLICATE_API_TOKEN=r8_seu_token

# 6. Deploy
railway up

# Railway vai detectar requirements.txt e fazer deploy automático
```

**Arquivo railway.json (opcional)**

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Opção 2: Render

1. Criar conta em render.com
2. Novo Web Service
3. Conectar repositório GitHub
4. Configurações:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Adicionar variável de ambiente: `REPLICATE_API_TOKEN`
6. Deploy

### Opção 3: DigitalOcean App Platform

1. Criar conta DigitalOcean
2. Apps → Create App
3. Conectar GitHub ou fazer upload
4. Configurar:
   - **Run Command**: `uvicorn main:app --host 0.0.0.0 --port 8080`
5. Adicionar variáveis de ambiente
6. Deploy

### Opção 4: VPS Manual (Controle Total)

```bash
# 1. Conectar ao VPS via SSH
ssh root@seu-ip

# 2. Instalar Python
apt update
apt install python3.10 python3-pip python3-venv nginx

# 3. Clonar código
git clone seu-repositorio
cd interior-ai-api

# 4. Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Criar arquivo .env
nano .env
# Adicionar REPLICATE_API_TOKEN=...

# 6. Criar serviço systemd
nano /etc/systemd/system/interior-ai.service
```

**Arquivo interior-ai.service**

```ini
[Unit]
Description=Interior AI API
After=network.target

[Service]
User=root
WorkingDirectory=/root/interior-ai-api
Environment="PATH=/root/interior-ai-api/venv/bin"
ExecStart=/root/interior-ai-api/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

```bash
# 7. Ativar serviço
systemctl enable interior-ai
systemctl start interior-ai

# 8. Configurar Nginx
nano /etc/nginx/sites-available/interior-ai
```

**Arquivo nginx**

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# 9. Ativar site
ln -s /etc/nginx/sites-available/interior-ai /etc/nginx/sites-enabled/
systemctl reload nginx

# 10. (Opcional) SSL com Let's Encrypt
apt install certbot python3-certbot-nginx
certbot --nginx -d seu-dominio.com
```

---

## Otimizações e Boas Práticas

### 1. Caching

```python
# Adicionar cache para estilos e room types
from functools import lru_cache

@lru_cache(maxsize=1)
def get_styles_cached():
    return load_styles()
```

### 2. Rate Limiting

```python
# Instalar slowapi
pip install slowapi

# Adicionar ao main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/generate")
@limiter.limit("10/minute")  # 10 requisições por minuto
async def generate_design(...):
    ...
```

### 3. Logging

```python
# Adicionar logging estruturado
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.post("/api/generate")
async def generate_design(...):
    logger.info(f"Generating design: style={style}, room={room_type}")
    try:
        ...
        logger.info(f"Success in {processing_time}s")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
```

### 4. Monitoramento

```python
# Adicionar Prometheus metrics
pip install prometheus-fastapi-instrumentator

from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### 5. Async para Melhor Performance

```python
# Usar replicate async
import replicate.async_api as replicate_async

@app.post("/api/generate")
async def generate_design(...):
    # Usar versão async do replicate
    output = await replicate_async.run(...)
```

### 6. Timeout e Retry

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def call_replicate(...):
    return replicate.run(...)
```

---

## Troubleshooting

### Problema: "REPLICATE_API_TOKEN não configurado"

**Solução:**
```bash
# Verificar se .env existe
cat .env

# Verificar se token está correto
echo $REPLICATE_API_TOKEN

# Recarregar variáveis
source .env  # Linux/Mac
```

### Problema: "Imagem muito grande"

**Solução:**
```python
# A função optimize_image já redimensiona
# Ajustar MAX_IMAGE_SIZE_MB no .env
MAX_IMAGE_SIZE_MB=15
```

### Problema: "Timeout ao chamar Replicate"

**Solução:**
```python
# Aumentar timeout
import httpx

client = httpx.Client(timeout=120.0)  # 120 segundos
```

### Problema: "CORS blocked"

**Solução:**
```python
# Atualizar CORS origins no .env
ALLOWED_ORIGINS=http://localhost:3000,https://seu-app.com

# Ou permitir todos (apenas desenvolvimento)
ALLOWED_ORIGINS=*
```

### Problema: "Out of memory"

**Solução:**
```python
# Reduzir tamanho máximo de imagem
def optimize_image(image_bytes: bytes, max_dimension: int = 768):
    # Usar 768 ao invés de 1024
```

### Problema: "Replicate rate limit"

**Solução:**
- Plano gratuito: Limite de requisições
- Upgrade para plano pago
- Implementar fila local para evitar burst

---

## Próximos Passos

### Features Adicionais

1. **Sistema de Créditos**
```python
# Adicionar verificação de créditos antes de gerar
def check_user_credits(user_id: str) -> bool:
    credits = db.get_credits(user_id)
    return credits > 0
```

2. **Histórico de Gerações**
```python
# Salvar histórico no banco
def save_generation(user_id, image_url, style, room_type):
    db.insert({
        'user_id': user_id,
        'image_url': image_url,
        'style': style,
        'room_type': room_type,
        'created_at': datetime.now()
    })
```

3. **Múltiplas Variações**
```python
# Gerar 4 variações simultaneamente
async def generate_multiple(image, prompt, count=4):
    tasks = [
        replicate_async.run(...) 
        for _ in range(count)
    ]
    results = await asyncio.gather(*tasks)
    return results
```

4. **Webhook para Notificações**
```python
# Quando geração completar, notificar app
@app.post("/webhook/replicate")
async def replicate_webhook(data: dict):
    # Processar webhook do Replicate
    # Enviar push notification para Android
    pass
```

---

## Recursos Adicionais

### Documentação Oficial

- **FastAPI**: https://fastapi.tiangolo.com
- **Replicate**: https://replicate.com/docs
- **Flux Models**: https://replicate.com/black-forest-labs
- **Uvicorn**: https://www.uvicorn.org

### Tutoriais Relacionados

- FastAPI + File Upload: https://fastapi.tiangolo.com/tutorial/request-files/
- Replicate Python SDK: https://github.com/replicate/replicate-python
- Deploy FastAPI: https://fastapi.tiangolo.com/deployment/

### Comunidades

- FastAPI Discord: https://discord.gg/fastapi
- Replicate Discord: https://discord.gg/replicate
- Reddit r/FastAPI: https://reddit.com/r/FastAPI

---

## Conclusão

Esta API fornece uma base sólida para um app de redesign de interiores com IA. O código é modular, bem documentado e pronto para produção.

**Principais Características:**
- ✅ Fácil integração com Android
- ✅ Validação robusta de entrada
- ✅ Otimização automática de imagens
- ✅ Prompts otimizados
- ✅ Tratamento de erros completo
- ✅ Pronto para deploy
- ✅ Documentação interativa (FastAPI docs)

**Próximos Passos Recomendados:**
1. Testar localmente com ngrok
2. Integrar com Android
3. Deploy em Railway/Render
4. Adicionar sistema de créditos
5. Implementar analytics
6. Expandir estilos e opções

Boa sorte com seu projeto! 🚀
