// ==========================================
// BIONET ANALYZER — LÓGICA FRONTEND
// ==========================================

// Instancia global de Cytoscape
let cy = null;

// Algoritmo actualmente activo
let algoActivo = null;

// ==========================================
// CONFIGURACIÓN POR ALGORITMO
// ==========================================

const CONFIG = {
  dyv: {
    titulo: "Divide y Vencerás — Interacción máxima",
    desc: "Encuentra recursivamente la arista con mayor peso de interacción biológica en el dataset de proteínas.",
    badges: [
      { texto: "O(n log n)", clase: "badge-teal" },
      { texto: "Máximo peso", clase: "badge-neutral" }
    ],
    colorNodo: "#5DCAA5",
    colorArista: "#D3D1C7",
    colorDestacado: "#D85A30",
    layout: "cose"
  },
  dfs: {
    titulo: "DFS — Búsqueda en profundidad desde MYC",
    desc: "Recorre la red de proteínas usando una pila LIFO, explorando cada camino hasta su fin antes de retroceder.",
    badges: [
      { texto: "O(V + E)", clase: "badge-teal" },
      { texto: "Desde MYC", clase: "badge-neutral" }
    ],
    colorNodo: "#AFA9EC",
    colorArista: "#D3D1C7",
    colorDestacado: "#534AB7",
    layout: "breadthfirst"
  },
  scc: {
    titulo: "SCC (Tarjan) — Componentes fuertemente conexas",
    desc: "Detecta grupos de proteínas que se regulan mutuamente mediante caminos bidireccionales. Cada grupo puede representar un módulo funcional.",
    badges: [
      { texto: "O(V + E)", clase: "badge-teal" },
      { texto: "Tarjan", clase: "badge-neutral" }
    ],
    colorNodo: "#5DCAA5",
    colorArista: "#D3D1C7",
    colorDestacado: "#0F6E56",
    layout: "circle"
  },
  backtracking: {
    titulo: "Backtracking — Árbol de alineamiento RFC2 / RFC4",
    desc: "Explora todas las formas posibles de alinear dos secuencias biológicas: match directo, gap en seq1 o gap en seq2.",
    badges: [
      { texto: "RFC2 / RFC4", clase: "badge-teal" },
      { texto: "Árbol recursivo", clase: "badge-neutral" }
    ],
    colorNodo: "#F0997B",
    colorArista: "#D3D1C7",
    colorDestacado: "#993C1D",
    layout: "dagre"
  },
  fuerza_bruta: {
    titulo: "Fuerza Bruta — Similitud entre proteínas",
    desc: "Compara carácter por carácter los nombres de proteínas y conecta aquellas con similitud ≥ 50%. Sirve como baseline de validación.",
    badges: [
      { texto: "Similitud ≥ 50%", clase: "badge-teal" },
      { texto: "300 primeras filas", clase: "badge-neutral" }
    ],
    colorNodo: "#EF9F27",
    colorArista: "#D3D1C7",
    colorDestacado: "#BA7517",
    layout: "cose"
  },
  ufsd: {
    titulo: "UFSD — Union-Find, agrupación de proteínas",
    desc: "Agrupa proteínas en conjuntos disjuntos usando compresión de camino. Visualiza el subgrafo del grupo más grande detectado.",
    badges: [
      { texto: "O(α·n)", clase: "badge-teal" },
      { texto: "Grupo mayor", clase: "badge-neutral" }
    ],
    colorNodo: "#AFA9EC",
    colorArista: "#D3D1C7",
    colorDestacado: "#534AB7",
    layout: "cose"
  },
  mst: {
    titulo: "MST (Kruskal) — Relaciones evolutivas mínimas",
    desc: "Construye el árbol de expansión mínima de la red biológica. Conecta todas las proteínas usando el menor peso total posible, revelando las relaciones evolutivas esenciales.",
    badges: [
      { texto: "O(E log E)", clase: "badge-teal" },
      { texto: "Kruskal", clase: "badge-neutral" }
    ],
    colorNodo: "#5DCAA5",
    colorArista: "#5DCAA5",
    colorDestacado: "#085041",
    layout: "cose"
  },
  flujo_maximo: {
    titulo: "Flujo Máximo — Rutas metabólicas (Ford-Fulkerson)",
    desc: "Calcula el flujo máximo entre las dos proteínas hub de la red. Las rutas encontradas representan caminos de señalización metabólica de mayor capacidad.",
    badges: [
      { texto: "Ford-Fulkerson", clase: "badge-teal" },
      { texto: "Rutas metabólicas", clase: "badge-neutral" }
    ],
    colorNodo: "#AFA9EC",
    colorArista: "#AFA9EC",
    colorDestacado: "#D85A30",
    layout: "breadthfirst"
  },
  voraz: {
    titulo: "Voraz — Alineamiento heurístico de proteínas",
    desc: "Aplica una estrategia greedy para alinear secuencias de proteínas carácter a carácter. Toma la decisión localmente óptima en cada posición: match (+2), mismatch (-1) o gap (-2).",
    badges: [
      { texto: "O(n)", clase: "badge-teal" },
      { texto: "Heurístico", clase: "badge-neutral" }
    ],
    colorNodo: "#EF9F27",
    colorArista: "#D3D1C7",
    colorDestacado: "#BA7517",
    layout: "cose"
  },
  dp: {
    titulo: "DP — Needleman-Wunsch (Alineamiento global óptimo)",
    desc: "Algoritmo clásico de programación dinámica para alineamiento global. Garantiza el alineamiento óptimo entre dos secuencias proteicas llenando una tabla de puntuaciones y aplicando traceback.",
    badges: [
      { texto: "O(n·m)", clase: "badge-teal" },
      { texto: "Óptimo garantizado", clase: "badge-neutral" }
    ],
    colorNodo: "#5DCAA5",
    colorArista: "#D3D1C7",
    colorDestacado: "#085041",
    layout: "cose"
  },
  dp_en_grafo: {
    titulo: "DP en Grafos — Camino óptimo (Bellman-Ford)",
    desc: "Programación dinámica sobre la estructura del grafo biológico. Encuentra el camino de mayor peso acumulado entre las proteínas hub, maximizando la fuerza de señalización.",
    badges: [
      { texto: "O(V·E)", clase: "badge-teal" },
      { texto: "Bellman-Ford Max", clase: "badge-neutral" }
    ],
    colorNodo: "#AFA9EC",
    colorArista: "#5DCAA5",
    colorDestacado: "#534AB7",
    layout: "breadthfirst"
  }
};

