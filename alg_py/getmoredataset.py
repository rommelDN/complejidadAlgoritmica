"""
Descarga las secuencias de aminoácidos (FASTA) desde UniProt
para cada gen presente en grafo_biologico_1500.csv

Requisitos:
    pip install requests pandas --break-system-packages

Uso:
    python descargar_secuencias_uniprot.py
"""

import time
import requests
import pandas as pd

CSV_ENTRADA = "grafo_biologico_1500.csv"
FASTA_SALIDA = "secuencias_proteinas.fasta"
TSV_SALIDA = "secuencias_proteinas.tsv"
ORGANISMO = "9606"  # Homo sapiens
LOTE = 50           # genes por consulta (UniProt soporta OR múltiples)
PAUSA_SEG = 1.0      # pausa entre lotes para no saturar la API

BASE_URL = "https://rest.uniprot.org/uniprotkb/search"


def obtener_genes_unicos(csv_path):
    df = pd.read_csv(csv_path)
    genes = sorted(set(df["protein1"]).union(set(df["protein2"])))
    return genes


def construir_query(lote_genes):
    # gene:X1 OR gene:X2 OR ...  filtrado a humano y revisado (Swiss-Prot)
    or_genes = " OR ".join(f"gene:{g}" for g in lote_genes)
    return f"({or_genes}) AND organism_id:{ORGANISMO} AND reviewed:true"


def descargar_lote(lote_genes):
    query = construir_query(lote_genes)
    params = {
        "query": query,
        "fields": "accession,gene_names,organism_name,length,sequence",
        "format": "tsv",
        "size": 500,
    }
    resp = requests.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    return resp.text


def main():
    genes = obtener_genes_unicos(CSV_ENTRADA)
    print(f"Genes únicos encontrados en el CSV: {len(genes)}")

    filas_tsv = []
    encontrados = set()

    for i in range(0, len(genes), LOTE):
        lote = genes[i : i + LOTE]
        print(f"Descargando lote {i // LOTE + 1} ({len(lote)} genes)...")
        texto = descargar_lote(lote)
        lineas = texto.strip().split("\n")
        if len(lineas) <= 1:
            continue
        encabezado = lineas[0]
        for linea in lineas[1:]:
            filas_tsv.append(linea)
            # registrar qué genes del lote sí se encontraron
            for g in lote:
                if g in linea.split("\t")[1]:  # columna Gene Names
                    encontrados.add(g)
        time.sleep(PAUSA_SEG)

    faltantes = set(genes) - encontrados
    print(f"\nEncontrados: {len(encontrados)} / {len(genes)}")
    if faltantes:
        print(f"No encontrados (revisar manualmente, p.ej. histonas H3-2, H3-4, etc.): {len(faltantes)}")
        print(sorted(faltantes)[:20], "...")

    # Guardar TSV consolidado
    with open(TSV_SALIDA, "w") as f:
        f.write("Entry\tGene Names\tOrganism\tLength\tSequence\n")
        for fila in filas_tsv:
            f.write(fila + "\n")
    print(f"\nGuardado: {TSV_SALIDA}")

    # Guardar también en FASTA puro (id_gen | secuencia)
    with open(FASTA_SALIDA, "w") as f:
        for fila in filas_tsv:
            cols = fila.split("\t")
            if len(cols) < 5:
                continue
            accession, gene_names, organismo, length, secuencia = cols[:5]
            primer_gen = gene_names.split()[0] if gene_names else accession
            f.write(f">{primer_gen}|{accession}\n{secuencia}\n")
    print(f"Guardado: {FASTA_SALIDA}")


if __name__ == "__main__":
    main()