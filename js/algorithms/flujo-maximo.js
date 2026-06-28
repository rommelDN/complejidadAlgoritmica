// ==========================================
// FLUJO MÁXIMO — EDMONDS-KARP
// Adaptado de flujo_maximo.py
//
// MEJORA respecto a la versión Python original:
// en vez de seleccionar automáticamente los dos
// nodos de mayor grado como source/sink, se
// permite que el usuario elija cualquier par de
// proteínas desde la interfaz, ya que en la
// propuesta corregida el flujo máximo debe
// poder consultarse "entre dos proteínas de
// interés" (no solo entre los dos hubs).
// Si no se especifican, se conserva el
// comportamiento original como valor por defecto.
// ==========================================

function bfsCaminoAumentante(source, sink, capacidadResidual, adyacencia) {
  const visitados = new Set([source]);
  const cola = [source];
  const padre = new Map();

  while (cola.length > 0) {
    const u = cola.shift();
    for (const v of adyacencia.get(u) || []) {
      const cap = capacidadResidual.get(u)?.get(v) || 0;
      if (!visitados.has(v) && cap > 0) {
        visitados.add(v);
        padre.set(v, u);
        if (v === sink) return padre;
        cola.push(v);
      }
    }
  }
  return null;
}

function ejecutarFlujoMaximo(sourceInput = null, sinkInput = null) {
  // Construir capacidades y adyacencia
  const capacidad = new Map(); // u -> Map(v -> cap)
  const adyacencia = new Map(); // u -> Set(v)

  for (const { p1, p2, weight } of DataStore.edges) {
    if (!capacidad.has(p1)) capacidad.set(p1, new Map());
    if (!capacidad.has(p2)) capacidad.set(p2, new Map());
    capacidad.get(p1).set(p2, (capacidad.get(p1).get(p2) || 0) + weight);
    capacidad.get(p2).set(p1, (capacidad.get(p2).get(p1) || 0) + weight);

    if (!adyacencia.has(p1)) adyacencia.set(p1, new Set());
    if (!adyacencia.has(p2)) adyacencia.set(p2, new Set());
    adyacencia.get(p1).add(p2);
    adyacencia.get(p2).add(p1);
  }

  let SOURCE = sourceInput;
  let SINK = sinkInput;

  if (!SOURCE || !SINK) {
    const topNodos = listaNodosOrdenadaPorGrado(2).map(([n]) => n);
    SOURCE = SOURCE || topNodos[0];
    SINK = SINK || topNodos[1];
  }

  if (!DataStore.nodes.has(SOURCE) || !DataStore.nodes.has(SINK)) {
    return { error: "Una o ambas proteínas seleccionadas no existen en la red." };
  }
  if (SOURCE === SINK) {
    return { error: "La fuente y el sumidero deben ser proteínas distintas." };
  }

  // Copia residual
  const capResidual = new Map();
  for (const [u, mapa] of capacidad) {
    capResidual.set(u, new Map(mapa));
  }

  let flujoTotal = 0;
  const rutasUsadas = [];

  while (true) {
    const padre = bfsCaminoAumentante(SOURCE, SINK, capResidual, adyacencia);
    if (!padre) break;

    let flujoCamino = Infinity;
    let v = SINK;
    const camino = [];
    while (v !== SOURCE) {
      const u = padre.get(v);
      flujoCamino = Math.min(flujoCamino, capResidual.get(u).get(v));
      camino.push(v);
      v = u;
    }
    camino.push(SOURCE);
    camino.reverse();

    v = SINK;
    while (v !== SOURCE) {
      const u = padre.get(v);
      capResidual.get(u).set(v, capResidual.get(u).get(v) - flujoCamino);
      if (!capResidual.has(v)) capResidual.set(v, new Map());
      capResidual.get(v).set(u, (capResidual.get(v).get(u) || 0) + flujoCamino);
      v = u;
    }

    flujoTotal += flujoCamino;
    rutasUsadas.push({ camino, flujo: flujoCamino });

    // Salvaguarda: en grafos densos con muchos caminos pequeños,
    // limitamos a 200 rutas para no bloquear el navegador
    if (rutasUsadas.length > 200) break;
  }

  // Subgrafo de visualización: primeras 6 rutas
  const rutasVis = rutasUsadas.slice(0, 6);
  const nodosVis = new Set();
  const aristasVis = [];
  for (const { camino, flujo } of rutasVis) {
    camino.forEach(n => nodosVis.add(n));
    for (let i = 0; i < camino.length - 1; i++) {
      aristasVis.push({ p1: camino[i], p2: camino[i + 1], weight: flujo });
    }
  }

  return {
    source: SOURCE,
    sink: SINK,
    flujoMaximo: flujoTotal,
    totalRutas: rutasUsadas.length,
    primerasRutas: rutasUsadas.slice(0, 5),
    subgrafo: { nodos: Array.from(nodosVis), aristas: aristasVis },
  };
}
