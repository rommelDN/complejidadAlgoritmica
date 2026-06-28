// ==========================================
// PREGUNTA 3 — ¿QUÉ GRUPOS DE PROTEÍNAS TRABAJAN JUNTAS?
// Reutiliza UFDS (agrupación por conjuntos disjuntos)
// para identificar comunidades de proteínas, excluyendo
// el grupo gigante (que no es informativo: es casi toda
// la red), y presenta cada grupo como un "equipo" con
// nombre simple y descriptivo en vez de un ID técnico.
// ==========================================

function identificarEquiposDeProteinas(umbralConfianza = 0.95, tamanoMinimoEquipo = 4) {
  if (!DataStore.ready.red) {
    return { error: "Primero cargue el dataset de la red." };
  }

  const inicio = performance.now();

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
    const ra = find(a), rb = find(b);
    if (ra === rb) return;
    if (rank[ra] < rank[rb]) parent[ra] = rb;
    else if (rank[ra] > rank[rb]) parent[rb] = ra;
    else { parent[rb] = ra; rank[ra]++; }
  }

  for (const { p1, p2, weight } of DataStore.edges) {
    if (weight < umbralConfianza) continue;
    union(ids.get(p1), ids.get(p2));
  }

  const grupos = new Map();
  for (const nodo of nodos) {
    const raiz = find(ids.get(nodo));
    if (!grupos.has(raiz)) grupos.set(raiz, []);
    grupos.get(raiz).push(nodo);
  }

  let listaGrupos = Array.from(grupos.values()).sort((a, b) => b.length - a.length);

  // Excluir el grupo gigante: no es un "equipo de trabajo", es casi toda la red
  const grupoGigante = listaGrupos[0];
  listaGrupos = listaGrupos.slice(1).filter(g => g.length >= tamanoMinimoEquipo);

  // Ordenar cada equipo internamente por grado (la proteína más conectada primero)
  const equipos = listaGrupos.map((grupo, idx) => {
    const miembrosOrdenados = [...grupo].sort((a, b) => (DataStore.degree.get(b) || 0) - (DataStore.degree.get(a) || 0));
    return {
      id: idx + 1,
      nombre: nombrarGrupoDeProteinasPorTamano(grupo.length, idx + 1),
      tamano: grupo.length,
      miembros: miembrosOrdenados,
      proteinaPrincipal: miembrosOrdenados[0],
    };
  });

  const tiempoMs = performance.now() - inicio;

  return {
    totalEquipos: equipos.length,
    tamanoGrupoGigante: grupoGigante.length,
    porcentajeFueraDeEquipos: (grupoGigante.length / nodos.length) * 100,
    umbralUsado: umbralConfianza,
    tiempoMs,
    equipos: equipos.sort((a, b) => b.tamano - a.tamano),
  };
}

// ------------------------------------------
// Construir el subgrafo de un equipo específico,
// para visualizarlo (reutiliza el motor de
// renderizado de grafos ya existente)
// ------------------------------------------
function obtenerSubgrafoDeEquipo(miembros, limiteVisualizacion = 25) {
  const nodosVis = miembros.slice(0, limiteVisualizacion);
  const setVis = new Set(nodosVis);
  const aristas = [];
  const vistos = new Set();

  for (const { p1, p2, weight } of DataStore.edges) {
    if (setVis.has(p1) && setVis.has(p2)) {
      const key = p1 < p2 ? `${p1}|${p2}` : `${p2}|${p1}`;
      if (!vistos.has(key)) {
        vistos.add(key);
        aristas.push({ p1, p2, weight });
      }
    }
  }

  return { nodos: nodosVis, aristas };
}
