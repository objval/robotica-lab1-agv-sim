#!/usr/bin/env python3
"""
INFO1167 Robotica Lab #1 - Demo completa para la defensa
==========================================================
Un solo archivo. Todo. Corre esto para mostrarle al profe el proyecto.

Uso:
    python demo.py              # demo completa + animacion pygame (default)
    python demo.py --tkinter    # fuerza animacion Tkinter
    python demo.py --verbose    # muestra reporte completo en consola
    python demo.py --no-gui     # solo tests + simulacion, sin ventana
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


# macOS 15: matplotlib backend 'macosx' inicializa NSApplication,
# lo que rompe Tkinter posteriormente.  Forzamos 'Agg' (no-interactivo)
# antes de que cualquier modulo importe pyplot.
if sys.platform == "darwin":
    import matplotlib
    matplotlib.use("Agg")


VERBOSE = False


def log(msg):
    if VERBOSE:
        print(msg)


def paso_tests():
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        capture_output=True,
        text=True,
    )
    log(result.stdout)
    if result.returncode != 0:
        log(result.stderr)
        print("X Tests fallaron")
        return False
    # Solo mostrar resumen
    passed = result.stdout.count(" PASSED")
    print(f"Tests: {passed}/11 PASSED")
    return True


def paso_simulacion(ticks, semilla, salida):
    from agv_sim.modelos import ConfigSimulacion
    from agv_sim.simulacion import SimulacionAGV

    config = ConfigSimulacion(
        semilla=semilla,
        ancho=10,
        alto=8,
        max_ticks=ticks,
        modo_ruta="random_shortest",
    )
    sim = SimulacionAGV(config)
    resumen = sim.correr(ticks)

    log(f"  Ticks simulados : {resumen['ticks']}")
    log(f"  Entregas totales: {resumen['entregas_totales']}")
    log(f"  Robots          : {resumen['seniales_requisitos']['cantidad_robots']}")
    log(f"  Colores unicos  : {resumen['seniales_requisitos']['colores_unicos']}")
    log(f"  Paso rotacion   : {resumen['seniales_requisitos']['paso_rotacion']} grados")
    log(f"  Modo ruta       : {resumen['seniales_requisitos']['modo_ruta']}")

    print(f"Simulacion: {resumen['entregas_totales']} entregas en {resumen['ticks']} ticks")
    return sim, resumen


def paso_artifacts(sim, resumen, salida):
    from agv_sim.verificador import verificar_requisitos
    from agv_sim.visualizador import guardar_captura

    salida.mkdir(parents=True, exist_ok=True)

    resumen_path = salida / "resumen.json"
    resumen_path.write_text(json.dumps(resumen, indent=2), encoding="utf-8")
    log(f"  Resumen JSON : {resumen_path}")

    reporte = verificar_requisitos(sim, resumen)
    req_path = salida / "reporte_requisitos.json"
    req_path.write_text(json.dumps(reporte, indent=2), encoding="utf-8")
    log(f"  Requisitos   : {req_path}")

    img_path = salida / "captura.png"
    guardar_captura(sim, str(img_path))
    log(f"  Captura PNG  : {img_path}")

    return reporte


def paso_reporte_defensa(reporte, resumen):
    log(f"\n  {'ID':<6} {'Estado':<8} {'Requisito'}")
    log(f"  {'-' * 54}")
    for c in reporte["checks"]:
        ok = "OK" if c["ok"] else "FAIL"
        icono = "V" if c["ok"] else "X"
        log(f"  {icono} {c['id']:<4} {ok:<8} {c['requisito']}")

    log(f"\n  {'-' * 54}")
    log(f"  Aprobado: {reporte['porcentaje']}%  ({reporte['aprobados']}/{len(reporte['checks'])} checks)")

    grafos = resumen.get("ejemplos_grafos", {})
    log(f"\n  Evidencia de algoritmos de grafos:")
    log(f"    - BFS  (anchura)      : {len(grafos.get('bfs', []))} nodos")
    log(f"    - Dijkstra (corta)    : {len(grafos.get('dijkstra', []))} nodos")
    log(f"    - DFS  (profundidad)  : {len(grafos.get('dfs', []))} nodos")
    log(f"    - Rutas posibles      : {grafos.get('cantidad_rutas', 0)}")
    log(f"    - Al menos una ruta   : {grafos.get('al_menos_una_ruta', False)}")

    eventos = resumen.get("ultimos_eventos", [])
    entregas = resumen.get("entregas_totales", 0)
    cargas = sum(1 for e in eventos if "llego a base y carga" in e)
    listos = sum(1 for e in eventos if "bateria 100% listo" in e)
    log(f"\n  Evidencia de ciclo (ultimos {len(eventos)} ticks):")
    log(f"    - Entregas hechas     : {entregas}")
    log(f"    - Retornos a base     : {cargas}")
    log(f"    - Baterias al 100%    : {listos}")

    print(f"Requisitos: {reporte['aprobados']}/{len(reporte['checks'])} OK ({reporte['porcentaje']}%)")


def main():
    parser = argparse.ArgumentParser(description="INFO1167 Lab #1 - Demo completa")
    parser.add_argument("--ticks", type=int, default=600, help="Ticks de simulacion (default: 600)")
    parser.add_argument("--semilla", type=int, default=123, help="Semilla aleatoria (default: 123)")
    parser.add_argument("--velocidad", type=int, default=15, help="Ticks por segundo (default: 15)")
    parser.add_argument("--salida", type=str, default="outputs")
    parser.add_argument("--tkinter", action="store_true", help="Usar Tkinter en vez de Pygame")
    parser.add_argument("--no-gui", action="store_true", help="Saltar animacion (solo reportes)")
    parser.add_argument("--verbose", action="store_true", help="Mostrar reporte completo en consola")
    args = parser.parse_args()

    global VERBOSE
    VERBOSE = args.verbose

    salida = Path(args.salida)

    if not paso_tests():
        sys.exit(1)

    sim, resumen = paso_simulacion(args.ticks, args.semilla, salida)
    reporte = paso_artifacts(sim, resumen, salida)
    paso_reporte_defensa(reporte, resumen)

    if args.no_gui:
        print("Animacion: omitida (--no-gui)")
        print(f"Archivos: {salida.resolve()}")
        return

    print("Abriendo animacion...")

    from agv_sim.modelos import ConfigSimulacion
    from agv_sim.simulacion import SimulacionAGV
    config = ConfigSimulacion(
        semilla=args.semilla, ancho=10, alto=8,
        max_ticks=args.ticks, modo_ruta="random_shortest"
    )
    sim_vis = SimulacionAGV(config)

    if args.tkinter:
        from agv_sim.animacion_tkinter import AnimadorTkinter
        animador = AnimadorTkinter(sim_vis, reporte=reporte, resumen=resumen)
        animador.animar(ticks=args.ticks, velocidad=args.velocidad)
    else:
        try:
            from agv_sim.animacion_pygame import AnimadorPygame
            animador = AnimadorPygame(sim_vis, reporte=reporte, resumen=resumen)
            animador.animar(ticks=args.ticks, velocidad=args.velocidad)
        except Exception as e:
            print(f"Pygame fallo: {e}")
            print("Cayendo a Tkinter...")
            from agv_sim.animacion_tkinter import AnimadorTkinter
            animador = AnimadorTkinter(sim_vis, reporte=reporte, resumen=resumen)
            animador.animar(ticks=args.ticks, velocidad=args.velocidad)

    print(f"Archivos: {salida.resolve()}")


if __name__ == "__main__":
    main()
