#Este algoritmo implementa la técnica de Strongly Connected Components (SCC) utilizando el algoritmo de Tarjan para detectar componentes fuertemente conectados dentro de una red biológica.
#En el contexto del proyecto:
# cada nodo representa una proteína,
# y cada arista representa una interacción biológica entre proteínas.
# El objetivo principal es identificar grupos de proteínas que se encuentren fuertemente relacionadas entre sí mediante caminos bidireccionales dentro del grafo. Estos grupos pueden representar módulos funcionales o ciclos biológicos importantes dentro de la red proteica

# ==========================================
# IMPORTACIÓN DE LIBRERÍAS
# ==========================================

# Pandas:
# Permite leer y manipular el archivo CSV
import pandas as pd

# Sys:
# Se utiliza para aumentar el límite
# de recursividad de Python
import sys

# Matplotlib:
# Permite visualizar el grafo
import matplotlib.pyplot as plt

# Math:
# Se utiliza para cálculos matemáticos
# en la distribución circular
import math


# ==========================================
# AUMENTAR LÍMITE DE RECURSIVIDAD
# ==========================================

# El algoritmo SCC usa recursión profunda.
# Aumentamos el límite para evitar errores.

sys.setrecursionlimit(5000)


# ==========================================
# LEER DATASET
# ==========================================

# Se carga el archivo CSV que contiene:
# protein1 | protein2 | weight

df = pd.read_csv("grafo_biologico_1500.csv")


# ==========================================
# CREAR LISTA DE ADYACENCIA
# ==========================================

# La lista de adyacencia representa
# el grafo dirigido.

# Formato:
# nodo -> vecinos

adj = {}

# Recorremos todas las filas del dataset
for u, v, _ in df.values:

    # Si el nodo no existe
    # se crea una lista vacía
    if u not in adj:
        adj[u] = []

    # Agregar conexión:
    # u -> v
    adj[u].append(v)

    # Asegurar que v exista
    # aunque no tenga salidas
    if v not in adj:
        adj[v] = []


# ==========================================
# ALGORITMO SCC (TARJAN)
# ==========================================

# Esta función detecta componentes
# fuertemente conectados en un grafo.

def algoritmo_scc(grafo):

    # Índice global del DFS
    indice = 0

    # Pila utilizada por Tarjan
    stack = []

    # Diccionario:
    # indica si un nodo está en la pila
    on_stack = {u: False for u in grafo}

    # Índice de descubrimiento
    indices = {u: -1 for u in grafo}

    # Lowlink:
    # nodo más bajo alcanzable
    lowlink = {u: -1 for u in grafo}

    # Resultado final:
    # lista de componentes SCC
    resultado = []


    # ======================================
    # DFS RECURSIVO
    # ======================================

    def fuerte_conexion(v):

        nonlocal indice

        # Asignar índice inicial
        indices[v] = lowlink[v] = indice

        indice += 1

        # Insertar nodo en pila
        stack.append(v)

        on_stack[v] = True


        # ==================================
        # RECORRER VECINOS
        # ==================================

        for w in grafo.get(v, []):

            # Nodo no visitado
            if indices[w] == -1:

                # DFS recursivo
                fuerte_conexion(w)

                # Actualizar lowlink
                lowlink[v] = min(
                    lowlink[v],
                    lowlink[w]
                )

            # Si el vecino está en pila
            elif on_stack[w]:

                lowlink[v] = min(
                    lowlink[v],
                    indices[w]
                )


        # ==================================
        # ENCONTRAR COMPONENTE SCC
        # ==================================

        # Si el nodo es raíz SCC
        if lowlink[v] == indices[v]:

            componente = []

            while True:

                # Sacar nodo de pila
                nodo = stack.pop()

                on_stack[nodo] = False

                componente.append(nodo)

                # Terminar SCC
                if nodo == v:
                    break

            # Guardar componente
            resultado.append(componente)


    # ======================================
    # RECORRER TODOS LOS NODOS
    # ======================================

    for n in grafo:

        # Si no fue visitado
        if indices[n] == -1:

            fuerte_conexion(n)


    # Retornar SCC encontrados
    return resultado


# ==========================================
# EJECUTAR ALGORITMO SCC
# ==========================================

sccs_detectados = algoritmo_scc(adj)


# ==========================================
# MOSTRAR RESULTADOS
# ==========================================

print(f"Total de componentes (SCC): {len(sccs_detectados)}")


# ==========================================
# FILTRAR CICLOS
# ==========================================

# Un SCC con más de 1 nodo
# representa un ciclo biológico

ciclos = [

    s for s in sccs_detectados

    if len(s) > 1

]

print(f"Ciclos biológicos encontrados: {len(ciclos)}")


# ==========================================
# VISUALIZAR COMPONENTE MÁS GRANDE
# ==========================================

if ciclos:

    # Tomar SCC más grande
    scc_ver = max(ciclos, key=len)[:20]

    # Convertir a conjunto
    n_set = set(scc_ver)


    # ======================================
    # POSICIONES CIRCULARES
    # ======================================

    # Se distribuyen nodos
    # formando un círculo

    pos = {}

    r = 10

    for i, nodo in enumerate(scc_ver):

        # Ángulo circular
        a = 2 * math.pi * i / len(scc_ver)

        # Coordenadas
        pos[nodo] = (
            r * math.cos(a),
            r * math.sin(a)
        )


    # ======================================
    # CREAR FIGURA
    # ======================================

    plt.figure(figsize=(10, 10))


    # ======================================
    # FILTRAR SOLO NODOS DEL SCC
    # ======================================

    df_plot = df[
        df['protein1'].isin(n_set)
        &
        df['protein2'].isin(n_set)
    ]


    # ======================================
    # DIBUJAR ARISTAS
    # ======================================

    for u, v in zip(
        df_plot['protein1'],
        df_plot['protein2']
    ):

        plt.plot(
            [pos[u][0], pos[v][0]],
            [pos[u][1], pos[v][1]],

            color='gray',
            alpha=0.5
        )


    # ======================================
    # DIBUJAR NODOS
    # ======================================

    for n, (x, y) in pos.items():

        plt.scatter(
            x,
            y,

            s=700,

            color='#5DADE2',

            edgecolors='black'
        )

        # Nombre del nodo
        plt.text(
            x,
            y,

            n,

            fontsize=8,

            ha='center',

            va='center',

            fontweight='bold'
        )


    # ======================================
    # TÍTULO
    # ======================================

    plt.title(
        "Visualización del Algoritmo SCC "
    )


    # ======================================
    # OCULTAR EJES
    # ======================================

    plt.axis('off')


    # ======================================
    # MOSTRAR GRAFO
    # ======================================

    plt.show()