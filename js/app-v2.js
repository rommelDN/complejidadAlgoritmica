// ==========================================
// APP-V2.JS — NAVEGACIÓN Y LÓGICA PRINCIPAL
// ==========================================

document.addEventListener("DOMContentLoaded", () => {
  inyectarVistasPreguntas();
  inicializarNavegacionPreguntas();
  inicializarCarga();
  inicializarManejadorRanking();
  inicializarManejadorRelacion();
  inicializarManejadorEquipos();
  inicializarManejadorProfundo();
});

// ------------------------------------------
// NAVEGACIÓN
// ------------------------------------------
function inicializarNavegacionPreguntas() {
  document.querySelectorAll(".pregunta-card").forEach(card => {
    card.addEventListener("click", () => irAVista(card.dataset.vista));
  });

  document.querySelectorAll("[data-volver]").forEach(btn => {
    btn.addEventListener("click", volverAInicio);
  });
}

function irAVista(viewId) {
  document.getElementById("vista-inicio").style.display = "none";
  document.querySelectorAll(".vista-pregunta").forEach(v => v.classList.remove("active"));
  document.getElementById(viewId).classList.add("active");
  window.scrollTo(0, 0);
}

function volverAInicio() {
  document.querySelectorAll(".vista-pregunta").forEach(v => v.classList.remove("active"));
  document.getElementById("vista-inicio").style.display = "block";
  window.scrollTo(0, 0);
}

// ------------------------------------------
// CARGA DE DATOS
// ------------------------------------------
function inicializarCarga() {
  document.getElementById("btn-carga-automatica").addEventListener("click", async () => {
    const card = document.getElementById("carga-card");
    const boton = document.getElementById("btn-carga-automatica");
    boton.textContent = "Cargando...";
    boton.disabled = true;
    try {
      await cargarDatasetsPorDefecto();
      actualizarEstadoCarga();
      refrescarSelectoresProteinas();
      boton.textContent = "Datos cargados";
      card.style.borderColor = "var(--accent-dim)";
    } catch (err) {
      boton.textContent = "Reintentar carga";
      boton.disabled = false;
      alert("No se pudieron cargar los datos automáticamente. Verifique que la carpeta data/ esté junto a index.html.");
    }
  });
}

function actualizarEstadoCarga() {
  const elRed = document.getElementById("status-red");
  const elSeq = document.getElementById("status-seq");
  if (DataStore.ready.red) {
    elRed.textContent = `red: ${DataStore.nodes.size} proteínas`;
    elRed.classList.add("ok");
  }
  if (DataStore.ready.secuencias) {
    elSeq.textContent = `secuencias: ${DataStore.sequences.size}`;
    elSeq.classList.add("ok");
  }
}

function refrescarSelectoresProteinas() {
  const listaGenes = Array.from(DataStore.nodes).sort();
  const listaGenesConSecuencia = listaGenes.filter(g => DataStore.sequences.has(g));

  const idsSoloRed = ["rel-proteina1", "rel-proteina2", "explorar-proteina"];
  const idsConSecuencia = ["prof-proteina1", "prof-proteina2"];

  for (const id of idsSoloRed) {
    const sel = document.getElementById(id);
    if (!sel) continue;
    const placeholder = sel.options[0].outerHTML;
    sel.innerHTML = placeholder + listaGenes.map(g => `<option value="${g}">${g}</option>`).join("");
  }
  for (const id of idsConSecuencia) {
    const sel = document.getElementById(id);
    if (!sel) continue;
    const placeholder = sel.options[0].outerHTML;
    sel.innerHTML = placeholder + listaGenesConSecuencia.map(g => `<option value="${g}">${g}</option>`).join("");
  }
}

function datosListos(contenedorId) {
  if (!DataStore.ready.red) {
    document.getElementById(contenedorId).innerHTML =
      '<div class="error-banner">Primero cargue los datos desde la pantalla de inicio (botón "Cargar datos de ejemplo").</div>';
    return false;
  }
  return true;
}

