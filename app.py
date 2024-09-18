import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
import time
import psutil
import sys
import os

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
        return f"Ovejas: {self.ovejas}, Lobos: {self.lobos}, Bote: {bote_posicion}"

    def to_id(self):
        return f"{self.ovejas}_{self.lobos}_{'Izquierda' if self.bote_izquierda else 'Derecha'}"

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

def guardar_arbol(arbol, caminos, nodos_expandidos, nodos_esteriles, archivo):
    pos = nx.spring_layout(arbol)  # Utiliza el diseño por defecto de networkx
    plt.figure(figsize=(10, 6))

    # Dibujar todos los nodos y conexiones
    nx.draw(arbol, pos, with_labels=True, node_size=300, font_size=8, font_weight="bold", node_color="lightblue")

    # Resaltar los nodos expandidos en verde
    nx.draw_networkx_nodes(arbol, pos, nodelist=nodos_expandidos, node_color='green', node_size=300)

    # Resaltar los nodos estériles en rojo
    if nodos_esteriles:
        nx.draw_networkx_nodes(arbol, pos, nodelist=nodos_esteriles, node_color='red', node_size=300)

    plt.savefig(archivo)  # Guarda la imagen en el archivo
    plt.close()  # Cierra la figura para liberar memoria

def buscar_todas_las_soluciones(estado_inicial, objetivo, tipo_busqueda):
    start_time = time.time()  # Tiempo inicial

    if tipo_busqueda == "anchura":
        # Crear carpeta para guardar las imágenes
        if not os.path.exists("anchura"):
            os.makedirs("anchura")

        frontera = deque([[estado_inicial]])
        visitados = set()
        arbol = nx.DiGraph()
        caminos = {}
        nodos_esteriles = []  # Lista para nodos estériles
        soluciones = []
        nodos_expandidos = []

        image_files = []  # Lista para archivos de imágenes

        while frontera:
            camino = frontera.popleft()
            estado_actual = camino[-1]

            # Agregar nodo expandido a la lista
            nodos_expandidos.append(estado_actual.to_id())

            # Imprimir el estado actual antes de expandir
            print(f"Expandiendo nodo: {estado_actual}")

            visitados.add(estado_actual)

            sucesores = expandir_estado(estado_actual)
            if not sucesores:
                nodos_esteriles.append(estado_actual.to_id())  # Marcar como nodo estéril si no hay sucesores

            for sucesor in sucesores:
                if sucesor not in visitados:
                    nuevo_camino = list(camino)
                    nuevo_camino.append(sucesor)
                    frontera.append(nuevo_camino)
                    arbol.add_edge(estado_actual.to_id(), sucesor.to_id())
                    caminos[(estado_actual.to_id(), sucesor.to_id())] = (estado_actual, sucesor)

            # Guardar el árbol actualizado con nodos expandidos y nodos estériles
            image_file = os.path.join("anchura", f"arbol_{estado_actual.to_id()}.png")
            guardar_arbol(arbol, caminos, nodos_expandidos, nodos_esteriles, image_file)
            image_files.append(image_file)

            if estado_actual == objetivo:
                soluciones.append(camino)
                continue  # Continúa buscando más soluciones

        elapsed_time = time.time() - start_time  # Tiempo transcurrido
        memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # Uso de memoria en MB

        return soluciones, arbol, caminos, elapsed_time, memory_usage, image_files

    else:
        raise ValueError("Tipo de búsqueda no válido")

def mostrar_camino(camino):
    resultado = ""
    for estado in camino:
        resultado += f"{estado}\n"
    return resultado

def imprimir_todas_las_soluciones(soluciones, arbol, caminos):
    resultado = ""
    for idx, camino in enumerate(soluciones):
        resultado += f"\nSolución {idx + 1}:\n"
        resultado += mostrar_camino(camino)
    return resultado

def main(tipo_busqueda):
    estado_inicial = Estado(3, 3, True)
    estado_objetivo = Estado(0, 0, False)

    print("\nBúsqueda por Anchura:")
    soluciones, arbol_anchura, caminos, elapsed_time, memory_usage, image_files = buscar_todas_las_soluciones(estado_inicial, estado_objetivo, tipo_busqueda)
    if soluciones:
        resultado = imprimir_todas_las_soluciones(soluciones, arbol_anchura, caminos)
        resultado += f"\nTiempo de ejecución: {elapsed_time} segundos"
        resultado += f"\nUso de memoria: {memory_usage:.2f} MB"
    else:
        resultado = "No se encontró solución."

    return resultado

if __name__ == "__main__":
    if len(sys.argv) > 1:
        tipo_busqueda = sys.argv[1]
        resultado = main(tipo_busqueda)
        print(resultado)  # Imprimir en la salida estándar
    else:
        print("Debe proporcionar el tipo de búsqueda.")
