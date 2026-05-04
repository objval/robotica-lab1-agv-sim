"""
Animador Tkinter con sprites amigables - INFO1167 Robotica Lab #1
=================================================================
Interfaz limpia, calida y facil de entender. Sprites propios generados
con Pillow: robots con ojos, carritos con ruedas, bases con rayo.
"""

import math
import random
import tkinter as tk
from tkinter import ttk

from .simulacion import SimulacionAGV
from .sprites import PALETA, crear_sprite_sheet, obtener_robot_mas_cercano

# Narrador entretenido
_NARRADOR = {
    "asignado": [
        "R{rid} recibio mision: buscar carrito {cid}",
        "Central -> R{rid}: Ve por el carrito {cid}",
        "R{rid}: 'Carrito {cid}, ya voy!'",
    ],
    "recogio": [
        "R{rid} recogio el carrito {cid}",
        "Carrito {cid} abordado por R{rid}",
        "R{rid} + Carrito {cid} = equipo perfecto",
    ],
    "entrego": [
        "R{rid} entrego carrito {cid}. Cliente feliz!",
        "Entrega exitosa! R{rid} completo mision con {cid}",
        "Ding! Carrito {cid} entregado",
    ],
    "llego_base": [
        "R{rid} de vuelta en base. Cargando...",
        "Base: R{rid} aterrizo. Iniciando carga",
        "R{rid} en base. Recarga rapida",
    ],
    "listo": [
        "R{rid} al 100%. Listo para siguiente mision!",
        "Bateria completa! R{rid} dice 'Vamos!'",
        "R{rid} cargado. Sistema operativo",
    ],
}


def _narrar(evento: str) -> str:
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


