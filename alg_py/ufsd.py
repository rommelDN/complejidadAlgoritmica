#Este algoritmo implementa la estructura UFDS (Union-Find Disjoint Set) para agrupar proteínas relacionadas dentro de una red biológica.
#El objetivo principal es identificar conjuntos de proteínas conectadas entre sí mediante interacciones biológicas. Para ello, el algoritmo utiliza las operaciones:
# ==========================================
# IMPORTACIÓN DE LIBRERÍAS
# ==========================================

# Pandas:
# Permite leer y manipular el CSV
import pandas as pd

# NetworkX:
# Permite trabajar con grafos
import networkx as nx

# Matplotlib:
# Se utiliza para visualizar el subgrafo
import matplotlib.pyplot as plt


# ==========================================
# LEER DATASET
# ==========================================

# Se carga el archivo CSV

df = pd.read_csv("grafo_biologico_1500.csv")


# ==========================================
# LISTA DE PROTEÍNAS
# ==========================================

# Aquí almacenaremos todas
# las proteínas únicas

proteinas = []


# ==========================================
# EXTRAER PROTEÍNAS ÚNICAS
# ==========================================

for i in range(len(df)):

    # Obtener proteínas
    p1 = df.iloc[i]["protein1"]

    p2 = df.iloc[i]["protein2"]

    # Agregar si no existe
    if p1 not in proteinas:
        proteinas.append(p1)

    if p2 not in proteinas:
        proteinas.append(p2)


# ==========================================
# ASIGNAR IDs NUMÉRICOS
# ==========================================

# Diccionario:
# proteína -> id

ids = {}

for i in range(len(proteinas)):

    ids[proteinas[i]] = i


# ==========================================
# ESTRUCTURA UNION-FIND
# ==========================================

# parent[i] = padre del nodo i

# Inicialmente cada nodo
# es su propio padre

parent = [

    i for i in range(len(proteinas))

]


# ==========================================
# FUNCIÓN FIND
# ==========================================

# Busca el representante
# principal del conjunto

def Find(s, a):

    # Mientras el nodo
    # no sea su propia raíz
    while s[a] != a:

        a = s[a]

    return a


# ==========================================
# FUNCIÓN UNION
# ==========================================

# Une dos conjuntos

def Union(s, a, b):

    # Buscar raíces
    pa = Find(s, a)

    pb = Find(s, b)

    # Unir conjuntos
    s[pa] = pb


# ==========================================
# UNIR PROTEÍNAS RELACIONADAS
# ==========================================

for i in range(len(df)):

    # Obtener proteínas
    p1 = df.iloc[i]["protein1"]

    p2 = df.iloc[i]["protein2"]

    # Obtener IDs
    id1 = ids[p1]

    id2 = ids[p2]

    # Unir conjuntos
    Union(parent, id1, id2)


# ==========================================
# CREAR GRUPOS
# ==========================================

# Diccionario:
# raíz -> lista de proteínas

grupos = {}


# ==========================================
# AGRUPAR PROTEÍNAS
# ==========================================

for proteina in proteinas:

    # Buscar raíz
    raiz = Find(
        parent,
        ids[proteina]
    )

    # Crear grupo si no existe
    if raiz not in grupos:

        grupos[raiz] = []

    # Agregar proteína
    grupos[raiz].append(proteina)


# ==========================================
# MOSTRAR RESULTADOS
# ==========================================

print(
    "UFDS - Agrupación de genes/proteínas\n"
)

print(
    "Cantidad de grupos encontrados:",
    len(grupos)
)


# ==========================================
# OBTENER GRUPO MÁS GRANDE
# ==========================================

grupo_mayor = max(
    grupos.values(),
    key=len
)

print(
    "\nGrupo más grande:",
    len(grupo_mayor),
    "proteínas/genomas"
)

print(
    "\nPrimeras 25 proteínas del grupo principal:\n"
)


# ==========================================
# MOSTRAR PROTEÍNAS
# ==========================================

for proteina in grupo_mayor[:25]:

    print(proteina)


# ==========================================
# CREAR GRAFO
# ==========================================

G = nx.Graph()


# ==========================================
# AGREGAR ARISTAS
# ==========================================

for i in range(len(df)):

    p1 = df.iloc[i]["protein1"]

    p2 = df.iloc[i]["protein2"]

    G.add_edge(p1, p2)


# ==========================================
# OBTENER NODOS MÁS IMPORTANTES
# ==========================================

# Degree:
# cantidad de conexiones

top_nodos = sorted(

    G.degree,

    key=lambda x: x[1],

    reverse=True
)


# ==========================================
# FILTRAR SOLO NODOS DEL GRUPO
# ==========================================

top_nodos = [

    n for n, d in top_nodos

    if n in grupo_mayor

][:25]


# ==========================================
# CREAR SUBGRAFO
# ==========================================

subG = G.subgraph(top_nodos)


# ==========================================
# CREAR FIGURA
# ==========================================

plt.figure(figsize=(12,10))


# ==========================================
# DISTRIBUCIÓN DE NODOS
# ==========================================

# spring_layout distribuye nodos
# usando simulación física

pos = nx.spring_layout(
    subG,
    seed=42
)


# ==========================================
# DIBUJAR NODOS
# ==========================================

nx.draw_networkx_nodes(

    subG,

    pos,

    # Tamaño nodos
    node_size=1400
)


# ==========================================
# DIBUJAR ARISTAS
# ==========================================

nx.draw_networkx_edges(

    subG,

    pos,

    # Grosor líneas
    width=2
)


# ==========================================
# DIBUJAR LABELS
# ==========================================

nx.draw_networkx_labels(

    subG,

    pos,

    # Tamaño texto
    font_size=9
)


# ==========================================
# TÍTULO
# ==========================================

plt.title(
    "Subgrafo UFDS de Proteínas Agrupadas"
)


# ==========================================
# OCULTAR EJES
# ==========================================

plt.axis("off")


# ==========================================
# MOSTRAR GRAFO
# ==========================================

plt.show()