// ==========================================
// PREGUNTA 1 — RANKING
// ==========================================
function inicializarManejadorRanking() {
  document.getElementById("ranking-ejecutar").addEventListener("click", () => {
    if (!datosListos("ranking-resultado")) return;
    const limite = parseInt(document.getElementById("ranking-limite").value, 10) || 15;

    document.getElementById("ranking-resultado").innerHTML = '<div class="loading-state"><div class="spinner"></div>Analizando la red completa...</div>';

    setTimeout(() => {
      const r = calcularRankingProteinasCriticas(0.7, 500); // traemos más para poder separar categorías
      if (r.error) {
        document.getElementById("ranking-resultado").innerHTML = `<div class="error-banner">${r.error}</div>`;
        return;
      }

      const conectoresGenerales = r.ranking.filter(p => p.criterioA && !p.criterioB);
      const especialistas = r.ranking.filter(p => p.criterioB);
      const otros = r.ranking.filter(p => !p.criterioA && !p.criterioB);

      const mitad = Math.ceil(limite / 2);
      const mostrarConectores = conectoresGenerales.slice(0, Math.max(mitad, limite - especialistas.length));
      const mostrarEspecialistas = especialistas.slice(0, limite - mostrarConectores.length);

      const tarjetaProteina = (p, i) => {
        const explicacion = explicarProteinaCritica(p, r.totalProteinasEvaluadas, i);
        return `
          <div class="proteina-card">
            <div class="proteina-rank">${i + 1}</div>
            <div>
              <p class="proteina-nombre">${p.proteina}</p>
              <p class="proteina-explicacion">${explicacion}</p>
            </div>
          </div>
        `;
      };

      let bloques = `
        <div class="respuesta-card">
          <p>De las <strong>${r.totalProteinasEvaluadas.toLocaleString("es")}</strong> proteínas analizadas, <strong>${r.totalProteinasCriticas.toLocaleString("es")}</strong> (${r.porcentajeCriticas.toFixed(1)}%) muestran evidencia suficiente para considerarse prioritarias. Se dividen en dos grupos con perfiles distintos.</p>
        </div>
      `;

      if (mostrarConectores.length > 0) {
        bloques += `
          <h3 style="font-size:15px;font-weight:600;margin:24px 0 4px;color:var(--text-primary);">Conectores generales</h3>
          <p style="font-size:13px;color:var(--text-muted);margin:0 0 14px;">Proteínas con un número muy alto de interacciones, sin pertenecer a un equipo pequeño y específico.</p>
          ${mostrarConectores.map((p, i) => tarjetaProteina(p, i)).join("")}
        `;
      }

      if (mostrarEspecialistas.length > 0) {
        bloques += `
          <h3 style="font-size:15px;font-weight:600;margin:24px 0 4px;color:var(--text-primary);">Especialistas de equipo</h3>
          <p style="font-size:13px;color:var(--text-muted);margin:0 0 14px;">Proteínas con menos conexiones totales, pero que forman parte de un grupo pequeño y específico de trabajo conjunto.</p>
          ${mostrarEspecialistas.map((p, i) => tarjetaProteina(p, i)).join("")}
        `;
      }

      document.getElementById("ranking-resultado").innerHTML = bloques;
    }, 20);
  });
}

