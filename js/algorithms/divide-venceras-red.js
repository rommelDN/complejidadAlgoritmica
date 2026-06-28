// ==========================================
// DIVIDE Y VENCERÁS — INTERACCIÓN MÁS FUERTE
// Adaptado de divide_y_venceras.py (lógica
// original conservada sin cambios funcionales)
//
// Encuentra la arista de mayor peso (confianza)
// en el dataset, dividiendo recursivamente la
// lista de interacciones hasta el caso base.
// ==========================================

function buscarMaximoDyV(lista) {
  if (lista.length === 1) return lista[0];

  const medio = Math.floor(lista.length / 2);
  const maxIzq = buscarMaximoDyV(lista.slice(0, medio));
  const maxDer = buscarMaximoDyV(lista.slice(medio));

  return maxIzq.weight > maxDer.weight ? maxIzq : maxDer;
}

function ejecutarDivideYVenceras() {
  if (DataStore.edges.length === 0) {
    return { error: "No hay datos de red cargados." };
  }

  const maxInteraccion = buscarMaximoDyV(DataStore.edges);
  const { p1: p1Max, p2: p2Max, weight: pesoMax } = maxInteraccion;

  // Vecinos relacionados (para el subgrafo, igual que en la versión original)
  const vecinosP1 = obtenerVecinos(p1Max).slice(0, 5).map(v => v.neighbor);
  const vecinosP2 = obtenerVecinos(p2Max).slice(0, 5).map(v => v.neighbor);

  const nodosSubgrafo = Array.from(new Set([p1Max, p2Max, ...vecinosP1, ...vecinosP2]));
  const setSubgrafo = new Set(nodosSubgrafo);

  const aristasSubgrafo = [];
  const vistos = new Set();
  for (const { p1, p2, weight } of DataStore.edges) {
    if (setSubgrafo.has(p1) && setSubgrafo.has(p2)) {
      const key = p1 < p2 ? `${p1}|${p2}` : `${p2}|${p1}`;
      if (!vistos.has(key)) {
        vistos.add(key);
        aristasSubgrafo.push({ p1, p2, weight, esMaxima: (p1 === p1Max && p2 === p2Max) || (p1 === p2Max && p2 === p1Max) });
      }
    }
  }

  return {
    p1Max, p2Max, pesoMax,
    subgrafo: { nodos: nodosSubgrafo, aristas: aristasSubgrafo },
  };
}
