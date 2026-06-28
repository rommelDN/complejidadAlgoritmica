#Este algoritmo utiliza la técnica de backtracking para explorar diferentes posibilidades de alineamiento entre dos secuencias biológicas. A partir de las secuencias "RFC2" y "RFC4",
#el programa genera múltiples caminos posibles de alineación mediante decisiones recursivas, permitiendo
#alinear caracteres directamente,
#insertar espacios (-) en una secuencia,
#o probar distintas combinaciones posibles.
#Cada decisión genera una nueva rama dentro de un árbol de exploración, lo que permite representar visualmente el funcionamiento del algoritmo de backtracking.
#El programa construye un grafo dirigido utilizando la librería NetworkX, donde:cada nodo representa un estado parcial del alineamiento,y cada arista representa una decisión tomada por el algoritmo durante la exploració

# ==========================================
# IMPORTACIÓN DE LIBRERÍAS
# ==========================================

# NetworkX:
# Se utiliza para crear y manipular grafos
import networkx as nx

# Matplotlib:
# Permite visualizar el grafo generado
import matplotlib.pyplot as plt


# ==========================================
# CREAR GRAFO DIRIGIDO
# ==========================================

# DiGraph():
# Crea un grafo dirigido

# Se usa dirigido porque el algoritmo
# sigue una dirección en la exploración
# de decisiones del backtracking

G = nx.DiGraph()


# ==========================================
# CONTADOR GLOBAL
# ==========================================

# Esta variable sirve para asignar
# IDs únicos a cada nodo del árbol

contador = 0


# ==========================================
# FUNCIÓN BACKTRACKING
# ==========================================

# Esta función explora múltiples caminos
# posibles para alinear dos secuencias.

# Parámetros:

# seq1, seq2:
# secuencias a comparar

# i, j:
# posiciones actuales en cada secuencia

# alineacion1, alineacion2:
# almacenan el alineamiento parcial

# padre:
# nodo anterior en el árbol

# profundidad:
# nivel actual de recursión

# max_profundidad:
# límite del árbol para evitar
# demasiados nodos

def backtracking_graph(
    seq1,
    seq2,
    i=0,
    j=0,
    alineacion1="",
    alineacion2="",
    padre=None,
    profundidad=0,
    max_profundidad=4
):

    # ======================================
    # USAR VARIABLE GLOBAL
    # ======================================

    global contador


    # ======================================
    # LIMITAR PROFUNDIDAD
    # ======================================

    # Si la profundidad supera
    # el límite establecido,
    # se detiene la recursión

    if profundidad > max_profundidad:
        return


    # ======================================
    # CREAR NODO ACTUAL
    # ======================================

    # Cada nodo representa
    # un estado parcial del alineamiento

    nodo_actual = contador

    # Aumentar contador para el siguiente nodo
    contador += 1


    # ======================================
    # ETIQUETA DEL NODO
    # ======================================

    # La etiqueta mostrará:
    # alineación parcial superior
    # alineación parcial inferior

    etiqueta = f"{alineacion1}\n{alineacion2}"


    # ======================================
    # AGREGAR NODO AL GRAFO
    # ======================================

    G.add_node(
        nodo_actual,

        # Texto mostrado en pantalla
        label=etiqueta
    )


    # ======================================
    # CONECTAR CON EL PADRE
    # ======================================

    # Si existe un nodo padre,
    # se crea una arista entre ambos

    if padre is not None:

        G.add_edge(
            padre,
            nodo_actual
        )


    # ======================================
    # CASO BASE
    # ======================================

    # Si ambas secuencias terminaron,
    # se detiene la exploración

    if i == len(seq1) and j == len(seq2):
        return


    # ======================================
    # OPCIÓN 1: MATCH DIRECTO
    # ======================================

    # Se alinean caracteres directamente

    if i < len(seq1) and j < len(seq2):

        backtracking_graph(

            # Secuencias originales
            seq1,
            seq2,

            # Avanzar ambas posiciones
            i + 1,
            j + 1,

            # Agregar caracteres actuales
            alineacion1 + seq1[i],
            alineacion2 + seq2[j],

            # Nodo actual será el padre
            nodo_actual,

            # Aumentar profundidad
            profundidad + 1,

            # Mantener límite
            max_profundidad
        )


    # ======================================
    # OPCIÓN 2: GAP EN SEQ2
    # ======================================

    # Se agrega un espacio "-"
    # en la segunda secuencia

    if i < len(seq1):

        backtracking_graph(

            seq1,
            seq2,

            # Solo avanza seq1
            i + 1,
            j,

            # Agregar carácter normal
            alineacion1 + seq1[i],

            # Agregar gap
            alineacion2 + "-",

            nodo_actual,

            profundidad + 1,

            max_profundidad
        )


    # ======================================
    # OPCIÓN 3: GAP EN SEQ1
    # ======================================

    # Se agrega un espacio "-"
    # en la primera secuencia

    if j < len(seq2):

        backtracking_graph(

            seq1,
            seq2,

            # Solo avanza seq2
            i,
            j + 1,

            # Gap en secuencia 1
            alineacion1 + "-",

            # Carácter normal
            alineacion2 + seq2[j],

            nodo_actual,

            profundidad + 1,

            max_profundidad
        )


# ==========================================
# EJECUCIÓN DEL ALGORITMO
# ==========================================

# Secuencias de prueba

seq1 = "RFC2"
seq2 = "RFC4"


# ==========================================
# INICIAR BACKTRACKING
# ==========================================

# max_profundidad = 3
# limita el tamaño del árbol

backtracking_graph(
    seq1,
    seq2,
    max_profundidad=3
)


# ==========================================
# VISUALIZACIÓN
# ==========================================

# Tamaño de la ventana

plt.figure(figsize=(18, 12))


# ==========================================
# DISTRIBUCIÓN DEL GRAFO
# ==========================================

# spring_layout organiza los nodos
# usando simulación física

pos = nx.spring_layout(
    G,

    # Distancia entre nodos
    k=2,

    # Iteraciones del algoritmo
    iterations=100,

    # Semilla fija
    seed=42
)


# ==========================================
# OBTENER ETIQUETAS
# ==========================================

# Obtiene los labels almacenados
# en cada nodo

labels = nx.get_node_attributes(
    G,
    "label"
)


# ==========================================
# DIBUJAR NODOS
# ==========================================

nx.draw_networkx_nodes(
    G,
    pos,

    # Tamaño nodos
    node_size=2500,

    # Transparencia
    alpha=0.9
)


# ==========================================
# DIBUJAR ARISTAS
# ==========================================

nx.draw_networkx_edges(
    G,
    pos,

    # Mostrar flechas
    arrows=True,

    # Transparencia
    alpha=0.5
)


# ==========================================
# DIBUJAR LABELS
# ==========================================

nx.draw_networkx_labels(
    G,
    pos,

    labels,

    # Tamaño letra
    font_size=8
)


# ==========================================
# TÍTULO
# ==========================================

plt.title(
    "Subgrafo del Árbol de Backtracking",
    fontsize=20
)


# ==========================================
# OCULTAR EJES
# ==========================================

plt.axis("off")


# ==========================================
# MOSTRAR GRAFO
# ==========================================

plt.show()