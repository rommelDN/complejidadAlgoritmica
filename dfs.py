import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

df = pd.read_csv("grafo_biologico_1500.csv")

G = nx.Graph()

for i in range(len(df)):

    proteina1 = df.iloc[i]["protein1"]
    proteina2 = df.iloc[i]["protein2"]

    G.add_edge(proteina1, proteina2)

# DFS usando LIFO
def buscar_conexiones_dfs(grafo, ini):

    visitados = []
    pila = [ini]

    while pila:

        nodo = pila.pop()

        if nodo not in visitados:

            visitados.append(nodo)

            for vecino in grafo[nodo]:

                if vecino not in visitados:

                    pila.append(vecino)

    return visitados


proteina_inicio = "MYC"

resultado_dfs = buscar_conexiones_dfs(
    G,
    proteina_inicio
)

print(f"DFS - Exploración desde: {proteina_inicio}")

print("\nPrimeras 25 proteínas/genomas encontrados:\n")

for nodo in resultado_dfs[:25]:
    print(nodo)

print(f"\nTotal de nodos recorridos: {len(resultado_dfs)}")

sub_nodos = resultado_dfs[:25]

subG = G.subgraph(sub_nodos)

plt.figure(figsize=(12,10))

pos = nx.spring_layout(subG, seed=42)

nx.draw_networkx_nodes(
    subG,
    pos,
    node_size=1400
)

nx.draw_networkx_edges(
    subG,
    pos
)

nx.draw_networkx_labels(
    subG,
    pos,
    font_size=9
)

plt.title("Subgrafo DFS de Proteínas Conectadas")

plt.axis("off")

plt.show()