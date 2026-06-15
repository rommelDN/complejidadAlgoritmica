# ==========================================
# VORAZ — ALINEAMIENTO HEURÍSTICO
# Greedy de proteínas por similitud
# ==========================================

# Este algoritmo aplica una estrategia
# voraz (greedy) para alinear secuencias
# de proteínas de forma heurística.

# La lógica greedy es:
# en cada posición del alineamiento,
# tomar la decisión LOCALMENTE ÓPTIMA:
# → si los caracteres coinciden: match (+2)
# → si no coinciden: mismatch (-1)
# → si hay gap necesario: penalización (-2)

# A diferencia de Needleman-Wunsch (DP),
# el algoritmo voraz NO garantiza el óptimo
# global, pero es mucho más rápido y sirve
# como heurística de alineamiento inicial.

# Sobre el dataset:
# Se toman pares de proteínas del CSV y
# se alinean vorazmente sus nombres/IDs
# para detectar similitudes estructurales.

# ==========================================
# IMPORTACIÓN DE LIBRERÍAS
# ==========================================

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


# ==========================================
# LEER DATASET
# ==========================================

df = pd.read_csv("grafo_biologico_1500.csv")


# ==========================================
# PARÁMETROS DE PUNTUACIÓN
# ==========================================

MATCH    =  2    # caracteres iguales
MISMATCH = -1    # caracteres distintos
GAP      = -2    # espacio insertado


# ==========================================
# ALGORITMO VORAZ
# ==========================================

def alineamiento_voraz(seq1, seq2):

    alin1  = []
    alin2  = []
    score  = 0
    i, j   = 0, 0
    ops    = []    # operaciones realizadas

    while i < len(seq1) and j < len(seq2):

        # ====================================
        # DECISIÓN LOCAL ÓPTIMA
        # ====================================

        # Opción A: match / mismatch
        if seq1[i] == seq2[j]:
            alin1.append(seq1[i])
            alin2.append(seq2[j])
            score += MATCH
            ops.append('M')     # Match
        else:
            # Opción B: greedy elige mismatch
            # antes que gap (penalización menor)
            alin1.append(seq1[i])
            alin2.append(seq2[j])
            score += MISMATCH
            ops.append('X')     # Mismatch

        i += 1
        j += 1

    # ====================================
    # MANEJAR RESIDUOS
    # ====================================

    # Si seq1 es más larga
    while i < len(seq1):
        alin1.append(seq1[i])
        alin2.append('-')
        score += GAP
        ops.append('G')
        i += 1

    # Si seq2 es más larga
    while j < len(seq2):
        alin1.append('-')
        alin2.append(seq2[j])
        score += GAP
        ops.append('G')
        j += 1

    return ''.join(alin1), ''.join(alin2), score, ops


# ==========================================
# APLICAR A PARES DEL DATASET
# ==========================================

resultados = []

# Analizar primeras 50 filas del CSV
for _, row in df.head(50).iterrows():
    p1 = str(row['protein1'])
    p2 = str(row['protein2'])

    a1, a2, score, ops = alineamiento_voraz(p1, p2)

    matches   = ops.count('M')
    mismatches = ops.count('X')
    gaps      = ops.count('G')
    longitud  = len(ops)
    identidad = (matches / longitud * 100) if longitud > 0 else 0

    resultados.append({
        'p1': p1, 'p2': p2,
        'alin1': a1, 'alin2': a2,
        'score': score,
        'matches': matches,
        'mismatches': mismatches,
        'gaps': gaps,
        'identidad': identidad
    })


# ==========================================
# MOSTRAR RESULTADOS
# ==========================================

print("=" * 55)
print("VORAZ — Alineamiento Heurístico de Proteínas")
print("=" * 55)

# Ordenar por score descendente
resultados_ord = sorted(
    resultados, key=lambda x: x['score'], reverse=True
)

print("\nTop 10 mejores alineamientos:\n")
print(f"{'Proteína 1':12s} {'Proteína 2':12s} {'Score':>6} {'Id%':>6} {'M':>4} {'X':>4} {'G':>4}")
print("-" * 55)

for r in resultados_ord[:10]:
    print(
        f"{r['p1']:12s} {r['p2']:12s} "
        f"{r['score']:>6} {r['identidad']:>5.1f}% "
        f"{r['matches']:>4} {r['mismatches']:>4} {r['gaps']:>4}"
    )

print("\nLeyenda: M=Match  X=Mismatch  G=Gap")

# Mostrar el mejor alineamiento detallado
mejor = resultados_ord[0]
print(f"\nMejor alineamiento detallado:")
print(f"  Seq1: {mejor['alin1']}")
print(f"  Seq2: {mejor['alin2']}")
print(f"  Score: {mejor['score']}  |  Identidad: {mejor['identidad']:.1f}%")


# ==========================================
# VISUALIZACIÓN — DISTRIBUCIÓN DE SCORES
# ==========================================

scores     = [r['score']     for r in resultados]
identidades = [r['identidad'] for r in resultados]
pares      = [f"{r['p1'][:6]}↔{r['p2'][:6]}" for r in resultados]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# --- Gráfico 1: Score por par ---
colores = ['#5DCAA5' if s > 0 else '#D85A30' for s in scores]
ax1.barh(range(len(scores[:20])), scores[:20],
         color=colores[:20], edgecolor='white', linewidth=0.5)
ax1.set_yticks(range(len(pares[:20])))
ax1.set_yticklabels(pares[:20], fontsize=8)
ax1.set_xlabel("Score voraz")
ax1.set_title("Score de alineamiento por par", fontweight='bold')
ax1.axvline(0, color='black', linewidth=0.8, linestyle='--')

patch_pos = mpatches.Patch(color='#5DCAA5', label='Score positivo')
patch_neg = mpatches.Patch(color='#D85A30', label='Score negativo')
ax1.legend(handles=[patch_pos, patch_neg], fontsize=8)

# --- Gráfico 2: Distribución de identidad ---
ax2.hist(identidades, bins=10, color='#AFA9EC',
         edgecolor='white', linewidth=0.5)
ax2.set_xlabel("Identidad (%)")
ax2.set_ylabel("Cantidad de pares")
ax2.set_title("Distribución de identidad entre proteínas", fontweight='bold')
ax2.axvline(
    sum(identidades)/len(identidades),
    color='#534AB7', linestyle='--',
    label=f"Media: {sum(identidades)/len(identidades):.1f}%"
)
ax2.legend(fontsize=8)

plt.suptitle(
    "Algoritmo Voraz — Alineamiento Heurístico de Proteínas NIH",
    fontsize=13, fontweight='bold', y=1.01
)
plt.tight_layout()
plt.show()