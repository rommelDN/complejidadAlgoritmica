// ==========================================
// DP — NEEDLEMAN-WUNSCH (ALINEAMIENTO GLOBAL)
// Reescrito a partir de dp.py
//
// CORRECCIÓN respecto a la versión Python
// original: dp.py alineaba los NOMBRES de gen
// del dataset, no las secuencias biológicas
// reales. Esta versión opera sobre las
// secuencias de aminoácidos de
// secuencias_proteinas.fasta, que es la fuente
// de datos correcta para esta técnica según la
// propuesta del proyecto (sección 3.2, Grupo 2).
//
// La tabla DP es O(n×m) en tiempo y espacio,
// por lo que se aplica un límite razonable de
// longitud (300 aminoácidos por secuencia,
// configurable) para mantener la respuesta
// instantánea en el navegador.
// ==========================================

const MATCH_SCORE = 2;
const MISMATCH_SCORE = -1;
const GAP_SCORE = -2;

function needlemanWunsch(seq1, seq2) {
  const n = seq1.length;
  const m = seq2.length;

  // Tabla DP (Float32Array por fila para eficiencia de memoria)
  const dp = Array.from({ length: n + 1 }, () => new Int32Array(m + 1));

  for (let i = 0; i <= n; i++) dp[i][0] = i * GAP_SCORE;
  for (let j = 0; j <= m; j++) dp[0][j] = j * GAP_SCORE;

  for (let i = 1; i <= n; i++) {
    for (let j = 1; j <= m; j++) {
      const scoreDiag = seq1[i - 1] === seq2[j - 1] ? MATCH_SCORE : MISMATCH_SCORE;
      const diagonal = dp[i - 1][j - 1] + scoreDiag;
      const arriba = dp[i - 1][j] + GAP_SCORE;
      const izquierda = dp[i][j - 1] + GAP_SCORE;
      dp[i][j] = Math.max(diagonal, arriba, izquierda);
    }
  }

  // Traceback
  let alin1 = [];
  let alin2 = [];
  let i = n, j = m;

  while (i > 0 || j > 0) {
    if (i > 0 && j > 0) {
      const scoreDiag = seq1[i - 1] === seq2[j - 1] ? MATCH_SCORE : MISMATCH_SCORE;
      if (dp[i][j] === dp[i - 1][j - 1] + scoreDiag) {
        alin1.push(seq1[i - 1]);
        alin2.push(seq2[j - 1]);
        i--; j--;
      } else if (dp[i][j] === dp[i - 1][j] + GAP_SCORE) {
        alin1.push(seq1[i - 1]);
        alin2.push("-");
        i--;
      } else {
        alin1.push("-");
        alin2.push(seq2[j - 1]);
        j--;
      }
    } else if (i > 0) {
      alin1.push(seq1[i - 1]);
      alin2.push("-");
      i--;
    } else {
      alin1.push("-");
      alin2.push(seq2[j - 1]);
      j--;
    }
  }

  alin1.reverse();
  alin2.reverse();

  return {
    scoreOptimo: dp[n][m],
    alineamiento1: alin1.join(""),
    alineamiento2: alin2.join(""),
    tablaPreview: n <= 12 && m <= 12 ? dp.map(fila => Array.from(fila)) : null,
  };
}

function ejecutarNeedlemanWunsch(gen1, gen2, limiteCaracteres = 300) {
  const s1 = obtenerSecuencia(gen1);
  const s2 = obtenerSecuencia(gen2);

  if (!s1 || !s2) {
    return { error: `No se encontró secuencia para ${!s1 ? gen1 : gen2}.` };
  }

  const seq1 = s1.sequence.slice(0, limiteCaracteres);
  const seq2 = s2.sequence.slice(0, limiteCaracteres);

  if (seq1.length * seq2.length > 200000) {
    return { error: `Las secuencias son demasiado largas para esta demostración (${seq1.length}×${seq2.length} celdas). Reduzca el límite de caracteres.` };
  }

  const inicio = performance.now();
  const resultado = needlemanWunsch(seq1, seq2);
  const tiempoMs = performance.now() - inicio;

  const matches = [...resultado.alineamiento1].filter((c, idx) => c === resultado.alineamiento2[idx] && c !== "-").length;
  const gaps = (resultado.alineamiento1.match(/-/g) || []).length + (resultado.alineamiento2.match(/-/g) || []).length;
  const identidad = resultado.alineamiento1.length > 0 ? (matches / resultado.alineamiento1.length) * 100 : 0;

  return {
    gen1, gen2,
    longitudComparada1: seq1.length,
    longitudComparada2: seq2.length,
    longitudReal1: s1.sequence.length,
    longitudReal2: s2.sequence.length,
    truncado: s1.sequence.length > limiteCaracteres || s2.sequence.length > limiteCaracteres,
    scoreOptimo: resultado.scoreOptimo,
    alineamiento1: resultado.alineamiento1,
    alineamiento2: resultado.alineamiento2,
    matches, gaps, identidad,
    tiempoMs,
    tablaPreview: resultado.tablaPreview,
  };
}
