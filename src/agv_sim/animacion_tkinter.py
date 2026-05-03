import math
import tkinter as tk

from .simulacion import SimulacionAGV


_COLORES_HEX = {
    "rojo": "#e74c3c",
    "azul": "#3498db",
    "verde": "#2ecc71",
    "naranja": "#f39c12",
    "gris": "#95a5a6",
}


def _color(c):
    return _COLORES_HEX.get(c, "#ecf0f1")


class AnimadorTkinter:
    def __init__(self, sim):
        self.sim = sim
        self.ventana = tk.Tk()
        self.ventana.title("INFO1167 AGV Lab #1 - Animacion Tkinter")
        self.ancho_canvas = 900
        self.alto_canvas = 720
        self.canvas = tk.Canvas(self.ventana, width=self.ancho_canvas, height=self.alto_canvas, bg="white")
        self.canvas.pack()

        w, h = sim.config.ancho, sim.config.alto
        self.celda_w = self.ancho_canvas / w
        self.celda_h = self.alto_canvas / h

        self.obj_robots = {}
        self.obj_textos = {}
        self.obj_carritos = {}
        self.obj_destinos = {}
        self.obj_bases = {}

        self._dibujar_grilla(w, h)

        for r in sim.robots:
            bx, by = self._coord(r.base[0], r.base[1])
            self.obj_bases[r.id] = self.canvas.create_oval(
                bx - 18, by - 18, bx + 18, by + 18,
                outline=_color(r.color), width=2, dash=(4, 2)
            )
            x, y = self._coord(r.nodo[0], r.nodo[1])
            self.obj_robots[r.id] = self.canvas.create_oval(
                x - 16, y - 16, x + 16, y + 16,
                fill=_color(r.color), outline="black", width=2
            )
            self.obj_textos[r.id] = self.canvas.create_text(
                x + 20, y - 16, text=f"R{r.id}", font=("Arial", 10, "bold")
            )

        for c in sim.carritos:
            x, y = self._coord(c.nodo[0], c.nodo[1])
            self.obj_carritos[c.id] = self.canvas.create_rectangle(
                x - 12, y - 12, x + 12, y + 12,
                fill=_color(c.color_original), outline="black", width=2
            )
            dx, dy = self._coord(c.destino[0], c.destino[1])
            self.obj_destinos[c.id] = self.canvas.create_text(
                dx, dy, text="X", font=("Arial", 16, "bold"), fill="black"
            )

        self.info = self.canvas.create_text(
            10, 10, anchor="nw",
            text="tick=0  entregas=0",
            font=("Arial", 12),
            fill="black"
        )

    def _coord(self, gx, gy):
        x = gx * self.celda_w + self.celda_w / 2
        y = gy * self.celda_h + self.celda_h / 2
        return x, y

    def _dibujar_grilla(self, w, h):
        for i in range(w + 1):
            x = i * self.celda_w
            self.canvas.create_line(x, 0, x, self.alto_canvas, fill="#ddd", width=1)
        for j in range(h + 1):
            y = j * self.celda_h
            self.canvas.create_line(0, y, self.ancho_canvas, y, fill="#ddd", width=1)

    def actualizar(self):
        for r in self.sim.robots:
            x, y = self._coord(r.nodo[0], r.nodo[1])
            self.canvas.coords(
                self.obj_robots[r.id],
                x - 16, y - 16, x + 16, y + 16
            )
            self.canvas.coords(self.obj_textos[r.id], x + 20, y - 16)

        for c in self.sim.carritos:
            x, y = self._coord(c.nodo[0], c.nodo[1])
            self.canvas.coords(
                self.obj_carritos[c.id],
                x - 12, y - 12, x + 12, y + 12
            )
            self.canvas.itemconfig(
                self.obj_carritos[c.id], fill=_color(c.color_original)
            )
            dx, dy = self._coord(c.destino[0], c.destino[1])
            self.canvas.coords(self.obj_destinos[c.id], dx, dy)

        entregas = sum(r.entregas_completadas for r in self.sim.robots)
        self.canvas.itemconfig(
            self.info,
            text=f"tick={self.sim.ticks}  entregas={entregas}"
        )

    def _paso(self, ticks, velocidad, contador):
        if contador >= ticks:
            return
        self.sim.paso()
        self.actualizar()
        self.ventana.after(int(1000 / velocidad), self._paso, ticks, velocidad, contador + 1)

    def animar(self, ticks=None, velocidad=10):
        limite = ticks if ticks is not None else self.sim.config.max_ticks
        self._paso(limite, velocidad, 0)
        self.ventana.mainloop()
