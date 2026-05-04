"""
Animador con Pygame - INFO1167 Robotica Lab #1
================================================
Visualizacion alternativa para macOS donde Tkinter tiene bugs.
Pygame usa SDL2, independiente de Cocoa/Tk.
"""

import math
from pathlib import Path

import pygame

from agv_sim.modelos import ConfigSimulacion, EstadoRobot
from agv_sim.simulacion import SimulacionAGV
from agv_sim.sprites import crear_sprite_sheet


class AnimadorPygame:
    def __init__(self, sim: SimulacionAGV):
        self.sim = sim
        self.cfg: ConfigSimulacion = sim.config
        self.ancho, self.alto = self.cfg.ancho, self.cfg.alto

        pygame.init()
        self.cell = 60
        self.map_w = self.ancho * self.cell
        self.map_h = self.alto * self.cell
        self.panel_w = 340
        self.screen = pygame.display.set_mode((self.map_w + self.panel_w, self.map_h + 80))
        pygame.display.set_caption("INFO1167 Robotica Lab #1 - Simulacion AGV")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("sfprotext", 18)
        self.font_small = pygame.font.SysFont("sfprotext", 14)
        self.font_mono = pygame.font.SysFont("menlo", 13)

        self.sprites = crear_sprite_sheet(tam=48)
        self.surf_robots = {}
        self.surf_carrito = None
        self.surf_base = None
        self.surf_destino = None
        self._preparar_sprites()

        self.log_lines = []
        self.max_log = 18

    def _preparar_sprites(self):
        from PIL import Image
        def pil_to_pygame(img):
            mode = img.mode
            data = img.tobytes("raw", mode)
            if mode == "RGBA":
                return pygame.image.fromstring(data, img.size, "RGBA")
            return pygame.image.fromstring(data, img.size, "RGB")

        for color in ["rojo", "azul", "verde", "naranja"]:
            self.surf_robots[color] = pil_to_pygame(self.sprites["robot"][color])
        self.surf_carrito = pil_to_pygame(self.sprites["carrito"])
        self.surf_base = pil_to_pygame(self.sprites["base"])
        self.surf_destino = pil_to_pygame(self.sprites["destino"])

    def _color_hex(self, hex_str):
        hex_str = hex_str.lstrip("#")
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

    def _color_estado(self, estado):
        return {
            EstadoRobot.EN_BASE: self._color_hex("#A78BFA"),
            EstadoRobot.BUSCANDO_CARRITO: self._color_hex("#60A5FA"),
            EstadoRobot.LLEVANDO_CARRITO: self._color_hex("#4ADE80"),
            EstadoRobot.VOLVIENDO_BASE: self._color_hex("#FBBF24"),
            EstadoRobot.CARGANDO: self._color_hex("#F472B6"),
        }.get(estado, (128, 128, 128))

    def _estado_texto(self, estado):
        return {
            EstadoRobot.EN_BASE: "En Base",
            EstadoRobot.BUSCANDO_CARRITO: "Buscando",
            EstadoRobot.LLEVANDO_CARRITO: "Llevando",
            EstadoRobot.VOLVIENDO_BASE: "Volviendo",
            EstadoRobot.CARGANDO: "Cargando",
        }.get(estado, "???")

    def _agregar_log(self, mensaje, tipo="info"):
        self.log_lines.append((mensaje, tipo))
        if len(self.log_lines) > self.max_log:
            self.log_lines.pop(0)

    def _procesar_logs(self):
        for ev in self.sim.eventos_del_tick:
            tipo = ev.get("tipo", "")
            r = ev.get("robot", "?")
            if tipo == "asignar":
                c = ev.get("carrito", "?")
                self._agregar_log(f"R{r} recibio mision: rescatar carrito {c}", "info")
            elif tipo == "recoger":
                c = ev.get("carrito", "?")
                self._agregar_log(f"R{r} abordo carrito {c}", "success")
            elif tipo == "entregar":
                c = ev.get("carrito", "?")
                self._agregar_log(f"Carrito {c} entregado por R{r}", "accent")
            elif tipo == "llegar_base":
                self._agregar_log(f"R{r} en base. Pausa cafe", "warning")
            elif tipo == "carga_completa":
                self._agregar_log(f"R{r} listo para mas", "success")
            elif tipo == "reposicionar":
                self._agregar_log(f"Carrito {ev.get('carrito','?')} reposicionado", "dim")

    def _dibujar_mapa(self):
        for y in range(self.alto):
            for x in range(self.ancho):
                rect = pygame.Rect(x * self.cell, y * self.cell, self.cell, self.cell)
                color = (250, 249, 247) if (x + y) % 2 == 0 else (243, 242, 240)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (220, 218, 214), rect, 1)

        for i in range(self.ancho):
            lbl = self.font_small.render(str(i), True, (100, 100, 100))
            self.screen.blit(lbl, (i * self.cell + self.cell // 2 - 4, self.map_h + 10))
        for j in range(self.alto):
            lbl = self.font_small.render(str(j), True, (100, 100, 100))
            self.screen.blit(lbl, (self.map_w + 10, j * self.cell + self.cell // 2 - 6))

    def _dibujar_elementos(self):
        for base in self.sim.bases:
            x = base[0] * self.cell + (self.cell - 48) // 2
            y = base[1] * self.cell + (self.cell - 48) // 2
            self.screen.blit(self.surf_base, (x, y))

        for dest in self.sim.destinos:
            x = dest[0] * self.cell + (self.cell - 48) // 2
            y = dest[1] * self.cell + (self.cell - 48) // 2
            self.screen.blit(self.surf_destino, (x, y))

        for carrito in self.sim.carritos:
            if carrito.entregado:
                continue
            x = carrito.nodo[0] * self.cell + (self.cell - 40) // 2
            y = carrito.nodo[1] * self.cell + (self.cell - 40) // 2
            if carrito.color_original:
                overlay = pygame.Surface((40, 40), pygame.SRCALPHA)
                color_map = {
                    "rojo": (239, 68, 68),
                    "azul": (59, 130, 246),
                    "verde": (34, 197, 94),
                    "naranja": (249, 115, 22),
                }
                c = color_map.get(carrito.color_original, (150, 150, 150))
                pygame.draw.ellipse(overlay, (*c, 80), (0, 0, 40, 40))
                self.screen.blit(overlay, (x, y))
            self.screen.blit(pygame.transform.scale(self.surf_carrito, (40, 40)), (x, y))

        for robot in self.sim.robots:
            x = robot.nodo[0] * self.cell + (self.cell - 48) // 2
            y = robot.nodo[1] * self.cell + (self.cell - 48) // 2
            surf = self.surf_robots.get(robot.color, self.surf_robots["rojo"])
            rot = -math.degrees(robot.angulo)
            rot_surf = pygame.transform.rotate(surf, rot)
            rect = rot_surf.get_rect(center=(x + 24, y + 24))
            self.screen.blit(rot_surf, rect.topleft)

            estado_color = self._color_estado(robot.estado)
            pygame.draw.circle(self.screen, estado_color, (x + 24, y + 24), 28, 2)

    def _dibujar_panel(self):
        pygame.draw.rect(self.screen, (248, 247, 245), pygame.Rect(self.map_w, 0, self.panel_w, self.map_h + 80))
        pygame.draw.line(self.screen, (220, 218, 214), (self.map_w, 0), (self.map_w, self.map_h + 80), 2)

        x = self.map_w + 15
        y = 10
        header = self.font.render("PANEL DE CONTROL", True, (30, 30, 30))
        self.screen.blit(header, (x, y))
        y += 30

        # Stats
        stats = [
            ("Tick", str(self.sim.tick), (100, 100, 100)),
            ("Entregas", str(self.sim.entregas_completadas), (34, 197, 94)),
            ("Robots", str(len(self.sim.robots)), (59, 130, 246)),
        ]
        for label, val, col in stats:
            pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(x, y, 100, 40), border_radius=6)
            pygame.draw.rect(self.screen, (220, 218, 214), pygame.Rect(x, y, 100, 40), 1, border_radius=6)
            l = self.font_small.render(label, True, (100, 100, 100))
            v = self.font.render(val, True, col)
            self.screen.blit(l, (x + 8, y + 4))
            self.screen.blit(v, (x + 8, y + 18))
            x += 110
        x = self.map_w + 15
        y += 50

        # Robots
        pygame.draw.line(self.screen, (220, 218, 214), (x, y), (x + 310, y), 1)
        y += 8
        for robot in self.sim.robots:
            color = {"rojo": (239,68,68), "azul": (59,130,246), "verde": (34,197,94), "naranja": (249,115,22)}.get(robot.color, (128,128,128))
            pygame.draw.rect(self.screen, color, pygame.Rect(x, y, 8, 8), border_radius=2)
            estado_txt = self._estado_texto(robot.estado)
            bateria = robot.bateria
            b_color = (34,197,94) if bateria >= 50 else (251,191,36) if bateria >= 20 else (239,68,68)
            txt = self.font_small.render(f"R{robot.id} | {estado_txt} | {bateria:.0f}%", True, (60,60,60))
            self.screen.blit(txt, (x + 14, y - 2))
            pygame.draw.rect(self.screen, (220,218,214), pygame.Rect(x + 14, y + 16, 120, 6), border_radius=3)
            pygame.draw.rect(self.screen, b_color, pygame.Rect(x + 14, y + 16, int(120 * bateria / 100), 6), border_radius=3)
            y += 32

        y += 5
        pygame.draw.line(self.screen, (220, 218, 214), (x, y), (x + 310, y), 1)
        y += 10

        # Log
        log_header = self.font.render("REGISTRO DE EVENTOS", True, (30, 30, 30))
        self.screen.blit(log_header, (x, y))
        y += 28
        for msg, tipo in self.log_lines[-12:]:
            colores = {
                "info": (59, 130, 246),
                "success": (34, 197, 94),
                "accent": (6, 182, 212),
                "warning": (251, 191, 36),
                "dim": (120, 120, 120),
            }
            c = colores.get(tipo, (100, 100, 100))
            ts = self.font_mono.render(f"[{self.sim.tick:04d}]", True, (150, 150, 150))
            m = self.font_small.render(msg, True, c)
            self.screen.blit(ts, (x, y))
            self.screen.blit(m, (x + 55, y))
            y += 20

    def _dibujar_footer(self):
        rect = pygame.Rect(0, self.map_h, self.map_w + self.panel_w, 80)
        pygame.draw.rect(self.screen, (255, 255, 255), rect)
        pygame.draw.line(self.screen, (220, 218, 214), (0, self.map_h), (self.map_w + self.panel_w, self.map_h), 2)
        status = "EN CURSO" if self.sim.tick < self.cfg.max_ticks else "COMPLETADO"
        color = (34, 197, 94) if status == "COMPLETADO" else (59, 130, 246)
        txt = self.font.render(f"Estado: {status}  |  Ticks: {self.sim.tick}/{self.cfg.max_ticks}  |  Entregas: {self.sim.entregas_completadas}", True, color)
        self.screen.blit(txt, (20, self.map_h + 15))

    def animar(self, ticks: int = None, velocidad: float = 20.0):
        if ticks is None:
            ticks = self.cfg.max_ticks
        running = True
        paused = False
        tick_delay = int(1000 / velocidad)
        last_tick = pygame.time.get_ticks()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_UP:
                        velocidad = min(60, velocidad + 5)
                        tick_delay = int(1000 / velocidad)
                    elif event.key == pygame.K_DOWN:
                        velocidad = max(5, velocidad - 5)
                        tick_delay = int(1000 / velocidad)

            now = pygame.time.get_ticks()
            if not paused and now - last_tick >= tick_delay and self.sim.tick < ticks:
                self.sim.tick_simulacion()
                self._procesar_logs()
                last_tick = now

            self.screen.fill((245, 244, 242))
            self._dibujar_mapa()
            self._dibujar_elementos()
            self._dibujar_panel()
            self._dibujar_footer()
            pygame.display.flip()
            self.clock.tick(60)

            if self.sim.tick >= ticks and not paused:
                paused = True
                self._agregar_log("=== Simulacion completada ===", "accent")

        pygame.quit()
