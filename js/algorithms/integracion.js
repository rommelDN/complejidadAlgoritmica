// ==========================================
// INTEGRACIÓN — RANKING DE PROTEÍNAS CRÍTICAS
// Implementa el criterio definido en la sección
// 5 del informe ("Validación de datos y pruebas",
// Interpretación de resultados):
//
// Una proteína se considera CRÍTICA si cumple
// al menos DOS de los siguientes tres criterios:
//   (a) está en el percentil superior de grado
//       de conexión en la red,
//   (b) pertenece a una componente fuertemente
//       conexa (SCC) o a un conjunto UFDS de
//       tamaño significativo,
//   (c) aparece como arista del árbol de
//       expansión mínima (MST) de mayor
//       confianza.
//
// Este módulo NO introduce un algoritmo nuevo:
// reutiliza los resultados ya calculados por
// los algoritmos de grafos (scc.js, ufds.js,
// mst.js, data-loader.js) y aplica la regla de
// combinación en tiempo lineal sobre ellos,
// exactamente como se describe en la sección
// 4.3 del informe ("Módulo de integración").
// ==========================================

const PERCENTIL_GRADO_CRITERIO_A = 0.90; // top 10% de grado
const TAMANO_MINIMO_MODULO_CRITERIO_B = 5; // tamaño mínimo de SCC/UFDS para considerarse "significativo"

function calcularRankingProteinasCriticas(umbralConfianza = 0.7, limiteRanking = 30) {
  if (!DataStore.ready.red) {
    return { error: "Primero cargue el dataset de la red." };
  }

  const inicio = performance.now();

  // ---------- CRITERIO A: percentil superior de grado ----------
  const gradosOrdenados = listaNodosOrdenadaPorGrado(); // [[nodo, grado], ...] descendente
  const totalNodos = gradosOrdenados.length;
  const corteIndice = Math.floor(totalNodos * (1 - PERCENTIL_GRADO_CRITERIO_A));
  const setCriterioA = new Set(gradosOrdenados.slice(0, Math.max(corteIndice, 1)).map(([n]) => n));
  const mapaGrados = new Map(gradosOrdenados);

  // ---------- CRITERIO B: SCC o UFDS de tamaño significativo ----------
  // Reutilizamos la lógica de scc.js y ufds.js, pero sin limitar la
  // visualización (necesitamos TODOS los componentes/grupos, no solo
  // el subgrafo de los 20-25 nodos que se muestra en sus pantallas).
  const componentesSignificativos = obtenerComponentesSCCSignificativos(umbralConfianza);
  const gruposSignificativos = obtenerGruposUFDSSignificativos(umbralConfianza);
  const setCriterioB = new Set([...componentesSignificativos, ...gruposSignificativos]);

  // ---------- CRITERIO C: aristas del MST ----------
  const resultadoMST = calcularMSTCompleto();
  const setCriterioC = new Set();
  for (const { p1, p2 } of resultadoMST.aristas) {
    setCriterioC.add(p1);
    setCriterioC.add(p2);
  }

  // ---------- COMBINAR ----------
  const ranking = [];
  for (const nodo of DataStore.nodes) {
    const a = setCriterioA.has(nodo);
    const b = setCriterioB.has(nodo);
    const c = setCriterioC.has(nodo);
    const criteriosCumplidos = [a, b, c].filter(Boolean).length;

    if (criteriosCumplidos >= 2) {
      ranking.push({
        proteina: nodo,
        grado: mapaGrados.get(nodo) || 0,
        criterioA: a,
        criterioB: b,
        criterioC: c,
        criteriosCumplidos,
      });
    }
  }

  // Ordenar por: cantidad de criterios cumplidos (desc), luego por grado (desc)
  ranking.sort((x, y) => {
    if (y.criteriosCumplidos !== x.criteriosCumplidos) return y.criteriosCumplidos - x.criteriosCumplidos;
    return y.grado - x.grado;
  });

  const tiempoMs = performance.now() - inicio;

  return {
    totalProteinasCriticas: ranking.length,
    totalProteinasEvaluadas: totalNodos,
    porcentajeCriticas: (ranking.length / totalNodos) * 100,
    umbralUsado: umbralConfianza,
    tiempoMs,
    ranking: ranking.slice(0, limiteRanking),
    rankingCompleto: ranking, // para exportar o consultar después
  };
}

