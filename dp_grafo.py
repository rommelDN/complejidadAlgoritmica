# ==========================================
# DP EN GRAFOS — CAMINOS ÓPTIMOS
# Redes biológicas de proteínas
# ==========================================

# Este algoritmo aplica Programación
# Dinámica directamente sobre la estructura
# del grafo biológico para encontrar los
# caminos de MAYOR PESO ACUMULADO entre
# proteínas (rutas biológicas óptimas).

# Se usa una variante de Bellman-Ford
# adaptada para maximizar en lugar de
# minimizar, lo que permite encontrar
# la ruta de señalización más "fuerte"
# entre dos proteínas hub de la red.

# Subestructura óptima:
# el mejor camino de A→C que pasa por B
# es el mejor camino A→B + mejor B→C.

# ==========================================
# IMPORTACIÓN DE LIBRERÍAS
# ==========================================

import pandas as pd
import matplotlib.pyplot as plt
import math
from collections import defaultdict


# ==========================================
# LEER DATASET
# ==========================================

df = pd.read_csv("grafo_biologico_1500.csv")


# ==========================================
# CONSTRUIR GRAFO
# ==========================================

grafo = defaultdict(list)

for _, row in df.iterrows():
    u = row['protein1']
    v = row['protein2']
    w = float(row['weight'])

    # Grafo no dirigido: ambas direcciones
    grafo[u].append((v, w))
    grafo[v].append((u, w))


# ==========================================
# SELECCIONAR NODOS FUENTE Y DESTINO
# ==========================================

# Elegir proteínas con más conexiones
grado = defaultdict(int)
for _, row in df.iterrows():
    grado[row['protein1']] += 1
    grado[row['protein2']] += 1

top = sorted(grado, key=grado.get, reverse=True)

FUENTE  = top[0]    # proteína hub principal
DESTINO = top[2]    # otra proteína importante


# ==========================================
# DP EN GRAFO — BELLMAN-FORD MAXIMIZACIÓN
# ==========================================

# dist[v] = máximo peso acumulado
# para llegar desde FUENTE hasta v

def dp_camino_optimo(grafo, fuente, destino, nodos):

    # Inicializar distancias
    # -inf = aún no alcanzado
    dist  = {n: float('-inf') for n in nodos}
    padre = {n: None           for n in nodos}

    # La fuente tiene distancia 0
    dist[fuente] = 0

    # Relajar todas las aristas |V|-1 veces
    num_nodos = len(nodos)

    for iteracion in range(num_nodos - 1):

        actualizado = False

        for u in nodos:
            if dist[u] == float('-inf'):
                continue

            for v, w in grafo.get(u, []):

                # Relajación: maximizar peso
                if dist[u] + w > dist[v]:
                    dist[v]  = dist[u] + w
                    padre[v] = u
                    actualizado = True

        # Si no hubo cambios, terminar antes
        if not actualizado:
            break

    # ======================================
    # RECONSTRUIR CAMINO
    # ======================================

    camino = []
    actual = destino

    # Seguir padres desde destino hasta fuente
    visitados_tb = set()
    while actual is not None:
        if actual in visitados_tb:
            break
        visitados_tb.add(actual)
        camino.append(actual)
        actual = padre[actual]

    camino.reverse()

    # Verificar que el camino es válido
    if camino and camino[0] == fuente:
        return dist[destino], camino, dist
    else:
        return float('-inf'), [], dist


# ==========================================
# EJECUTAR ALGORITMO
# ==========================================

# Usar solo nodos del top para eficiencia
nodos_top = set(top[:100])

# Asegurar que fuente y destino estén
nodos_top.add(FUENTE)
nodos_top.add(DESTINO)

peso_optimo, camino_optimo, distancias = dp_camino_optimo(
    grafo, FUENTE, DESTINO, nodos_top
)


# ==========================================
# MOSTRAR RESULTADOS
# ==========================================

print("=" * 55)
print("DP EN GRAFOS — Caminos Óptimos (Bellman-Ford Max)")
print("=" * 55)
print(f"Fuente  : {FUENTE}")
print(f"Destino : {DESTINO}")
print()

