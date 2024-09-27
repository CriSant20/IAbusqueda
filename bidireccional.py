import time
import psutil  # Para medir el consumo de memoria
from collections import deque, defaultdict
import networkx as nx
import matplotlib.pyplot as plt

# Variables globales para asignar IDs y almacenar nodos y aristas
node_counter = 0
nodes_data = []
edges_data = []

class Nodo:
    def __init__(self, estado, padre=None, id=None, depth=0, node_type='default'):
        self.estado = estado
        self.padre = padre
        self.id = id  # ID único para visualización
        self.depth = depth
        self.node_type = node_type

def create_node(estado, padre=None, node_type='default'):
    global node_counter
    depth = padre.depth + 1 if padre else 0
    node = Nodo(estado, padre, id=node_counter, depth=depth, node_type=node_type)
    
    # Añadir nodo a nodes_data
    node_label = str(estado)
    nodes_data.append({
        'id': str(node.id),
        'label': node_label,
        'depth': depth,
        'node_type': node_type
    })
    node_counter += 1
    return node

def validar_estado(estado):
    o_izq, l_izq, b, o_der, l_der = estado
    if o_izq < 0 or l_izq < 0 or o_der < 0 or l_der < 0:
        return False
    if (o_izq > 0 and o_izq < l_izq) or (o_der > 0 and o_der < l_der):
        return False
    return True

def generar_acciones(estado):
    acciones = []
    o_izq, l_izq, b, o_der, l_der = estado
    movimientos = [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]
    for do, dl in movimientos:
        if b == 1:
            nuevo_estado = (o_izq - do, l_izq - dl, 0, o_der + do, l_der + dl)
        else:
            nuevo_estado = (o_izq + do, l_izq + dl, 1, o_der - do, l_der - dl)
        if validar_estado(nuevo_estado):
            acciones.append(nuevo_estado)
    return acciones

def bidireccional(nodo_inicial, nodo_final):
    global edges_data
    frontera_inicial = deque([nodo_inicial])
    frontera_final = deque([nodo_final])
    explorado_inicial = set()
    explorado_final = set()
    nodos_visitados = 0

    padres_inicial = {nodo_inicial.estado: nodo_inicial}
    padres_final = {nodo_final.estado: nodo_final}

    process = psutil.Process()  # Medir el uso de memoria
    memoria_inicial = process.memory_info().rss / (1024 * 1024)  # Convertir a MB

    while frontera_inicial and frontera_final:
        # Expandir desde el lado inicial
        nodo_actual_inicial = frontera_inicial.popleft()
        explorado_inicial.add(nodo_actual_inicial.estado)
        nodos_visitados += 1

        acciones = generar_acciones(nodo_actual_inicial.estado)

        for accion in acciones:
            if accion not in explorado_inicial:
                hijo = create_node(accion, padre=nodo_actual_inicial)
                # Añadir arista de padre a hijo
                edges_data.append({
                    'source': str(nodo_actual_inicial.id),
                    'target': str(hijo.id)
                })
                if accion in padres_inicial:
                    continue
                padres_inicial[accion] = hijo
                frontera_inicial.append(hijo)

                if accion in padres_final:
                    # Se encontró una conexión
                    memoria_final = process.memory_info().rss / (1024 * 1024)  # Convertir a MB
                    memoria_consumida = memoria_final - memoria_inicial
                    print(f"Memoria consumida al encontrar conexión: {memoria_consumida:.4f} MB")
                    return hijo, padres_final[accion], nodos_visitados

        # Simulamos trabajo para mejorar la medición
        time.sleep(0.01)  # Retardo de 10ms

        # Expandir desde el lado final
        nodo_actual_final = frontera_final.popleft()
        explorado_final.add(nodo_actual_final.estado)
        nodos_visitados += 1

        acciones = generar_acciones(nodo_actual_final.estado)

        for accion in acciones:
            if accion not in explorado_final:
                hijo = create_node(accion, padre=nodo_actual_final)
                # Añadir arista de padre a hijo
                edges_data.append({
                    'source': str(nodo_actual_final.id),
                    'target': str(hijo.id)
                })
                if accion in padres_final:
                    continue
                padres_final[accion] = hijo
                frontera_final.append(hijo)

                if accion in padres_inicial:
                    # Se encontró una conexión
                    memoria_final = process.memory_info().rss / (1024 * 1024)  # Convertir a MB
                    memoria_consumida = memoria_final - memoria_inicial
                    return padres_inicial[accion], hijo, nodos_visitados

    return None, None, nodos_visitados

