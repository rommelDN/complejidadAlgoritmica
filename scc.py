import pandas as pd
import sys
import matplotlib.pyplot as plt
import math

sys.setrecursionlimit(5000)

df = pd.read_csv("grafo_biologico_1500.csv")

adj = {}
for u, v, _ in df.values:
    if u not in adj: adj[u] = []
    adj[u].append(v)
    if v not in adj: adj[v] = []

def algoritmo_scc(grafo):
    indice = 0
    stack = []
    on_stack = {u: False for u in grafo}
    indices = {u: -1 for u in grafo}
    lowlink = {u: -1 for u in grafo}
    resultado = []

    def fuerte_conexion(v):
        nonlocal indice
        indices[v] = lowlink[v] = indice
        indice += 1
        stack.append(v)
        on_stack[v] = True

        for w in grafo.get(v, []):
            if indices[w] == -1:
                fuerte_conexion(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif on_stack[w]:
                lowlink[v] = min(lowlink[v], indices[w])

        if lowlink[v] == indices[v]:
            componente = []
            while True:
                nodo = stack.pop()
                on_stack[nodo] = False
                componente.append(nodo)
                if nodo == v: break
            resultado.append(componente)

    for n in grafo:
        if indices[n] == -1:
            fuerte_conexion(n)
    return resultado

sccs_detectados = algoritmo_scc(adj)
print(f"Total de componentes (SCC): {len(sccs_detectados)}")
ciclos = [s for s in sccs_detectados if len(s) > 1]
print(f"Ciclos biológicos encontrados: {len(ciclos)}")

if ciclos:
    scc_ver = max(ciclos, key=len)[:20]
    n_set = set(scc_ver)
    pos = {}
    r = 10
    for i, nodo in enumerate(scc_ver):
        a = 2 * math.pi * i / len(scc_ver)
        pos[nodo] = (r * math.cos(a), r * math.sin(a))

    plt.figure(figsize=(10, 10))
    df_plot = df[df['protein1'].isin(n_set) & df['protein2'].isin(n_set)]

    for u, v in zip(df_plot['protein1'], df_plot['protein2']):
        plt.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], color='gray', alpha=0.5)

    for n, (x, y) in pos.items():
        plt.scatter(x, y, s=700, color='#5DADE2', edgecolors='black')
        plt.text(x, y, n, fontsize=8, ha='center', va='center', fontweight='bold')

    plt.title("Visualización del Algoritmo SCC ")
    plt.axis('off')
    plt.show()
