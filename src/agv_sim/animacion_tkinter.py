"""
Animador Tkinter Profesional - INFO1167 Robotica Lab #1
=======================================================
Interfaz de grado profesional con tema oscuro cyber-industrial,
log en tiempo real con narrador, y visualizacion premium del mapa AGV.
"""

import math
import random
import tkinter as tk
from tkinter import ttk

from .simulacion import SimulacionAGV

# ═══════════════════════════════════════════════════════════════════
# PALETA DE COLORES - TEMA OSCURO INDUSTRIAL
# ═══════════════════════════════════════════════════════════════════
THEME = {
    "bg_main": "#0a0e17",
    "bg_panel": "#111827",
    "bg_card": "#1f2937",
    "bg_input": "#374151",
    "border": "#374151",
    "border_glow": "#3b82f6",
    "text_main": "#f3f4f6",
    "text_dim": "#9ca3af",
    "text_muted": "#6b7280",
    "accent": "#3b82f6",
    "accent_bright": "#60a5fa",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "info": "#06b6d4",
    "grid_line": "#1f2937",
    "grid_line_bold": "#374151",
}

_COLORES_ROBOT = {
    "rojo": "#ef4444",
    "azul": "#3b82f6",
    "verde": "#10b981",
    "naranja": "#f97316",
    "gris": "#6b7280",
}

_COLORES_GLOW = {
    "rojo": "#fca5a5",
    "azul": "#93c5fd",
    "verde": "#6ee7b7",
    "naranja": "#fdba74",
    "gris": "#d1d5db",
}


def _color(c):
    return _COLORES_ROBOT.get(c, "#9ca3af")


def _glow(c):
    return _COLORES_GLOW.get(c, "#d1d5db")


# ═══════════════════════════════════════════════════════════════════
# NARRADOR ENTRETENIDO - Convierte eventos tecnicos en logs divertidos
# ═══════════════════════════════════════════════════════════════════
_NARRADOR = {
    "asignado": [
        "Robot {rid} recibio mision: rescatar carrito {cid}",
        "Central asigno carrito {cid} al robot {rid}",
        "Robot {rid}: 'Carrito {cid}, voy por ti!'",
        "Mision asignada -> Robot {rid} -> Carrito {cid}",
    ],
    "recogio": [
        "Robot {rid} abordo carrito {cid} con estilo",
        "Carrito {cid} capturado por robot {rid}",
        "Robot {rid} y carrito {cid} son ahora inseparables",
        "Abordaje exitoso: R{rid} + C{cid}",
    ],
    "entrego": [
        "Robot {rid} completo entrega de carrito {cid}. Cliente feliz!",
        "Entrega exitosa! Robot {rid} dejo carrito {cid} en destino",
        "Ding! Carrito {cid} entregado por robot {rid}",
        "Mision cumplida: Robot {rid} entrego carrito {cid}",
    ],
    "llego_base": [
        "Robot {rid} de vuelta en base. Recargando baterias...",
        "Base: Robot {rid} aterrizo. Iniciando carga rapida",
        "Robot {rid} en base. Pausa para cafe electrico",
        "R{rid} -> BASE. Carga iniciada.",
    ],
    "listo": [
        "Robot {rid} al 100%. Listo para la siguiente mision!",
        "Bateria completa! Robot {rid} dice 'Vamos de nuevo!'",
        "Robot {rid} cargado y listo para el caos",
        "R{rid}: Bateria 100%. Sistema operativo.",
    ],
}


def _narrar(evento: str) -> str:
    """Convierte un evento tecnico en un mensaje entretenido."""
    try:
        if "asignado" in evento:
            rid = evento.split("robot ")[1].split()[0]
            cid = evento.split("carrito ")[1]
            return random.choice(_NARRADOR["asignado"]).format(rid=rid, cid=cid)
        elif "recogio" in evento:
            rid = evento.split("robot ")[1].split()[0]
            cid = evento.split("carrito ")[1]
            return random.choice(_NARRADOR["recogio"]).format(rid=rid, cid=cid)
        elif "entrego" in evento:
            rid = evento.split("robot ")[1].split()[0]
            cid = evento.split("carrito ")[1]
            return random.choice(_NARRADOR["entrego"]).format(rid=rid, cid=cid)
        elif "llego a base" in evento:
            rid = evento.split("robot ")[1].split()[0]
            return random.choice(_NARRADOR["llego_base"]).format(rid=rid)
        elif "bateria 100%" in evento:
            rid = evento.split("robot ")[1].split()[0]
            return random.choice(_NARRADOR["listo"]).format(rid=rid)
    except Exception:
        pass
    return evento


