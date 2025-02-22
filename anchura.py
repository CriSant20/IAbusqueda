import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
import time
import psutil
from io import BytesIO  # Para manejar la imagen en memoria
class Nodo:
    def __init__(self, estado, padre=None, accion=None, id=None, valido=True):
        self.estado = estado
        self.padre = padre
        self.accion = accion
        self.hijos = []
        self.id = id  # Identificador único para cada nodo
        self.valido = valido  # Indica si el estado es válido o no
    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)
def validar_estado(estado):
    o_izq, l_izq, b, o_der, l_der = estado
    if o_izq < 0 or l_izq < 0 or o_der < 0 or l_der < 0:
        return False
    if o_izq > 3 or l_izq > 3 or o_der > 3 or l_der > 3:
        return False
    if (o_izq > 0 and o_izq < l_izq):
        return False
    if (o_der > 0 and o_der < l_der):
        return False
    return True
def generar_acciones():
    return [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]
def expandir_nodo(nodo, node_id_counter, estados_generados):
    acciones = generar_acciones()
    hijos = []
    for accion in acciones:
        do, dl = accion
        if nodo.estado[2] == 1:  # Barco en la izquierda
            nuevo_estado = (nodo.estado[0] - do, nodo.estado[1] - dl, 0,
                            nodo.estado[3] + do, nodo.estado[4] + dl)
        else:  # Barco en la derecha
            nuevo_estado = (nodo.estado[0] + do, nodo.estado[1] + dl, 1,
                            nodo.estado[3] - do, nodo.estado[4] - dl)
        es_valido = validar_estado(nuevo_estado)
        nuevo_nodo = Nodo(nuevo_estado, padre=nodo, accion=accion, id=node_id_counter, valido=es_valido)
        nodo.agregar_hijo(nuevo_nodo)
        estados_generados.add(nuevo_estado)
        hijos.append(nuevo_nodo)
        node_id_counter += 1
    return hijos, node_id_counter
def bfs(nodo_raiz):
    inicio_tiempo = time.time()
    proceso = psutil.Process()
    memoria_inicial = proceso.memory_info().rss
    frontera = deque([nodo_raiz])
    estados_visitados = set()
    estados_generados = set()
    nodos_visitados = 1
    node_id_counter = 1
    all_nodes = [nodo_raiz]
    all_edges = []
    soluciones = []
    while frontera:
        nodo_actual = frontera.popleft()
        time.sleep(0.01)  # Retardo de 10ms
        hijos, node_id_counter = expandir_nodo(nodo_actual, node_id_counter, estados_generados)
        for hijo in hijos:
            all_nodes.append(hijo)
            all_edges.append((nodo_actual.id, hijo.id))
            # Si el estado es válido, se debe continuar la exploración
            if hijo.valido:
                if hijo.estado not in estados_visitados:
                    frontera.append(hijo)
                    estados_visitados.add(hijo.estado)
                    nodos_visitados += 1
                if hijo.estado == (0, 0, 0, 3, 3):  # Condición de solución
                    soluciones.append(hijo)  # Guardar todas las soluciones

    fin_tiempo = time.time()
    tiempo_total = fin_tiempo - inicio_tiempo
    memoria_final = proceso.memory_info().rss
    memoria_consumida = memoria_final - memoria_inicial
    return soluciones, nodos_visitados, all_nodes, all_edges, memoria_consumida, tiempo_total

def dibujar_arbol(all_nodes, all_edges, filename="anchura.png"):
    G = nx.DiGraph()

    for nodo in all_nodes:
        G.add_node(nodo.id, label=str(nodo.estado))

    for parent_id, child_id in all_edges:
        G.add_edge(parent_id, child_id)

    levels = {}
    def asignar_niveles(nodo, depth=0):
        if depth not in levels:
            levels[depth] = []
        levels[depth].append(nodo.id)
        for hijo in nodo.hijos:
            asignar_niveles(hijo, depth+1)

    asignar_niveles(all_nodes[0])

    pos = {}
    for depth, ids in levels.items():
        for i, node_id in enumerate(ids):
            pos[node_id] = (i, -depth)

    labels = nx.get_node_attributes(G, 'label')

    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, labels=labels, node_color='lightgreen', node_size=2000, font_size=10, font_weight='bold', arrows=True)
    plt.title("Árbol de Búsqueda de Anchura - Ovejas y Lobos")

    # Guardar el gráfico en un archivo
    plt.savefig(filename)
    
    plt.close() 
   
def main():
    estado_inicial = (3, 3, 1, 0, 0)
    nodo_raiz = Nodo(estado_inicial, id=0)
    soluciones, nodos_visitados, all_nodes, all_edges, memoria_consumida, tiempo_total = bfs(nodo_raiz)

    if soluciones:
        print("Se encontraron soluciones:")
        for idx, solucion in enumerate(soluciones):
            print(f"Solución {idx + 1}:")
            camino = []
            nodo = solucion
            while nodo:
                camino.append(nodo.estado)
                nodo = nodo.padre
            camino.reverse()
            for step_idx, estado in enumerate(camino):
                print(f"Paso {step_idx + 1}: {estado}")
            print("************************************")
    else:
        print("No se encontraron soluciones.")

    print(f"\nMedidas de rendimiento:")
    print(f"Nodos visitados (válidos): {nodos_visitados}")
    print(f"Total de nodos generados: {len(all_nodes)}")
    print(f"Tiempo total de ejecución: {tiempo_total:.4f} segundos")
    print(f"Memoria RAM total consumida: {memoria_consumida / 1024:.2f} bytes")

    # Retornar el buffer con la imagen del árbol de búsqueda
    return dibujar_arbol(all_nodes, all_edges)

if __name__ == "__main__":
    main()