// ==========================================
// LAYOUTS DE CYTOSCAPE
// ==========================================

function getLayout(tipo) {
  const base = { animate: true, animationDuration: 500, fit: true, padding: 40 };

  switch (tipo) {
    case "breadthfirst":
      return { ...base, name: "breadthfirst", directed: true, spacingFactor: 1.4 };
    case "circle":
      return { ...base, name: "circle", spacingFactor: 1.2 };
    case "dagre":
      return { ...base, name: "breadthfirst", directed: true, roots: "#0", spacingFactor: 1.5 };
    case "cose":
    default:
      return { ...base, name: "cose", nodeRepulsion: 8000, idealEdgeLength: 80, gravity: 0.25 };
  }
}

// ==========================================
// FUNCIÓN PRINCIPAL: CARGAR ALGORITMO
// ==========================================

async function cargarAlgoritmo(algo, btnEl) {
  if (algoActivo === algo) return;
  algoActivo = algo;

  const cfg = CONFIG[algo];

  // Marcar botón activo
  document.querySelectorAll(".algo-btn").forEach(b => b.classList.remove("active"));
  btnEl.classList.add("active");

  // Actualizar header
  document.getElementById("graph-title").textContent = cfg.titulo;
  document.getElementById("graph-desc").textContent = cfg.desc;

  const badgesEl = document.getElementById("graph-badges");
  badgesEl.innerHTML = cfg.badges
    .map(b => `<span class="badge ${b.clase}">${b.texto}</span>`)
    .join("");

  // Mostrar estado de carga
  mostrarOverlay(true, "Ejecutando algoritmo…");
  ocultarEmpty();
  document.getElementById("graph-controls").style.display = "none";

  // Limpiar grafo anterior
  if (cy) { cy.destroy(); cy = null; }

  try {
    // Llamar al endpoint de Flask
    const res = await fetch(`/api/${algo}`);
    if (!res.ok) throw new Error(`Error ${res.status}`);
    const data = await res.json();

    // Renderizar grafo
    renderizarGrafo(data, cfg);

    // Actualizar panel de resultados
    actualizarResultados(data, algo);

    // Mostrar controles
    document.getElementById("graph-controls").style.display = "flex";

  } catch (err) {
    mostrarOverlay(false);
    mostrarError(err.message);
  }
}