// ==========================================
// PREGUNTA 2 — RELACIÓN ENTRE DOS PROTEÍNAS
// ==========================================
function inicializarManejadorRelacion() {
  document.getElementById("rel-ejecutar").addEventListener("click", () => {
    if (!datosListos("rel-resultado")) return;

    const p1 = document.getElementById("rel-proteina1").value;
    const p2 = document.getElementById("rel-proteina2").value;

    if (!p1 || !p2) {
      document.getElementById("rel-resultado").innerHTML = '<div class="error-banner">Elija ambas proteínas para continuar.</div>';
      return;
    }

    document.getElementById("rel-resultado").innerHTML = '<div class="loading-state"><div class="spinner"></div>Buscando la relación entre ambas proteínas...</div>';

    setTimeout(() => {
      const r = consultarRelacionEntreProteinas(p1, p2);
      if (r.error) {
        document.getElementById("rel-resultado").innerHTML = `<div class="error-banner">${r.error}</div>`;
        return;
      }

      const claseRespuesta = (!r.conexionDirecta && !r.caminoEncontrado) ? "vacia" : "";
      const parrafos = r.explicacion.map(p => `<p>${p}</p>`).join("");

      let grafoHtml = "";
      if (r.conexionDirecta) {
        grafoHtml = `<div class="graph-container" id="rel-grafo"></div>`;
      } else if (r.caminoEncontrado && r.caminoProteinas.length <= 15) {
        grafoHtml = `<div class="graph-container" id="rel-grafo"></div>`;
      }

      document.getElementById("rel-resultado").innerHTML = `
        <div class="respuesta-card ${claseRespuesta}">
          ${parrafos}
        </div>
        ${grafoHtml}
      `;

      if (r.conexionDirecta) {
        renderizarSubgrafo("rel-grafo", [p1, p2], [{ p1, p2, weight: r.pesoConexionDirecta }], {
          nodoFuente: p1, nodoDestino: p2,
        });
      } else if (r.caminoEncontrado && r.caminoProteinas.length <= 15) {
        const aristas = [];
        for (let i = 0; i < r.caminoProteinas.length - 1; i++) {
          aristas.push({ p1: r.caminoProteinas[i], p2: r.caminoProteinas[i + 1], weight: r.pesoCamino });
        }
        renderizarSubgrafo("rel-grafo", r.caminoProteinas, aristas, {
          nodoFuente: p1, nodoDestino: p2,
          resaltarAristas: () => true,
        });
      }
    }, 20);
  });
}

// ==========================================
// PREGUNTA 3 — EQUIPOS DE PROTEÍNAS
// ==========================================
function inicializarManejadorEquipos() {
  const sliderUmbral = document.getElementById("equipos-umbral");
  const valorUmbral = document.getElementById("equipos-umbral-valor");
  sliderUmbral.addEventListener("input", () => {
    const v = parseFloat(sliderUmbral.value);
    valorUmbral.textContent = v.toFixed(2) + (v >= 0.95 ? " (más específico)" : v <= 0.8 ? " (más amplio)" : "");
  });

  document.getElementById("equipos-ejecutar").addEventListener("click", () => {
    if (!datosListos("equipos-resultado")) return;
    const umbral = parseFloat(sliderUmbral.value);

    document.getElementById("equipos-resultado").innerHTML = '<div class="loading-state"><div class="spinner"></div>Buscando equipos de proteínas...</div>';
    document.getElementById("equipos-detalle").innerHTML = "";

    setTimeout(() => {
      const r = identificarEquiposDeProteinas(umbral, 4);
      if (r.error) {
        document.getElementById("equipos-resultado").innerHTML = `<div class="error-banner">${r.error}</div>`;
        return;
      }

      if (r.equipos.length === 0) {
        document.getElementById("equipos-resultado").innerHTML = `
          <div class="respuesta-card alerta">
            <p>Con este nivel de especificidad no se encontraron equipos de al menos 4 proteínas. Reduzca la especificidad (mueva el control hacia la izquierda) para encontrar grupos más amplios.</p>
          </div>
        `;
        return;
      }

      const tarjetasEquipos = r.equipos.map(eq => `
        <div class="equipo-card" data-equipo-id="${eq.id}">
          <p class="equipo-nombre">${eq.nombre}</p>
          <p class="equipo-meta">${eq.tamano} proteínas · liderado en conexiones por ${eq.proteinaPrincipal}</p>
          <p class="equipo-miembros">${eq.miembros.join(", ")}</p>
        </div>
      `).join("");

      document.getElementById("equipos-resultado").innerHTML = `
        <div class="respuesta-card">
          <p>Se identificaron <strong>${r.totalEquipos}</strong> equipos de proteínas con este nivel de especificidad. El resto de la red (${r.tamanoGrupoGigante.toLocaleString("es")} proteínas, ${r.porcentajeFueraDeEquipos.toFixed(0)}%) está demasiado interconectado entre sí como para formar grupos claramente diferenciados — esto es normal: muchas proteínas tienen un rol general en vez de pertenecer a un equipo específico.</p>
        </div>
        ${tarjetasEquipos}
      `;

      document.querySelectorAll(".equipo-card").forEach(card => {
        card.addEventListener("click", () => {
          const eq = r.equipos.find(e => e.id === parseInt(card.dataset.equipoId, 10));
          mostrarDetalleEquipo(eq);
        });
      });
    }, 20);
  });
}

