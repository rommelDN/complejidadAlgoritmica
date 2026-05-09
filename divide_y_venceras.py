import pandas as pd

df = pd.read_csv("grafo_biologico_1500.csv")
interacciones = df.values.tolist()  # [protein1, protein2, weight]


def buscar_maximo_dyv(lista):
    # Caso base: un solo elemento
    if len(lista) == 1:
        return lista[0]

    # DIVIDE
    medio = len(lista) // 2
    parte_izq = lista[:medio]
    parte_der = lista[medio:]

    # VENCER (Recursión)
    max_izq = buscar_maximo_dyv(parte_izq)
    max_der = buscar_maximo_dyv(parte_der)

    # COMBINA (Comparar pesos en el índice 2)
    if max_izq[2] > max_der[2]:
        return max_izq
    else:
        return max_der


# Ejecución
max_interaccion = buscar_maximo_dyv(interacciones)
print(f"D&V - Interacción más fuerte: {max_interaccion[0]} y {max_interaccion[1]} (Peso: {max_interaccion[2]})")