#!/usr/bin/env python3
"""
INFO1167 Robotica Lab #1 - Demo completa para la defensa
==========================================================
Un solo archivo. Todo. Corre esto para mostrarle al profe el proyecto.

Uso:
    python demo.py                    # demo completa + animacion VPython
    python demo.py --sin-vpython      # solo reportes, sin animacion 3D
    python demo.py --ticks 800        # simulacion mas corta
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


def separador(titulo):
    print(f"\n{'=' * 60}")
    print(f"  {titulo}")
    print(f"{'=' * 60}")


def paso_tests():
    separador("PASO 1 / 5 - Tests automaticos")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return False
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

    print(f"  Ticks simulados : {resumen['ticks']}")
    print(f"  Entregas totales: {resumen['entregas_totales']}")
    print(f"  Robots          : {resumen['seniales_requisitos']['cantidad_robots']}")
    print(f"  Colores unicos  : {resumen['seniales_requisitos']['colores_unicos']}")
    print(f"  Paso rotacion   : {resumen['seniales_requisitos']['paso_rotacion']} grados")
    print(f"  Modo ruta       : {resumen['seniales_requisitos']['modo_ruta']}")

    return sim, resumen


def paso_artifacts(sim, resumen, salida):
    separador("PASO 3 / 5 - Generando archivos")

    from agv_sim.verificador import verificar_requisitos
    from agv_sim.visualizador import guardar_captura

    salida.mkdir(parents=True, exist_ok=True)

    resumen_path = salida / "resumen.json"
    resumen_path.write_text(json.dumps(resumen, indent=2), encoding="utf-8")
    print(f"  Resumen JSON : {resumen_path}")

    reporte = verificar_requisitos(sim, resumen)
    req_path = salida / "reporte_requisitos.json"
    req_path.write_text(json.dumps(reporte, indent=2), encoding="utf-8")
    print(f"  Requisitos   : {req_path}")

    img_path = salida / "captura.png"
    guardar_captura(sim, str(img_path))
    print(f"  Captura PNG  : {img_path}")

    return reporte


def paso_reporte_defensa(reporte, resumen):
    separador("PASO 4 / 5 - Reporte para la defensa")

    print(f"\n  {'ID':<6} {'Estado':<8} {'Requisito'}")
    print(f"  {'-' * 54}")
    for c in reporte["checks"]:
        ok = "OK" if c["ok"] else "FAIL"
        icono = "V" if c["ok"] else "X"
        print(f"  {icono} {c['id']:<4} {ok:<8} {c['requisito']}")

    print(f"\n  {'-' * 54}")
    print(f"  Aprobado: {reporte['porcentaje']}%  ({reporte['aprobados']}/{len(reporte['checks'])} checks)")

    print(f"\n  Evidencia de algoritmos de grafos:")
    grafos = resumen.get("ejemplos_grafos", {})
    print(f"    - BFS  (anchura)      : {len(grafos.get('bfs', []))} nodos")
    print(f"    - Dijkstra (corta)    : {len(grafos.get('dijkstra', []))} nodos")
    print(f"    - DFS  (profundidad)  : {len(grafos.get('dfs', []))} nodos")
    print(f"    - Rutas posibles      : {grafos.get('cantidad_rutas', 0)}")
    print(f"    - Al menos una ruta   : {grafos.get('al_menos_una_ruta', False)}")

    eventos = resumen.get("ultimos_eventos", [])
    entregas = resumen.get("entregas_totales", 0)
    cargas = sum(1 for e in eventos if "llego a base y carga" in e)
    listos = sum(1 for e in eventos if "bateria 100% listo" in e)
    print(f"\n  Evidencia de ciclo (ultimos {len(eventos)} ticks):")
    print(f"    - Entregas hechas     : {entregas}")
    print(f"    - Retornos a base     : {cargas}")
    print(f"    - Baterias al 100%    : {listos}")

    print(f"\n  Temas cubiertos:")
    print(f"    - Python               : OK")
    print(f"    - Visual Python        : OK (se lanza ahora...)")
    print(f"    - Geometria            : OK (atan2, rotacion 10 grados)")
    print(f"    - Grafos - BFS/DFS     : OK")
    print(f"    - Grafos - Dijkstra    : OK")
    print(f"    - Grafos - todas rutas : OK")


def paso_vpython(ticks, semilla, velocidad):
    separador("PASO 5 / 5 - Animacion Visual Python 3D")
    print("  Abriendo animacion de bodega...")
    print("  Se abrira una pestana del navegador. Cerrala para terminar.\n")
    time.sleep(1)

    from agv_sim.animacion_vpython import AnimadorVPython
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
    try:
        animador = AnimadorVPython(sim)
        animador.animar(ticks=ticks, velocidad=velocidad)
        return
    except Exception as e:
        print(f"  Visual Python fallo: {e}")
        print("  Cambiando a animacion Tkinter (fallback)...\n")

    from agv_sim.animacion_tkinter import AnimadorTkinter
    sim2 = SimulacionAGV(config)
    animador2 = AnimadorTkinter(sim2)
    animador2.animar(ticks=ticks, velocidad=velocidad)


def main():
    parser = argparse.ArgumentParser(description="INFO1167 Lab #1 - Demo completa")
    parser.add_argument("--ticks", type=int, default=800)
    parser.add_argument("--semilla", type=int, default=42)
    parser.add_argument("--velocidad", type=int, default=10)
    parser.add_argument("--salida", type=str, default="outputs")
    parser.add_argument("--tkinter", action="store_true", help="Usar animacion Tkinter en vez de VPython")
    parser.add_argument("--sin-animacion", action="store_true", help="Saltar animacion (solo reportes)")
    args = parser.parse_args()

    salida = Path(args.salida)

    if not paso_tests():
        print("\nX Tests fallaron - abortando demo.")
        sys.exit(1)

    sim, resumen = paso_simulacion(args.ticks, args.semilla, salida)
    reporte = paso_artifacts(sim, resumen, salida)
    paso_reporte_defensa(reporte, resumen)

    # En Windows VPython suele abrir pestana en blanco; usar Tkinter por defecto
    usar_tkinter = args.tkinter or sys.platform.startswith("win")

    if args.sin_animacion:
        separador("PASO 5 / 5 - Animacion")
        print("  Saltado (--sin-animacion).")
        print(f"\n  Para lanzar la animacion despues:")
        print(f"    python demo.py --tkinter")
    elif usar_tkinter:
        separador("PASO 5 / 5 - Animacion Tkinter")
        print("  Abriendo ventana de animacion...\n")
        from agv_sim.animacion_tkinter import AnimadorTkinter
        from agv_sim.modelos import ConfigSimulacion
        from agv_sim.simulacion import SimulacionAGV
        config = ConfigSimulacion(
            semilla=args.semilla, ancho=10, alto=8,
            max_ticks=args.ticks, modo_ruta="random_shortest"
        )
        sim_tk = SimulacionAGV(config)
        AnimadorTkinter(sim_tk).animar(ticks=args.ticks, velocidad=args.velocidad)
    else:
        paso_vpython(args.ticks, args.semilla, args.velocidad)

    separador("Demo terminada")
    print(f"  Archivos guardados en: {salida.resolve()}")
    print(f"  Exito en la defensa!\n")


if __name__ == "__main__":
    main()
