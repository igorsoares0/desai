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
