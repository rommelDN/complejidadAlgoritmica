// ==========================================
// UFDS — UNION-FIND DISJOINT SET
// Adaptado de ufsd.py
//
// MEJORA respecto a la versión Python original:
// se agrega compresión de camino y unión por
// rango, lo que reduce la complejidad amortizada
// de cada operación de O(n) a O(log n) (cercana
// a O(1) en la práctica), tal como se describe
// en la sección 4.3 del informe.
// ==========================================

// Mismo razonamiento que en SCC (ver scc.js): sin umbral, la red
// completa colapsa en un único grupo de ~1500 proteínas. Filtrar por
// confianza mínima revela comunidades biológicas más pequeñas y
// específicas, que es lo realmente útil para identificar módulos
// funcionales según la propuesta del proyecto.
function ejecutarUFDS(limiteVisualizacion = 25, umbralConfianza = 0.7) {
  const nodos = Array.from(DataStore.nodes);
  const ids = new Map();
  nodos.forEach((n, i) => ids.set(n, i));

  const parent = nodos.map((_, i) => i);
  const rank = nodos.map(() => 0);

  function find(x) {
    // Compresión de camino
    if (parent[x] !== x) {
      parent[x] = find(parent[x]);
    }
    return parent[x];
  }

  function union(a, b) {
    const ra = find(a);
    const rb = find(b);
    if (ra === rb) return;

    // Unión por rango
    if (rank[ra] < rank[rb]) {
      parent[ra] = rb;
    } else if (rank[ra] > rank[rb]) {
      parent[rb] = ra;
    } else {
      parent[rb] = ra;
      rank[ra]++;
    }
  }

  for (const { p1, p2, weight } of DataStore.edges) {
    if (weight < umbralConfianza) continue;
    union(ids.get(p1), ids.get(p2));
  }

  // Agrupar
  const grupos = new Map(); // raiz -> [proteinas]
  for (const nodo of nodos) {
    const raiz = find(ids.get(nodo));
    if (!grupos.has(raiz)) grupos.set(raiz, []);
    grupos.get(raiz).push(nodo);
  }

  const listaGrupos = Array.from(grupos.values());
  const grupoMayor = listaGrupos.reduce((a, b) => (a.length > b.length ? a : b));

  // Subgrafo: top nodos por grado dentro del grupo mayor
  const grupoMayorSet = new Set(grupoMayor);
  const topNodos = listaNodosOrdenadaPorGrado()
    .filter(([nodo]) => grupoMayorSet.has(nodo))
    .slice(0, limiteVisualizacion)
    .map(([nodo]) => nodo);

  const topSet = new Set(topNodos);
  const aristasSubgrafo = [];
  const vistos = new Set();
  for (const { p1, p2, weight } of DataStore.edges) {
    if (weight < umbralConfianza) continue;
    if (topSet.has(p1) && topSet.has(p2)) {
      const key = p1 < p2 ? `${p1}|${p2}` : `${p2}|${p1}`;
      if (!vistos.has(key)) {
        vistos.add(key);
        aristasSubgrafo.push({ p1, p2, weight });
      }
    }
  }

  return {
    totalGrupos: listaGrupos.length,
    tamanoGrupoMayor: grupoMayor.length,
    primeras25DelGrupo: grupoMayor.slice(0, 25),
    umbralUsado: umbralConfianza,
    subgrafo: { nodos: topNodos, aristas: aristasSubgrafo },
  };
}
