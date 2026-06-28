// ==========================================
// DIVIDE Y VENCERÁS — FRAGMENTACIÓN DE SECUENCIAS
// Algoritmo NUEVO (no existía en el código
// original entregado por el equipo).
//
// El archivo divide_y_venceras.py implementaba
// una búsqueda de máximo sobre la lista de
// interacciones (técnica D&V válida, pero
// aplicada a la RED, no a secuencias). Esa
// versión se conserva en divide-venceras-red.js.
//
// Sin embargo, en la propuesta del proyecto
// (sección 3.2) se le asignó a Divide y Vencerás
// el rol de "fragmentar secuencias extensas de
// ADN/proteína en subsecciones más pequeñas
// para su procesamiento", que es el uso real que
// recibe esta técnica en bioinformática (p. ej.
// para luego alinear cada fragmento por separado
// y combinar resultados). Este archivo implementa
// ese rol: divide recursivamente una secuencia en
// bloques hasta un tamaño base, y luego compara
// cada bloque correspondiente entre dos secuencias
// usando el mismo criterio de fuerza bruta, para
// finalmente combinar (reducir) los resultados.
// ==========================================

function dividirSecuencia(seq, tamanoBase) {
  // Caso base: el fragmento ya es suficientemente pequeño
  if (seq.length <= tamanoBase) {
    return [{ inicio: 0, fragmento: seq }];
  }

  const medio = Math.floor(seq.length / 2);
  const izquierda = dividirSecuencia(seq.slice(0, medio), tamanoBase);
  const derecha = dividirSecuencia(seq.slice(medio), tamanoBase);

  // Ajustar los índices de inicio de la mitad derecha
  const derechaAjustada = derecha.map(f => ({ inicio: f.inicio + medio, fragmento: f.fragmento }));

  return [...izquierda, ...derechaAjustada];
}

function compararFragmento(frag1, frag2) {
  const longitud = Math.min(frag1.length, frag2.length);
  let coincidencias = 0;
  for (let i = 0; i < longitud; i++) {
    if (frag1[i] === frag2[i]) coincidencias++;
  }
  return { coincidencias, longitud };
}

function ejecutarDivideYVenceresSecuencia(gen1, gen2, tamanoBase = 20, limiteCaracteres = 300) {
  const s1 = obtenerSecuencia(gen1);
  const s2 = obtenerSecuencia(gen2);

  if (!s1 || !s2) {
    return { error: `No se encontró secuencia para ${!s1 ? gen1 : gen2}.` };
  }

  const seq1 = s1.sequence.slice(0, limiteCaracteres);
  const seq2 = s2.sequence.slice(0, limiteCaracteres);
  const longitudComun = Math.min(seq1.length, seq2.length);

  const inicio = performance.now();

  // DIVIDIR: fragmentamos seq1 según el tamaño base (técnica D&V)
  const fragmentos1 = dividirSecuencia(seq1.slice(0, longitudComun), tamanoBase);

  // VENCER + COMBINAR: comparamos cada fragmento de seq1
  // contra el fragmento correspondiente (misma posición) de seq2,
  // y combinamos sumando coincidencias y longitudes
  const detalleFragmentos = [];
  let coincidenciasTotal = 0;
  let longitudTotal = 0;

  for (const { inicio: idx, fragmento } of fragmentos1) {
    const fragmento2 = seq2.slice(idx, idx + fragmento.length);
    const { coincidencias, longitud } = compararFragmento(fragmento, fragmento2);
    coincidenciasTotal += coincidencias;
    longitudTotal += longitud;
    detalleFragmentos.push({
      inicio: idx,
      fin: idx + fragmento.length,
      fragmento1: fragmento,
      fragmento2,
      coincidencias,
      similitudFragmento: longitud > 0 ? (coincidencias / longitud) * 100 : 0,
    });
  }

  const tiempoMs = performance.now() - inicio;
  const similitudGlobal = longitudTotal > 0 ? (coincidenciasTotal / longitudTotal) * 100 : 0;

  return {
    gen1, gen2,
    longitudComparada: longitudComun,
    tamanoBase,
    cantidadFragmentos: fragmentos1.length,
    coincidenciasTotal,
    similitudGlobal,
    tiempoMs,
    detalleFragmentos,
  };
}
