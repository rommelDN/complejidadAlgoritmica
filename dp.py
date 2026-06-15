# ==========================================
# DP — NEEDLEMAN-WUNSCH
# Alineamiento global óptimo de proteínas
# ==========================================

# Needleman-Wunsch es el algoritmo clásico
# de programación dinámica para alineamiento
# GLOBAL de secuencias biológicas.

# A diferencia del algoritmo voraz, este
# garantiza el alineamiento ÓPTIMO porque
# considera todas las posibles combinaciones
# mediante una tabla de puntuaciones.

# Fases del algoritmo:
# 1. INICIALIZACIÓN: llenar bordes con gaps
# 2. LLENADO: completar la tabla DP
# 3. TRACEBACK: reconstruir el alineamiento
#    óptimo siguiendo las flechas de decisión

# En el proyecto:
# Se alinean nombres/IDs de proteínas del
# dataset NIH para encontrar la similitud
# óptima entre pares de secuencias.

# ==========================================
# IMPORTACIÓN DE LIBRERÍAS
# ==========================================

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np


# ==========================================
# LEER DATASET
# ==========================================

df = pd.read_csv("grafo_biologico_1500.csv")


# ==========================================
# PARÁMETROS DE PUNTUACIÓN
# ==========================================

MATCH    =  2     # caracteres iguales
MISMATCH = -1     # caracteres distintos
GAP      = -2     # penalización por gap


# ==========================================
# ALGORITMO NEEDLEMAN-WUNSCH
# ==========================================

def needleman_wunsch(seq1, seq2):

    n = len(seq1)
    m = len(seq2)

    # ======================================
    # CREAR TABLA DP
    # ======================================

    # dp[i][j] = mejor score para alinear
    # seq1[:i] con seq2[:j]

    dp = [[0] * (m + 1) for _ in range(n + 1)]


    # ======================================
    # FASE 1: INICIALIZACIÓN
    # ======================================

    # Llenar primera columna con gaps
    for i in range(n + 1):
        dp[i][0] = i * GAP

    # Llenar primera fila con gaps
    for j in range(m + 1):
        dp[0][j] = j * GAP


    # ======================================
    # FASE 2: LLENADO DE LA TABLA
    # ======================================

    for i in range(1, n + 1):
        for j in range(1, m + 1):

            # Puntuación de match/mismatch
            score_diag = (
                MATCH if seq1[i-1] == seq2[j-1]
                else MISMATCH
            )

            # Las tres opciones posibles
            diagonal = dp[i-1][j-1] + score_diag
            arriba   = dp[i-1][j]   + GAP
            izquierda = dp[i][j-1]  + GAP

            # Tomar el máximo (decisión óptima)
            dp[i][j] = max(diagonal, arriba, izquierda)


    # ======================================
    # FASE 3: TRACEBACK
    # ======================================

    alin1 = []
    alin2 = []
    i, j  = n, m

    while i > 0 or j > 0:

        if i > 0 and j > 0:
            score_diag = (
                MATCH if seq1[i-1] == seq2[j-1]
                else MISMATCH
            )

            # Vino de la diagonal
            if dp[i][j] == dp[i-1][j-1] + score_diag:
                alin1.append(seq1[i-1])
                alin2.append(seq2[j-1])
                i -= 1
                j -= 1

            # Vino de arriba (gap en seq2)
            elif dp[i][j] == dp[i-1][j] + GAP:
                alin1.append(seq1[i-1])
                alin2.append('-')
                i -= 1

            # Vino de la izquierda (gap en seq1)
            else:
                alin1.append('-')
                alin2.append(seq2[j-1])
                j -= 1

        elif i > 0:
            alin1.append(seq1[i-1])
            alin2.append('-')
            i -= 1

        else:
            alin1.append('-')
            alin2.append(seq2[j-1])
            j -= 1

    # Invertir (traceback va de atrás hacia adelante)
    alin1.reverse()
    alin2.reverse()

    return dp, ''.join(alin1), ''.join(alin2), dp[n][m]


# ==========================================
# SELECCIONAR PARES REPRESENTATIVOS
# ==========================================