def reconstruir_camino(nodo_desde_inicial, nodo_desde_final):
    # Camino desde el inicio hasta el punto de encuentro
    camino_inicial = []
    nodo = nodo_desde_inicial
    while nodo:
        camino_inicial.append(nodo.estado)
        nodo = nodo.padre
    camino_inicial.reverse()

    # Camino desde el punto de encuentro hasta el objetivo
    camino_final = []
    nodo = nodo_desde_final.padre  # Evitar duplicar el estado de encuentro
    while nodo:
        camino_final.append(nodo.estado)
        nodo = nodo.padre

    camino_total = camino_inicial + camino_final
    return camino_total

def assign_positions(nodes_data):
    depth_dict = defaultdict(list)
    for node in nodes_data:
        depth = node['depth']
        depth_dict[depth].append(node)

    for depth, nodes in depth_dict.items():
        x_spacing = 100  # Espaciado entre nodos a la misma profundidad
        y = -depth * 200  # La profundidad determina la posición en y (vertical)
        num_nodes = len(nodes)
        total_width = (num_nodes - 1) * x_spacing
        x_start = -total_width / 2
        for i, node in enumerate(nodes):
            x = x_start + i * x_spacing
            node['pos'] = (x, y)  # x será la coordenada horizontal y y será la vertical
    return nodes_data

def dibujar_arbol():
    G = nx.DiGraph()

    # Agregar nodos
    pos = {}
    for node in nodes_data:
        G.add_node(node['id'], label=node['label'])
        pos[node['id']] = node['pos']

    # Agregar aristas
    for edge in edges_data:
        G.add_edge(edge['source'], edge['target'])

    labels = nx.get_node_attributes(G, 'label')

    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, labels=labels, node_color='lightblue', node_size=2000, font_size=10, font_weight='bold', arrows=True)
    plt.title("Árbol de Búsqueda - Ovejas y Lobos")

    # Guardar el gráfico como archivo PNG
    plt.savefig("bidireccional.png")

    # Mostrar el gráfico
    plt.close() 

def main():
    global nodes_data, edges_data

    # Iniciar el seguimiento de memoria y tiempo
    process = psutil.Process()
    memoria_inicial = process.memory_info().rss / (1024 * 1024)  # Convertir a MB
    inicio_tiempo = time.time()

    estado_inicial = (3, 3, 1, 0, 0)  # (ovejas_izq, lobos_izq, barco, ovejas_der, lobos_der)
    nodo_raiz_inicial = create_node(estado_inicial, node_type='input')

    estado_final = (0, 0, 0, 3, 3)
    nodo_raiz_final = create_node(estado_final, node_type='output')

    solucion_desde_inicial, solucion_desde_final, nodos_visitados = bidireccional(
        nodo_raiz_inicial, nodo_raiz_final)

    # Medir tiempo y memoria después de la ejecución
    fin_tiempo = time.time()
    memoria_final = process.memory_info().rss / (1024 * 1024)  # Convertir a MB

    memoria_consumida = memoria_final - memoria_inicial
    tiempo_ejecucion = (fin_tiempo - inicio_tiempo)  # Tiempo total de ejecución

    if solucion_desde_inicial and solucion_desde_final:
        camino_total = reconstruir_camino(solucion_desde_inicial, solucion_desde_final)
        print("Solución encontrada:")
        for paso in camino_total:
            print(paso)

    print(f"Nodos visitados: {nodos_visitados}")
    print(f"Tiempo de ejecución: {tiempo_ejecucion:.4f} segundos")
    print(f"Memoria consumida: {memoria_consumida:.4f} MB")

    # Asignar posiciones para los nodos antes de dibujar
    nodes_data = assign_positions(nodes_data)

    # Dibujar el árbol de búsqueda
    dibujar_arbol()

if __name__ == "__main__":
    main()
