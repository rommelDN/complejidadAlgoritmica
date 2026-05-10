import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

df = pd.read_csv("grafo_biologico_1500.csv")

proteinas = []

for i in range(len(df)):

    p1 = df.iloc[i]["protein1"]
    p2 = df.iloc[i]["protein2"]

    if p1 not in proteinas:
        proteinas.append(p1)

    if p2 not in proteinas:
        proteinas.append(p2)

ids = {}

for i in range(len(proteinas)):
    ids[proteinas[i]] = i

parent = [i for i in range(len(proteinas))]


def Find(s, a):

    while s[a] != a:
        a = s[a]

    return a


def Union(s, a, b):

    pa = Find(s, a)
    pb = Find(s, b)

    s[pa] = pb


for i in range(len(df)):

    p1 = df.iloc[i]["protein1"]
    p2 = df.iloc[i]["protein2"]

    id1 = ids[p1]
    id2 = ids[p2]

    Union(parent, id1, id2)


grupos = {}

for proteina in proteinas:

    raiz = Find(parent, ids[proteina])

    if raiz not in grupos:
        grupos[raiz] = []

    grupos[raiz].append(proteina)


print("UFDS - Agrupación de genes/proteínas\n")

print("Cantidad de grupos encontrados:",
      len(grupos))

grupo_mayor = max(grupos.values(), key=len)

print("\nGrupo más grande:",
      len(grupo_mayor),
      "proteínas/genomas")

print("\nPrimeras 25 proteínas del grupo principal:\n")

for proteina in grupo_mayor[:25]:
    print(proteina)

G = nx.Graph()

for i in range(len(df)):

    p1 = df.iloc[i]["protein1"]
    p2 = df.iloc[i]["protein2"]

    G.add_edge(p1, p2)

top_nodos = sorted(
    G.degree,
    key=lambda x: x[1],
    reverse=True
)

top_nodos = [
    n for n, d in top_nodos
    if n in grupo_mayor
][:25]

subG = G.subgraph(top_nodos)

plt.figure(figsize=(12,10))

pos = nx.spring_layout(subG, seed=42)

nx.draw_networkx_nodes(
    subG,
    pos,
    node_size=1400
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

plt.title("Subgrafo UFDS de Proteínas Agrupadas")

plt.axis("off")

plt.show()