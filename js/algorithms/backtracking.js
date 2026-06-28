// ==========================================
// BACKTRACKING — ÁRBOL DE ALINEAMIENTO
// Reescrito a partir de backtraking.py
//
// CORRECCIÓN respecto a la versión Python
// original: backtraking.py usaba las cadenas
// hardcodeadas "RFC2" y "RFC4" (nombres de gen
// de 4 caracteres) en vez de secuencias de
// aminoácidos reales. Esta versión recibe dos
// genes, obtiene sus secuencias reales de
// secuencias_proteinas.fasta, y construye el
// árbol de backtracking sobre ellas.
//
// LÍMITE DE SEGURIDAD: el backtracking puro
// genera hasta 3^n nodos (match, gap-seq1,
// gap-seq2 en cada paso). Sobre una secuencia
// de 300+ aminoácidos esto es computacionalmente
// inviable en el navegador. Se aplica un límite
// por defecto de profundidad (8 niveles) que el
// usuario puede aumentar bajo advertencia
// explícita en la interfaz, igual que se acordó
// para el proyecto.
// ==========================================

const LIMITE_PROFUNDIDAD_SEGURO = 6;
const LIMITE_PROFUNDIDAD_MAXIMO = 12; // a partir de aquí, no se permite ni con advertencia

function construirArbolBacktracking(seq1, seq2, maxProfundidad) {
  const nodos = [];   // {id, label, padre}
  const aristas = []; // {de, a}
  let contador = 0;
  let nodosExplorados = 0;
  let limiteAlcanzado = false;
  const LIMITE_NODOS_DURO = 5000; // salvaguarda anti-congelamiento del navegador

  function backtrack(i, j, alin1, alin2, padre, profundidad) {
    if (nodosExplorados >= LIMITE_NODOS_DURO) {
      limiteAlcanzado = true;
      return;
    }
    if (profundidad > maxProfundidad) return;

    const nodoActual = contador++;
    nodosExplorados++;
    nodos.push({ id: nodoActual, label: `${alin1}\n${alin2}`, profundidad });
    if (padre !== null) aristas.push({ de: padre, a: nodoActual });

    if (i === seq1.length && j === seq2.length) return;

    // Opción 1: match/mismatch directo
    if (i < seq1.length && j < seq2.length) {
      backtrack(i + 1, j + 1, alin1 + seq1[i], alin2 + seq2[j], nodoActual, profundidad + 1);
    }
    // Opción 2: gap en seq2
    if (i < seq1.length) {
      backtrack(i + 1, j, alin1 + seq1[i], alin2 + "-", nodoActual, profundidad + 1);
    }
    // Opción 3: gap en seq1
    if (j < seq2.length) {
      backtrack(i, j + 1, alin1 + "-", alin2 + seq2[j], nodoActual, profundidad + 1);
    }
  }

  backtrack(0, 0, "", "", null, 0);
  return { nodos, aristas, limiteAlcanzado, nodosExplorados };
}

function ejecutarBacktracking(gen1, gen2, profundidad = LIMITE_PROFUNDIDAD_SEGURO, recorteSecuencia = 12) {
  const s1 = obtenerSecuencia(gen1);
  const s2 = obtenerSecuencia(gen2);

  if (!s1 || !s2) {
    return { error: `No se encontró secuencia para ${!s1 ? gen1 : gen2}.` };
  }

  if (profundidad > LIMITE_PROFUNDIDAD_MAXIMO) {
    return { error: `La profundidad máxima permitida es ${LIMITE_PROFUNDIDAD_MAXIMO}. Backtracking crece de forma exponencial (hasta 3^n nodos); valores mayores pueden congelar el navegador.` };
  }

  // Se recorta la secuencia de entrada porque el árbol de backtracking
  // ya está limitado por profundidad; recortar la secuencia además
  // evita construir ramas que de todas formas se cortarían por el límite,
  // y hace que la fracción de la proteína mostrada sea representativa.
  const seq1 = s1.sequence.slice(0, recorteSecuencia);
  const seq2 = s2.sequence.slice(0, recorteSecuencia);

  const inicio = performance.now();
  const { nodos, aristas, limiteAlcanzado, nodosExplorados } = construirArbolBacktracking(seq1, seq2, profundidad);
  const tiempoMs = performance.now() - inicio;

  // Encontrar la mejor hoja (mayor score simple: +1 por match, 0 por mismatch/gap)
  // útil para resaltar un camino representativo en el árbol
  let mejorHoja = null;
  let mejorScore = -Infinity;
  for (const n of nodos) {
    const [a1, a2] = n.label.split("\n");
    let score = 0;
    for (let k = 0; k < Math.max(a1.length, a2.length); k++) {
      if (a1[k] && a2[k] && a1[k] === a2[k]) score++;
    }
    if (score > mejorScore) {
      mejorScore = score;
      mejorHoja = n;
    }
  }

  return {
    gen1, gen2,
    seq1Usada: seq1,
    seq2Usada: seq2,
    longitudReal1: s1.sequence.length,
    longitudReal2: s2.sequence.length,
    profundidadUsada: profundidad,
    totalNodosArbol: nodos.length,
    nodosExplorados,
    limiteAlcanzado,
    tiempoMs,
    mejorAlineamientoParcial: mejorHoja ? mejorHoja.label : null,
    arbol: { nodos, aristas },
  };
}
