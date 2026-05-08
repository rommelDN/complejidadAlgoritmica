import pandas as pd
import time

# ==========================================
# LEER DATASET
# ==========================================
df = pd.read_csv("grafo_biologico_1500.csv")

# ==========================================
# FUNCIÓN FUERZA BRUTA
# ==========================================

def comprar_secuencias(seq1,seq2):
    coincidencias = 0
    longitud = min(len(seq1),len(seq2))

    for i in range(longitud):
        if seq1[i]==seq2[i]:
            coincidencias += 1
    similitud = (coincidencias/longitud)*100

    return coincidencias,similitud

# ==========================================
# INICIO TEMPORIZADOR
# ==========================================

inicio = time.time()

# ==========================================
# ANALIZAMOS PRIMERAS 20 RELACIONES
# ==========================================
print("\n===== COMPARACIÓN FUERZA BRUTA =====\n")
# for index,row in df.iterrows():
# for index,row in df.head(20).iterrows():
for index,row in df.head(1000).iterrows():
    proteina_1=row["protein1"]
    proteina_2=row["protein2"]

    coincidencias,similitud = comprar_secuencias(
        proteina_1,
        proteina_2
    )

    print(f"Protenina 1: {proteina_1}")
    print(f"Protenina 2: {proteina_2}")

    print(f"Coincidencias: {coincidencias}")
    print(f"Similitud: {similitud}")
    print("-" * 40)

# ==========================================
# FIN TEMPORIZADOR
# ==========================================

fin = time.time()

print("\nTiempo total:",
      round(fin - inicio, 6),
      "segundos")