def _tipo_evento(evento: str) -> str:
    if "asignado" in evento:
        return "info"
    elif "recogio" in evento:
        return "success"
    elif "entrego" in evento:
        return "accent"
    elif "llego a base" in evento:
        return "warning"
    elif "bateria 100%" in evento:
        return "success"
    return "dim"


# ═══════════════════════════════════════════════════════════════════
# COMPONENTE: BARRA DE PROGRESO PERSONALIZADA
# ═══════════════════════════════════════════════════════════════════
class ProgressBar(tk.Canvas):
    def __init__(self, parent, width=120, height=8, **kw):
        super().__init__(parent, width=width, height=height, bg=THEME["bg_card"],
                         highlightthickness=0, **kw)
        self.width = width
        self.height = height
        self._value = 0
        self._color = THEME["success"]
        self._draw()

    def _draw(self):
        self.delete("all")
        # Fondo
        self.create_rectangle(0, 0, self.width, self.height,
                              fill=THEME["bg_input"], outline="", width=0)
        # Barra
        fill_w = int(self.width * (self._value / 100))
        if fill_w > 0:
            self.create_rectangle(0, 0, fill_w, self.height,
                                  fill=self._color, outline="", width=0)

    def set_value(self, value, color=None):
        self._value = max(0, min(100, value))
        if color:
            self._color = color
        elif self._value < 20:
            self._color = THEME["danger"]
        elif self._value < 50:
            self._color = THEME["warning"]
        else:
            self._color = THEME["success"]
        self._draw()


# ═══════════════════════════════════════════════════════════════════
# COMPONENTE: STAT CARD
# ═══════════════════════════════════════════════════════════════════
class StatCard(tk.Frame):
    def __init__(self, parent, title, value="0", color=THEME["accent"]):
        super().__init__(parent, bg=THEME["bg_card"], padx=12, pady=8)
        self.configure(highlightbackground=THEME["border"], highlightthickness=1)
        tk.Label(self, text=title.upper(), font=("JetBrains Mono", 8),
                bg=THEME["bg_card"], fg=THEME["text_muted"]).pack(anchor="w")
        self.val_label = tk.Label(self, text=value, font=("JetBrains Mono", 18, "bold"),
                                   bg=THEME["bg_card"], fg=color)
        self.val_label.pack(anchor="w")

    def set_value(self, value, color=None):
        self.val_label.config(text=str(value))
        if color:
            self.val_label.config(fg=color)


