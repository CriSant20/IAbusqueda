import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
import time
import psutil

class Nodo:
    def __init__(self, estado, padre=None, accion=None, id=None, valido=True):
        self.estado = estado
        self.padre = padre
        self.accion = accion
        self.hijos = []
        self.id = id
        self.valido = valido

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

def dfs(nodo_raiz):
    inicio_tiempo = time.time()
    proceso = psutil.Process()
    memoria_inicial = proceso.memory_info().rss

    frontera = [nodo_raiz]  # Usar una pila en lugar de una cola
    estados_visitados = set()
    estados_visitados.add(nodo_raiz.estado)
    estados_generados = set()
    estados_generados.add(nodo_raiz.estado)
    nodos_visitados = 1
    node_id_counter = 1

    all_nodes = [nodo_raiz]
    all_edges = []
    soluciones = []

    while frontera:
        nodo_actual = frontera.pop()  # Sacar el último nodo (LIFO)
        # Simular trabajo para mejorar la medición de tiempo
        time.sleep(0.01)  # Retardo de 10ms
        hijos, node_id_counter = expandir_nodo(nodo_actual, node_id_counter, estados_generados)
        for hijo in hijos:
            all_nodes.append(hijo)
            all_edges.append((nodo_actual.id, hijo.id))
            if hijo.valido:
                if hijo.estado not in estados_visitados:
                    frontera.append(hijo)
                    estados_visitados.add(hijo.estado)
                    nodos_visitados += 1
                    
                    # Agregar solución y continuar buscando
                    if hijo.estado == (0, 0, 0, 3, 3):
                        soluciones.append(hijo)
                        # Añadir todos los hijos a la frontera para seguir buscando
                        frontera.extend(hijo.hijos)

    fin_tiempo = time.time()
    tiempo_total = fin_tiempo - inicio_tiempo
    memoria_final = proceso.memory_info().rss
    memoria_consumida = memoria_final - memoria_inicial

    return soluciones, nodos_visitados, all_nodes, all_edges, memoria_consumida, tiempo_total

def encontrar_camino(solucion):
    camino = []
    nodo = solucion
    while nodo:
        camino.append(nodo)
        nodo = nodo.padre
    return camino[::-1]  # Invertir para obtener el camino desde la raíz

def dibujar_arbol(all_nodes, all_edges, soluciones):
    G = nx.DiGraph()

    for nodo in all_nodes:
        G.add_node(nodo.id, label=str(nodo.estado))

    for parent_id, child_id in all_edges:
        G.add_edge(parent_id, child_id)

    # Simulamos un layout jerárquico basado en niveles de profundidad en el árbol
    levels = {}
    
    def asignar_niveles(nodo, depth=0):
        if depth not in levels:
            levels[depth] = []
        levels[depth].append(nodo.id)
        for hijo in nodo.hijos:
            asignar_niveles(hijo, depth + 1)

    asignar_niveles(all_nodes[0])

    pos = {}
    for depth, ids in levels.items():
        for i, node_id in enumerate(ids):
            pos[node_id] = (i, -depth)

    labels = nx.get_node_attributes(G, 'label')

    plt.figure(figsize=(12, 8))
    
    # Colores para nodos
    color_map = []
    for nodo in all_nodes:
        if nodo in soluciones:
            color_map.append('green')  # Nodo en el camino de solución
        elif not nodo.valido:
            color_map.append('red')  # Nodo estéril
        else:
            color_map.append('lightgreen')  # Nodos válidos

    nx.draw(G, pos, with_labels=True, labels=labels, node_color=color_map, node_size=2000, font_size=10, font_weight='bold', arrows=True)
    plt.title("Árbol de Búsqueda en Profundidad - Ovejas y Lobos")

    # Guardar el gráfico como archivo PNG
    plt.savefig("profundidad.png")
    plt.close()

def main():
    estado_inicial = (3, 3, 1, 0, 0)
    nodo_raiz = Nodo(estado_inicial, id=0)
    soluciones, nodos_visitados, all_nodes, all_edges, memoria_consumida, tiempo_total = dfs(nodo_raiz)

    if soluciones:
        print("Se encontraron soluciones:")
        for idx, solucion in enumerate(soluciones):
            print(f"Solución {idx + 1}:")
            camino = encontrar_camino(solucion)
            for step_idx, nodo in enumerate(camino):
                print(f"Paso {step_idx + 1}: {nodo.estado}")
            print("---")
    else:
        print("No se encontraron soluciones.")

    # Dibujar el árbol de búsqueda usando networkx
    dibujar_arbol(all_nodes, all_edges, soluciones)

    print(f"\nMedidas de rendimiento:")
    print(f"Nodos visitados (válidos): {nodos_visitados}")
    print(f"Total de nodos generados: {len(all_nodes)}")
    print(f"Tiempo total de ejecución: {tiempo_total:.4f} segundos")
    print(f"Memoria RAM total consumida: {memoria_consumida / 1024:.2f} bytes")
    
if __name__ == "__main__":
    main()
