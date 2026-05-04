"""
Generador de sprites amigables para la simulacion AGV.
Crea imagenes PNG con Pillow usando estilo flat-design limpio.
"""

import math
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw

# Paleta amigable y cálida
PALETA = {
    "rojo": "#e85d5d",
    "azul": "#4a90d9",
    "verde": "#5cb85c",
    "naranja": "#f0ad4e",
    "gris": "#95a5a6",
    "gris_claro": "#bdc3c7",
    "fondo": "#faf9f7",
    "grid": "#e8e6e1",
    "sombra": "#00000033",
    "blanco": "#ffffff",
    "negro": "#2c3e50",
    "destino": "#e74c3c",
    "base": "#8e44ad",
}

_SHEET = None


def _circulo(draw, cx, cy, r, fill, outline=None, width=1):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=outline, width=width)


def _rect_redondeado(draw, xy, radius, fill, outline=None, width=1):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def _sombra(draw, xy, radius=0):
    """Dibuja una sombra suave debajo de un objeto."""
    x1, y1, x2, y2 = xy
    offset = 3
    if radius:
        draw.rounded_rectangle(
            [x1 + offset, y1 + offset, x2 + offset, y2 + offset],
            radius=radius, fill=PALETA["sombra"]
        )
    else:
        draw.ellipse([x1 + offset, y1 + offset, x2 + offset, y2 + offset], fill=PALETA["sombra"])


def generar_robot(tam=64, color="rojo", angulo=0):
    """
    Sprite de robot amigable con ojos, antena y ruedas.
    El angulo rota la cara/direccion del robot.
    """
    img = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = tam // 2, tam // 2

    c = PALETA.get(color, PALETA["rojo"])
    c_oscuro = _oscurecer(c, 0.75)
    c_claro = _aclarar(c, 1.3)

    # Sombra
    _sombra(draw, [cx - 22, cy + 14, cx + 22, cy + 24], radius=8)

    # Ruedas (pequenos circulos a los lados)
    _circulo(draw, cx - 18, cy + 16, 6, PALETA["negro"])
    _circulo(draw, cx + 18, cy + 16, 6, PALETA["negro"])

    # Cuerpo principal (redondeado)
    _rect_redondeado(draw, [cx - 20, cy - 14, cx + 20, cy + 16], radius=10,
                     fill=c, outline=c_oscuro, width=2)

    # Brillo en el cuerpo
    _rect_redondeado(draw, [cx - 14, cy - 10, cx + 10, cy - 4], radius=4,
                     fill=c_claro)

    # Cabeza (circulo)
    _circulo(draw, cx, cy - 20, 14, c, outline=c_oscuro, width=2)

    # Antena
    draw.line([(cx, cy - 34), (cx, cy - 42)], fill=PALETA["negro"], width=2)
    _circulo(draw, cx, cy - 44, 4, PALETA["destino"])

    # Ojos (blancos con pupilas)
    # Rotar los ojos segun angulo para mostrar direccion
    rad = math.radians(-angulo)
    ojo_offset = 6
    ojo_dx = math.cos(rad) * ojo_offset
    ojo_dy = math.sin(rad) * ojo_offset

    # Ojo izquierdo
    _circulo(draw, cx - 6 + ojo_dx * 0.3, cy - 22 + ojo_dy * 0.3, 5, PALETA["blanco"])
    _circulo(draw, cx - 6 + ojo_dx, cy - 22 + ojo_dy, 2.5, PALETA["negro"])

    # Ojo derecho
    _circulo(draw, cx + 6 + ojo_dx * 0.3, cy - 22 + ojo_dy * 0.3, 5, PALETA["blanco"])
    _circulo(draw, cx + 6 + ojo_dx, cy - 22 + ojo_dy, 2.5, PALETA["negro"])

    # Boca (pequena sonrisa)
    draw.arc([cx - 5, cy - 18, cx + 5, cy - 12], start=0, end=180, fill=c_oscuro, width=2)

    return img


def generar_carrito(tam=48, color="gris"):
    """
    Sprite de carrito: una caja con ruedas y una etiqueta.
    """
    img = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = tam // 2, tam // 2

    c = PALETA.get(color, PALETA["gris"])
    c_oscuro = _oscurecer(c, 0.7)

    # Sombra
    _sombra(draw, [cx - 14, cy + 10, cx + 14, cy + 18], radius=4)

    # Ruedas
    _circulo(draw, cx - 10, cy + 14, 4, PALETA["negro"])
    _circulo(draw, cx + 10, cy + 14, 4, PALETA["negro"])

    # Caja (rectangulo redondeado)
    _rect_redondeado(draw, [cx - 14, cy - 12, cx + 14, cy + 10], radius=5,
                     fill=c, outline=c_oscuro, width=2)

    # Etiqueta/franja en la caja
    _rect_redondeado(draw, [cx - 10, cy - 6, cx + 10, cy + 2], radius=3,
                     fill=PALETA["blanco"])

    # Lineas de la etiqueta (simula texto)
    draw.line([(cx - 6, cy - 2), (cx + 6, cy - 2)], fill=c_oscuro, width=2)
    draw.line([(cx - 4, cy + 2), (cx + 4, cy + 2)], fill=c_oscuro, width=2)

    return img


