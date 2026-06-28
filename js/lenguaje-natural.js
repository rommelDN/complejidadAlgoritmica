// ==========================================
// MOTOR DE LENGUAJE NATURAL
// Convierte los resultados de los algoritmos
// (grado, SCC, UFDS, MST, rutas, similitud) en
// explicaciones en español sencillo, sin
// terminología de teoría de grafos. Esto es lo
// que ve el usuario final; los 12 algoritmos
// quedan como motor interno.
// ==========================================

function formatearNumero(n, decimales = 0) {
  return Number(n).toLocaleString("es-PE", { maximumFractionDigits: decimales, minimumFractionDigits: decimales });
}

// ------------------------------------------
// EXPLICAR POR QUÉ UNA PROTEÍNA ES CRÍTICA
// (basado en los 3 patrones reales observados
// en los datos: AC = hub general, BC = especialista
// de equipo pequeño, y el caso raro de solo A o solo C)
// ------------------------------------------
function explicarProteinaCritica(p, totalNodos, posicionEnSuPatron = 0) {
  if (p.criterioA && p.criterioC && !p.criterioB) {
    const variantes = [
      (n) => `${n} interactúa con un número muy alto de otras proteínas y forma parte del esqueleto de relaciones de mayor confianza de toda la red.`,
      (n) => `${n} es otro de los grandes conectores de la red: muchísimas proteínas dependen de ella de forma directa o indirecta.`,
      (n) => `${n} también destaca por su altísima conectividad y por ubicarse en las relaciones más confiables del sistema.`,
      (n) => `${n} repite el mismo patrón: pocas proteínas tienen tantas conexiones registradas como ella.`,
    ];
    const variante = variantes[Math.min(posicionEnSuPatron, variantes.length - 1)];
    const base = variante(p.proteina);
    if (posicionEnSuPatron === 0) {
      return `${base} Tiene ${formatearNumero(p.grado)} conexiones registradas. Es del tipo "conector general": no pertenece a un equipo pequeño y específico, sino que su influencia se extiende ampliamente por el sistema — un patrón típico de reguladores maestros y proteínas estructurales centrales.`;
    }
    return `${base} (${formatearNumero(p.grado)} conexiones registradas).`;
  }
  if (p.criterioB && p.criterioC && !p.criterioA) {
    if (posicionEnSuPatron === 0) {
      return `${p.proteina} es distinta a las anteriores: tiene relativamente pocas conexiones (${formatearNumero(p.grado)}), pero forma parte de un grupo pequeño y específico de proteínas que trabajan de forma muy cercana entre sí, y esa relación es además una de las más confiables registradas en la red. Es del tipo "especialista de equipo": probablemente cumple un rol concreto dentro de una vía biológica acotada, no una función general.`;
    }
    return `${p.proteina} sigue el mismo patrón de especialista de equipo, con ${formatearNumero(p.grado)} conexiones dentro de un grupo de trabajo específico.`;
  }
  if (p.criterioA && p.criterioB && p.criterioC) {
    return `${p.proteina} combina las tres señales: está entre las proteínas más conectadas de la red, pertenece además a un grupo específico de trabajo conjunto, y aparece en el esqueleto de mayor confianza. Es la combinación de evidencia más fuerte que puede tener una proteína en este análisis.`;
  }
  if (p.criterioA) {
    return `${p.proteina} está entre las proteínas con más conexiones registradas (${formatearNumero(p.grado)}), aunque la evidencia de pertenecer a un grupo específico o a las relaciones de mayor confianza es más débil que en otras proteínas del listado.`;
  }
  if (p.criterioB) {
    return `${p.proteina} pertenece a un grupo pequeño y específico de proteínas relacionadas entre sí, aunque su número total de conexiones (${formatearNumero(p.grado)}) no la posiciona entre las más conectadas de la red.`;
  }
  return `${p.proteina} aparece en el esqueleto de relaciones de mayor confianza de la red, aunque no se observa evidencia adicional de pertenecer a un grupo específico o de tener un número de conexiones particularmente alto.`;
}

