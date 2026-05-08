import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import time

# ==========================================
# INICIO
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
# Complejidad:
# O(E)
# ==========================================

for _, row in df.iterrows():

    G.add_edge(
        row["protein1"],
        row["protein2"],
        weight=row["weight"]
    )

# ==========================================
# INFORMACIÓN GENERAL
# ==========================================

print("\n===== INFORMACIÓN DEL GRAFO =====")

print("Cantidad de nodos:",
      G.number_of_nodes())

print("Cantidad de aristas:",
      G.number_of_edges())

# ==========================================
# DENSIDAD
# ==========================================

densidad = nx.density(G)

print("Densidad:",
      densidad)

# ==========================================
# TOP NODOS POR GRADO
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
# PAGERANK
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
# CREAR SUBGRAFO
# ==========================================

# Tomar top 40 nodos más conectados

top_nodes = sorted(
    G.degree,
    key=lambda x: x[1],
    reverse=True
)[:20]

# Extraer nombres de nodos

top_nodes = [n for n, d in top_nodes]

# Crear subgrafo

subG = G.subgraph(top_nodes)

# ==========================================
# VISUALIZACIÓN
# ==========================================

plt.figure(figsize=(22, 22))

# Layout físico
# k controla separación entre nodos

pos = nx.spring_layout(
    subG,
    k=2,
    iterations=200,
    seed=42
)

# ==========================================
# TAMAÑO DE NODOS
# proporcional al grado
# ==========================================

node_sizes = [

    subG.degree(n) * 120

    for n in subG.nodes()

]

# ==========================================
# GROSOR DE ARISTAS
# proporcional al peso
# ==========================================

edge_widths = [

    d["weight"] * 5

    for _, _, d in subG.edges(data=True)

]

# ==========================================
# DIBUJAR NODOS
# ==========================================

nx.draw_networkx_nodes(
    subG,
    pos,
    node_size=node_sizes,
    alpha=0.9
)

# ==========================================
# DIBUJAR ARISTAS
# ==========================================

nx.draw_networkx_edges(
    subG,
    pos,
    width=edge_widths,
    alpha=0.4
)

# ==========================================
# LABELS DE NODOS
# ==========================================

nx.draw_networkx_labels(
    subG,
    pos,
    font_size=11,
    font_weight="bold"
)

# ==========================================
# PESOS DE ARISTAS
# ==========================================

edge_labels = {

    (u, v): f"{d['weight']:.2f}"

    for u, v, d in subG.edges(data=True)

}

nx.draw_networkx_edge_labels(
    subG,
    pos,
    edge_labels=edge_labels,
    font_size=7
)

# ==========================================
# TÍTULO
# ==========================================

plt.title(
    "Subgrafo de Proteínas Críticas",
    fontsize=24
)

plt.axis("off")

plt.show()