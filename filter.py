import pandas as pd

# =========================
# LEER DATASET
# =========================

df = pd.read_csv(
    "9606.protein.links.full.v12.0.txt",
    sep=" "
)

# Seleccionar columnas necesarias
df = df[[
    "protein1",
    "protein2",
    "combined_score"
]]

# =========================
# ORDENAR POR SCORE
# =========================

df = df.sort_values(
    by="combined_score",
    ascending=False
)

# =========================
# NORMALIZAR PESOS
# =========================

df["weight"] = (
    df["combined_score"] / 1000
)

# =========================
# LEER NOMBRES REALES
# =========================

info = pd.read_csv(
    "9606.protein.info.v12.0.txt",
    sep="\t"
)

mapping = dict(zip(
    info["#string_protein_id"],
    info["preferred_name"]
))

# Reemplazar IDs
df["protein1"] = df["protein1"].map(mapping)
df["protein2"] = df["protein2"].map(mapping)

# Eliminar vacíos
df = df.dropna()

# =========================
# OBTENER SOLO 1500 NODOS
# =========================

nodos = pd.unique(
    df[["protein1", "protein2"]].values.ravel()
)

# Primeros 1500 nodos
nodos_1500 = set(nodos[:1500])

# Filtrar aristas
df_final = df[
    (df["protein1"].isin(nodos_1500)) &
    (df["protein2"].isin(nodos_1500))
]

# =========================
# DATASET FINAL
# =========================

df_final = df_final[[
    "protein1",
    "protein2",
    "weight"
]]

# Guardar CSV
df_final.to_csv(
    "grafo_biologico_1500.csv",
    index=False
)

# =========================
# CONTAR NODOS REALES
# =========================

nodos_finales = len(
    set(df_final["protein1"]).union(
        set(df_final["protein2"])
    )
)

print(df_final.head())

print("\nCantidad REAL de nodos:", nodos_finales)
print("Cantidad de aristas:", len(df_final))