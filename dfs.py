import pandas as pd
import networkx as nx

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