# ═══════════════════════════════════════════════════════════════════
# ANIMADOR PRINCIPAL
# ═══════════════════════════════════════════════════════════════════
class AnimadorTkinter:
    def __init__(self, sim):
        self.sim = sim
        self.ventana = tk.Tk()
        self.ventana.title("INFO1167 Robotica | Lab #1 AGV - Control de Bodega")
        self.ventana.configure(bg=THEME["bg_main"])

        # Dimensiones
        self.ancho_ventana = 1280
        self.alto_ventana = 860
        self.ancho_mapa = 800
        self.ancho_panel = self.ancho_ventana - self.ancho_mapa

        # Centrar
        sw = self.ventana.winfo_screenwidth()
        sh = self.ventana.winfo_screenheight()
        x = (sw - self.ancho_ventana) // 2
        y = (sh - self.alto_ventana) // 2 - 20
        self.ventana.geometry(f"{self.ancho_ventana}x{self.alto_ventana}+{x}+{y}")
        self.ventana.minsize(1100, 700)

        # Layout principal: izquierda mapa, derecha panel
        self._crear_panel_izquierdo()
        self._crear_panel_derecho()

        # Inicializar objetos del canvas
        self._init_canvas_objects()

        # Estado para logs
        self._ultimos_eventos = 0

    # ──────────────────────────────────────────────────────────────
    # PANEL IZQUIERDO: MAPA
    # ──────────────────────────────────────────────────────────────
    def _crear_panel_izquierdo(self):
        self.frame_mapa = tk.Frame(self.ventana, bg=THEME["bg_main"], width=self.ancho_mapa)
        self.frame_mapa.pack(side="left", fill="both", expand=False)
        self.frame_mapa.pack_propagate(False)

        # Header del mapa
        hdr = tk.Frame(self.frame_mapa, bg=THEME["bg_panel"], height=44)
        hdr.pack(fill="x", padx=8, pady=(8, 0))
        hdr.pack_propagate(False)

        tk.Label(hdr, text="● SISTEMA DE NAVEGACION AGV", font=("JetBrains Mono", 11, "bold"),
                bg=THEME["bg_panel"], fg=THEME["accent_bright"]).pack(side="left", padx=12, pady=8)

        self.lbl_status = tk.Label(hdr, text="ONLINE", font=("JetBrains Mono", 9, "bold"),
                                    bg=THEME["bg_panel"], fg=THEME["success"])
        self.lbl_status.pack(side="right", padx=12, pady=8)

        # Canvas del mapa
        alto_canvas = self.alto_ventana - 60
        self.canvas = tk.Canvas(self.frame_mapa, width=self.ancho_mapa - 16,
                                height=alto_canvas, bg=THEME["bg_main"],
                                highlightthickness=1, highlightbackground=THEME["border"])
        self.canvas.pack(padx=8, pady=8)

        self.alto_canvas = alto_canvas

        w, h = self.sim.config.ancho, self.sim.config.alto
        margen = 50
        self.celda_w = (self.ancho_mapa - 16 - margen * 2) / w
        self.celda_h = (alto_canvas - margen * 2) / h
        self.offset_x = margen
        self.offset_y = margen

        self._dibujar_grilla(w, h)

    # ──────────────────────────────────────────────────────────────
    # PANEL DERECHO: STATS, LOGS, CONTROLES
    # ──────────────────────────────────────────────────────────────
    def _crear_panel_derecho(self):
        self.frame_der = tk.Frame(self.ventana, bg=THEME["bg_main"], width=self.ancho_panel)
        self.frame_der.pack(side="right", fill="both", expand=True)
        self.frame_der.pack_propagate(False)

        pad = 10

        # === HEADER ===
        hdr = tk.Frame(self.frame_der, bg=THEME["bg_panel"], height=44)
        hdr.pack(fill="x", padx=pad, pady=(pad, 0))
        hdr.pack_propagate(False)
        tk.Label(hdr, text="PANEL DE CONTROL", font=("JetBrains Mono", 11, "bold"),
                bg=THEME["bg_panel"], fg=THEME["text_main"]).pack(side="left", padx=12, pady=8)

        # === STATS CARDS ===
        stats_frame = tk.Frame(self.frame_der, bg=THEME["bg_main"])
        stats_frame.pack(fill="x", padx=pad, pady=(pad, 0))

        self.stat_tick = StatCard(stats_frame, "Tick", "0", THEME["accent"])
        self.stat_tick.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.stat_entregas = StatCard(stats_frame, "Entregas", "0", THEME["success"])
        self.stat_entregas.pack(side="left", fill="x", expand=True, padx=(2, 2))
        self.stat_robots = StatCard(stats_frame, "Robots", str(len(self.sim.robots)), THEME["info"])
        self.stat_robots.pack(side="left", fill="x", expand=True, padx=(4, 0))

        # === BATERIAS ===
        batt_frame = tk.LabelFrame(self.frame_der, text=" NIVELES DE BATERIA ",
                                    font=("JetBrains Mono", 9, "bold"),
                                    bg=THEME["bg_main"], fg=THEME["text_dim"],
                                    highlightbackground=THEME["border"], highlightthickness=1)
        batt_frame.pack(fill="x", padx=pad, pady=(pad, 0))

        self.barras_bateria = {}
        for r in self.sim.robots:
            row = tk.Frame(batt_frame, bg=THEME["bg_main"])
            row.pack(fill="x", padx=8, pady=3)
            tk.Label(row, text=f"R{r.id}", font=("JetBrains Mono", 9, "bold"),
                    bg=THEME["bg_main"], fg=_color(r.color), width=3).pack(side="left")
            bar = ProgressBar(row, width=140, height=10)
            bar.pack(side="left", padx=(6, 0))
            bar.set_value(int(r.bateria))
            lbl = tk.Label(row, text=f"{int(r.bateria)}%", font=("JetBrains Mono", 9),
                          bg=THEME["bg_main"], fg=THEME["text_dim"], width=5)
            lbl.pack(side="right")
            self.barras_bateria[r.id] = (bar, lbl)

        # === ESTADOS ===
        estado_frame = tk.LabelFrame(self.frame_der, text=" ESTADOS ",
                                      font=("JetBrains Mono", 9, "bold"),
                                      bg=THEME["bg_main"], fg=THEME["text_dim"],
                                      highlightbackground=THEME["border"], highlightthickness=1)
        estado_frame.pack(fill="x", padx=pad, pady=(pad, 0))
        self.lbl_estados = tk.Label(estado_frame, text="Inicializando...",
                                     font=("JetBrains Mono", 9),
                                     bg=THEME["bg_main"], fg=THEME["text_dim"],
                                     justify="left", wraplength=self.ancho_panel - 40)
        self.lbl_estados.pack(padx=8, pady=6, anchor="w")

        # === LOG EN TIEMPO REAL ===
        log_frame = tk.LabelFrame(self.frame_der, text=" LOG DE OPERACIONES ",
                                   font=("JetBrains Mono", 9, "bold"),
                                   bg=THEME["bg_main"], fg=THEME["text_dim"],
                                   highlightbackground=THEME["border"], highlightthickness=1)
        log_frame.pack(fill="both", expand=True, padx=pad, pady=(pad, pad))

        # Toolbar del log
        log_toolbar = tk.Frame(log_frame, bg=THEME["bg_main"])
        log_toolbar.pack(fill="x", padx=4, pady=(4, 0))

        tk.Button(log_toolbar, text="Limpiar", font=("JetBrains Mono", 8),
                 bg=THEME["bg_card"], fg=THEME["text_dim"],
                 activebackground=THEME["bg_input"], activeforeground=THEME["text_main"],
                 relief="flat", cursor="hand2",
                 command=self._limpiar_log).pack(side="right", padx=2)

        # Widget Text para logs
        self.txt_log = tk.Text(log_frame, font=("JetBrains Mono", 9),
                               bg=THEME["bg_panel"], fg=THEME["text_dim"],
                               highlightthickness=0, relief="flat",
                               wrap="word", state="disabled",
                               padx=8, pady=6)
        self.txt_log.pack(fill="both", expand=True, padx=4, pady=4)

        # Scrollbar personalizada
        sb = ttk.Scrollbar(self.txt_log, command=self.txt_log.yview)
        sb.pack(side="right", fill="y")
        self.txt_log.config(yscrollcommand=sb.set)

        # Tags de colores para el log
        self.txt_log.tag_configure("timestamp", foreground=THEME["text_muted"], font=("JetBrains Mono", 8))
        self.txt_log.tag_configure("dim", foreground=THEME["text_dim"])
        self.txt_log.tag_configure("info", foreground=THEME["accent_bright"])
        self.txt_log.tag_configure("success", foreground=THEME["success"])
        self.txt_log.tag_configure("accent", foreground=THEME["accent"])
        self.txt_log.tag_configure("warning", foreground=THEME["warning"])
        self.txt_log.tag_configure("danger", foreground=THEME["danger"])

        # Mensaje inicial
        self._log("Sistema iniciado. Bodega AGV operativa.", "success")
        self._log("4 robots en espera. 8 carritos en almacen.", "info")
        self._log("Algoritmos de grafos cargados: BFS, DFS, Dijkstra", "dim")

    def _limpiar_log(self):
        self.txt_log.config(state="normal")
        self.txt_log.delete("1.0", "end")
        self.txt_log.config(state="disabled")

    def _log(self, mensaje, tag="dim"):
        self.txt_log.config(state="normal")
        ts = f"[{self.sim.ticks:04d}] "
        self.txt_log.insert("end", ts, "timestamp")
        self.txt_log.insert("end", mensaje + "\n", tag)
        self.txt_log.see("end")
        self.txt_log.config(state="disabled")

    # ──────────────────────────────────────────────────────────────
    # CANVAS: GRILLA Y OBJETOS
    # ──────────────────────────────────────────────────────────────
    def _coord(self, gx, gy):
        x = gx * self.celda_w + self.celda_w / 2 + self.offset_x
        y = gy * self.celda_h + self.celda_h / 2 + self.offset_y
        return x, y

    def _dibujar_grilla(self, w, h):
        # Fondo sutil con gradiente simulado (rectangulos horizontales)
        for j in range(h):
            y1 = j * self.celda_h + self.offset_y
            y2 = (j + 1) * self.celda_h + self.offset_y
            color = "#0f172a" if j % 2 == 0 else "#0a0e17"
            self.canvas.create_rectangle(self.offset_x, y1,
                                         w * self.celda_w + self.offset_x, y2,
                                         fill=color, outline="", width=0)

        # Lineas de grilla
        for i in range(w + 1):
            x = i * self.celda_w + self.offset_x
            self.canvas.create_line(x, self.offset_y, x, h * self.celda_h + self.offset_y,
                                    fill=THEME["grid_line"], width=1)
        for j in range(h + 1):
            y = j * self.celda_h + self.offset_y
            self.canvas.create_line(self.offset_x, y, w * self.celda_w + self.offset_x, y,
                                    fill=THEME["grid_line"], width=1)

        # Bordes externos mas gruesos
        self.canvas.create_rectangle(self.offset_x, self.offset_y,
                                     w * self.celda_w + self.offset_x,
                                     h * self.celda_h + self.offset_y,
                                     outline=THEME["border"], width=2)

        # Labels de coordenadas (eje X)
        for i in range(w):
            x = i * self.celda_w + self.offset_x + self.celda_w / 2
            self.canvas.create_text(x, self.offset_y - 12, text=str(i),
                                    font=("JetBrains Mono", 8),
                                    fill=THEME["text_muted"])

        # Labels de coordenadas (eje Y)
        for j in range(h):
            y = j * self.celda_h + self.offset_y + self.celda_h / 2
            self.canvas.create_text(self.offset_x - 12, y, text=str(j),
                                    font=("JetBrains Mono", 8),
                                    fill=THEME["text_muted"])

    def _init_canvas_objects(self):
        self.obj_robots = {}
        self.obj_glow = {}
        self.obj_dir = {}
        self.obj_textos = {}
        self.obj_carritos = {}
        self.obj_destinos = {}
        self.obj_bases = {}
        self.obj_trails = {}  # Rastro de movimiento

        # Dibujar bases
        for r in self.sim.robots:
            bx, by = self._coord(r.base[0], r.base[1])
            # Zona de base (circulo punteado grande)
            self.obj_bases[r.id] = self.canvas.create_oval(
                bx - 28, by - 28, bx + 28, by + 28,
                outline=_color(r.color), width=2, dash=(4, 4)
            )
            # Label BASE
            self.canvas.create_text(bx, by - 32, text=f"BASE {r.id}",
                                    font=("JetBrains Mono", 7, "bold"),
                                    fill=_color(r.color))

        # Dibujar destinos
        for c in self.sim.carritos:
            dx, dy = self._coord(c.destino[0], c.destino[1])
            # Cruz de destino
            self.obj_destinos[c.id] = [
                self.canvas.create_line(dx - 10, dy - 10, dx + 10, dy + 10,
                                        fill=THEME["danger"], width=2),
                self.canvas.create_line(dx - 10, dy + 10, dx + 10, dy - 10,
                                        fill=THEME["danger"], width=2),
                self.canvas.create_oval(dx - 14, dy - 14, dx + 14, dy + 14,
                                        outline=THEME["danger"], width=1, dash=(3, 3)),
            ]

        # Dibujar carritos
        for c in self.sim.carritos:
            x, y = self._coord(c.nodo[0], c.nodo[1])
            self.obj_carritos[c.id] = self.canvas.create_polygon(
                x, y - 12, x + 12, y, x, y + 12, x - 12, y,
                fill=_color(c.color_original), outline=THEME["text_main"], width=2
            )
            # Label carrito
            self.canvas.create_text(x, y, text=str(c.id),
                                    font=("JetBrains Mono", 8, "bold"),
                                    fill=THEME["bg_main"])

        # Dibujar robots (ultimo para estar arriba)
        for r in self.sim.robots:
            x, y = self._coord(r.nodo[0], r.nodo[1])
            # Glow effect (circulo grande semitransparente)
            self.obj_glow[r.id] = self.canvas.create_oval(
                x - 24, y - 24, x + 24, y + 24,
                fill="", outline=_glow(r.color), width=3
            )
            # Cuerpo del robot
            self.obj_robots[r.id] = self.canvas.create_oval(
                x - 16, y - 16, x + 16, y + 16,
                fill=_color(r.color), outline=THEME["text_main"], width=2
            )
            # Linea de direccion
            dx = x + math.cos(math.radians(r.angulo)) * 14
            dy = y - math.sin(math.radians(r.angulo)) * 14
            self.obj_dir[r.id] = self.canvas.create_line(
                x, y, dx, dy, fill=THEME["text_main"], width=3
            )
            # ID del robot
            self.obj_textos[r.id] = self.canvas.create_text(
                x + 20, y - 20, text=f"R{r.id}",
                font=("JetBrains Mono", 10, "bold"),
                fill=THEME["text_main"], anchor="w"
            )
            # Rastro (linea que se extiende con el movimiento)
            self.obj_trails[r.id] = []

    # ──────────────────────────────────────────────────────────────
    # ACTUALIZACION EN TIEMPO REAL
    # ──────────────────────────────────────────────────────────────
    def actualizar(self):
        # Actualizar robots
        for r in self.sim.robots:
            x, y = self._coord(r.nodo[0], r.nodo[1])

            # Glow sigue al robot
            self.canvas.coords(self.obj_glow[r.id], x - 24, y - 24, x + 24, y + 24)
            # Color del glow segun estado
            if r.estado.value == "cargando":
                self.canvas.itemconfig(self.obj_glow[r.id], outline=THEME["warning"])
            elif r.estado.value == "llevando_carrito":
                self.canvas.itemconfig(self.obj_glow[r.id], outline=_glow(r.color))
            else:
                self.canvas.itemconfig(self.obj_glow[r.id], outline=_glow(r.color))

            # Cuerpo
            self.canvas.coords(self.obj_robots[r.id], x - 16, y - 16, x + 16, y + 16)

            # Linea de direccion
            dx = x + math.cos(math.radians(r.angulo)) * 14
            dy = y - math.sin(math.radians(r.angulo)) * 14
            self.canvas.coords(self.obj_dir[r.id], x, y, dx, dy)

            # Texto
            self.canvas.coords(self.obj_textos[r.id], x + 20, y - 20)

            # Rastro: agregar punto cada ciertos ticks
            if self.sim.ticks % 5 == 0:
                trail = self.obj_trails[r.id]
                dot = self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3,
                                              fill=_color(r.color), outline="", width=0)
                trail.append(dot)
                if len(trail) > 15:
                    old = trail.pop(0)
                    self.canvas.delete(old)

        # Actualizar carritos
        for c in self.sim.carritos:
            x, y = self._coord(c.nodo[0], c.nodo[1])
            self.canvas.coords(self.obj_carritos[c.id],
                               x, y - 12, x + 12, y, x, y + 12, x - 12, y)
            color = _color(c.color_original)
            self.canvas.itemconfig(self.obj_carritos[c.id], fill=color)

        # Actualizar stats
        self.stat_tick.set_value(self.sim.ticks)
        entregas = sum(r.entregas_completadas for r in self.sim.robots)
        self.stat_entregas.set_value(entregas)

        # Actualizar baterias
        for r in self.sim.robots:
            bar, lbl = self.barras_bateria[r.id]
            bar.set_value(int(r.bateria))
            lbl.config(text=f"{int(r.bateria)}%")

        # Actualizar estados
        estados_texto = "  ".join(
            f"R{r.id}:{r.estado.value.upper()}" for r in self.sim.robots
        )
        self.lbl_estados.config(text=estados_texto)

        # Procesar nuevos eventos para el log
        nuevos = self.sim.eventos[self._ultimos_eventos:]
        self._ultimos_eventos = len(self.sim.eventos)
        for ev in nuevos:
            narrado = _narrar(ev)
            tag = _tipo_evento(ev)
            self._log(narrado, tag)

    # ──────────────────────────────────────────────────────────────
    # ANIMACION LOOP
    # ──────────────────────────────────────────────────────────────
    def _paso(self, ticks, velocidad, contador):
        if contador >= ticks:
            self.lbl_status.config(text="COMPLETADO", fg=THEME["success"])
            self._log("=" * 40, "dim")
            self._log("SIMULACION COMPLETADA", "success")
            self._log(f"Total entregas: {sum(r.entregas_completadas for r in self.sim.robots)}", "accent")
            self._log("Cierre la ventana para salir", "dim")
            return

        self.sim.paso()
        self.actualizar()
        self.ventana.after(int(1000 / velocidad), self._paso, ticks, velocidad, contador + 1)

    def animar(self, ticks=None, velocidad=20):
        limite = ticks if ticks is not None else self.sim.config.max_ticks
        self._paso(limite, velocidad, 0)
        self.ventana.mainloop()
