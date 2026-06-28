import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import time

# ==========================================
# MEDIR TIEMPO DE EJECUCIÓN
# ==========================================

inicio = time.time()

# ==========================================
# LEER DATASET
# ==========================================

df = pd.read_csv("grafo_biologico_1500.csv")

# ==========================================
# CREAR GRAFO PONDERADO
# ==========================================

G = nx.Graph()

# ==========================================
# AGREGAR ARISTAS
# ==========================================

for _, row in df.iterrows():

    G.add_edge(
        row["protein1"],
        row["protein2"],
        weight=row["weight"]
    )

# ==========================================
# INFORMACIÓN DEL GRAFO
# ==========================================

print("\n===== INFORMACIÓN DEL GRAFO =====")

print("Cantidad de nodos:",
      G.number_of_nodes())

print("Cantidad de aristas:",
      G.number_of_edges())

# ==========================================
# DENSIDAD DEL GRAFO
# ==========================================

densidad = nx.density(G)

print("Densidad:",
      densidad)

# ==========================================
# NODOS MÁS IMPORTANTES
# (GRADO)
# ==========================================

grados = dict(G.degree())

top_grados = sorted(
    grados.items(),
    key=lambda x: x[1],
    reverse=True
)[:10]

print("\n===== TOP 10 NODOS CRÍTICOS =====")

for nodo, grado in top_grados:
    print(f"{nodo}: {grado}")

# ==========================================
# PAGE RANK
# ==========================================

pagerank = nx.pagerank(
    G,
    weight='weight'
)

top_pagerank = sorted(
    pagerank.items(),
    key=lambda x: x[1],
    reverse=True
)[:10]

print("\n===== TOP 10 PAGERANK =====")

for nodo, score in top_pagerank:
    print(f"{nodo}: {score:.6f}")

# ==========================================
# COMPONENTES CONEXAS
# ==========================================

componentes = nx.number_connected_components(G)

print("\nCantidad de componentes conexas:",
      componentes)

# ==========================================
# TIEMPO TOTAL
# ==========================================

fin = time.time()

print("\nTiempo total:",
      round(fin - inicio, 4),
      "segundos")

# ==========================================
# VISUALIZACIÓN SIMPLE
# ==========================================

plt.figure(figsize=(12, 12))

nx.draw_networkx(
    G,
    node_size=15,
    with_labels=False
)

plt.title("Grafo Biológico")

plt.show()