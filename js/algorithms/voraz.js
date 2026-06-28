// ==========================================
// VORAZ — ALINEAMIENTO HEURÍSTICO
// Reescrito a partir de voraz.py
//
// CORRECCIÓN respecto a la versión Python
// original: voraz.py alineaba los nombres de
// gen, no las secuencias biológicas reales.
// Esta versión opera sobre secuencias_proteinas.fasta,
// y además reporta el score junto al de
// Needleman-Wunsch para el mismo par, de forma
// que la interfaz pueda mostrar directamente la
// comparación de velocidad/precisión descrita
// en la sección 4.3 del informe.
// ==========================================

function alineamientoVoraz(seq1, seq2) {
  const alin1 = [];
  const alin2 = [];
  let score = 0;
  let i = 0, j = 0;
  const ops = [];

  while (i < seq1.length && j < seq2.length) {
    if (seq1[i] === seq2[j]) {
      alin1.push(seq1[i]);
      alin2.push(seq2[j]);
      score += MATCH_SCORE;
      ops.push("M");
    } else {
      alin1.push(seq1[i]);
      alin2.push(seq2[j]);
      score += MISMATCH_SCORE;
      ops.push("X");
    }
    i++; j++;
  }

  while (i < seq1.length) {
    alin1.push(seq1[i]);
    alin2.push("-");
    score += GAP_SCORE;
    ops.push("G");
    i++;
  }
  while (j < seq2.length) {
    alin1.push("-");
    alin2.push(seq2[j]);
    score += GAP_SCORE;
    ops.push("G");
    j++;
  }

  return { alin1: alin1.join(""), alin2: alin2.join(""), score, ops };
}

function ejecutarVoraz(gen1, gen2, limiteCaracteres = 300, compararConDP = true) {
  const s1 = obtenerSecuencia(gen1);
  const s2 = obtenerSecuencia(gen2);

  if (!s1 || !s2) {
    return { error: `No se encontró secuencia para ${!s1 ? gen1 : gen2}.` };
  }

  const seq1 = s1.sequence.slice(0, limiteCaracteres);
  const seq2 = s2.sequence.slice(0, limiteCaracteres);

  const inicio = performance.now();
  const { alin1, alin2, score, ops } = alineamientoVoraz(seq1, seq2);
  const tiempoMs = performance.now() - inicio;

  const matches = ops.filter(o => o === "M").length;
  const mismatches = ops.filter(o => o === "X").length;
  const gaps = ops.filter(o => o === "G").length;
  const identidad = ops.length > 0 ? (matches / ops.length) * 100 : 0;

  const resultado = {
    gen1, gen2,
    longitudComparada: Math.max(seq1.length, seq2.length),
    score, matches, mismatches, gaps, identidad,
    alineamiento1: alin1, alineamiento2: alin2,
    tiempoMs,
  };

  if (compararConDP) {
    const dpResultado = ejecutarNeedlemanWunsch(gen1, gen2, limiteCaracteres);
    if (!dpResultado.error) {
      resultado.comparacionDP = {
        scoreDP: dpResultado.scoreOptimo,
        tiempoMsDP: dpResultado.tiempoMs,
        diferenciaScore: dpResultado.scoreOptimo - score,
        vorazEsOptimo: dpResultado.scoreOptimo === score,
      };
    }
  }

  return resultado;
}
