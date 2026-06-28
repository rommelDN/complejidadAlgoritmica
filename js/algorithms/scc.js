// ==========================================
// SCC — COMPONENTES FUERTEMENTE CONEXAS (TARJAN)
// Adaptado de scc.py
//
// NOTA IMPORTANTE (documentada también en el
// informe): la red original es no dirigida
// (estructura tipo STRING). Para aplicar SCC
// de forma significativa, igual que en la
// versión Python, se trata la red como un
// grafo DIRIGIDO usando el orden de aparición
// protein1 -> protein2 de cada fila del CSV.
//
// A diferencia de la versión Python (recursiva,
// puede desbordar la pila de llamadas en redes
// grandes), esta versión usa una pila explícita
// para soportar los 1500 nodos sin problemas.
// ==========================================

function construirGrafoDirigido(umbralConfianza = 0) {
  const adj = new Map();
  for (const { p1, p2, weight } of DataStore.edges) {
    if (weight < umbralConfianza) continue;
    if (!adj.has(p1)) adj.set(p1, []);
    if (!adj.has(p2)) adj.set(p2, []);
    adj.get(p1).push(p2);
  }
  return adj;
}

// NOTA DE DISEÑO: con la red completa (177 044 aristas), SCC y UFDS
// colapsan casi todos los nodos en un único componente gigante, porque
// la red está muy densamente conectada incluso con asociaciones de baja
// confianza. Para revelar módulos funcionales realmente informativos
// (decenas de ciclos pequeños en vez de uno solo de ~1500 nodos), se
// permite filtrar por un umbral mínimo de confianza antes de aplicar
// el algoritmo. Un umbral de 0.7-0.9 produce entre 150 y 300 componentes
// con ciclos biológicos de tamaño manejable, mucho más útiles para la
// priorización de proteínas que describe la propuesta del proyecto.
function ejecutarSCC(limiteVisualizacion = 20, umbralConfianza = 0.7) {
  const grafo = construirGrafoDirigido(umbralConfianza);

  let indiceGlobal = 0;
  const indices = new Map();
  const lowlink = new Map();
  const enPila = new Map();
  const pilaTarjan = [];
  const resultado = [];

  // Pila explícita para simular la recursión de Tarjan
  // Cada elemento: { nodo, iteradorVecinos, padre }
  for (const nodoRaiz of grafo.keys()) {
    if (indices.has(nodoRaiz)) continue;

    const callStack = [{ nodo: nodoRaiz, vecinos: grafo.get(nodoRaiz) || [], idx: 0 }];
    indices.set(nodoRaiz, indiceGlobal);
    lowlink.set(nodoRaiz, indiceGlobal);
    indiceGlobal++;
    pilaTarjan.push(nodoRaiz);
    enPila.set(nodoRaiz, true);

    while (callStack.length > 0) {
      const frame = callStack[callStack.length - 1];
      const { nodo, vecinos } = frame;

      if (frame.idx < vecinos.length) {
        const w = vecinos[frame.idx];
        frame.idx++;

        if (!indices.has(w)) {
          indices.set(w, indiceGlobal);
          lowlink.set(w, indiceGlobal);
          indiceGlobal++;
          pilaTarjan.push(w);
          enPila.set(w, true);
          callStack.push({ nodo: w, vecinos: grafo.get(w) || [], idx: 0 });
        } else if (enPila.get(w)) {
          lowlink.set(nodo, Math.min(lowlink.get(nodo), indices.get(w)));
        }
      } else {
        // Terminamos de explorar los vecinos de "nodo"
        callStack.pop();
        if (callStack.length > 0) {
          const padre = callStack[callStack.length - 1].nodo;
          lowlink.set(padre, Math.min(lowlink.get(padre), lowlink.get(nodo)));
        }

        if (lowlink.get(nodo) === indices.get(nodo)) {
          const componente = [];
          let actual;
          do {
            actual = pilaTarjan.pop();
            enPila.set(actual, false);
            componente.push(actual);
          } while (actual !== nodo);
          resultado.push(componente);
        }
      }
    }
  }

  const ciclos = resultado.filter(c => c.length > 1);
  const mayor = ciclos.length > 0
    ? ciclos.reduce((a, b) => (a.length > b.length ? a : b))
    : null;

  let subgrafo = { nodos: [], aristas: [] };
  if (mayor) {
    const nodosVis = mayor.slice(0, limiteVisualizacion);
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
    subgrafo = { nodos: nodosVis, aristas };
  }

  return {
    totalComponentes: resultado.length,
    ciclosEncontrados: ciclos.length,
    componenteMayor: mayor ? mayor.length : 0,
    umbralUsado: umbralConfianza,
    subgrafo,
  };
}
