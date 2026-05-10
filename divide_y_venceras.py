import pandas as pd
import matplotlib.pyplot as plt
import math

df = pd.read_csv("grafo_biologico_1500.csv")
interacciones = df.values.tolist()

def buscar_maximo_dyv(lista):
    if len(lista) == 1:
        return lista[0]

    medio = len(lista) // 2
    max_izq = buscar_maximo_dyv(lista[:medio])
    max_der = buscar_maximo_dyv(lista[medio:])

    return max_izq if max_izq[2] > max_der[2] else max_der

max_interaccion = buscar_maximo_dyv(interacciones)
p1_max, p2_max, peso_max = max_interaccion

print(f"D&V - Interacción más fuerte: {p1_max} y {p2_max} (Peso: {peso_max})")

vecinos_p1 = df[df['protein1'] == p1_max]['protein2'].tolist()[:5]
vecinos_p2 = df[df['protein2'] == p2_max]['protein1'].tolist()[:5]

nodos_subgrafo = list(set([p1_max, p2_max] + vecinos_p1 + vecinos_p2))

posiciones = {}
radio = 10
for i, nodo in enumerate(nodos_subgrafo):
    angulo = 2 * math.pi * i / len(nodos_subgrafo)
    posiciones[nodo] = (radio * math.cos(angulo), radio * math.sin(angulo))


plt.figure(figsize=(10, 8))

for u, v, w in interacciones:
    if u in posiciones and v in posiciones:
        x_coords = [posiciones[u][0], posiciones[v][0]]
        y_coords = [posiciones[u][1], posiciones[v][1]]

        # Resaltar la interacción máxima en rojo, las demás en gris
        es_la_maxima = (u == p1_max and v == p2_max) or (u == p2_max and v == p1_max)
        color = 'red' if es_la_maxima else 'lightgray'
        ancho = 4 if es_la_maxima else 1
        plt.plot(x_coords, y_coords, color=color, linewidth=ancho, zorder=1)

# Dibujar los nodos
for nodo, (x, y) in posiciones.items():
    color_nodo = 'orange' if (nodo == p1_max or nodo == p2_max) else 'skyblue'
    plt.scatter(x, y, s=800, color=color_nodo, edgecolors='black', zorder=2)
    plt.text(x, y, nodo, fontsize=9, ha='center', va='center', fontweight='bold')

plt.title(f"Subgrafo de la Interacción Máxima (D&V)\n{p1_max} <-> {p2_max}", fontsize=12)
plt.axis('off')
plt.show()