pares_analizar = [
    (str(df.iloc[i]['protein1']), str(df.iloc[i]['protein2']))
    for i in range(min(20, len(df)))
]


# ==========================================
# EJECUTAR NW SOBRE PARES
# ==========================================

resultados = []

for p1, p2 in pares_analizar:
    dp_tabla, a1, a2, score = needleman_wunsch(p1, p2)

    matches    = sum(1 for x, y in zip(a1, a2) if x == y and x != '-')
    gaps       = a1.count('-') + a2.count('-')
    identidad  = matches / max(len(a1), 1) * 100

    resultados.append({
        'p1': p1, 'p2': p2,
        'alin1': a1, 'alin2': a2,
        'score': score,
        'matches': matches,
        'gaps': gaps,
        'identidad': identidad,
        'tabla': dp_tabla
    })


# ==========================================
# MOSTRAR RESULTADOS
# ==========================================

print("=" * 55)
print("DP — Needleman-Wunsch (Alineamiento Global)")
print("=" * 55)

resultados_ord = sorted(
    resultados, key=lambda x: x['score'], reverse=True
)

print(f"\n{'Proteína 1':12s} {'Proteína 2':12s} {'Score':>6} {'Id%':>6} {'M':>4} {'Gaps':>5}")
print("-" * 55)

for r in resultados_ord[:10]:
    print(
        f"{r['p1']:12s} {r['p2']:12s} "
        f"{r['score']:>6} {r['identidad']:>5.1f}% "
        f"{r['matches']:>4} {r['gaps']:>5}"
    )

mejor = resultados_ord[0]
print(f"\nMejor alineamiento NW:")
print(f"  {mejor['p1']} vs {mejor['p2']}")
print(f"  Seq1: {mejor['alin1']}")
print(f"  Seq2: {mejor['alin2']}")
print(f"  Score óptimo: {mejor['score']}  |  Identidad: {mejor['identidad']:.1f}%")


# ==========================================
# VISUALIZACIÓN — TABLA DP DEL MEJOR PAR
# ==========================================

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# --- Gráfico 1: Tabla DP ---
tabla_np = np.array(mejor['tabla'])

im = ax1.imshow(
    tabla_np, cmap='YlGn', aspect='auto'
)
plt.colorbar(im, ax=ax1, shrink=0.8)

ax1.set_xticks(range(len(mejor['p2']) + 1))
ax1.set_xticklabels(['-'] + list(mejor['p2']), fontsize=9)
ax1.set_yticks(range(len(mejor['p1']) + 1))
ax1.set_yticklabels(['-'] + list(mejor['p1']), fontsize=9)

# Mostrar valores en la tabla si es pequeña
if tabla_np.shape[0] <= 10 and tabla_np.shape[1] <= 10:
    for i in range(tabla_np.shape[0]):
        for j in range(tabla_np.shape[1]):
            ax1.text(j, i, str(tabla_np[i, j]),
                     ha='center', va='center', fontsize=8)

ax1.set_title(
    f"Tabla DP: {mejor['p1']} vs {mejor['p2']}",
    fontweight='bold'
)
ax1.set_xlabel("Secuencia 2")
ax1.set_ylabel("Secuencia 1")

# --- Gráfico 2: Scores de todos los pares ---
scores  = [r['score'] for r in resultados_ord]
pares   = [f"{r['p1'][:5]}↔{r['p2'][:5]}" for r in resultados_ord]
colores = ['#5DCAA5' if s >= 0 else '#D85A30' for s in scores]

ax2.barh(range(len(scores)), scores,
         color=colores, edgecolor='white', linewidth=0.5)
ax2.set_yticks(range(len(pares)))
ax2.set_yticklabels(pares, fontsize=8)
ax2.set_xlabel("Score NW óptimo")
ax2.set_title("Scores Needleman-Wunsch por par", fontweight='bold')
ax2.axvline(0, color='black', linewidth=0.8, linestyle='--')

plt.suptitle(
    "DP — Needleman-Wunsch · Alineamiento Global Óptimo",
    fontsize=13, fontweight='bold'
)
plt.tight_layout()
plt.show()