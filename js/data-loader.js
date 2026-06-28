// ==========================================
// MÓDULO DE CARGA DE DATOS
// Lee y parsea los dos datasets del proyecto:
//  - grafo_biologico_1500.csv  (red de interacción)
//  - secuencias_proteinas.fasta (secuencias de aminoácidos)
// ==========================================

const DataStore = {
  edges: [],          // [{p1, p2, weight}]
  nodes: new Set(),   // nombres de proteína únicos
  adjacency: new Map(),     // nodo -> [{neighbor, weight}]
  sequences: new Map(),     // gen -> {accession, sequence, organism}
  degree: new Map(),  // nodo -> grado (cantidad de conexiones)
  ready: { red: false, secuencias: false },
};

// ------------------------------------------
// PARSEAR CSV DE LA RED
// ------------------------------------------
function parseRedCSV(text) {
  DataStore.edges = [];
  DataStore.nodes = new Set();
  DataStore.adjacency = new Map();
  DataStore.degree = new Map();

  const seenPairs = new Set(); // para deduplicar A-B y B-A
  const lines = text.split(/\r?\n/).filter(l => l.trim().length > 0);

  // Saltar encabezado
  for (let i = 1; i < lines.length; i++) {
    const parts = lines[i].split(",");
    if (parts.length < 3) continue;
    const p1 = parts[0].trim();
    const p2 = parts[1].trim();
    const weight = parseFloat(parts[2]);
    if (!p1 || !p2 || Number.isNaN(weight)) continue;

    // Deduplicar: solo guardamos una vez cada par no dirigido
    const key = p1 < p2 ? `${p1}|${p2}` : `${p2}|${p1}`;
    if (seenPairs.has(key)) continue;
    seenPairs.add(key);

    DataStore.edges.push({ p1, p2, weight });
    DataStore.nodes.add(p1);
    DataStore.nodes.add(p2);

    if (!DataStore.adjacency.has(p1)) DataStore.adjacency.set(p1, []);
    if (!DataStore.adjacency.has(p2)) DataStore.adjacency.set(p2, []);
    DataStore.adjacency.get(p1).push({ neighbor: p2, weight });
    DataStore.adjacency.get(p2).push({ neighbor: p1, weight });

    DataStore.degree.set(p1, (DataStore.degree.get(p1) || 0) + 1);
    DataStore.degree.set(p2, (DataStore.degree.get(p2) || 0) + 1);
  }

  DataStore.ready.red = true;
  return {
    nodos: DataStore.nodes.size,
    aristas: DataStore.edges.length,
  };
}

// ------------------------------------------
// PARSEAR FASTA DE SECUENCIAS
// Formato esperado: >GEN|ACCESSION seguido de la secuencia en una línea
// ------------------------------------------
function parseSecuenciasFASTA(text) {
  DataStore.sequences = new Map();
  const lines = text.split(/\r?\n/);

  let currentGene = null;
  let currentAccession = null;

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) continue;

    if (line.startsWith(">")) {
      const header = line.slice(1);
      const [gene, accession] = header.split("|");
      currentGene = gene ? gene.trim() : header.trim();
      currentAccession = accession ? accession.trim() : "";
    } else if (currentGene) {
      // Si el gen tiene isoformas duplicadas, conservamos la primera
      if (!DataStore.sequences.has(currentGene)) {
        DataStore.sequences.set(currentGene, {
          accession: currentAccession,
          sequence: line,
        });
      }
      currentGene = null; // cada secuencia ocupa una sola línea en nuestro archivo
    }
  }

  DataStore.ready.secuencias = true;
  return { totalSecuencias: DataStore.sequences.size };
}

// ------------------------------------------
// UTILIDADES DE CONSULTA
// ------------------------------------------
function obtenerVecinos(nodo) {
  return DataStore.adjacency.get(nodo) || [];
}

function obtenerSecuencia(gen) {
  return DataStore.sequences.get(gen) || null;
}

function listaNodosOrdenadaPorGrado(top = null) {
  const arr = Array.from(DataStore.degree.entries())
    .sort((a, b) => b[1] - a[1]);
  return top ? arr.slice(0, top) : arr;
}

function listaGenesConSecuencia() {
  // Solo genes que están en la red Y tienen secuencia descargada
  return Array.from(DataStore.nodes).filter(n => DataStore.sequences.has(n)).sort();
}

// ------------------------------------------
// CARGA DESDE ARCHIVOS LOCALES (fetch relativo)
// ------------------------------------------
async function cargarDatasetsPorDefecto() {
  const [csvResp, fastaResp] = await Promise.all([
    fetch("data/grafo_biologico_1500.csv"),
    fetch("data/secuencias_proteinas.fasta"),
  ]);
  const csvText = await csvResp.text();
  const fastaText = await fastaResp.text();

  const redInfo = parseRedCSV(csvText);
  const secInfo = parseSecuenciasFASTA(fastaText);

  return { redInfo, secInfo };
}

// ------------------------------------------
// CARGA DESDE ARCHIVOS SUBIDOS POR EL USUARIO
// ------------------------------------------
function cargarArchivoLocal(file, tipo) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        if (tipo === "red") {
          resolve(parseRedCSV(e.target.result));
        } else {
          resolve(parseSecuenciasFASTA(e.target.result));
        }
      } catch (err) {
        reject(err);
      }
    };
    reader.onerror = reject;
    reader.readAsText(file);
  });
}
