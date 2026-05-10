import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import time

# ==========================================
# LEER DATASET
# ==========================================

df = pd.read_csv("grafo_biologico_1500.csv")

# ==========================================
# FUNCIÓN FUERZA BRUTA
# ==========================================

def comparar_secuencias(seq1, seq2):

    coincidencias = 0

    longitud = min(len(seq1), len(seq2))

    for i in range(longitud):

        if seq1[i] == seq2[i]:
            coincidencias += 1

    similitud = (
        coincidencias / longitud
    ) * 100

    return coincidencias, similitud

# ==========================================
# CREAR GRAFO
# ==========================================

G = nx.Graph()

# ==========================================
# TEMPORIZADOR
# ==========================================

inicio = time.time()

print("\n===== GRAFO DE SIMILITUD =====\n")

# ==========================================
# ANALIZAR RELACIONES
# ==========================================

for index, row in df.head(300).iterrows():

    proteina_1 = str(row["protein1"])

    proteina_2 = str(row["protein2"])

    coincidencias, similitud = comparar_secuencias(
        proteina_1,
        proteina_2
    )

    # ======================================
    # SOLO SIMILITUDES ALTAS
    # ======================================

    if similitud >= 50:

        G.add_edge(
            proteina_1,
            proteina_2,
            weight=similitud
        )

        print(f"{proteina_1} ↔ {proteina_2}")
        print(f"Similitud: {similitud:.2f}%")
        print("-" * 40)

# ==========================================
# FIN
# ==========================================

fin = time.time()

print("\nTiempo total:",
      round(fin - inicio, 4),
      "segundos")

# ==========================================
# INFORMACIÓN
# ==========================================

print("\n===== INFORMACIÓN DEL GRAFO =====")

print("Nodos:",
      G.number_of_nodes())

print("Aristas:",
      G.number_of_edges())

# ==========================================
# VISUALIZACIÓN
# ==========================================

plt.figure(figsize=(18, 18))

# Layout distribuido
pos = nx.spring_layout(
    G,
    k=1.8,
    iterations=100,
    seed=42
)

# Tamaño nodos
node_sizes = [

    G.degree(n) * 250

    for n in G.nodes()

]

# Grosor aristas
edge_widths = [

    d["weight"] / 20

    for _, _, d in G.edges(data=True)

]

# Dibujar nodos
nx.draw_networkx_nodes(
    G,
    pos,
    node_size=node_sizes,
    alpha=0.9
)

# Dibujar aristas
nx.draw_networkx_edges(
    G,
    pos,
    width=edge_widths,
    alpha=0.4
)

# Labels
nx.draw_networkx_labels(
    G,
    pos,
    font_size=10,
    font_weight="bold"
)

# Pesos
edge_labels = {

    (u, v): f"{d['weight']:.0f}%"

    for u, v, d in G.edges(data=True)

}

nx.draw_networkx_edge_labels(
    G,
    pos,
    edge_labels=edge_labels,
    font_size=8
)

plt.title(
    "Subgrafo de Similitud entre Proteínas",
    fontsize=22
)

plt.axis("off")

plt.show()