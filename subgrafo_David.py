import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

df = pd.read_csv("grafo_biologico_1500.csv")

G = nx.Graph()

for i in range(len(df)):

    p1 = df.iloc[i]["protein1"]
    p2 = df.iloc[i]["protein2"]

    peso = df.iloc[i]["weight"]

    G.add_edge(p1, p2, weight=peso)

top_nodos = sorted(
    G.degree,
    key=lambda x: x[1],
    reverse=True
)[:25]

top_nodos = [n for n, d in top_nodos]

subG = G.subgraph(top_nodos)

plt.figure(figsize=(14,12))

pos = nx.spring_layout(subG, seed=42)

nx.draw_networkx_nodes(
    subG,
    pos,
    node_size=1500
)

nx.draw_networkx_edges(
    subG,
    pos,
    width=2
)

nx.draw_networkx_labels(
    subG,
    pos,
    font_size=9
)

plt.title("Subgrafo de Proteínas Altamente Conectadas")

plt.axis("off")

plt.show()