// ------------------------------------------
// EXPLICAR LA RELACIÓN ENTRE DOS PROTEÍNAS
// Combina: ¿hay conexión directa?, ¿cuál es la
// ruta de mayor confianza?, ¿cuánta "capacidad"
// de señal hay entre ellas?, y ¿qué tan parecidas
// son sus secuencias?
// ------------------------------------------
function explicarRelacionEntreProteinas(datos) {
  const {
    proteina1, proteina2,
    conexionDirecta, pesoConexionDirecta,
    caminoEncontrado, caminoProteinas, pesoCamino,
    flujoMaximo,
    similitudSecuencia, longitudReal1, longitudReal2,
  } = datos;

  const parrafos = [];

  // Párrafo 1: conexión
  if (conexionDirecta) {
    parrafos.push(`${proteina1} y ${proteina2} están directamente conectadas en la red, con un nivel de confianza de ${(pesoConexionDirecta * 100).toFixed(1)}% según la evidencia disponible. Esta es la relación más directa posible entre dos proteínas.`);
  } else if (caminoEncontrado && caminoProteinas.length > 2) {
    const intermedias = caminoProteinas.slice(1, -1);
    const textoIntermedias = intermedias.length <= 6
      ? `a través de ${intermedias.length === 1 ? "una proteína intermedia" : `${intermedias.length} proteínas intermedias`}: ${caminoProteinas.join(" → ")}`
      : `a través de una cadena de ${intermedias.length} proteínas intermedias (la ruta completa es larga; las primeras son ${intermedias.slice(0, 4).join(", ")}, hasta llegar a ${proteina2})`;
    parrafos.push(`${proteina1} y ${proteina2} no están conectadas directamente, pero sí existe una ruta de relación entre ellas ${textoIntermedias}. Esta es la ruta más confiable encontrada: la que evita el tramo más débil posible en todo el recorrido (un nivel de confianza mínimo de ${(pesoCamino * 100).toFixed(1)}% en su punto más frágil).`);
  } else {
    parrafos.push(`No se encontró ninguna ruta de relación entre ${proteina1} y ${proteina2} dentro de la red analizada. Esto no descarta una relación biológica real, solo indica que no hay evidencia de asociación funcional directa o indirecta en este dataset.`);
  }

  // Párrafo 2: capacidad de señal (flujo), solo si hay conexión de algún tipo
  if ((conexionDirecta || caminoEncontrado) && flujoMaximo !== null && flujoMaximo !== undefined) {
    if (flujoMaximo > 5) {
      parrafos.push(`Además, existen múltiples rutas alternativas de relación entre ambas proteínas, lo que sugiere una conexión robusta dentro del sistema: aunque una vía específica se interrumpiera, hay otras formas en que la influencia podría propagarse entre ellas.`);
    } else if (flujoMaximo > 0) {
      parrafos.push(`La relación entre ambas depende de relativamente pocas rutas alternativas, lo que sugiere una conexión más específica que general dentro del sistema.`);
    }
  }

  // Párrafo 3: similitud de secuencia
  if (similitudSecuencia !== null && similitudSecuencia !== undefined) {
    if (similitudSecuencia >= 30) {
      parrafos.push(`A nivel de secuencia, ambas proteínas son notablemente parecidas (${similitudSecuencia.toFixed(1)}% de coincidencia en los primeros aminoácidos comparados), lo que es compatible con un origen evolutivo común o una función estructural compartida.`);
    } else if (similitudSecuencia >= 10) {
      parrafos.push(`A nivel de secuencia, la similitud entre ambas es moderada (${similitudSecuencia.toFixed(1)}%), insuficiente para sugerir parentesco evolutivo directo, pero no descartable sin un análisis más detallado.`);
    } else {
      parrafos.push(`A nivel de secuencia, la similitud entre ambas es baja (${similitudSecuencia.toFixed(1)}%). Esto, combinado con la conexión observada en la red, sugiere que la relación entre ellas es probablemente funcional (por ejemplo, trabajar en una misma vía de señalización) en lugar de evolutiva.`);
    }
  }

  return parrafos;
}

// ------------------------------------------
// NOMBRAR UN GRUPO DE PROTEÍNAS (equipo funcional)
// Genera un nombre descriptivo simple en vez de
// "Componente 47" o "Grupo UFDS #12"
// ------------------------------------------
function nombrarGrupoDeProteinasPorTamano(tamano, indice) {
  if (tamano >= 50) return `Equipo grande ${indice}`;
  if (tamano >= 10) return `Equipo mediano ${indice}`;
  return `Equipo especializado ${indice}`;
}
