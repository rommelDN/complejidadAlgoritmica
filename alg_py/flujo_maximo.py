# ==========================================
# FLUJO MÁXIMO — FORD-FULKERSON
# Rutas metabólicas entre proteínas
# ==========================================

# Este algoritmo aplica Ford-Fulkerson con
# BFS (Edmonds-Karp) para encontrar el flujo
# máximo entre dos proteínas hub de la red.

# En el contexto del proyecto:
# la fuente (source) es la proteína con
# más conexiones salientes (hub de entrada),
# el sumidero (sink) es la proteína con
# más conexiones entrantes (hub de salida),
# el peso de cada arista es la capacidad
# de la ruta metabólica.

# El flujo máximo representa la cantidad
# máxima de "señal biológica" que puede
# fluir entre dos proteínas clave.

# ==========================================
# IMPORTACIÓN DE LIBRERÍAS
# ==========================================

import pandas as pd
import matplotlib.pyplot as plt
import math
from collections import defaultdict, deque


# ==========================================
# LEER DATASET
# ==========================================

df = pd.read_csv("grafo_biologico_1500.csv")


# ==========================================
# CONSTRUIR GRAFO DE CAPACIDADES
# ==========================================

# Usamos un diccionario de diccionarios:
# capacidad[u][v] = peso de la arista

capacidad  = defaultdict(lambda: defaultdict(float))
grafo_ady  = defaultdict(set)

for _, row in df.iterrows():
    u = row['protein1']
    v = row['protein2']
    w = float(row['weight'])

    capacidad[u][v] += w
    capacidad[v][u] += w   # grafo no dirigido
    grafo_ady[u].add(v)
    grafo_ady[v].add(u)


# ==========================================
# SELECCIONAR SOURCE Y SINK
# ==========================================

# Source: proteína con mayor grado saliente
# Sink:   proteína con mayor grado entrante
# (excluir la misma proteína)

grado = defaultdict(int)
for _, row in df.iterrows():
    grado[row['protein1']] += 1
    grado[row['protein2']] += 1

top_nodos = sorted(grado, key=grado.get, reverse=True)

SOURCE = top_nodos[0]
SINK   = top_nodos[1]


# ==========================================
# BFS — CAMINO AUMENTANTE
# ==========================================

def bfs(source, sink, padre, cap, ady):
    visitados = {source}
    cola      = deque([source])

    while cola:
        u = cola.popleft()
        for v in ady[u]:
            if v not in visitados and cap[u][v] > 0:
                visitados.add(v)
                padre[v] = u
                if v == sink:
                    return True
                cola.append(v)
    return False


# ==========================================
# FORD-FULKERSON (EDMONDS-KARP)
# ==========================================

def ford_fulkerson(source, sink, cap, ady):

    # Copia de capacidades (grafo residual)
    cap_residual = defaultdict(lambda: defaultdict(float))
    for u in cap:
        for v in cap[u]:
            cap_residual[u][v] = cap[u][v]

    flujo_total  = 0
    rutas_usadas = []

    while True:
        padre = {}
        if not bfs(source, sink, padre, cap_residual, ady):
            break

        # Encontrar capacidad mínima del camino
        flujo_camino = float('inf')
        v = sink
        camino = []
        while v != source:
            u = padre[v]
            flujo_camino = min(flujo_camino, cap_residual[u][v])
            camino.append(v)
            v = u
        camino.append(source)
        camino.reverse()

        # Actualizar grafo residual
        v = sink
        while v != source:
            u = padre[v]
            cap_residual[u][v] -= flujo_camino
            cap_residual[v][u] += flujo_camino
            v = u

        flujo_total += flujo_camino
        rutas_usadas.append((camino, flujo_camino))

    return flujo_total, rutas_usadas


# ==========================================
# EJECUTAR ALGORITMO
# ==========================================

flujo_max, rutas = ford_fulkerson(
    SOURCE, SINK, capacidad, grafo_ady
)


# ==========================================
# MOSTRAR RESULTADOS
# ==========================================

print("=" * 50)
print("FLUJO MÁXIMO — Ford-Fulkerson (Edmonds-Karp)")
print("=" * 50)
print(f"Fuente (source) : {SOURCE}")
print(f"Sumidero (sink) : {SINK}")
print(f"Flujo máximo    : {flujo_max:.4f}")
print(f"Rutas usadas    : {len(rutas)}")
print()
print("Rutas metabólicas encontradas:")
print("-" * 50)
for i, (camino, flujo) in enumerate(rutas[:5], 1):
    ruta_str = " → ".join(camino)
    print(f"  Ruta {i}: {ruta_str}")
    print(f"          Flujo: {flujo:.4f}")


# ==========================================
# SUBGRAFO DE RUTAS METABÓLICAS
# ==========================================

# Recolectar nodos y aristas de las rutas
nodos_vis = set()
aristas_vis = []

for camino, flujo in rutas[:6]:
    for nodo in camino:
        nodos_vis.add(nodo)
    for i in range(len(camino) - 1):
        aristas_vis.append((camino[i], camino[i+1], flujo))


# ==========================================
# POSICIONES CIRCULARES
# ==========================================

nodos_lista = list(nodos_vis)
posiciones  = {}
radio       = 10

for i, nodo in enumerate(nodos_lista):
    angulo = 2 * math.pi * i / len(nodos_lista)
    posiciones[nodo] = (
        radio * math.cos(angulo),
        radio * math.sin(angulo)
    )

# Posicionar source y sink al centro
if len(nodos_lista) > 2:
    posiciones[SOURCE] = (0, 3)
    posiciones[SINK]   = (0, -3)


# ==========================================
# VISUALIZACIÓN
# ==========================================

plt.figure(figsize=(13, 10))

# Dibujar aristas de flujo
for u, v, flujo in aristas_vis:
    if u in posiciones and v in posiciones:
        x = [posiciones[u][0], posiciones[v][0]]
        y = [posiciones[u][1], posiciones[v][1]]
        grosor = 1 + flujo / (flujo_max + 1) * 4
        plt.plot(x, y, color='#AFA9EC',
                 linewidth=grosor, alpha=0.6, zorder=1)

# Dibujar nodos
for nodo, (x, y) in posiciones.items():
    if nodo == SOURCE:
        color = '#D85A30'   # rojo: fuente
    elif nodo == SINK:
        color = '#0F6E56'   # verde: sumidero
    else:
        color = '#534AB7'   # morado: intermedios

    plt.scatter(x, y, s=800, color=color,
                edgecolors='black', zorder=2)
    plt.text(x, y, nodo, fontsize=8,
             ha='center', va='center',
             color='white', fontweight='bold')

# Leyenda
plt.scatter([], [], color='#D85A30', label=f'Source: {SOURCE}')
plt.scatter([], [], color='#0F6E56', label=f'Sink: {SINK}')
plt.scatter([], [], color='#534AB7', label='Nodo intermedio')
plt.legend(loc='upper right', fontsize=9)

plt.title(
    f"Flujo Máximo — Rutas Metabólicas (Ford-Fulkerson)\n"
    f"Flujo total: {flujo_max:.4f}  ·  {len(rutas)} rutas",
    fontsize=12
)
plt.axis('off')
plt.tight_layout()
plt.show()