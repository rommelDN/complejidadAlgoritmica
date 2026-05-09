import pandas as pd
import sys

# Aumentar límite para grafos de 1500 nodos
sys.setrecursionlimit(3000)

df = pd.read_csv("grafo_biologico_1500.csv")
# Construcción manual de lista de adyacencia
adj = {}
for u, v, _ in df.values:
    if u not in adj: adj[u] = []
    adj[u].append(v)
    if v not in adj: adj[v] = []

def scc_tarjan_manual(grafo):
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

# Ejecución y reporte
sccs = scc_tarjan_manual(adj)
print(f"Total de componentes (SCC): {len(sccs)}")
print(f"Ciclos detectados: {len([s for s in sccs if len(s) > 1])}")