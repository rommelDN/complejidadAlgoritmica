import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import random

df = pd.read_csv("grafo_biologico_1500.csv")

G = nx.Graph()

for i in range(len(df)):

    proteina1 = df.iloc[i]["protein1"]
    proteina2 = df.iloc[i]["protein2"]

    peso = df.iloc[i]["weight"]

    G.add_edge(
        proteina1,
        proteina2,
        weight=peso
    )

proteina_inicio = random.choice(
    list(G.nodes())
)

visitados = []
pila = [proteina_inicio]

while pila:

    nodo = pila.pop()

    if nodo not in visitados:

        visitados.append(nodo)

        for vecino in G[nodo]:

            if vecino not in visitados:

                pila.append(vecino)

sub_nodos = visitados[:25]

subG = G.subgraph(sub_nodos)

plt.figure(figsize=(14, 12))

pos = nx.spring_layout(
    subG,
    seed=42
)

nx.draw_networkx_nodes(
    subG,
    pos,
    node_size=1200,
    alpha=0.9
)

nx.draw_networkx_edges(
    subG,
    pos,
    width=2,
    alpha=0.5
)

nx.draw_networkx_labels(
    subG,
    pos,
    font_size=9,
    font_weight="bold"
)

plt.title(
    f"Subgrafo DFS desde {proteina_inicio}",
    fontsize=16
)

plt.axis("off")

plt.show()