// ==========================================
// RENDERIZAR GRAFO CON CYTOSCAPE
// ==========================================

function renderizarGrafo(data, cfg) {
  // Construir elementos de Cytoscape
  const elementos = [];

  // Nodos
  if (data.nodos && data.nodos.length > 0) {
    data.nodos.forEach((nodo, i) => {
      const id   = typeof nodo === "object" ? String(nodo.id) : nodo;
      const label = typeof nodo === "object" ? (nodo.label || id) : nodo;
      const prof  = typeof nodo === "object" ? (nodo.profundidad || 0) : 0;

      elementos.push({
        data: { id, label, profundidad: prof }
      });
    });
  }

  // Aristas
  if (data.aristas && data.aristas.length > 0) {
    data.aristas.forEach((arista, i) => {
      const src = String(arista.source);
      const tgt = String(arista.target);
      const esMax = arista.es_maxima || false;
      const peso  = arista.weight || arista.similitud || "";

      elementos.push({
        data: {
          id: `e${i}`,
          source: src,
          target: tgt,
          es_maxima: esMax,
          peso
        }
      });
    });
  }

  // Inicializar Cytoscape
  cy = cytoscape({
    container: document.getElementById("cy"),
    elements: elementos,
    style: estilosCytoscape(cfg),
    layout: getLayout(cfg.layout),
    minZoom: 0.2,
    maxZoom: 4
  });

  // Tooltip al hacer hover en nodo
  cy.on("mouseover", "node", evt => {
    const nodo = evt.target;
    nodo.style("border-width", "3px");
    nodo.style("border-color", "#1A1A18");
  });

  cy.on("mouseout", "node", evt => {
    const nodo = evt.target;
    nodo.style("border-width", "2px");
    nodo.style("border-color", "rgba(0,0,0,0.15)");
  });

  // Ocultar overlay cuando el layout termina
  cy.one("layoutstop", () => {
    mostrarOverlay(false);
    actualizarCtrlInfo(data);
  });
}

// ==========================================
// ESTILOS DE CYTOSCAPE
// ==========================================

function estilosCytoscape(cfg) {
  return [
    {
      selector: "node",
      style: {
        "background-color": cfg.colorNodo,
        "label": "data(label)",
        "font-size": "10px",
        "font-family": "'Inter', sans-serif",
        "color": "#1A1A18",
        "text-valign": "center",
        "text-halign": "center",
        "text-wrap": "wrap",
        "text-max-width": "80px",
        "width": "label",
        "height": "label",
        "padding": "8px",
        "border-width": "2px",
        "border-color": "rgba(0,0,0,0.12)",
        "min-width": "40px",
        "min-height": "24px"
      }
    },
    {
      selector: "edge",
      style: {
        "line-color": cfg.colorArista,
        "width": 1.5,
        "curve-style": "bezier",
        "opacity": 0.7
      }
    },
    {
      // Arista destacada (interacción máxima en D&V)
      selector: "edge[?es_maxima]",
      style: {
        "line-color": cfg.colorDestacado,
        "width": 4,
        "opacity": 1
      }
    },
    {
      selector: "node:selected",
      style: {
        "background-color": cfg.colorDestacado,
        "color": "#fff",
        "border-color": "#1A1A18",
        "border-width": "3px"
      }
    }
  ];
}

// ==========================================
// ACTUALIZAR PANEL DE RESULTADOS
// ==========================================

