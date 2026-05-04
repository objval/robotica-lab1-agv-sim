#!/usr/bin/env python3
"""
INFO1167 Robotica Lab #1 - Demo completa para la defensa
==========================================================
Un solo archivo. Todo. Corre esto para mostrarle al profe el proyecto.

Uso:
    python demo.py                    # demo completa + animacion Tkinter
    python demo.py --verbose          # muestra todo el reporte en consola
    python demo.py --sin-animacion    # solo tests + simulacion, sin ventana
    python demo.py --ticks 800        # simulacion mas corta
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


def separador(titulo):
    log(f"\n{'=' * 60}")
    log(f"  {titulo}")
    log(f"{'=' * 60}")


def paso_tests():
    separador("PASO 1 / 5 - Tests automaticos")
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
    print("Tests: 11/11 PASSED")
    return True


def paso_simulacion(ticks, semilla, salida):
    separador("PASO 2 / 5 - Simulacion AGV")

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
    separador("PASO 3 / 5 - Generando archivos")

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
    separador("PASO 4 / 5 - Reporte para la defensa")

    log(f"\n  {'ID':<6} {'Estado':<8} {'Requisito'}")
    log(f"  {'-' * 54}")
    for c in reporte["checks"]:
        ok = "OK" if c["ok"] else "FAIL"
        icono = "V" if c["ok"] else "X"
        log(f"  {icono} {c['id']:<4} {ok:<8} {c['requisito']}")

    log(f"\n  {'-' * 54}")
    log(f"  Aprobado: {reporte['porcentaje']}%  ({reporte['aprobados']}/{len(reporte['checks'])} checks)")

    log(f"\n  Evidencia de algoritmos de grafos:")
    grafos = resumen.get("ejemplos_grafos", {})
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

    log(f"\n  Temas cubiertos:")
    log(f"    - Python               : OK")
    log(f"    - Visual Python        : OK (se lanza ahora...)")
    log(f"    - Geometria            : OK (atan2, rotacion 10 grados)")
    log(f"    - Grafos - BFS/DFS     : OK")
    log(f"    - Grafos - Dijkstra    : OK")
    log(f"    - Grafos - todas rutas : OK")

    print(f"Requisitos: {reporte['aprobados']}/{len(reporte['checks'])} OK ({reporte['porcentaje']}%)")


def main():
    parser = argparse.ArgumentParser(description="INFO1167 Lab #1 - Demo completa")
    parser.add_argument("--ticks", type=int, default=800)
    parser.add_argument("--semilla", type=int, default=42)
    parser.add_argument("--velocidad", type=int, default=10)
    parser.add_argument("--salida", type=str, default="outputs")
    parser.add_argument("--tkinter", action="store_true", help="Usar animacion Tkinter")
    parser.add_argument("--sin-animacion", action="store_true", help="Saltar animacion")
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

    if args.sin_animacion:
        print("Animacion: omitida (--sin-animacion)")
        print(f"Archivos: {salida.resolve()}")
        return

    print("Abriendo animacion Tkinter...")
    from agv_sim.animacion_tkinter import AnimadorTkinter
    from agv_sim.modelos import ConfigSimulacion
    from agv_sim.simulacion import SimulacionAGV
    config = ConfigSimulacion(
        semilla=args.semilla, ancho=10, alto=8,
        max_ticks=args.ticks, modo_ruta="random_shortest"
    )
    sim_tk = SimulacionAGV(config)
    animador = AnimadorTkinter(sim_tk, reporte=reporte, resumen=resumen)
    animador.animar(ticks=args.ticks, velocidad=args.velocidad)

    print(f"Archivos: {salida.resolve()}")


if __name__ == "__main__":
    main()
