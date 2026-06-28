// ==========================================
// DFS — BÚSQUEDA EN PROFUNDIDAD
// Adaptado de dfs.py (lógica original conservada)
// Explora conexiones dentro de la red biológica
// usando una pila (LIFO), igual que en la
// versión Python original.
// ==========================================

function ejecutarDFS(nodoInicio, limiteVisualizacion = 25) {
  if (!DataStore.adjacency.has(nodoInicio)) {
    return { error: `La proteína "${nodoInicio}" no existe en la red cargada.` };
  }

  const visitados = [];
  const visitadosSet = new Set();
  const pila = [nodoInicio];

  while (pila.length > 0) {
    const nodo = pila.pop();

    if (!visitadosSet.has(nodo)) {
      visitadosSet.add(nodo);
      visitados.push(nodo);

      // Recorrer vecinos (mismo orden de inserción que NetworkX/Python)
      const vecinos = obtenerVecinos(nodo);
      for (const { neighbor } of vecinos) {
        if (!visitadosSet.has(neighbor)) {
          pila.push(neighbor);
        }
      }
    }
  }

  const subNodos = visitados.slice(0, limiteVisualizacion);
  const subAristas = [];
  const subSet = new Set(subNodos);
  for (const n of subNodos) {
    for (const { neighbor, weight } of obtenerVecinos(n)) {
      if (subSet.has(neighbor) && n < neighbor) {
        subAristas.push({ p1: n, p2: neighbor, weight });
      } else if (subSet.has(neighbor) && neighbor < n) {
        // evitar duplicar arista en ambos sentidos
        if (!subAristas.some(a => (a.p1 === neighbor && a.p2 === n))) {
          subAristas.push({ p1: neighbor, p2: n, weight });
        }
      }
    }
  }

  return {
    inicio: nodoInicio,
    totalRecorridos: visitados.length,
    recorrido: visitados,
    subgrafo: { nodos: subNodos, aristas: subAristas },
  };
}