function mostrarDetalleEquipo(equipo) {
  const subgrafo = obtenerSubgrafoDeEquipo(equipo.miembros, 30);
  document.getElementById("equipos-detalle").innerHTML = `
    <div class="form-card">
      <p class="proteina-nombre" style="margin-bottom:4px;">${equipo.nombre}</p>
      <p class="proteina-explicacion" style="margin-bottom:0;">Estas ${equipo.tamano} proteínas están conectadas entre sí con un nivel de confianza alto, lo que sugiere que trabajan de forma conjunta en una función biológica específica.</p>
      <div class="graph-container" id="equipo-grafo-detalle"></div>
    </div>
  `;
  renderizarSubgrafo("equipo-grafo-detalle", subgrafo.nodos, subgrafo.aristas, {});
  document.getElementById("equipos-detalle").scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// ==========================================
// PREGUNTA 4 — COMPARACIÓN PROFUNDA + EXPLORAR VECINDARIO
// Usa los 5 algoritmos que no participan en las
// preguntas 1-3: backtracking, divide y vencerás
// sobre secuencias, voraz, DP (Needleman-Wunsch),
// DFS y divide y vencerás sobre la red.
// ==========================================

function inicializarManejadorProfundo() {
  document.getElementById("prof-ejecutar").addEventListener("click", () => {
    if (!datosListos("prof-resultado")) return;
    const p1 = document.getElementById("prof-proteina1").value;
    const p2 = document.getElementById("prof-proteina2").value;

    if (!p1 || !p2) {
      document.getElementById("prof-resultado").innerHTML = '<div class="error-banner">Elija ambas proteínas para continuar.</div>';
      return;
    }
    if (p1 === p2) {
      document.getElementById("prof-resultado").innerHTML = '<div class="error-banner">Elija dos proteínas distintas.</div>';
      return;
    }

    document.getElementById("prof-resultado").innerHTML = '<div class="loading-state"><div class="spinner"></div>Aplicando los cuatro métodos de comparación...</div>';

    setTimeout(() => {
      const fb = ejecutarFuerzaBruta(p1, p2, 300);
      const dp = ejecutarNeedlemanWunsch(p1, p2, 300);
      const vz = ejecutarVoraz(p1, p2, 300, false);
      const dyv = ejecutarDivideYVenceresSecuencia(p1, p2, 20, 300);
      const bt = ejecutarBacktracking(p1, p2, 6, 12);

      if (fb.error || dp.error) {
        document.getElementById("prof-resultado").innerHTML = `<div class="error-banner">${fb.error || dp.error}</div>`;
        return;
      }

      const metodos = [
        {
          nombre: "Comparación directa",
          resultado: `${fb.similitud.toFixed(1)}% de coincidencia`,
          tiempo: fb.tiempoMs,
          detalle: "Compara las dos secuencias posición por posición, sin ningún ajuste. Es el método más simple y rápido, pero el más sensible a pequeños desplazamientos.",
        },
        {
          nombre: "Comparación por bloques",
          resultado: `${dyv.similitudGlobal.toFixed(1)}% de coincidencia`,
          tiempo: dyv.tiempoMs,
          detalle: `Divide cada secuencia en ${dyv.cantidadFragmentos} bloques más pequeños y los compara por separado antes de combinar el resultado. Da una idea de qué tramos se parecen más entre sí.`,
        },
        {
          nombre: "Alineamiento rápido (aproximado)",
          resultado: `${vz.identidad.toFixed(1)}% de identidad`,
          tiempo: vz.tiempoMs,
          detalle: "Permite pequeños desplazamientos para encontrar mejores coincidencias, decidiendo en cada paso lo que parece mejor en el momento. Es rápido, pero no garantiza encontrar el mejor alineamiento posible.",
        },
        {
          nombre: "Alineamiento exacto (óptimo)",
          resultado: `${dp.identidad.toFixed(1)}% de identidad`,
          tiempo: dp.tiempoMs,
          detalle: "Evalúa sistemáticamente todas las formas posibles de alinear ambas secuencias y garantiza encontrar la mejor combinación posible. Es el método más confiable, a cambio de ser más lento.",
        },
      ];

      const masRapido = metodos.reduce((a, b) => a.tiempo < b.tiempo ? a : b);
      const exacto = metodos[3];

      const tarjetasMetodos = metodos.map(m => `
        <div class="proteina-card">
          <div>
            <p class="proteina-nombre" style="font-size:14.5px;">${m.nombre}</p>
            <p class="proteina-explicacion">${m.detalle}</p>
            <div class="proteina-badges">
              <span class="badge activo">${m.resultado}</span>
              <span class="badge">${m.tiempo < 1 ? m.tiempo.toFixed(2) : m.tiempo.toFixed(1)} ms</span>
            </div>
          </div>
        </div>
      `).join("");

      document.getElementById("prof-resultado").innerHTML = `
        <div class="respuesta-card">
          <p>Se compararon ${p1} y ${p2} con cuatro métodos distintos. El método <strong>${masRapido.nombre.toLowerCase()}</strong> fue el más rápido (${masRapido.tiempo.toFixed(2)} ms), mientras que el <strong>alineamiento exacto</strong> es el único que garantiza haber encontrado la mejor combinación posible, a cambio de tardar más (${exacto.tiempo.toFixed(1)} ms). Según este último, la identidad real entre ambas secuencias es de ${dp.identidad.toFixed(1)}%.</p>
        </div>
        ${tarjetasMetodos}
        <div class="form-card" style="margin-top:14px;">
          <p style="font-size:13px;color:var(--text-muted);margin:0;">También se construyó un árbol con las combinaciones posibles de alineamiento para los primeros 12 aminoácidos de cada proteína (método de exploración exhaustiva limitada): se generaron ${bt.totalNodosArbol} combinaciones distintas en ${bt.tiempoMs.toFixed(2)} ms. Este crecimiento tan rápido es la razón por la que el método de alineamiento exacto evita probar todas las combinaciones una por una.</p>
        </div>
      `;
    }, 20);
  });

  document.getElementById("explorar-ejecutar").addEventListener("click", () => {
    if (!datosListos("explorar-resultado")) return;
    const proteina = document.getElementById("explorar-proteina").value;

    if (!proteina) {
      document.getElementById("explorar-resultado").innerHTML = '<div class="error-banner">Elija una proteína de partida.</div>';
      return;
    }

    const dfsResultado = ejecutarDFS(proteina, 18);
    if (dfsResultado.error) {
      document.getElementById("explorar-resultado").innerHTML = `<div class="error-banner">${dfsResultado.error}</div>`;
      return;
    }

    const dyvRed = ejecutarDivideYVenceras();

    document.getElementById("explorar-resultado").innerHTML = `
      <div class="respuesta-card">
        <p>Partiendo de <strong>${proteina}</strong> y explorando paso a paso, se puede llegar a un total de <strong>${dfsResultado.totalRecorridos.toLocaleString("es")}</strong> proteínas dentro de la red — prácticamente toda ella, lo cual confirma que el sistema está muy interconectado. A continuación se muestra el vecindario más cercano (las primeras proteínas que se alcanzan).</p>
        <p style="margin-top:12px;">Como dato de referencia: la relación más fuerte registrada en toda la red, sin importar qué proteína se elija, es entre <strong>${dyvRed.p1Max}</strong> y <strong>${dyvRed.p2Max}</strong>, con un nivel de confianza de ${(dyvRed.pesoMax * 100).toFixed(1)}%.</p>
      </div>
      <div class="graph-container" id="explorar-grafo"></div>
    `;

    renderizarSubgrafo("explorar-grafo", dfsResultado.subgrafo.nodos, dfsResultado.subgrafo.aristas, {
      resaltarNodos: new Set([proteina]),
    });
  });
}
