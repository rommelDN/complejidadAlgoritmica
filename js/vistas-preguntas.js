// ==========================================
// VISTAS DE LAS 3 PREGUNTAS DEL INVESTIGADOR
// ==========================================

function selectorProteinas(id, conSecuencia = false, placeholder = "Buscar proteína...") {
  return `<select id="${id}"><option value="">${placeholder}</option></select>`;
}

const VISTAS_PREGUNTAS_HTML = {

  // ============ PREGUNTA 1: RANKING ============
  "vista-ranking": `
    <button class="volver-btn" data-volver="true">‹ Volver a las preguntas</button>
    <div class="pregunta-header">
      <h2>¿Qué proteínas debería priorizar?</h2>
      <p>Se identifican las proteínas con mayor evidencia combinada de importancia dentro de la red: cuántas conexiones tienen, si forman parte de un equipo de trabajo específico, y si están en la columna vertebral de relaciones más confiables del sistema.</p>
    </div>

    <div class="form-card">
      <div class="control-row">
        <div class="control-group">
          <label>Cantidad de proteínas a mostrar</label>
          <input type="number" id="ranking-limite" value="15" min="3" max="50">
        </div>
        <button class="btn" id="ranking-ejecutar">Generar lista de prioridad</button>
      </div>
    </div>

    <div id="ranking-resultado"></div>
  `,

  // ============ PREGUNTA 2: RELACIÓN ============
  "vista-relacion": `
    <button class="volver-btn" data-volver="true">‹ Volver a las preguntas</button>
    <div class="pregunta-header">
      <h2>¿Estas dos proteínas están relacionadas?</h2>
      <p>Elija dos proteínas para conocer si están conectadas directamente, cuál es la ruta más confiable entre ellas si no lo están, y qué tan parecidas son sus secuencias reales.</p>
    </div>

    <div class="form-card">
      <div class="control-row">
        <div class="control-group">
          <label>Primera proteína</label>
          ${selectorProteinas("rel-proteina1")}
        </div>
        <div class="control-group">
          <label>Segunda proteína</label>
          ${selectorProteinas("rel-proteina2")}
        </div>
        <button class="btn" id="rel-ejecutar">Consultar relación</button>
      </div>
    </div>

    <div id="rel-resultado"></div>
  `,

  // ============ PREGUNTA 3: EQUIPOS ============
  "vista-equipos": `
    <button class="volver-btn" data-volver="true">‹ Volver a las preguntas</button>
    <div class="pregunta-header">
      <h2>¿Qué grupos de proteínas trabajan juntos?</h2>
      <p>Algunas proteínas forman equipos pequeños y específicos que cumplen una función conjunta (por ejemplo, una vía metabólica completa). Esta vista identifica esos equipos dentro de la red.</p>
    </div>

    <div class="form-card">
      <div class="control-row">
        <div class="control-group">
          <label>Especificidad de los equipos</label>
          <input type="range" id="equipos-umbral" min="0.7" max="0.99" step="0.01" value="0.95">
          <span class="mono text-muted" id="equipos-umbral-valor" style="font-size:12px;">0.95 (más específico)</span>
        </div>
        <button class="btn" id="equipos-ejecutar">Buscar equipos</button>
      </div>
    </div>

    <div id="equipos-resultado"></div>
    <div id="equipos-detalle"></div>
  `,

  // ============ PREGUNTA 4: COMPARACIÓN PROFUNDA + EXPLORAR ============
  "vista-profundo": `
    <button class="volver-btn" data-volver="true">‹ Volver a las preguntas</button>
    <div class="pregunta-header">
      <h2>¿Qué tan parecidas son, y qué hay alrededor de una de ellas?</h2>
      <p>Compare dos proteínas con cuatro métodos distintos de análisis de secuencia, y explore qué otras proteínas se alcanzan partiendo de una de ellas.</p>
    </div>

    <h3 style="font-size:15.5px;font-weight:600;margin:0 0 4px;">Comparar dos secuencias a fondo</h3>
    <p style="font-size:13px;color:var(--text-muted);margin:0 0 14px;">Se aplican cuatro métodos distintos sobre la secuencia real de aminoácidos, para mostrar cómo cambia el resultado y el tiempo según la técnica usada.</p>

    <div class="form-card">
      <div class="control-row">
        <div class="control-group">
          <label>Primera proteína</label>
          ${selectorProteinas("prof-proteina1")}
        </div>
        <div class="control-group">
          <label>Segunda proteína</label>
          ${selectorProteinas("prof-proteina2")}
        </div>
        <button class="btn" id="prof-ejecutar">Comparar con los 4 métodos</button>
      </div>
    </div>

    <div id="prof-resultado"></div>

    <h3 style="font-size:15.5px;font-weight:600;margin:36px 0 4px;">Explorar alrededor de una proteína</h3>
    <p style="font-size:13px;color:var(--text-muted);margin:0 0 14px;">Vea qué proteínas se alcanzan explorando paso a paso desde una proteína de partida, y cuál es la conexión más fuerte de toda la red como dato de referencia.</p>

    <div class="form-card">
      <div class="control-row">
        <div class="control-group">
          <label>Proteína de partida</label>
          ${selectorProteinas("explorar-proteina")}
        </div>
        <button class="btn" id="explorar-ejecutar">Explorar vecindario</button>
      </div>
    </div>

    <div id="explorar-resultado"></div>
  `,

};

function inyectarVistasPreguntas() {
  const contenedor = document.getElementById("vistas-preguntas");
  let html = "";
  for (const [id, contenido] of Object.entries(VISTAS_PREGUNTAS_HTML)) {
    html += `<section id="${id}" class="vista-pregunta">${contenido}</section>`;
  }
  contenedor.innerHTML = html;
}
