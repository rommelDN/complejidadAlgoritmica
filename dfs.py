#Este algoritmo implementa la técnica de DFS (Depth First Search) o búsqueda en profundidad para explorar conexiones dentro de una red biológica de proteínas.

#El algoritmo comienza desde una proteína inicial (MYC) y recorre la red siguiendo caminos profundos antes de retroceder, utilizando una estructura tipo pila (LIFO: Last In First Out).
# ==========================================
# IMPORTACIÓN DE LIBRERÍAS
# ==========================================

# Pandas:
# Permite leer el archivo CSV
import pandas as pd

# NetworkX:
# Permite crear y trabajar con grafos
import networkx as nx

# Matplotlib:
# Se utiliza para visualizar el subgrafo
import matplotlib.pyplot as plt


# ==========================================
# LEER DATASET
# ==========================================

# Cargar archivo CSV

df = pd.read_csv("grafo_biologico_1500.csv")


# ==========================================
# CREAR GRAFO
# ==========================================

# Grafo no dirigido

G = nx.Graph()


# ==========================================
# AGREGAR ARISTAS
# ==========================================

# Cada fila del dataset representa:
# proteína1 <-> proteína2

for i in range(len(df)):

    # Obtener proteínas
    proteina1 = df.iloc[i]["protein1"]

    proteina2 = df.iloc[i]["protein2"]

    # Crear conexión
    G.add_edge(
        proteina1,
        proteina2
    )


# ==========================================
# ALGORITMO DFS
# ==========================================

# DFS:
# Depth First Search
# Búsqueda en profundidad

# Utiliza una pila LIFO:
# Last In First Out

def buscar_conexiones_dfs(
    grafo,
    ini
):

    # ======================================
    # LISTA DE VISITADOS
    # ======================================

    # Guarda nodos ya recorridos
    visitados = []


    # ======================================
    # PILA
    # ======================================

    # La pila comienza
    # con el nodo inicial

    pila = [ini]


    # ======================================
    # RECORRIDO DFS
    # ======================================

    while pila:

        # Sacar último elemento
        nodo = pila.pop()


        # ==============================
        # EVITAR REPETIDOS
        # ==============================

        if nodo not in visitados:

            # Marcar como visitado
            visitados.append(nodo)


            # ==========================
            # RECORRER VECINOS
            # ==========================

            for vecino in grafo[nodo]:

                # Si aún no fue visitado
                if vecino not in visitados:

                    # Agregar a la pila
                    pila.append(vecino)


    # Retornar recorrido DFS
    return visitados


# ==========================================
# NODO INICIAL
# ==========================================

# Proteína desde donde inicia DFS

proteina_inicio = "MYC"


# ==========================================
# EJECUTAR DFS
# ==========================================

resultado_dfs = buscar_conexiones_dfs(
    G,
    proteina_inicio
)


# ==========================================
# MOSTRAR RESULTADOS
# ==========================================

print(
    f"DFS - Exploración desde:"
    f" {proteina_inicio}"
)

print(
    "\nPrimeras 25 proteínas/genomas encontrados:\n"
)


# ==========================================
# MOSTRAR PRIMEROS NODOS
# ==========================================

for nodo in resultado_dfs[:25]:

    print(nodo)


# ==========================================
# TOTAL DE NODOS RECORRIDOS
# ==========================================

print(
    f"\nTotal de nodos recorridos:"
    f" {len(resultado_dfs)}"
)


# ==========================================
# CREAR SUBGRAFO
# ==========================================

# Tomamos solo los primeros 25 nodos
# para evitar saturación visual

sub_nodos = resultado_dfs[:25]

# Crear subgrafo
subG = G.subgraph(sub_nodos)


# ==========================================
# CREAR FIGURA
# ==========================================

plt.figure(figsize=(12,10))


# ==========================================
# DISTRIBUCIÓN DE NODOS
# ==========================================

# spring_layout organiza nodos
# mediante simulación física

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

    pos
)


# ==========================================
# DIBUJAR LABELS
# ==========================================

nx.draw_networkx_labels(

    subG,

    pos,

    # Tamaño letra
    font_size=9
)


# ==========================================
# TÍTULO
# ==========================================

plt.title(
    "Subgrafo DFS de Proteínas Conectadas"
)


# ==========================================
# OCULTAR EJES
# ==========================================

plt.axis("off")


# ==========================================
# MOSTRAR GRAFO
# ==========================================

plt.show()