# ==========================================
# MST — ÁRBOL DE EXPANSIÓN MÍNIMA
# Relaciones mínimas evolutivas
# ==========================================

# Este algoritmo aplica el método de Kruskal
# para encontrar el Árbol de Expansión Mínima
# (Minimum Spanning Tree) sobre la red de
# interacciones biológicas.

# En el contexto del proyecto:
# cada nodo representa una proteína,
# cada arista representa una interacción,
# el peso representa la fuerza de interacción.

# El MST conecta todas las proteínas usando
# el menor peso total posible, revelando
# las relaciones evolutivas mínimas
# necesarias para mantener la red conectada.

# ==========================================
# IMPORTACIÓN DE LIBRERÍAS
# ==========================================

import pandas as pd
import matplotlib.pyplot as plt
import math


# ==========================================
# LEER DATASET
# ==========================================

df = pd.read_csv("grafo_biologico_1500.csv")


# ==========================================
# ESTRUCTURA UNION-FIND
# ==========================================

# Se usa internamente por Kruskal
# para detectar ciclos

def make_set(nodos):
    parent = {n: n for n in nodos}
    rank   = {n: 0  for n in nodos}
    return parent, rank


def find(parent, x):
    if parent[x] != x:
        parent[x] = find(parent, parent[x])
    return parent[x]


def union(parent, rank, x, y):
    rx, ry = find(parent, x), find(parent, y)
    if rx == ry:
        return False
    if rank[rx] < rank[ry]:
        rx, ry = ry, rx
    parent[ry] = rx
    if rank[rx] == rank[ry]:
        rank[rx] += 1
    return True


# ==========================================
# ALGORITMO DE KRUSKAL
# ==========================================

def kruskal(nodos, aristas):

    # Ordenar aristas por peso ascendente
    # (relaciones más débiles primero)
    aristas_ord = sorted(aristas, key=lambda x: x[2])

    parent, rank = make_set(nodos)

    mst        = []
    peso_total = 0

    for u, v, w in aristas_ord:

        # Si conecta dos componentes distintas
        # no genera ciclo → agregar al MST
        if union(parent, rank, u, v):
            mst.append((u, v, w))
            peso_total += w

            # El MST tiene exactamente n-1 aristas
            if len(mst) == len(nodos) - 1:
                break

    return mst, peso_total


# ==========================================
# PREPARAR DATOS
# ==========================================

# Extraer nodos únicos
nodos = set(df['protein1']).union(set(df['protein2']))

# Convertir aristas a lista de tuplas
aristas = list(df[['protein1', 'protein2', 'weight']].itertuples(
    index=False, name=None
))


# ==========================================
# EJECUTAR KRUSKAL
# ==========================================

mst_aristas, peso_total = kruskal(nodos, aristas)


# ==========================================
# MOSTRAR RESULTADOS
# ==========================================

print("=" * 45)
print("MST — Árbol de Expansión Mínima (Kruskal)")
print("=" * 45)
print(f"Nodos en la red      : {len(nodos)}")
print(f"Aristas en el MST    : {len(mst_aristas)}")
print(f"Peso total del MST   : {peso_total:.4f}")
print()
print("Primeras 10 relaciones evolutivas mínimas:")
print("-" * 45)
for u, v, w in mst_aristas[:10]:
    print(f"  {u:10s} ↔ {v:10s}  (peso: {w:.4f})")


# ==========================================
# SUBGRAFO: 20 PRIMERAS ARISTAS MST
# ==========================================

sub_aristas = mst_aristas[:20]

sub_nodos = list(set(
    [u for u, v, w in sub_aristas] +
    [v for u, v, w in sub_aristas]
))


# ==========================================
# POSICIONES CIRCULARES
# ==========================================

posiciones = {}
radio = 10

for i, nodo in enumerate(sub_nodos):
    angulo = 2 * math.pi * i / len(sub_nodos)
    posiciones[nodo] = (
        radio * math.cos(angulo),
        radio * math.sin(angulo)
    )


# ==========================================
# VISUALIZACIÓN
# ==========================================

plt.figure(figsize=(12, 10))

# Dibujar aristas del MST
for u, v, w in sub_aristas:
    x = [posiciones[u][0], posiciones[v][0]]
    y = [posiciones[u][1], posiciones[v][1]]
    plt.plot(x, y, color='#5DCAA5', linewidth=1.5, zorder=1)

    # Peso en el centro de la arista
    mx = (posiciones[u][0] + posiciones[v][0]) / 2
    my = (posiciones[u][1] + posiciones[v][1]) / 2
    plt.text(mx, my, f"{w:.2f}", fontsize=7,
             ha='center', color='#5F5E5A')

# Dibujar nodos
for nodo, (x, y) in posiciones.items():
    plt.scatter(x, y, s=700, color='#085041',
                edgecolors='black', zorder=2)
    plt.text(x, y, nodo, fontsize=8,
             ha='center', va='center',
             color='white', fontweight='bold')

plt.title(
    f"MST — Relaciones Evolutivas Mínimas (Kruskal)\n"
    f"Peso total: {peso_total:.4f} · {len(mst_aristas)} aristas",
    fontsize=12
)
plt.axis('off')
plt.tight_layout()
plt.show()