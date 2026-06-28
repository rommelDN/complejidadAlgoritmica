// ==========================================
// PREGUNTA 2 — ¿ESTAS DOS PROTEÍNAS ESTÁN RELACIONADAS?
// Combina, para un par de proteínas:
//   - conexión directa (consulta simple sobre la adyacencia)
//   - ruta de mayor confianza si no hay conexión directa
//     (reutiliza la lógica de dp-grafo.js)
//   - capacidad de señal entre ambas (reutiliza flujo-maximo.js)
//   - similitud de secuencia real (reutiliza fuerza-bruta.js)
// No es un algoritmo nuevo: es la orquestación de los
// algoritmos existentes para responder una sola pregunta
// en lenguaje de investigador.
// ==========================================

function consultarRelacionEntreProteinas(proteina1, proteina2, limiteCaracteresSecuencia = 300) {
  if (!DataStore.nodes.has(proteina1) || !DataStore.nodes.has(proteina2)) {
    return { error: "Una o ambas proteínas no existen en la red cargada." };
  }
  if (proteina1 === proteina2) {
    return { error: "Seleccione dos proteínas distintas." };
  }

  // 1) Conexión directa
  const vecinosP1 = obtenerVecinos(proteina1);
  const directa = vecinosP1.find(v => v.neighbor === proteina2);
  const conexionDirecta = !!directa;
  const pesoConexionDirecta = directa ? directa.weight : null;

  // 2) Ruta de mayor confianza (solo si no hay conexión directa).
  // Se reutiliza directamente ejecutarDPGrafo (dp-grafo.js), pidiéndole
  // que considere la red completa (limiteNodos = null) en vez de
  // restringirse a las proteínas de mayor grado, ya que aquí el usuario
  // puede elegir cualquier proteína, incluidas las de bajo grado.
  let caminoEncontrado = false;
  let caminoProteinas = [];
  let pesoCamino = null;

  if (!conexionDirecta) {
    const resultadoRuta = ejecutarDPGrafo(proteina1, proteina2, null);
    caminoEncontrado = resultadoRuta.encontrado || false;
    caminoProteinas = resultadoRuta.camino || [];
    pesoCamino = resultadoRuta.pesoOptimo ?? null;
  }

  // 3) Capacidad de señal (flujo máximo), solo si existe algún tipo de conexión
  let flujoMaximo = null;
  if (conexionDirecta || caminoEncontrado) {
    const resultadoFlujo = ejecutarFlujoMaximo(proteina1, proteina2);
    if (!resultadoFlujo.error) flujoMaximo = resultadoFlujo.flujoMaximo;
  }

  // 4) Similitud de secuencia real
  let similitudSecuencia = null;
  let longitudReal1 = null, longitudReal2 = null;
  const s1 = obtenerSecuencia(proteina1);
  const s2 = obtenerSecuencia(proteina2);
  if (s1 && s2) {
    const resultadoFB = ejecutarFuerzaBruta(proteina1, proteina2, limiteCaracteresSecuencia);
    if (!resultadoFB.error) {
      similitudSecuencia = resultadoFB.similitud;
      longitudReal1 = resultadoFB.longitudReal1;
      longitudReal2 = resultadoFB.longitudReal2;
    }
  }

  const datos = {
    proteina1, proteina2,
    conexionDirecta, pesoConexionDirecta,
    caminoEncontrado, caminoProteinas, pesoCamino,
    flujoMaximo,
    similitudSecuencia, longitudReal1, longitudReal2,
  };

  return {
    ...datos,
    explicacion: explicarRelacionEntreProteinas(datos),
  };
}
