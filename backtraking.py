import pandas as pd
import time

# ==========================================
# LEER DATASET
# ==========================================

df = pd.read_csv("grafo_biologico_1500.csv")

# ==========================================
# BACKTRACKING ALIGNMENT
# ==========================================

def backtracking_alignment(seq1, seq2,
                           i=0, j=0,
                           alineacion1="",
                           alineacion2=""):

    # Caso base
    if i == len(seq1) and j == len(seq2):

        return [(alineacion1, alineacion2)]

    resultados = []

    # ======================================
    # Coincidencia directa
    # ======================================

    if i < len(seq1) and j < len(seq2):

        resultados.extend(

            backtracking_alignment(
                seq1,
                seq2,
                i + 1,
                j + 1,
                alineacion1 + seq1[i],
                alineacion2 + seq2[j]
            )

        )

    # ======================================
    # Insertar espacio en seq2
    # ======================================

    if i < len(seq1):

        resultados.extend(

            backtracking_alignment(
                seq1,
                seq2,
                i + 1,
                j,
                alineacion1 + seq1[i],
                alineacion2 + "-"
            )

        )

    # ======================================
    # Insertar espacio en seq1
    # ======================================

    if j < len(seq2):

        resultados.extend(

            backtracking_alignment(
                seq1,
                seq2,
                i,
                j + 1,
                alineacion1 + "-",
                alineacion2 + seq2[j]
            )

        )

    return resultados

# ==========================================
# INICIO
# ==========================================

inicio = time.time()

print("\n===== BACKTRACKING ALIGNMENT =====\n")

# ==========================================
# ANALIZAR SOLO ALGUNOS EJEMPLOS
# ==========================================

for index, row in df.head(3).iterrows():

    seq1 = str(row["protein1"])

    seq2 = str(row["protein2"])

    print(f"\nSecuencia 1: {seq1}")
    print(f"Secuencia 2: {seq2}")

    alineamientos = backtracking_alignment(
        seq1,
        seq2
    )

    print("\nPrimeros 5 alineamientos encontrados:\n")

    for a1, a2 in alineamientos[:5]:

        print(a1)
        print(a2)
        print()

# ==========================================
# FIN
# ==========================================

fin = time.time()

print("Tiempo total:",
      round(fin - inicio, 4),
      "segundos")