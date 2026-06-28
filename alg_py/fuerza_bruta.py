#
#Este algoritmo utiliza el enfoque de fuerza bruta para comparar secuencias de proteínas obtenidas desde un dataset biológico. El programa analiza carácter por carácter los nombres de dos proteínas y calcula un porcentaje de similitud según la cantidad de coincidencias encontradas en la misma posición.
#se construye un grafo de similitud utilizando la librería NetworkX, donde:
# cada nodo representa una proteína,
# cada arista representa una relación de similitud entre dos proteínas,y el peso de la arista corresponde al porcentaje de similitud calculado.
# Para evitar una visualización demasiado compleja, el algoritmo únicamente conecta proteínas cuya similitud sea igual o superior al 50%, generando así un subgrafo más comprensible visualmente.

# ==========================================
# IMPORTACIÓN DE LIBRERÍAS
# ==========================================

# Pandas:
# Se utiliza para leer y manipular el archivo CSV
import pandas as pd

# NetworkX:
# Permite crear y trabajar con grafos
import networkx as nx

# Matplotlib:
# Se utiliza para visualizar el grafo
import matplotlib.pyplot as plt

# Time:
# Permite medir el tiempo de ejecución
import time


# ==========================================
# LEER DATASET
# ==========================================

# Se carga el archivo CSV que contiene:
# protein1 | protein2 | weight

df = pd.read_csv("grafo_biologico_1500.csv")


# ==========================================
# FUNCIÓN FUERZA BRUTA
# ==========================================

# Esta función compara dos secuencias
# carácter por carácter.

# Parámetros:
# seq1 -> primera secuencia
# seq2 -> segunda secuencia

def comparar_secuencias(seq1, seq2):

    # Variable que almacenará
    # cuántos caracteres coinciden
    coincidencias = 0

    # Se toma la longitud mínima
    # para evitar errores de índice
    longitud = min(len(seq1), len(seq2))

    # Recorremos cada posición
    for i in range(longitud):

        # Si los caracteres coinciden
        # aumentamos el contador
        if seq1[i] == seq2[i]:

            coincidencias += 1

    # ======================================
    # CÁLCULO DE SIMILITUD
    # ======================================

    # Fórmula:
    # (coincidencias / longitud) * 100

    similitud = (
        coincidencias / longitud
    ) * 100

    # Retornamos:
    # cantidad de coincidencias
    # porcentaje de similitud
    return coincidencias, similitud


# ==========================================
# CREAR GRAFO
# ==========================================

# Se crea un grafo no dirigido
# porque la relación de similitud
# es mutua entre proteínas

G = nx.Graph()


# ==========================================
# TEMPORIZADOR
# ==========================================

# Guardamos el tiempo inicial
# para medir rendimiento

inicio = time.time()

print("\n===== GRAFO DE SIMILITUD =====\n")


# ==========================================
# ANALIZAR RELACIONES DEL DATASET
# ==========================================

# Recorremos las primeras 300 filas
# del dataset

# row representa una fila del CSV

for index, row in df.head(300).iterrows():

    # ======================================
    # OBTENER PROTEÍNAS
    # ======================================

    # Convertimos a string por seguridad

    proteina_1 = str(row["protein1"])

    proteina_2 = str(row["protein2"])

    # ======================================
    # COMPARACIÓN FUERZA BRUTA
    # ======================================

    coincidencias, similitud = comparar_secuencias(
        proteina_1,
        proteina_2
    )

    # ======================================
    # FILTRAR SIMILITUDES ALTAS
    # ======================================

    # Solo se conectan proteínas
    # con similitud mayor o igual a 50%

    if similitud >= 50:

        # ==================================
        # AGREGAR ARISTA AL GRAFO
        # ==================================

        # Se crea una conexión entre:
        # proteina_1 y proteina_2

        # weight almacena el porcentaje
        # de similitud

        G.add_edge(
            proteina_1,
            proteina_2,
            weight=similitud
        )

        # ==================================
        # MOSTRAR RESULTADOS
        # ==================================

        print(f"{proteina_1} ↔ {proteina_2}")

        print(f"Similitud: {similitud:.2f}%")

        print("-" * 40)


# ==========================================
# FIN DEL TEMPORIZADOR
# ==========================================

# Guardamos tiempo final

fin = time.time()

# Mostramos tiempo total
print("\nTiempo total:",
      round(fin - inicio, 4),
      "segundos")


# ==========================================
# INFORMACIÓN GENERAL DEL GRAFO
# ==========================================

print("\n===== INFORMACIÓN DEL GRAFO =====")

# Cantidad de nodos
print("Nodos:",
      G.number_of_nodes())

# Cantidad de aristas
print("Aristas:",
      G.number_of_edges())


# ==========================================
# VISUALIZACIÓN DEL GRAFO
# ==========================================

# Tamaño de ventana
plt.figure(figsize=(18, 18))


# ==========================================
# LAYOUT DEL GRAFO
# ==========================================

# spring_layout distribuye nodos
# usando simulación física

# k:
# controla separación entre nodos

# iterations:
# cantidad de iteraciones del algoritmo

pos = nx.spring_layout(
    G,
    k=1.8,
    iterations=100,
    seed=42
)


# ==========================================
# TAMAÑO DE NODOS
# ==========================================

# Mientras más conexiones tenga un nodo
# más grande será visualmente

node_sizes = [

    G.degree(n) * 250

    for n in G.nodes()

]


# ==========================================
# GROSOR DE ARISTAS
# ==========================================

# Mientras mayor sea la similitud
# más gruesa será la conexión

edge_widths = [

    d["weight"] / 20

    for _, _, d in G.edges(data=True)

]


# ==========================================
# DIBUJAR NODOS
# ==========================================

nx.draw_networkx_nodes(
    G,
    pos,

    # Tamaño de nodos
    node_size=node_sizes,

    # Transparencia
    alpha=0.9
)


# ==========================================
# DIBUJAR ARISTAS
# ==========================================

nx.draw_networkx_edges(
    G,
    pos,

    # Grosor
    width=edge_widths,

    # Transparencia
    alpha=0.4
)


# ==========================================
# MOSTRAR NOMBRES DE NODOS
# ==========================================

nx.draw_networkx_labels(
    G,
    pos,

    # Tamaño letra
    font_size=10,

    # Negrita
    font_weight="bold"
)


# ==========================================
# ETIQUETAS DE PESOS
# ==========================================

# Diccionario:
# (nodo1, nodo2) -> peso

edge_labels = {

    (u, v): f"{d['weight']:.0f}%"

    for u, v, d in G.edges(data=True)

}


# ==========================================
# DIBUJAR PESOS EN ARISTAS
# ==========================================

nx.draw_networkx_edge_labels(
    G,
    pos,

    edge_labels=edge_labels,

    font_size=8
)


# ==========================================
# TÍTULO
# ==========================================

plt.title(
    "Subgrafo de Similitud entre Proteínas",
    fontsize=22
)


# ==========================================
# OCULTAR EJES
# ==========================================

plt.axis("off")


# ==========================================
# MOSTRAR GRAFO
# ==========================================

plt.show()