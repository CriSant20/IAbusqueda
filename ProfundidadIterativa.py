import time
import matplotlib.pyplot as plt
import networkx as nx
from collections import deque

class Nodo:
    def __init__(self, estado, padre=None, accion=None, id=None):
        self.estado = estado
        self.padre = padre
        self.accion = accion
        self.hijos = []
        self.id = id  # Identificador único para cada nodo

    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)

def validar_estado(estado):
    s_izq, l_izq, b, s_der, l_der = estado
    if s_izq < 0 or l_izq < 0 or s_der < 0 or l_der < 0:
        return False
    if (s_izq > 0 and s_izq < l_izq) or (s_der > 0 and s_der < l_der):
        return False
    return True

def generar_acciones(estado):
    acciones = []
    movimientos = [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]
    for ds, dl in movimientos:
        acciones.append((ds, dl))
    return acciones

def expandir_nodo(nodo):
    acciones = generar_acciones(nodo.estado)
    for accion in acciones:
        ds, dl = accion
        if nodo.estado[2] == 1:
            nuevo_estado = (nodo.estado[0] - ds, nodo.estado[1] - dl, 0,
                            nodo.estado[3] + ds, nodo.estado[4] + dl)
        else:
            nuevo_estado = (nodo.estado[0] + ds, nodo.estado[1] + dl, 1,
                            nodo.estado[3] - ds, nodo.estado[4] - dl)
        nuevo_nodo = Nodo(nuevo_estado, padre=nodo, accion=accion)
        if validar_estado(nuevo_estado):
            nodo.agregar_hijo(nuevo_nodo)
    return nodo.hijos

def bfs_with_visualizacion(nodo_inicial):
    inicio_tiempo = time.time()
    frontera = deque()
    frontera.append(nodo_inicial)
    visitados = set()
    visitados.add(nodo_inicial.estado)
    nodos_expandidos = 0

    G = nx.DiGraph()
    pos = {}
    node_counter = 0

    nodo_inicial.id = str(node_counter)
    node_counter += 1
    G.add_node(nodo_inicial.id, label=str(nodo_inicial.estado))
    pos[nodo_inicial.id] = (0, 0)  # Posición inicial

    while frontera:
        nodo_actual = frontera.popleft()
        nodos_expandidos += 1

        if nodo_actual.estado == (0, 0, 0, 3, 3):
            fin_tiempo = time.time()
            tiempo_ejecucion = (fin_tiempo - inicio_tiempo) * 1000  # Convertir a milisegundos
            return nodo_actual, nodos_expandidos, tiempo_ejecucion, G, pos

        hijos = expandir_nodo(nodo_actual)

        depth = get_depth(nodo_actual) + 1

        for hijo in hijos:
            if hijo.estado not in visitados:
                hijo.id = str(node_counter)
                node_counter += 1

                frontera.append(hijo)
                visitados.add(hijo.estado)

                G.add_node(hijo.id, label=str(hijo.estado))
                G.add_edge(nodo_actual.id, hijo.id)

                # Ajustar posición de los nodos
                x = depth * 2  # Separación en el eje x
                y = len(hijos) * -1  # Separación en el eje y
                pos[hijo.id] = (x, y + (depth * 0.5))

    return None, nodos_expandidos, None, G, pos

def get_depth(nodo):
    depth = 0
    while nodo.padre:
        nodo = nodo.padre
        depth += 1
    return depth

def imprimir_camino(nodo):
    camino = []
    while nodo:
        camino.append(nodo.estado)
        nodo = nodo.padre
    camino.reverse()
    for idx, estado in enumerate(camino):
        s_izq, l_izq, b, s_der, l_der = estado
        print(f"Paso {idx + 1}: Ovejas Izquierda: {s_izq}, Lobos Izquierda: {l_izq}, Barco: {'Izquierda' if b == 1 else 'Derecha'}, Ovejas Derecha: {s_der}, Lobos Derecha: {l_der}")

def dibujar_grafo(G, pos):
    labels = nx.get_node_attributes(G, 'label')
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, labels=labels, node_size=3000, node_color='lightgreen', font_size=10, font_weight='bold', arrows=True)
    plt.title("Árbol de búsqueda - Ovejas y Lobos", fontsize=15)
    plt.axis('off')  # Ocultar ejes
    plt.tight_layout()  # Ajustar la visualización
    plt.show()

def main():
    estado_inicial = (3, 3, 1, 0, 0)
    nodo_raiz = Nodo(estado_inicial)
    solucion, nodos_expandidos, tiempo_ejecucion, G, pos = bfs_with_visualizacion(nodo_raiz)

    if solucion:
        
        print("Se encontró una solución:")
        imprimir_camino(solucion)
        print(f"\nMedidas de rendimiento:")
        print(f"Nodos expandidos: {nodos_expandidos}")
        print(f"Tiempo de ejecución: {tiempo_ejecucion:.2f} ms")
        print(f"Memoria RAM total consumida: {memoria_consumida} bytes")

        # Dibujar el árbol de búsqueda
        dibujar_grafo(G, pos)
    else:
        print("No se encontró una solución.")

if __name__ == "__main__":
    main()