function actualizarResultados(data, algo) {
  const titleEl = document.getElementById("result-title");
  const statsEl = document.getElementById("result-stats");

  titleEl.textContent = data.algoritmo || algo.toUpperCase();
  titleEl.style.color = "rgba(255,255,255,0.7)";

  let html = "";

  // Resultado específico por algoritmo
  if (algo === "dyv" && data.resultado) {
    const r = data.resultado;
    html += stat("Proteína 1", r.protein1, true);
    html += stat("Proteína 2", r.protein2, true);
    html += stat("Peso máximo", r.peso.toFixed ? r.peso.toFixed(4) : r.peso, true);
  }

  if (algo === "dfs") {
    html += stat("Inicio", data.inicio, true);
    html += stat("Total recorridos", data.total_recorridos);
  }

  if (algo === "scc") {
    html += stat("Componentes SCC", data.total_componentes);
    html += stat("Ciclos biológicos", data.ciclos_biologicos, true);
  }

  if (algo === "fuerza_bruta") {
    html += stat("Tiempo", data.tiempo_segundos + " s", true);
    html += stat("Pares similares", data.total_aristas);
  }

  if (algo === "ufsd") {
    html += stat("Grupos detectados", data.total_grupos);
    html += stat("Grupo mayor", data.grupo_mayor_size + " proteínas", true);
  }

  if (algo === "mst") {
    html += stat("Aristas en MST", data.total_aristas_mst);
    html += stat("Peso total MST", data.peso_total, true);
  }

  if (algo === "flujo_maximo") {
    html += stat("Source", data.source, true);
    html += stat("Sink", data.sink, true);
    html += stat("Flujo máximo", data.flujo_maximo, true);
    html += stat("Rutas usadas", data.rutas);
  }

  if (algo === "voraz") {
    html += stat("Pares analizados", data.total_pares);
    html += stat("Pares con score > 0", data.aristas ? data.aristas.length : 0, true);
  }

  if (algo === "dp") {
    html += stat("Mejor score NW", data.mejor_score, true);
    if (data.mejor_par) {
      html += stat("Mejor par", `${data.mejor_par.p1} / ${data.mejor_par.p2}`, true);
    }
    html += stat("Pares analizados", data.total_pares);
  }

  if (algo === "dp_en_grafo") {
    html += stat("Fuente", data.fuente, true);
    html += stat("Destino", data.destino, true);
    html += stat("Peso óptimo", data.peso_optimo, true);
    html += stat("Nodos en camino", data.longitud_camino);
  }

  if (algo === "backtracking") {
    html += stat("Secuencia 1", data.secuencia1);
    html += stat("Secuencia 2", data.secuencia2);
    html += stat("Nodos en árbol", data.nodos.length, true);
  }

  // Siempre mostrar nodos y aristas del subgrafo
  html += stat("Nodos (subgrafo)", data.nodos ? data.nodos.length : 0);
  html += stat("Aristas (subgrafo)", data.aristas ? data.aristas.length : 0);

  statsEl.innerHTML = html;
}

// Helper para filas de estadísticas
function stat(label, value, highlight = false) {
  return `
    <div class="stat-row">
      <span class="stat-label">${label}</span>
      <span class="stat-value ${highlight ? "highlight" : ""}">${value}</span>
    </div>`;
}

// ==========================================
// UTILIDADES DE UI
// ==========================================

function mostrarOverlay(visible, msg = "") {
  const el = document.getElementById("graph-overlay");
  const msgEl = document.getElementById("overlay-msg");
  el.classList.toggle("visible", visible);
  if (msg) msgEl.textContent = msg;
}

function ocultarEmpty() {
  document.getElementById("graph-empty").classList.add("hidden");
}

function mostrarError(msg) {
  const statsEl = document.getElementById("result-stats");
  statsEl.innerHTML = `<p class="result-hint" style="color:#F0997B">Error: ${msg}<br>Verifica que Flask esté corriendo y el CSV cargado.</p>`;
}

function actualizarCtrlInfo(data) {
  const nodos   = data.nodos   ? data.nodos.length   : 0;
  const aristas = data.aristas ? data.aristas.length : 0;
  document.getElementById("ctrl-info").textContent =
    `${nodos} nodos · ${aristas} aristas`;
}