// ==========================================
// MST — ÁRBOL DE EXPANSIÓN MÍNIMA (KRUSKAL)
// Adaptado de mst.py
//
// CORRECCIÓN respecto a la versión Python
// original: el archivo mst.py ordenaba las
// aristas por peso ASCENDENTE (criterio de
// "costo mínimo"), lo cual en este dataset
// construye el árbol con las interacciones
// de MENOR confianza.
//
// Según el rol que se le asignó a esta técnica
// en la propuesta del proyecto ("esqueleto de
// MAYOR confianza que mantiene la red
// conectada"), el criterio correcto es ordenar
// las aristas por peso DESCENDENTE, igual que
// se documentó en la sección 4.3 del informe.
// ==========================================

function ejecutarMST(limiteVisualizacion = 20) {
  const nodos = Array.from(DataStore.nodes);
  const ids = new Map();
  nodos.forEach((n, i) => ids.set(n, i));

  const parent = nodos.map((_, i) => i);
  const rank = nodos.map(() => 0);

  function find(x) {
    if (parent[x] !== x) parent[x] = find(parent[x]);
    return parent[x];
  }
  function union(a, b) {
    const ra = find(a);
    const rb = find(b);
    if (ra === rb) return false;
    if (rank[ra] < rank[rb]) parent[ra] = rb;
    else if (rank[ra] > rank[rb]) parent[rb] = ra;
    else { parent[rb] = ra; rank[ra]++; }
    return true;
  }

  // Ordenar DESCENDENTE por peso: priorizamos las relaciones
  // de mayor confianza primero (criterio corregido)
  const aristasOrdenadas = [...DataStore.edges].sort((a, b) => b.weight - a.weight);

  const mst = [];
  let pesoTotal = 0;

  for (const { p1, p2, weight } of aristasOrdenadas) {
    if (union(ids.get(p1), ids.get(p2))) {
      mst.push({ p1, p2, weight });
      pesoTotal += weight;
      if (mst.length === nodos.length - 1) break;
    }
  }

  const subAristas = mst.slice(0, limiteVisualizacion);
  const subNodos = Array.from(new Set(subAristas.flatMap(a => [a.p1, a.p2])));

  return {
    totalNodos: nodos.length,
    aristasEnMST: mst.length,
    pesoTotalConfianza: pesoTotal,
    subgrafo: { nodos: subNodos, aristas: subAristas },
  };
}
