#Este algoritmo aplica la técnica de Divide y Vencerás (Divide and Conquer) para encontrar la interacción biológica más fuerte dentro del dataset de proteínas.

#El programa divide recursivamente la lista de interacciones en partes más pequeñas hasta llegar a casos simples de un solo elemento. Luego, durante el proceso de retorno, compara los pesos de interacción y selecciona la conexión con el valor más alto.

#En el contexto del proyecto:
#cada nodo representa una proteína,
#cada arista representa una interacción biológica,
#y el peso representa la fuerza de interacción entre proteínas.
# ==========================================
# IMPORTACIÓN DE LIBRERÍAS
# ==========================================

# Pandas:
# Permite leer y manipular el CSV
import pandas as pd

# Matplotlib:
# Se utiliza para visualizar el subgrafo
import matplotlib.pyplot as plt

# Math:
# Se utiliza para cálculos circulares
import math


# ==========================================
# LEER DATASET
# ==========================================

# Se carga el archivo CSV

df = pd.read_csv("grafo_biologico_1500.csv")


# ==========================================
# CONVERTIR A LISTA
# ==========================================

# Cada elemento tendrá:
# [protein1, protein2, weight]

interacciones = df.values.tolist()


# ==========================================
# ALGORITMO DIVIDE Y VENCERÁS
# ==========================================

# Esta función encuentra la interacción
# con mayor peso utilizando recursión.

def buscar_maximo_dyv(lista):

    # ======================================
    # CASO BASE
    # ======================================

    # Si solo queda un elemento,
    # se retorna directamente

    if len(lista) == 1:

        return lista[0]


    # ======================================
    # DIVIDIR LISTA
    # ======================================

    # Se obtiene el punto medio

    medio = len(lista) // 2


    # ======================================
    # LLAMADAS RECURSIVAS
    # ======================================

    # Buscar máximo en mitad izquierda
    max_izq = buscar_maximo_dyv(
        lista[:medio]
    )

    # Buscar máximo en mitad derecha
    max_der = buscar_maximo_dyv(
        lista[medio:]
    )


    # ======================================
    # COMPARAR RESULTADOS
    # ======================================

    # El índice [2] representa el peso

    return max_izq if max_izq[2] > max_der[2] else max_der


# ==========================================
# EJECUTAR ALGORITMO
# ==========================================

max_interaccion = buscar_maximo_dyv(
    interacciones
)


# ==========================================
# GUARDAR RESULTADO
# ==========================================

# protein1, protein2, peso

p1_max, p2_max, peso_max = max_interaccion


# ==========================================
# MOSTRAR RESULTADO
# ==========================================

print(
    f"D&V - Interacción más fuerte:"
    f" {p1_max} y {p2_max}"
    f" (Peso: {peso_max})"
)


# ==========================================
# BUSCAR VECINOS RELACIONADOS
# ==========================================

# Se buscan proteínas conectadas
# con la proteína principal

vecinos_p1 = df[
    df['protein1'] == p1_max
]['protein2'].tolist()[:5]


vecinos_p2 = df[
    df['protein2'] == p2_max
]['protein1'].tolist()[:5]


# ==========================================
# CREAR SUBGRAFO
# ==========================================

# Se unen:
# proteínas principales + vecinos

nodos_subgrafo = list(set(
    [p1_max, p2_max]
    +
    vecinos_p1
    +
    vecinos_p2
))


# ==========================================
# POSICIONES CIRCULARES
# ==========================================

# Diccionario:
# nodo -> coordenadas

posiciones = {}

# Radio del círculo
radio = 10


# ==========================================
# DISTRIBUIR NODOS
# ==========================================

for i, nodo in enumerate(nodos_subgrafo):

    # Ángulo del nodo
    angulo = (
        2 * math.pi * i
        /
        len(nodos_subgrafo)
    )

    # Coordenadas (x,y)
    posiciones[nodo] = (
        radio * math.cos(angulo),
        radio * math.sin(angulo)
    )


# ==========================================
# CREAR FIGURA
# ==========================================

plt.figure(figsize=(10, 8))


# ==========================================
# DIBUJAR ARISTAS
# ==========================================

for u, v, w in interacciones:

    # Solo conexiones del subgrafo
    if u in posiciones and v in posiciones:

        # Coordenadas X
        x_coords = [
            posiciones[u][0],
            posiciones[v][0]
        ]

        # Coordenadas Y
        y_coords = [
            posiciones[u][1],
            posiciones[v][1]
        ]


        # ==================================
        # RESALTAR INTERACCIÓN MÁXIMA
        # ==================================

        es_la_maxima = (
            (u == p1_max and v == p2_max)
            or
            (u == p2_max and v == p1_max)
        )

        # Color especial
        color = 'red' if es_la_maxima else 'lightgray'

        # Grosor especial
        ancho = 4 if es_la_maxima else 1


        # ==================================
        # DIBUJAR ARISTA
        # ==================================

        plt.plot(
            x_coords,
            y_coords,

            color=color,

            linewidth=ancho,

            zorder=1
        )


# ==========================================
# DIBUJAR NODOS
# ==========================================

for nodo, (x, y) in posiciones.items():

    # Resaltar nodos principales
    color_nodo = (
        'orange'
        if (
            nodo == p1_max
            or
            nodo == p2_max
        )
        else 'skyblue'
    )

    # Dibujar nodo
    plt.scatter(
        x,
        y,

        s=800,

        color=color_nodo,

        edgecolors='black',

        zorder=2
    )

    # Mostrar nombre
    plt.text(
        x,
        y,

        nodo,

        fontsize=9,

        ha='center',

        va='center',

        fontweight='bold'
    )


# ==========================================
# TÍTULO
# ==========================================

plt.title(
    f"Subgrafo de la Interacción Máxima (D&V)\n"
    f"{p1_max} <-> {p2_max}",

    fontsize=12
)


# ==========================================
# OCULTAR EJES
# ==========================================

plt.axis('off')


# ==========================================
# MOSTRAR GRAFO
# ==========================================

plt.show()