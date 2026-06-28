// ==========================================
// FUERZA BRUTA — COMPARACIÓN DE SECUENCIAS
// Reescrito a partir de fuerza_bruta.py
//
// CORRECCIÓN IMPORTANTE respecto a la versión
// Python original: fuerza_bruta.py comparaba
// los NOMBRES de las proteínas (p. ej. "MYC"
// vs "GAPDH", strings de 3 a 6 caracteres),
// no su secuencia biológica real. Esta versión
// usa las secuencias de aminoácidos reales
// obtenidas de UniProt (secuencias_proteinas.fasta),
// consistente con la propuesta corregida del
// proyecto (sección 3.2, Grupo 2).
//
// Se conserva la idea original de fuerza bruta:
// comparación posición por posición, sin
// optimización, como línea base de referencia
// frente a las demás técnicas de alineamiento.
// ==========================================

function compararFuerzaBruta(seq1, seq2) {
  const inicio = performance.now();

  let coincidencias = 0;
  const longitud = Math.min(seq1.length, seq2.length);

  for (let i = 0; i < longitud; i++) {
    if (seq1[i] === seq2[i]) coincidencias++;
  }

  const similitud = longitud > 0 ? (coincidencias / longitud) * 100 : 0;
  const tiempoMs = performance.now() - inicio;

  return { coincidencias, longitud, similitud, tiempoMs };
}

function ejecutarFuerzaBruta(gen1, gen2, limiteCaracteres = 300) {
  const s1 = obtenerSecuencia(gen1);
  const s2 = obtenerSecuencia(gen2);

  if (!s1 || !s2) {
    return { error: `No se encontró secuencia para ${!s1 ? gen1 : gen2}. Verifique que esté en secuencias_proteinas.fasta.` };
  }

  const seq1 = s1.sequence.slice(0, limiteCaracteres);
  const seq2 = s2.sequence.slice(0, limiteCaracteres);

  const { coincidencias, longitud, similitud, tiempoMs } = compararFuerzaBruta(seq1, seq2);

  return {
    gen1, gen2,
    longitudComparada: longitud,
    longitudReal1: s1.sequence.length,
    longitudReal2: s2.sequence.length,
    truncado: s1.sequence.length > limiteCaracteres || s2.sequence.length > limiteCaracteres,
    coincidencias,
    similitud,
    tiempoMs,
    seq1Mostrada: seq1,
    seq2Mostrada: seq2,
  };
}

// ------------------------------------------
// BARRIDO SOBRE MUCHOS PARES DE LA RED
// (equivalente al "head(50)" de la versión Python,
// pero ahora opera sobre secuencias reales)
// ------------------------------------------
function barridoFuerzaBruta(cantidadPares = 50, limiteCaracteres = 300) {
  const resultados = [];
  let analizados = 0;

  for (const { p1, p2 } of DataStore.edges) {
    if (analizados >= cantidadPares) break;
    const s1 = obtenerSecuencia(p1);
    const s2 = obtenerSecuencia(p2);
    if (!s1 || !s2) continue; // saltar pares sin secuencia disponible

    const r = ejecutarFuerzaBruta(p1, p2, limiteCaracteres);
    if (!r.error) {
      resultados.push(r);
      analizados++;
    }
  }

  resultados.sort((a, b) => b.similitud - a.similitud);
  return resultados;
}