def generar_base(tam=56, color="base"):
    """
    Sprite de base de carga: una plataforma con un rayo.
    """
    img = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = tam // 2, tam // 2

    c = PALETA.get(color, PALETA["base"])
    c_oscuro = _oscurecer(c, 0.7)

    # Sombra
    _sombra(draw, [cx - 20, cy + 12, cx + 20, cy + 20], radius=6)

    # Plataforma exterior (ovalo)
    draw.ellipse([cx - 22, cy - 8, cx + 22, cy + 16], fill=c, outline=c_oscuro, width=2)

    # Plataforma interior (mas clara)
    draw.ellipse([cx - 14, cy - 2, cx + 14, cy + 12], fill=_aclarar(c, 1.4), outline=c_oscuro, width=1)

    # Rayo / icono de carga
    rayo = [
        (cx - 2, cy - 2),
        (cx + 4, cy - 2),
        (cx, cy + 4),
        (cx + 6, cy + 4),
        (cx + 1, cy + 12),
        (cx - 2, cy + 6),
        (cx - 6, cy + 6),
    ]
    draw.polygon(rayo, fill=PALETA["blanco"], outline=c_oscuro)

    return img


def generar_destino(tam=40):
    """
    Sprite de destino: una bandera en un palo.
    """
    img = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = tam // 2, tam // 2

    c = PALETA["destino"]
    c_oscuro = _oscurecer(c, 0.7)

    # Sombra
    _sombra(draw, [cx - 4, cy + 14, cx + 4, cy + 20])

    # Palo
    draw.line([(cx, cy - 16), (cx, cy + 16)], fill=PALETA["negro"], width=3)

    # Bandera (triangulo)
    bandera = [
        (cx + 2, cy - 16),
        (cx + 16, cy - 10),
        (cx + 2, cy - 4),
    ]
    draw.polygon(bandera, fill=c, outline=c_oscuro)

    # Base del palo
    _circulo(draw, cx, cy + 16, 5, PALETA["negro"])

    return img


def generar_suelo_tile(tam=64):
    """
    Tile de suelo con cuadricula muy sutil.
    """
    img = Image.new("RGBA", (tam, tam), PALETA["fondo"])
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, tam - 1, tam - 1], outline=PALETA["grid"], width=1)
    return img


def _oscurecer(hex_color, factor):
    """Oscurece un color hex."""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


def _aclarar(hex_color, factor):
    """Aclara un color hex."""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    r = min(255, int(r * factor))
    g = min(255, int(g * factor))
    b = min(255, int(b * factor))
    return f"#{r:02x}{g:02x}{b:02x}"


def _img_to_tk(img):
    """Convierte PIL Image a PhotoImage de Tkinter via buffer."""
    from tkinter import PhotoImage
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return PhotoImage(data=buffer.read())


def crear_sprite_sheet(robots_colores=None, tam_robot=56, tam_carrito=40, tam_base=48, tam_destino=36):
    """
    Genera un diccionario de PhotoImages listos para usar en Tkinter.
    Se debe mantener una referencia fuerte a estas imagenes para evitar GC.
    """
    from tkinter import PhotoImage

    if robots_colores is None:
        robots_colores = ["rojo", "azul", "verde", "naranja"]

    sheet = {
        "robot": {},
        "carrito": {},
        "base": {},
        "destino": None,
        "suelo": None,
    }

    # Robots por color y angulo (cada 30 grados para suavidad)
    for color in robots_colores:
        sheet["robot"][color] = {}
        for ang in range(0, 360, 30):
            img = generar_robot(tam=tam_robot, color=color, angulo=ang)
            sheet["robot"][color][ang] = _img_to_tk(img)

    # Carritos por color
    for color in list(robots_colores) + ["gris"]:
        img = generar_carrito(tam=tam_carrito, color=color)
        sheet["carrito"][color] = _img_to_tk(img)

    # Bases
    for color in robots_colores:
        img = generar_base(tam=tam_base, color=color)
        sheet["base"][color] = _img_to_tk(img)

    # Destino
    sheet["destino"] = _img_to_tk(generar_destino(tam_destino))

    # Suelo
    sheet["suelo"] = _img_to_tk(generar_suelo_tile(64))

    return sheet


def obtener_robot_mas_cercano(sheet, color, angulo):
    """Devuelve el sprite de robot con el angulo mas cercano disponible."""
    angulos = sorted(sheet["robot"][color].keys())
    # Normalizar angulo a 0-360
    angulo = angulo % 360
    # Encontrar el mas cercano
    return sheet["robot"][color][min(angulos, key=lambda a: abs(a - angulo))]
