// ==========================================
// MOTOR DE RENDERIZADO DE GRAFOS (SVG)
// Dibuja subgrafos pequeños (≤30 nodos) con
// layout circular o de fuerza simplificado,
// reutilizable por todas las vistas de
// algoritmos de red.
// ==========================================

function calcularLayoutCircular(nodos, radio = 200, cx = 320, cy = 260) {
  const pos = new Map();
  nodos.forEach((n, i) => {
    const angulo = (2 * Math.PI * i) / nodos.length - Math.PI / 2;
    pos.set(n, {
      x: cx + radio * Math.cos(angulo),
      y: cy + radio * Math.sin(angulo),
    });
  });
  return pos;
}

// Layout de fuerza simplificado (Fruchterman-Reingold básico),
// suficiente para subgrafos de hasta ~30 nodos sin depender de librerías externas.
function calcularLayoutFuerza(nodos, aristas, ancho = 640, alto = 480, iteraciones = 150) {
  const pos = new Map();
  const vel = new Map();
  nodos.forEach((n) => {
    pos.set(n, { x: ancho / 2 + (Math.random() - 0.5) * 300, y: alto / 2 + (Math.random() - 0.5) * 300 });
    vel.set(n, { x: 0, y: 0 });
  });

  const k = Math.sqrt((ancho * alto) / Math.max(nodos.length, 1)) * 0.9;
  const adyacenciaSet = new Set(aristas.map(a => `${a.p1}|${a.p2}`));

  for (let iter = 0; iter < iteraciones; iter++) {
    const fuerzas = new Map(nodos.map(n => [n, { x: 0, y: 0 }]));

    // Repulsión entre todos los pares
    for (let i = 0; i < nodos.length; i++) {
      for (let j = i + 1; j < nodos.length; j++) {
        const a = nodos[i], b = nodos[j];
        const pa = pos.get(a), pb = pos.get(b);
        let dx = pa.x - pb.x, dy = pa.y - pb.y;
        let dist = Math.sqrt(dx * dx + dy * dy) || 0.01;
        const fuerza = (k * k) / dist;
        const fx = (dx / dist) * fuerza;
        const fy = (dy / dist) * fuerza;
        fuerzas.get(a).x += fx; fuerzas.get(a).y += fy;
        fuerzas.get(b).x -= fx; fuerzas.get(b).y -= fy;
      }
    }

    // Atracción por arista
    for (const { p1, p2 } of aristas) {
      if (!pos.has(p1) || !pos.has(p2)) continue;
      const pa = pos.get(p1), pb = pos.get(p2);
      let dx = pa.x - pb.x, dy = pa.y - pb.y;
      let dist = Math.sqrt(dx * dx + dy * dy) || 0.01;
      const fuerza = (dist * dist) / k;
      const fx = (dx / dist) * fuerza;
      const fy = (dy / dist) * fuerza;
      fuerzas.get(p1).x -= fx; fuerzas.get(p1).y -= fy;
      fuerzas.get(p2).x += fx; fuerzas.get(p2).y += fy;
    }

    const temp = Math.max(1, 10 * (1 - iter / iteraciones));
    for (const n of nodos) {
      const f = fuerzas.get(n);
      const dist = Math.sqrt(f.x * f.x + f.y * f.y) || 0.01;
      const p = pos.get(n);
      p.x += (f.x / dist) * Math.min(dist, temp);
      p.y += (f.y / dist) * Math.min(dist, temp);
      p.x = Math.max(40, Math.min(ancho - 40, p.x));
      p.y = Math.max(40, Math.min(alto - 40, p.y));
    }
  }

  return pos;
}

// ------------------------------------------
// RENDERIZAR SUBGRAFO COMO SVG
// opciones: { resaltarNodos: Set, resaltarAristas: fn(a,b)->bool,
//             colorNodo: fn(nodo)->color, etiquetaArista: bool,
//             nodoFuente, nodoDestino }
// ------------------------------------------
function renderizarSubgrafo(contenedorId, nodos, aristas, opciones = {}) {
  const contenedor = document.getElementById(contenedorId);
  if (!contenedor) return;

  if (nodos.length === 0) {
    contenedor.innerHTML = '<div class="empty-state">No hay datos suficientes para visualizar este subgrafo.</div>';
    return;
  }

  const ancho = 680, alto = 520;
  const pos = nodos.length <= 12
    ? calcularLayoutCircular(nodos, Math.min(180, 60 + nodos.length * 8), ancho / 2, alto / 2)
    : calcularLayoutFuerza(nodos, aristas, ancho, alto, 180);

  const colorNodoFn = opciones.colorNodo || (() => "var(--accent)");
  const radioNodo = nodos.length > 20 ? 14 : nodos.length > 10 ? 18 : 24;
  const fontSize = nodos.length > 20 ? 9 : 11;

  let svg = `<svg viewBox="0 0 ${ancho} ${alto}" xmlns="http://www.w3.org/2000/svg">`;

  // Aristas primero (para que queden detrás de los nodos)
  for (const arista of aristas) {
    const pa = pos.get(arista.p1);
    const pb = pos.get(arista.p2);
    if (!pa || !pb) continue;

    const esResaltada = opciones.resaltarAristas ? opciones.resaltarAristas(arista) : false;
    const colorLinea = esResaltada ? "#D85A30" : "#3A4D3F";
    const grosor = esResaltada ? 2.5 : Math.max(0.6, (arista.weight || 0.3) * 1.8);
    const opacidad = esResaltada ? 0.95 : 0.45;

    svg += `<line x1="${pa.x.toFixed(1)}" y1="${pa.y.toFixed(1)}" x2="${pb.x.toFixed(1)}" y2="${pb.y.toFixed(1)}" stroke="${colorLinea}" stroke-width="${grosor}" opacity="${opacidad}" />`;
  }

  // Nodos
  for (const nodo of nodos) {
    const p = pos.get(nodo);
    if (!p) continue;

    let fill = colorNodoFn(nodo);
    let strokeColor = "#0E1410";

    if (opciones.nodoFuente === nodo) fill = "#D85A30";
    if (opciones.nodoDestino === nodo) fill = "#0F6E56";
    if (opciones.resaltarNodos && opciones.resaltarNodos.has(nodo)) fill = "#E8A23B";

    svg += `<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="${radioNodo}" fill="${fill}" stroke="${strokeColor}" stroke-width="2" />`;

    const etiqueta = nodo.length > 8 ? nodo.slice(0, 7) + "…" : nodo;
    svg += `<text x="${p.x.toFixed(1)}" y="${p.y.toFixed(1)}" text-anchor="middle" dominant-baseline="central" font-size="${fontSize}" font-family="IBM Plex Mono, monospace" font-weight="600" fill="#06140F">${etiqueta}</text>`;
  }

  svg += `</svg>`;
  contenedor.innerHTML = svg;
}
