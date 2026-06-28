// ==========================================
// DP EN GRAFOS — CAMINO DE MAYOR CONFIANZA
// Adaptado de dp_grafo.py
//
// CORRECCIÓN 1 respecto a la versión Python
// original: dp_grafo.py usaba una variante de
// Bellman-Ford para MAXIMIZAR el peso acumulado.
// Bellman-Ford está diseñado para grafos que
// pueden tener pesos negativos; al maximizar
// sobre un grafo NO dirigido con pesos siempre
// positivos, cualquier ciclo puede "inflar" la
// distancia indefinidamente si se permiten
// repetir nodos.
//
// CORRECCIÓN 2 (tras probar la primera corrección
// con datos reales): maximizar la SUMA de pesos
// acumulados, aunque matemáticamente válida, no
// es lo que un investigador entiende por "ruta
// más confiable" en una red tan densa como esta
// (177 044 aristas entre 1500 nodos): favorece
// rutas de cientos de proteínas intermedias,
// porque sumar más pasos casi siempre da un total
// mayor. El criterio correcto es MAXIMIN (cuello
// de botella): de todas las rutas posibles, se
// busca la que maximiza el peso MÍNIMO de sus
// aristas, es decir, la ruta cuyo tramo más débil
// es el menos débil posible. Esto sigue siendo
// programación dinámica con la misma subestructura
// óptima (el mejor camino A→C que pasa por B es la
// combinación de los mejores tramos A→B y B→C),
// solo que la función de combinación es mínimo en
// vez de suma, y se resuelve con una variante de
// Dijkstra que propaga el mínimo en lugar de la suma.
// ==========================================

function ejecutarDPGrafo(fuenteInput = null, destinoInput = null, limiteNodos = 150) {
  const topNodos = listaNodosOrdenadaPorGrado(limiteNodos).map(([n]) => n);
  const FUENTE = fuenteInput || topNodos[0];
  const DESTINO = destinoInput || topNodos[2];

  if (!DataStore.nodes.has(FUENTE) || !DataStore.nodes.has(DESTINO)) {
    return { error: "Una o ambas proteínas seleccionadas no existen en la red." };
  }

  // Si limiteNodos es null, se considera la red completa (necesario cuando
  // el usuario elige proteínas de bajo grado, como en la Pregunta 2 del
  // aplicativo: restringir al top-150 dejaría fuera a esas proteínas).
  // Por defecto se mantiene la restricción a las proteínas de mayor grado,
  // ya que para el caso de uso original (fuente/destino automáticos sobre
  // hubs) es suficiente y mucho más rápido sobre los 1500 nodos completos.
  const nodosConsiderados = limiteNodos === null
    ? new Set(DataStore.nodes)
    : new Set(topNodos);
  nodosConsiderados.add(FUENTE);
  nodosConsiderados.add(DESTINO);

  const mejorMinimo = new Map(); // nodo -> mejor cuello de botella alcanzado hasta aquí
  const padre = new Map();
  for (const n of nodosConsiderados) mejorMinimo.set(n, -Infinity);
  mejorMinimo.set(FUENTE, Infinity); // la fuente no tiene restricción todavía


  // Dijkstra de maximin (cuello de botella): cola de prioridad simple
  // (array + búsqueda lineal, suficiente para el tamaño del subconjunto considerado)
  const visitado = new Set();
  const pendientes = new Set(nodosConsiderados);

  while (pendientes.size > 0) {
    // Extraer el nodo no visitado con mejor "ancho" de ruta hasta ahora
    let actual = null;
    let mejorValor = -Infinity;
    for (const n of pendientes) {
      const v = mejorMinimo.get(n);
      if (v > mejorValor) {
        mejorValor = v;
        actual = n;
      }
    }
    if (actual === null || mejorValor === -Infinity) break;

    pendientes.delete(actual);
    visitado.add(actual);

    if (actual === DESTINO) break;

    for (const { neighbor, weight } of obtenerVecinos(actual)) {
      if (!nodosConsiderados.has(neighbor) || visitado.has(neighbor)) continue;
      // El "ancho" hasta neighbor es el mínimo entre lo mejor que se
      // tenía hasta "actual" y el peso de esta arista (cuello de botella)
      const anchoCandidato = Math.min(mejorMinimo.get(actual), weight);
      if (anchoCandidato > (mejorMinimo.get(neighbor) ?? -Infinity)) {
        mejorMinimo.set(neighbor, anchoCandidato);
        padre.set(neighbor, actual);
      }
    }
  }

  // Reconstruir camino
  const camino = [];
  let actual = DESTINO;
  const vistosCamino = new Set();
  while (actual !== undefined && !vistosCamino.has(actual)) {
    vistosCamino.add(actual);
    camino.push(actual);
    actual = padre.get(actual);
  }
  camino.reverse();

  const caminoValido = camino.length > 0 && camino[0] === FUENTE;

  // Top 10 nodos con mejor "ancho de ruta" (cuello de botella) desde la fuente
  const minimoOrdenado = Array.from(mejorMinimo.entries())
    .filter(([n, v]) => v > -Infinity && n !== FUENTE)
    .sort((a, b) => b[1] - a[1]);

  return {
    fuente: FUENTE,
    destino: DESTINO,
    pesoOptimo: caminoValido ? mejorMinimo.get(DESTINO) : null,
    camino: caminoValido ? camino : [],
    encontrado: caminoValido,
    top10Alcanzables: minimoOrdenado.slice(0, 10),
  };
}
