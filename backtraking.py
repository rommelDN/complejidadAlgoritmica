import networkx as nx
import matplotlib.pyplot as plt

# ==========================================
# GRAFO
# ==========================================

G = nx.DiGraph()

contador = 0

# ==========================================
# BACKTRACKING LIMITADO
# ==========================================

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

    global contador

    # ======================================
    # LIMITAR PROFUNDIDAD
    # ======================================

    if profundidad > max_profundidad:
        return

    # ======================================
    # CREAR NODO
    # ======================================

    nodo_actual = contador

    contador += 1

    etiqueta = f"{alineacion1}\n{alineacion2}"

    G.add_node(
        nodo_actual,
        label=etiqueta
    )

    # ======================================
    # CONECTAR
    # ======================================

    if padre is not None:

        G.add_edge(
            padre,
            nodo_actual
        )

    # ======================================
    # CASO BASE
    # ======================================

    if i == len(seq1) and j == len(seq2):
        return

    # ======================================
    # MATCH
    # ======================================

    if i < len(seq1) and j < len(seq2):

        backtracking_graph(
            seq1,
            seq2,
            i + 1,
            j + 1,
            alineacion1 + seq1[i],
            alineacion2 + seq2[j],
            nodo_actual,
            profundidad + 1,
            max_profundidad
        )

    # ======================================
    # GAP EN SEQ2
    # ======================================

    if i < len(seq1):

        backtracking_graph(
            seq1,
            seq2,
            i + 1,
            j,
            alineacion1 + seq1[i],
            alineacion2 + "-",
            nodo_actual,
            profundidad + 1,
            max_profundidad
        )

    # ======================================
    # GAP EN SEQ1
    # ======================================

    if j < len(seq2):

        backtracking_graph(
            seq1,
            seq2,
            i,
            j + 1,
            alineacion1 + "-",
            alineacion2 + seq2[j],
            nodo_actual,
            profundidad + 1,
            max_profundidad
        )

# ==========================================
# EJECUTAR
# ==========================================

seq1 = "RFC2"
seq2 = "RFC4"

backtracking_graph(
    seq1,
    seq2,
    max_profundidad=3
)

# ==========================================
# VISUALIZACIÓN
# ==========================================

plt.figure(figsize=(18, 12))

# Layout jerárquico simple
pos = nx.spring_layout(
    G,
    k=2,
    iterations=100,
    seed=42
)

# Labels
labels = nx.get_node_attributes(
    G,
    "label"
)

# Dibujar nodos
nx.draw_networkx_nodes(
    G,
    pos,
    node_size=2500,
    alpha=0.9
)

# Dibujar aristas
nx.draw_networkx_edges(
    G,
    pos,
    arrows=True,
    alpha=0.5
)

# Dibujar labels
nx.draw_networkx_labels(
    G,
    pos,
    labels,
    font_size=8
)

plt.title(
    "Subgrafo del Árbol de Backtracking",
    fontsize=20
)

plt.axis("off")

plt.show()