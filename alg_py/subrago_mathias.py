import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Carga de datos
df = pd.read_csv("grafo_biologico_1500.csv")

# Creamos el grafo completo para analizar importancia
G_completo = nx.from_pandas_edgelist(df, 'protein1', 'protein2', ['weight'], create_using=nx.DiGraph())

# RESULTADO: Obtenemos los 25 nodos más importantes (PageRank)
importancia = nx.pagerank(G_completo, weight='weight')
nodos_clave = sorted(importancia.items(), key=lambda x: x[1], reverse=True)[:25]
nodos_a_dibujar = [n[0] for n in nodos_clave]

# Creamos el SUBGRAFO con esos resultados
subG = G_completo.subgraph(nodos_a_dibujar)

# Configuración visual robusta
plt.figure(figsize=(12, 10))
pos = nx.spring_layout(subG, k=1.2, seed=42)

# Dibujamos
nx.draw_networkx_nodes(subG, pos, node_size=1500, node_color='#58D68D', alpha=0.9)
nx.draw_networkx_edges(subG, pos, width=1.5, edge_color='gray', arrows=True, arrowsize=15)
nx.draw_networkx_labels(subG, pos, font_size=10, font_weight='bold')

plt.title("Subgrafo de Proteínas Críticas (Análisis de Importancia)", fontsize=14)
plt.axis('off')
plt.show()