class AnimadorTkinter:
    def __init__(self, sim):
        self.sim = sim
        self.ventana = tk.Tk()
        self.ventana.title("INFO1167 Robotica | Lab #1 - Simulacion AGV")
        self.ventana.configure(bg=PALETA["fondo"])

        # Dimensiones
        self.ancho_ventana = 1200
        self.alto_ventana = 800
        self.ancho_mapa = 780
        self.ancho_panel = self.ancho_ventana - self.ancho_mapa - 20

        # Centrar
        sw = self.ventana.winfo_screenwidth()
        sh = self.ventana.winfo_screenheight()
        x = (sw - self.ancho_ventana) // 2
        y = (sh - self.alto_ventana) // 2 - 20
        self.ventana.geometry(f"{self.ancho_ventana}x{self.alto_ventana}+{x}+{y}")
        self.ventana.minsize(1050, 650)

        # Generar sprites (MANTENER REFERENCIA para evitar GC!)
        colores = [r.color for r in sim.robots]
        self.sprite_sheet = crear_sprite_sheet(
            robots_colores=colores,
            tam_robot=50,
            tam_carrito=34,
            tam_base=44,
            tam_destino=32,
        )

        # Layout
        self._crear_panel_izquierdo()
        self._crear_panel_derecho()
        self._init_canvas_objects()

        self._ultimos_eventos = 0

    # ------------------------------------------------------------------
    # PANEL IZQUIERDO: MAPA
    # ------------------------------------------------------------------
    def _crear_panel_izquierdo(self):
        pad = 10
        self.frame_mapa = tk.Frame(self.ventana, bg=PALETA["fondo"], width=self.ancho_mapa)
        self.frame_mapa.pack(side="left", fill="both", expand=False, padx=(pad, 0), pady=pad)
        self.frame_mapa.pack_propagate(False)

        # Header
        hdr = tk.Frame(self.frame_mapa, bg=PALETA["blanco"], height=42)
        hdr.pack(fill="x", padx=0, pady=(0, pad))
        hdr.pack_propagate(False)
        tk.Label(hdr, text="Mapa de Bodega", font=("Segoe UI", 13, "bold"),
                bg=PALETA["blanco"], fg=PALETA["negro"]).pack(side="left", padx=14, pady=6)

        self.lbl_status = tk.Label(hdr, text="EN LINEA", font=("Segoe UI", 9, "bold"),
                                    bg=PALETA["blanco"], fg=PALETA["verde"])
        self.lbl_status.pack(side="right", padx=14, pady=6)

        # Canvas
        alto_c = self.alto_ventana - 80
        self.canvas = tk.Canvas(self.frame_mapa, width=self.ancho_mapa - 20,
                                height=alto_c, bg=PALETA["fondo"],
                                highlightthickness=1, highlightbackground=PALETA["grid"])
        self.canvas.pack()
        self.alto_canvas = alto_c

        w, h = self.sim.config.ancho, self.sim.config.alto
        margen = 45
        self.celda_w = (self.ancho_mapa - 20 - margen * 2) / w
        self.celda_h = (alto_c - margen * 2) / h
        self.offset_x = margen
        self.offset_y = margen

        self._dibujar_grilla(w, h)

    def _dibujar_grilla(self, w, h):
        # Fondo de celdas alternadas (sutil)
        for j in range(h):
            for i in range(w):
                x1 = i * self.celda_w + self.offset_x
                y1 = j * self.celda_h + self.offset_y
                x2 = x1 + self.celda_w
                y2 = y1 + self.celda_h
                color = "#ffffff" if (i + j) % 2 == 0 else "#f5f4f2"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="", width=0)

        # Lineas de grilla
        for i in range(w + 1):
            x = i * self.celda_w + self.offset_x
            self.canvas.create_line(x, self.offset_y, x, h * self.celda_h + self.offset_y,
                                    fill=PALETA["grid"], width=1)
        for j in range(h + 1):
            y = j * self.celda_h + self.offset_y
            self.canvas.create_line(self.offset_x, y, w * self.celda_w + self.offset_x, y,
                                    fill=PALETA["grid"], width=1)

        # Borde exterior
        self.canvas.create_rectangle(
            self.offset_x, self.offset_y,
            w * self.celda_w + self.offset_x, h * self.celda_h + self.offset_y,
            outline=PALETA["gris"], width=2
        )

        # Ejes numerados
        for i in range(w):
            x = i * self.celda_w + self.offset_x + self.celda_w / 2
            self.canvas.create_text(x, self.offset_y - 14, text=str(i),
                                    font=("Segoe UI", 9), fill=PALETA["gris"])
        for j in range(h):
            y = j * self.celda_h + self.offset_y + self.celda_h / 2
            self.canvas.create_text(self.offset_x - 14, y, text=str(j),
                                    font=("Segoe UI", 9), fill=PALETA["gris"])

    def _coord(self, gx, gy):
        x = gx * self.celda_w + self.celda_w / 2 + self.offset_x
        y = gy * self.celda_h + self.celda_h / 2 + self.offset_y
        return x, y

    # ------------------------------------------------------------------
    # PANEL DERECHO: STATS + LOG
    # ------------------------------------------------------------------
    def _crear_panel_derecho(self):
        pad = 10
        self.frame_der = tk.Frame(self.ventana, bg=PALETA["fondo"], width=self.ancho_panel)
        self.frame_der.pack(side="right", fill="both", expand=True, padx=(0, pad), pady=pad)
        self.frame_der.pack_propagate(False)

        # --- Stats ---
        stats = tk.Frame(self.frame_der, bg=PALETA["blanco"])
        stats.pack(fill="x", pady=(0, pad))
        stats.configure(highlightbackground=PALETA["grid"], highlightthickness=1)

        self._stat_box(stats, "Tick", "0", PALETA["negro"], "tick")
        self._stat_box(stats, "Entregas", "0", PALETA["verde"], "entregas")
        self._stat_box(stats, "Robots", str(len(self.sim.robots)), PALETA["azul"], "robots")

        # --- Baterias ---
        batt = tk.LabelFrame(self.frame_der, text=" Bateria de Robots ",
                             font=("Segoe UI", 10, "bold"),
                             bg=PALETA["fondo"], fg=PALETA["negro"],
                             highlightbackground=PALETA["grid"], highlightthickness=1)
        batt.pack(fill="x", pady=(0, pad))

        self.barras_bateria = {}
        for r in self.sim.robots:
            row = tk.Frame(batt, bg=PALETA["fondo"])
            row.pack(fill="x", padx=8, pady=3)

            # Mini sprite del robot
            tk.Label(row, image=self.sprite_sheet["robot"][r.color][0],
                    bg=PALETA["fondo"]).pack(side="left")

            tk.Label(row, text=f"R{r.id}", font=("Segoe UI", 10, "bold"),
                    bg=PALETA["fondo"], fg=PALETA["negro"], width=3).pack(side="left")

            bar = tk.Canvas(row, width=110, height=10, bg=PALETA["grid"],
                           highlightthickness=0)
            bar.pack(side="left", padx=(6, 0))
            fill_id = bar.create_rectangle(0, 0, 110, 10, fill=PALETA["verde"], width=0)

            lbl = tk.Label(row, text="100%", font=("Segoe UI", 9),
                          bg=PALETA["fondo"], fg=PALETA["negro"], width=5)
            lbl.pack(side="right")
            self.barras_bateria[r.id] = (bar, fill_id, lbl)

        # --- Estados ---
        est = tk.LabelFrame(self.frame_der, text=" Estados ",
                            font=("Segoe UI", 10, "bold"),
                            bg=PALETA["fondo"], fg=PALETA["negro"],
                            highlightbackground=PALETA["grid"], highlightthickness=1)
        est.pack(fill="x", pady=(0, pad))
        self.lbl_estados = tk.Label(est, text="Inicializando...",
                                     font=("Segoe UI", 9),
                                     bg=PALETA["fondo"], fg=PALETA["negro"],
                                     justify="left", wraplength=self.ancho_panel - 40)
        self.lbl_estados.pack(padx=8, pady=6, anchor="w")

        # --- Log ---
        log_frame = tk.LabelFrame(self.frame_der, text=" Registro de Eventos ",
                                   font=("Segoe UI", 10, "bold"),
                                   bg=PALETA["fondo"], fg=PALETA["negro"],
                                   highlightbackground=PALETA["grid"], highlightthickness=1)
        log_frame.pack(fill="both", expand=True)

        self.txt_log = tk.Text(log_frame, font=("Segoe UI", 9),
                               bg=PALETA["blanco"], fg=PALETA["negro"],
                               highlightthickness=0, relief="flat",
                               wrap="word", state="disabled",
                               padx=8, pady=6)
        self.txt_log.pack(fill="both", expand=True, padx=4, pady=4)

        sb = ttk.Scrollbar(self.txt_log, command=self.txt_log.yview)
        sb.pack(side="right", fill="y")
        self.txt_log.config(yscrollcommand=sb.set)

        self.txt_log.tag_configure("timestamp", foreground=PALETA["gris"], font=("Segoe UI", 8))
        self.txt_log.tag_configure("dim", foreground=PALETA["negro"])
        self.txt_log.tag_configure("info", foreground=PALETA["azul"])
        self.txt_log.tag_configure("success", foreground=PALETA["verde"])
        self.txt_log.tag_configure("accent", foreground=PALETA["naranja"])
        self.txt_log.tag_configure("warning", foreground=PALETA["naranja"])
        self.txt_log.tag_configure("danger", foreground=PALETA["rojo"])

        self._log("Sistema iniciado. Bodega AGV lista.", "success")
        self._log("4 robots en espera. 8 carritos en almacen.", "info")

    def _stat_box(self, parent, title, value, color, attr_name):
        box = tk.Frame(parent, bg=PALETA["blanco"], padx=10, pady=8)
        box.pack(side="left", fill="x", expand=True)
        tk.Label(box, text=title, font=("Segoe UI", 9),
                bg=PALETA["blanco"], fg=PALETA["gris"]).pack(anchor="w")
        lbl = tk.Label(box, text=value, font=("Segoe UI", 20, "bold"),
                      bg=PALETA["blanco"], fg=color)
        lbl.pack(anchor="w")
        setattr(self, f"val_{attr_name}", lbl)

    def _log(self, mensaje, tag="dim"):
        self.txt_log.config(state="normal")
        ts = f"[{self.sim.ticks:04d}] "
        self.txt_log.insert("end", ts, "timestamp")
        self.txt_log.insert("end", mensaje + "\n", tag)
        self.txt_log.see("end")
        self.txt_log.config(state="disabled")

    # ------------------------------------------------------------------
    # OBJETOS EN CANVAS
    # ------------------------------------------------------------------
    def _init_canvas_objects(self):
        self.obj_bases = {}
        self.obj_robots = {}
        self.obj_carritos = {}
        self.obj_destinos = {}

        # Bases (sprite)
        for r in self.sim.robots:
            bx, by = self._coord(r.base[0], r.base[1])
            sprite = self.sprite_sheet["base"].get(r.color, self.sprite_sheet["base"][list(self.sprite_sheet["base"].keys())[0]])
            self.obj_bases[r.id] = self.canvas.create_image(bx, by, image=sprite)
            self.canvas.create_text(bx, by + 26, text=f"Base {r.id}",
                                    font=("Segoe UI", 8), fill=PALETA["gris"])

        # Destinos (sprite)
        for c in self.sim.carritos:
            dx, dy = self._coord(c.destino[0], c.destino[1])
            self.obj_destinos[c.id] = self.canvas.create_image(dx, dy - 8,
                image=self.sprite_sheet["destino"])

        # Carritos (sprite)
        for c in self.sim.carritos:
            x, y = self._coord(c.nodo[0], c.nodo[1])
            color = c.color_original if c.color_original in self.sprite_sheet["carrito"] else "gris"
            self.obj_carritos[c.id] = self.canvas.create_image(x, y,
                image=self.sprite_sheet["carrito"][color])

        # Robots (sprite) - van al final para estar arriba
        for r in self.sim.robots:
            x, y = self._coord(r.nodo[0], r.nodo[1])
            sprite = obtener_robot_mas_cercano(self.sprite_sheet, r.color, r.angulo)
            self.obj_robots[r.id] = self.canvas.create_image(x, y, image=sprite)

    # ------------------------------------------------------------------
    # ACTUALIZACION
    # ------------------------------------------------------------------
    def actualizar(self):
        # Robots: posicion + sprite rotado
        for r in self.sim.robots:
            x, y = self._coord(r.nodo[0], r.nodo[1])
            self.canvas.coords(self.obj_robots[r.id], x, y)
            sprite = obtener_robot_mas_cercano(self.sprite_sheet, r.color, r.angulo)
            self.canvas.itemconfig(self.obj_robots[r.id], image=sprite)

        # Carritos
        for c in self.sim.carritos:
            x, y = self._coord(c.nodo[0], c.nodo[1])
            self.canvas.coords(self.obj_carritos[c.id], x, y)
            color = c.color_original if c.color_original in self.sprite_sheet["carrito"] else "gris"
            self.canvas.itemconfig(self.obj_carritos[c.id],
                                   image=self.sprite_sheet["carrito"][color])

        # Destinos
        for c in self.sim.carritos:
            dx, dy = self._coord(c.destino[0], c.destino[1])
            self.canvas.coords(self.obj_destinos[c.id], dx, dy - 8)

        # Stats
        self.val_tick.config(text=str(self.sim.ticks))
        entregas = sum(r.entregas_completadas for r in self.sim.robots)
        self.val_entregas.config(text=str(entregas))

        # Baterias
        for r in self.sim.robots:
            bar, fill_id, lbl = self.barras_bateria[r.id]
            pct = max(0, min(100, int(r.bateria)))
            w = int(110 * (pct / 100))
            bar.coords(fill_id, 0, 0, w, 10)
            if pct < 20:
                bar.itemconfig(fill_id, fill=PALETA["rojo"])
            elif pct < 50:
                bar.itemconfig(fill_id, fill=PALETA["naranja"])
            else:
                bar.itemconfig(fill_id, fill=PALETA["verde"])
            lbl.config(text=f"{pct}%")

        # Estados
        partes = []
        for r in self.sim.robots:
            estado = r.estado.value.replace("_", " ").title()
            partes.append(f"R{r.id}: {estado}")
        self.lbl_estados.config(text="  |  ".join(partes))

        # Nuevos eventos -> log
        nuevos = self.sim.eventos[self._ultimos_eventos:]
        self._ultimos_eventos = len(self.sim.eventos)
        for ev in nuevos:
            self._log(_narrar(ev), _tipo_evento(ev))

    # ------------------------------------------------------------------
    # LOOP
    # ------------------------------------------------------------------
    def _paso(self, ticks, velocidad, contador):
        if contador >= ticks:
            self.lbl_status.config(text="COMPLETADO", fg=PALETA["azul"])
            self._log("=" * 30, "dim")
            self._log("Simulacion completada", "success")
            self._log(f"Total entregas: {sum(r.entregas_completadas for r in self.sim.robots)}", "accent")
            return
        self.sim.paso()
        self.actualizar()
        self.ventana.after(int(1000 / velocidad), self._paso, ticks, velocidad, contador + 1)

    def animar(self, ticks=None, velocidad=20):
        limite = ticks if ticks is not None else self.sim.config.max_ticks
        self._paso(limite, velocidad, 0)
        self.ventana.mainloop()