// ------------------------------------------
// CRITERIO B — helper: componentes SCC significativas
// (todas, no solo la mayor, a diferencia de ejecutarSCC)
// ------------------------------------------
function obtenerComponentesSCCSignificativos(umbralConfianza) {
  const grafo = construirGrafoDirigido(umbralConfianza);

  let indiceGlobal = 0;
  const indices = new Map();
  const lowlink = new Map();
  const enPila = new Map();
  const pilaTarjan = [];
  const resultado = [];

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

  const nodosSignificativos = new Set();

  // Excluimos el componente MÁS grande, por la misma razón que en UFDS
  // (ver obtenerGruposUFDSSignificativos): en una red tan densa, el SCC
  // gigante no aporta información específica, es casi toda la red.
  const componentesOrdenados = [...resultado].sort((a, b) => b.length - a.length);
  const componenteMasGrande = componentesOrdenados[0];

  for (const comp of resultado) {
    if (comp === componenteMasGrande) continue;
    if (comp.length >= TAMANO_MINIMO_MODULO_CRITERIO_B) {
      for (const n of comp) nodosSignificativos.add(n);
    }
  }
  return nodosSignificativos;
}

// ------------------------------------------
// CRITERIO B — helper: grupos UFDS significativos
// (todos los grupos de tamaño suficiente, no solo el mayor)
// ------------------------------------------
function obtenerGruposUFDSSignificativos(umbralConfianza) {
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

  // Excluimos el grupo MÁS grande: en una red densa, el grupo gigante
  // (cientos o miles de nodos) no es informativo como "módulo
  // específico" — es prácticamente toda la red. Solo los grupos
  // pequeños/medianos son evidencia real de comunidad funcional.
  const listaGrupos = Array.from(grupos.values()).sort((a, b) => b.length - a.length);
  const grupoMasGrande = listaGrupos[0];

  const nodosSignificativos = new Set();
  for (const grupo of listaGrupos) {
    if (grupo === grupoMasGrande) continue;
    if (grupo.length >= TAMANO_MINIMO_MODULO_CRITERIO_B) {
      for (const n of grupo) nodosSignificativos.add(n);
    }
  }
  return nodosSignificativos;
}

// ------------------------------------------
// CRITERIO C — helper: MST completo (todas las aristas, sin límite de visualización)
// ------------------------------------------
function calcularMSTCompleto() {
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
    if (ra === rb) return false;
    if (rank[ra] < rank[rb]) parent[ra] = rb;
    else if (rank[ra] > rank[rb]) parent[rb] = ra;
    else { parent[rb] = ra; rank[ra]++; }
    return true;
  }

  const aristasOrdenadas = [...DataStore.edges].sort((a, b) => b.weight - a.weight);
  const mst = [];
  for (const { p1, p2, weight } of aristasOrdenadas) {
    if (union(ids.get(p1), ids.get(p2))) {
      mst.push({ p1, p2, weight });
      if (mst.length === nodos.length - 1) break;
    }
  }
  return { aristas: mst };
}

// ------------------------------------------
// EVIDENCIA COMPLEMENTARIA DE SECUENCIA
// Para una proteína crítica seleccionada, busca
// sus vecinos en la red y calcula similitud de
// secuencia real con cada uno (cuando ambos
// tengan secuencia disponible). Esto materializa
// la "evidencia complementaria" descrita en la
// sección 5 del informe.
// ------------------------------------------
function evidenciaSecuenciaParaProteina(proteina, limiteVecinos = 8, limiteCaracteres = 300) {
  const vecinos = obtenerVecinos(proteina)
    .sort((a, b) => b.weight - a.weight)
    .slice(0, limiteVecinos);

  const propia = obtenerSecuencia(proteina);
  if (!propia) {
    return { error: `No hay secuencia disponible para ${proteina}.` };
  }

  const resultados = [];
  for (const { neighbor, weight } of vecinos) {
    const vecinoSeq = obtenerSecuencia(neighbor);
    if (!vecinoSeq) continue;

    const r = ejecutarFuerzaBruta(proteina, neighbor, limiteCaracteres);
    if (!r.error) {
      resultados.push({
        vecino: neighbor,
        pesoRed: weight,
        similitudSecuencia: r.similitud,
      });
    }
  }

  return { proteina, evidencias: resultados };
}