if camino_optimo:
    print(f"Peso acumulado óptimo : {peso_optimo:.4f}")
    print(f"Longitud del camino   : {len(camino_optimo)} nodos")
    print()
    print("Camino óptimo encontrado:")
    print("  " + " → ".join(camino_optimo))
else:
    print("No se encontró camino entre los nodos seleccionados.")

# Mostrar top 10 nodos más alcanzables
print()
print("Top 10 nodos con mayor peso acumulado desde la fuente:")
print("-" * 55)
dist_ord = sorted(
    [(n, d) for n, d in distancias.items() if d != float('-inf')],
    key=lambda x: x[1], reverse=True
)
for nodo, dist_val in dist_ord[:10]:
    print(f"  {nodo:15s}  peso acumulado: {dist_val:.4f}")


# ==========================================
# VISUALIZACIÓN
# ==========================================

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))


# --- Gráfico 1: Camino óptimo ---

if camino_optimo and len(camino_optimo) > 1:

    # Posicionar nodos del camino en línea
    pos_camino = {}
    for i, nodo in enumerate(camino_optimo):
        pos_camino[nodo] = (i, 0)

    # Dibujar aristas del camino
    for i in range(len(camino_optimo) - 1):
        u = camino_optimo[i]
        v = camino_optimo[i + 1]
        ax1.annotate(
            "", xy=pos_camino[v], xytext=pos_camino[u],
            arrowprops=dict(
                arrowstyle="->", color='#5DCAA5', lw=2.5
            )
        )

    # Dibujar nodos
    for nodo, (x, y) in pos_camino.items():
        if nodo == FUENTE:
            color = '#D85A30'
        elif nodo == DESTINO:
            color = '#0F6E56'
        else:
            color = '#534AB7'

        ax1.scatter(x, y, s=900, color=color,
                    edgecolors='black', zorder=3)
        ax1.text(x, y + 0.15, nodo, ha='center',
                 fontsize=8, fontweight='bold')

    ax1.set_xlim(-0.5, len(camino_optimo) - 0.5)
    ax1.set_ylim(-0.5, 0.8)
    ax1.axis('off')
    ax1.set_title(
        f"Camino óptimo: {FUENTE} → {DESTINO}\nPeso: {peso_optimo:.4f}",
        fontweight='bold'
    )

    # Leyenda
    from matplotlib.lines import Line2D
    leyenda = [
        Line2D([0], [0], marker='o', color='w',
               markerfacecolor='#D85A30', markersize=10, label='Fuente'),
        Line2D([0], [0], marker='o', color='w',
               markerfacecolor='#0F6E56', markersize=10, label='Destino'),
        Line2D([0], [0], marker='o', color='w',
               markerfacecolor='#534AB7', markersize=10, label='Intermedio'),
    ]
    ax1.legend(handles=leyenda, loc='lower right', fontsize=8)

else:
    ax1.text(0.5, 0.5, "Camino no encontrado\nentre los nodos seleccionados",
             ha='center', va='center', transform=ax1.transAxes,
             fontsize=12, color='gray')
    ax1.axis('off')


# --- Gráfico 2: Distribución de distancias ---

dist_vals = [d for n, d in dist_ord if d > 0][:50]
nodos_lbls = [n[:8] for n, d in dist_ord if d > 0][:50]

colores_bar = []
for n, d in dist_ord[:50]:
    if n == FUENTE:
        colores_bar.append('#D85A30')
    elif n == DESTINO:
        colores_bar.append('#0F6E56')
    else:
        colores_bar.append('#AFA9EC')

if dist_vals:
    ax2.barh(range(len(dist_vals)), dist_vals,
             color=colores_bar, edgecolor='white', linewidth=0.3)
    ax2.set_yticks(range(len(nodos_lbls)))
    ax2.set_yticklabels(nodos_lbls, fontsize=7)
    ax2.set_xlabel("Peso acumulado desde la fuente")
    ax2.set_title(
        "Distribución de pesos acumulados\n(top 50 nodos)",
        fontweight='bold'
    )

plt.suptitle(
    "DP en Grafos — Caminos Óptimos en Redes Biológicas",
    fontsize=13, fontweight='bold'
)
plt.tight_layout()
plt.show()