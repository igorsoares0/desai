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

# Estilos expandidos com todos os novos
STYLE_DESCRIPTIONS = {
    "eclectic": "eclectic, mixed styles, diverse elements, unique combinations, artistic",
    "modern": "modern, clean lines, neutral colors, contemporary furniture",
    "minimalist": "minimalist, simple, white and wood tones, uncluttered",
    "contemporary": "contemporary, sleek, sophisticated, mixed materials",
    "scandinavian": "scandinavian, cozy, natural materials, bright and airy",
    "mediterranean": "mediterranean, warm colors, terracotta, natural textures, coastal vibes",
    "industrial": "industrial style, exposed brick, metal fixtures, concrete, raw materials",
    "bohemian": "bohemian, colorful, eclectic, plants, textured fabrics, relaxed",
    "rustic": "rustic, wooden elements, warm tones, natural textures",
    "japanese_design": "japanese design, zen, minimalist, natural wood, tatami, shoji screens",
    "arabic": "arabic, ornate patterns, rich colors, arches, mosaic tiles, luxurious textiles",
    "futuristic": "futuristic, high-tech, sleek, metallic, LED lighting, cutting-edge design",
    "luxurious": "luxurious, opulent, rich materials, elegant, high-end furnishings, sophisticated",
    "retro": "retro, vintage inspired, bold colors, nostalgic elements, mid-century influences",
    "professional": "professional, corporate, clean, organized, modern office aesthetic",
    "vintage": "vintage, antique, classic pieces, timeless, traditional craftsmanship",
    "eco_friendly": "eco-friendly, sustainable materials, natural, green, organic, recycled elements",
    "gothic": "gothic, dark colors, dramatic, ornate details, Victorian influences, moody",
    "traditional": "traditional, classic, elegant, rich colors",
    "coastal": "coastal, beach inspired, light colors, natural light",
    "midcentury": "mid-century modern, retro, clean lines, organic shapes"
}

# Room types expandidos
ROOM_DESCRIPTIONS = {
    "living_room": "living room",
    "bedroom": "bedroom",
    "bathroom": "bathroom",
    "kitchen": "kitchen",
    "dining_room": "dining room",
    "home_office": "home office",
    "study_room": "study room",
    "office": "office",
    "coworking": "coworking space"
}

def build_prompt_interior(style: str, room_type: str) -> str:
    """
    Constrói prompt otimizado para redesign de interiores com máximo fotorrealismo

    Args:
        style: Estilo selecionado
        room_type: Tipo de cômodo

    Returns:
        Prompt formatado para alta qualidade e realismo
    """
    style_desc = STYLE_DESCRIPTIONS.get(style.lower(), "modern")
    room_desc = ROOM_DESCRIPTIONS.get(room_type.lower(), "living room")

    # Prompt otimizado para fotorrealismo, composição e definição profissional
    prompt = (
        f"{style_desc} {room_desc}, "
        f"professional interior design photography, "
        f"shot with DSLR camera, wide angle lens, "
        f"perfect composition, rule of thirds, "
        f"natural lighting with ambient light, "
        f"photorealistic, hyperrealistic rendering, "
        f"sharp focus, high detail textures, "
        f"architectural photography, magazine quality, "
        f"8k uhd, crystal clear, professional grade"
    )

    return prompt

def build_prompt_exterior(style: str) -> str:
    """
    Constrói prompt para redesign de exterior mantendo estrutura arquitetônica

    Args:
        style: Estilo arquitetônico

    Returns:
        Prompt formatado para manter estrutura e mudar apenas estilo
    """
    style_desc = STYLE_DESCRIPTIONS.get(style.lower(), "modern")

    # Prompt com forte ênfase em MANTER estrutura e mudar APENAS estilo
    prompt = (
        f"{style_desc} architectural style applied to house exterior, "
        f"keep same building structure and shape, "
        f"maintain original architecture layout, "
        f"same windows and doors placement, "
        f"only change facade style and materials to {style_desc}, "
        f"professional architecture photography, "
        f"photorealistic, high quality, sharp focus, natural lighting"
    )

    return prompt

def build_prompt_garden(style: str, garden_type: str = "garden") -> str:
    """
    Constrói prompt para design de jardins com foco em fotorrealismo

    Args:
        style: Estilo de jardim
        garden_type: Tipo (garden, backyard, front yard, etc)

    Returns:
        Prompt formatado para máximo realismo fotográfico
    """
    style_desc = STYLE_DESCRIPTIONS.get(style.lower(), "modern")

    garden_types = {
        "garden": "garden",
        "backyard": "backyard",
        "front_yard": "front yard",
        "patio": "patio",
        "terrace": "terrace",
        "rooftop": "rooftop garden"
    }

    garden_desc = garden_types.get(garden_type.lower(), "garden")

    # Prompt ultra-direto focado em fotografia real
    prompt = (
        f"real photograph, {style_desc} {garden_desc}, "
        f"actual outdoor photo, DSLR camera, natural lighting, "
        f"real garden, photorealistic, professional landscape photography"
    )

    return prompt

def build_prompt_reference(room_type: str) -> str:
    """
    Constrói prompt para reference style transfer
    Este prompt instrui o modelo a transferir o estilo da imagem de referência
    para a imagem base, mantendo a estrutura do ambiente

    Args:
        room_type: Tipo de cômodo

    Returns:
        Prompt formatado
    """
    room_desc = ROOM_DESCRIPTIONS.get(room_type.lower(), "room")

    prompt = f"{room_desc} interior design, match the style and aesthetic from reference image, apply color palette and design elements from reference, maintain room structure, professional interior design, photorealistic, high quality, well lit, 8k resolution"

    return prompt
