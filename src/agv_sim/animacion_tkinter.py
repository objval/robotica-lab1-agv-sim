import math
import tkinter as tk

from .simulacion import SimulacionAGV


_COLORES_HEX = {
    "rojo": "#e74c3c",
    "azul": "#3498db",
    "verde": "#2ecc71",
    "naranja": "#f39c12",
    "gris": "#bdc3c7",
}


def _color(c):
    return _COLORES_HEX.get(c, "#ecf0f1")


class AnimadorTkinter:
    def __init__(self, sim):
        self.sim = sim
        self.ventana = tk.Tk()
        self.ventana.title("INFO1167 Robotica - Lab #1 AGV")
        self.ancho_canvas = 950
        self.alto_canvas = 750

        # Centrar ventana en pantalla
        sw = self.ventana.winfo_screenwidth()
        sh = self.ventana.winfo_screenheight()
        x = (sw - self.ancho_canvas) // 2
        y = (sh - self.alto_canvas) // 2 - 30
        self.ventana.geometry(f"{self.ancho_canvas}x{self.alto_canvas}+{x}+{y}")

        # Panel superior con info
        self.frame_info = tk.Frame(self.ventana, bg="#2c3e50", height=40)
        self.frame_info.pack(fill="x")
        self.label_info = tk.Label(
            self.frame_info, text="Iniciando...", bg="#2c3e50", fg="white",
            font=("Segoe UI", 12, "bold")
        )
        self.label_info.pack(pady=6)

        self.canvas = tk.Canvas(
            self.ventana, width=self.ancho_canvas, height=self.alto_canvas - 40,
            bg="#ecf0f1", highlightthickness=0
        )
        self.canvas.pack()

        w, h = sim.config.ancho, sim.config.alto
        margen = 40
        self.celda_w = (self.ancho_canvas - margen * 2) / w
        self.celda_h = (self.alto_canvas - 40 - margen * 2) / h
        self.offset_x = margen
        self.offset_y = margen

        self.obj_robots = {}
        self.obj_textos = {}
        self.obj_carritos = {}
        self.obj_destinos = {}
        self.obj_bases = {}

        self._dibujar_grilla(w, h)
        self._dibujar_leyenda()

        for r in sim.robots:
            bx, by = self._coord(r.base[0], r.base[1])
            self.obj_bases[r.id] = self.canvas.create_oval(
                bx - 20, by - 20, bx + 20, by + 20,
                outline=_color(r.color), width=3, dash=(5, 3)
            )
            x, y = self._coord(r.nodo[0], r.nodo[1])
            self.obj_robots[r.id] = self.canvas.create_oval(
                x - 18, y - 18, x + 18, y + 18,
                fill=_color(r.color), outline="black", width=2
            )
            self.obj_textos[r.id] = self.canvas.create_text(
                x + 22, y - 18, text=f"R{r.id}", font=("Segoe UI", 10, "bold"),
                fill="black", anchor="w"
            )

        for c in sim.carritos:
            x, y = self._coord(c.nodo[0], c.nodo[1])
            self.obj_carritos[c.id] = self.canvas.create_rectangle(
                x - 14, y - 14, x + 14, y + 14,
                fill=_color(c.color_original), outline="black", width=2
            )
            dx, dy = self._coord(c.destino[0], c.destino[1])
            self.obj_destinos[c.id] = self.canvas.create_text(
                dx, dy, text="X", font=("Segoe UI", 18, "bold"), fill="#2c3e50"
            )

    def _coord(self, gx, gy):
        x = gx * self.celda_w + self.celda_w / 2 + self.offset_x
        y = gy * self.celda_h + self.celda_h / 2 + self.offset_y
        return x, y

    def _dibujar_grilla(self, w, h):
        for i in range(w + 1):
            x = i * self.celda_w + self.offset_x
            self.canvas.create_line(x, self.offset_y, x, h * self.celda_h + self.offset_y, fill="#bdc3c7", width=1)
        for j in range(h + 1):
            y = j * self.celda_h + self.offset_y
            self.canvas.create_line(self.offset_x, y, w * self.celda_w + self.offset_x, y, fill="#bdc3c7", width=1)
        # Titulo del canvas
        self.canvas.create_text(
            self.ancho_canvas / 2, 18, text="Bodega AGV - Mapa 2D",
            font=("Segoe UI", 14, "bold"), fill="#2c3e50"
        )

    def _dibujar_leyenda(self):
        lx = self.ancho_canvas - 180
        ly = self.alto_canvas - 120
        self.canvas.create_rectangle(lx - 10, ly - 25, lx + 170, ly + 80, fill="white", outline="#bdc3c7", width=1)
        self.canvas.create_text(lx + 80, ly - 10, text="Leyenda", font=("Segoe UI", 10, "bold"), fill="#2c3e50")
        self.canvas.create_oval(lx, ly + 5, lx + 14, ly + 19, fill="#e74c3c", outline="black")
        self.canvas.create_text(lx + 22, ly + 12, text="Robot", font=("Segoe UI", 9), anchor="w")
        self.canvas.create_rectangle(lx, ly + 25, lx + 14, ly + 39, fill="#bdc3c7", outline="black")
        self.canvas.create_text(lx + 22, ly + 32, text="Carrito", font=("Segoe UI", 9), anchor="w")
        self.canvas.create_text(lx + 7, ly + 52, text="X", font=("Segoe UI", 12, "bold"), fill="#2c3e50")
        self.canvas.create_text(lx + 22, ly + 52, text="Destino", font=("Segoe UI", 9), anchor="w")

    def actualizar(self):
        for r in self.sim.robots:
            x, y = self._coord(r.nodo[0], r.nodo[1])
            self.canvas.coords(self.obj_robots[r.id], x - 18, y - 18, x + 18, y + 18)
            self.canvas.coords(self.obj_textos[r.id], x + 22, y - 18)

        for c in self.sim.carritos:
            x, y = self._coord(c.nodo[0], c.nodo[1])
            self.canvas.coords(self.obj_carritos[c.id], x - 14, y - 14, x + 14, y + 14)
            self.canvas.itemconfig(self.obj_carritos[c.id], fill=_color(c.color_original))
            dx, dy = self._coord(c.destino[0], c.destino[1])
            self.canvas.coords(self.obj_destinos[c.id], dx, dy)

        entregas = sum(r.entregas_completadas for r in self.sim.robots)
        estados = ", ".join(f"R{r.id}={r.estado.value}" for r in self.sim.robots)
        self.label_info.config(
            text=f"tick={self.sim.ticks}  |  entregas={entregas}  |  {estados}"
        )

    def _paso(self, ticks, velocidad, contador):
        if contador >= ticks:
            self.label_info.config(text=f"FINALIZADO - tick={self.sim.ticks} - Cerrar ventana")
            return
        self.sim.paso()
        self.actualizar()
        self.ventana.after(int(1000 / velocidad), self._paso, ticks, velocidad, contador + 1)

    def animar(self, ticks=None, velocidad=10):
        limite = ticks if ticks is not None else self.sim.config.max_ticks
        self._paso(limite, velocidad, 0)
        self.ventana.mainloop()
