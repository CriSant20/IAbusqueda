import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
import psutil
import time

class Estado:
    def __init__(self, ovejas, lobos, bote_izquierda):
        self.ovejas = ovejas
        self.lobos = lobos
        self.bote_izquierda = bote_izquierda

    def es_valido(self):
        return (0 <= self.ovejas <= 3 and 0 <= self.lobos <= 3 and
                (self.ovejas == 0 or self.ovejas >= self.lobos) and
                (3 - self.ovejas == 0 or (3 - self.ovejas) >= (3 - self.lobos)))

    def es_final(self):
        return self.ovejas == 0 and self.lobos == 0 and not self.bote_izquierda

    def __eq__(self, other):
        return (self.ovejas, self.lobos, self.bote_izquierda) == (other.ovejas, other.lobos, other.bote_izquierda)

    def __hash__(self):
        return hash((self.ovejas, self.lobos, self.bote_izquierda))

    def __str__(self):
        bote_posicion = "Izquierda" if self.bote_izquierda else "Derecha"
        return f"Lobos: {self.lobos}, Ovejas: {self.ovejas}, Bote: {bote_posicion}"

    def to_id(self):
        return f"{self.ovejas}{self.lobos}{'Izquierda' if self.bote_izquierda else 'Derecha'}"


class Nodo:
    def __init__(self, estado, padre=None):
        self.estado = estado
        self.padre = padre
        self.hijos = []

    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)


def expandir_estado(estado):
    movimientos = [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]
    sucesores = []

    for o, l in movimientos:
        if estado.bote_izquierda:
            nuevo_estado = Estado(estado.ovejas - o, estado.lobos - l, False)
        else:
            nuevo_estado = Estado(estado.ovejas + o, estado.lobos + l, True)

        if nuevo_estado.es_valido():
            sucesores.append(nuevo_estado)

    return sucesores


def mostrar_arbol_con_matplotlib(arbol, nodos_expandidos, nodos_esteriles):
    pos = nx.spring_layout(arbol)
    plt.figure(figsize=(10, 6))

    nx.draw(arbol, pos, with_labels=True, node_size=300, font_size=8, font_weight="bold", node_color="lightblue", edge_color="gray")

    nx.draw_networkx_nodes(arbol, pos, nodelist=nodos_expandidos, node_color='green', node_size=300)

    if nodos_esteriles:
        nx.draw_networkx_nodes(arbol, pos, nodelist=nodos_esteriles, node_color='red', node_size=300)

    plt.show()


def depth_limited_search(nodo_actual, depth_limit, path, arbol, caminos, nodos_expandidos, nodos_esteriles):
    estado_actual = nodo_actual.estado

    nodos_expandidos.append(estado_actual.to_id())

    print(f"Expandiendo nodo: {estado_actual}")

    if estado_actual.es_final():
        return [path + [nodo_actual]]

    if depth_limit == 0:
        return []

    soluciones_locales = []
    sucesores = expandir_estado(estado_actual)

    if not sucesores:
        nodos_esteriles.append(estado_actual.to_id())

    for sucesor in sucesores:
        if sucesor not in [nodo.estado for nodo in path]:
            nuevo_nodo = Nodo(sucesor, nodo_actual)
            nodo_actual.agregar_hijo(nuevo_nodo)
            arbol.add_edge(estado_actual.to_id(), sucesor.to_id())
            caminos[(estado_actual.to_id(), sucesor.to_id())] = (estado_actual, sucesor)

            soluciones_hijo = depth_limited_search(
                nuevo_nodo, depth_limit - 1, path + [nodo_actual], arbol, caminos, nodos_expandidos, nodos_esteriles
            )

            soluciones_locales.extend(soluciones_hijo)

    return soluciones_locales


def buscar_todas_las_soluciones(estado_inicial, objetivo, tipo_busqueda):
    start_time = time.time()

    if tipo_busqueda == "anchura":
        frontera = deque([[Nodo(estado_inicial)]])
        visitados = set()
        arbol = nx.DiGraph()
        caminos = {}
        nodos_esteriles = []
        soluciones = []
        nodos_expandidos = []

        while frontera:
            camino = frontera.popleft()
            nodo_actual = camino[-1]
            estado_actual = nodo_actual.estado

            nodos_expandidos.append(estado_actual.to_id())

            print(f"Expandiendo nodo: {estado_actual}")

            visitados.add(estado_actual)

            sucesores = expandir_estado(estado_actual)
            if not sucesores:
                nodos_esteriles.append(estado_actual.to_id())

            for sucesor in sucesores:
                if sucesor not in visitados:
                    nuevo_nodo = Nodo(sucesor, nodo_actual)
                    nodo_actual.agregar_hijo(nuevo_nodo)
                    nuevo_camino = list(camino)
                    nuevo_camino.append(nuevo_nodo)
                    frontera.append(nuevo_camino)
                    arbol.add_edge(estado_actual.to_id(), sucesor.to_id())
                    caminos[(estado_actual.to_id(), sucesor.to_id())] = (estado_actual, sucesor)

            mostrar_arbol_con_matplotlib(arbol, nodos_expandidos, nodos_esteriles)

            if estado_actual.es_final():
                soluciones.append(camino)
                continue

        elapsed_time = time.time() - start_time
        process = psutil.Process()
        memory_usage = process.memory_info().rss / (1024 * 1024)

        return soluciones, arbol, caminos, elapsed_time, memory_usage

    elif tipo_busqueda == "profundidad_iterativa":
        max_depth = 20
        soluciones = []
        arbol = nx.DiGraph()
        caminos = {}
        nodos_expandidos = []
        nodos_esteriles = []

        for depth_limit in range(1, max_depth + 1):
            print(f"Profundidad límite: {depth_limit}")
            nodos_expandidos_current = []
            nodos_esteriles_current = []

            soluciones_depth = depth_limited_search(
                Nodo(estado_inicial), depth_limit, [], arbol, caminos, nodos_expandidos_current, nodos_esteriles_current
            )

            if soluciones_depth:
                soluciones.extend(soluciones_depth)
                nodos_expandidos.extend(nodos_expandidos_current)
                nodos_esteriles.extend(nodos_esteriles_current)

                mostrar_arbol_con_matplotlib(arbol, nodos_expandidos, nodos_esteriles)
                break

        elapsed_time = time.time() - start_time
        process = psutil.Process()
        memory_usage = process.memory_info().rss / (1024 * 1024)

        return soluciones, arbol, caminos, elapsed_time, memory_usage

    else:
        raise ValueError("Tipo de búsqueda no válido")


def mostrar_camino(camino):
    for nodo in camino:
        print(nodo.estado)


def imprimir_todas_las_soluciones(soluciones, arbol, caminos):
    for idx, camino in enumerate(soluciones):
        print(f"\nSolución {idx + 1}:")
        mostrar_camino(camino)
        print()


if __name__ == "__main__":
    estado_inicial = Estado(3, 3, True)
    estado_objetivo = Estado(0, 0, False)

    print("\nBúsqueda por Profundidad Iterativa:")
    soluciones, arbol, caminos, elapsed_time, memory_usage = buscar_todas_las_soluciones(
        estado_inicial, estado_objetivo, "profundidad_iterativa"
    )

    if soluciones:
        imprimir_todas_las_soluciones(soluciones, arbol, caminos)
        print(f"Tiempo de ejecución: {elapsed_time} segundos")
        print(f"Uso de memoria: {memory_usage} MB")
    else:
        print("No se encontró solución.")
