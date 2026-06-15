# ==========================================
# BIONET ANALYZER - SERVIDOR FLASK
# Análisis de Redes Biológicas NIH
# ==========================================
# ESTRATEGIA: todos los algoritmos se
# pre-calculan al arrancar el servidor.
# Los endpoints solo devuelven el caché.
# Tiempo de respuesta: < 50 ms por petición.
# ==========================================

from flask import Flask, render_template, jsonify
import pandas as pd
import sys, os, time, math
from collections import defaultdict, deque

app = Flask(__name__)

# ==========================================
# CARGAR DATASET
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "grafo_biologico_1500.csv")

df            = pd.read_csv(CSV_PATH)
interacciones = df.values.tolist()

# Listas y sets reutilizables
p1_col = df['protein1'].tolist()
p2_col = df['protein2'].tolist()
w_col  = df['weight'].tolist()

print(f"[BioNet] Dataset cargado: {len(df)} interacciones")

# ==========================================
# CACHÉ GLOBAL
# ==========================================
# Diccionario donde se guardan los
# resultados pre-calculados de cada algo.

CACHE = {}

# ==========================================
# ESTRUCTURAS COMPARTIDAS
# (se construyen una sola vez)
# ==========================================

# Lista de adyacencia no dirigida
grafo_ady = defaultdict(list)
grado     = defaultdict(int)

for u, v, w in zip(p1_col, p2_col, w_col):
    grafo_ady[u].append((v, float(w)))
    grafo_ady[v].append((u, float(w)))
    grado[u] += 1
    grado[v] += 1

nodos_todos = list(grafo_ady.keys())
top_nodos   = sorted(grado, key=grado.get, reverse=True)

print(f"[BioNet] Grafo construido: {len(nodos_todos)} nodos")

# ==========================================
# PRE-CÁLCULO 1: DIVIDE Y VENCERÁS
# ==========================================

def precalc_dyv():
    def buscar_maximo(lista):
        if len(lista) == 1:
            return lista[0]
        m = len(lista) // 2
        izq = buscar_maximo(lista[:m])
        der = buscar_maximo(lista[m:])
        return izq if izq[2] > der[2] else der

    sys.setrecursionlimit(10000)
    p1, p2, peso = buscar_maximo(interacciones)

    vecinos_p1 = df[df['protein1'] == p1]['protein2'].tolist()[:5]
    vecinos_p2 = df[df['protein2'] == p2]['protein1'].tolist()[:5]
    nodos = list(set([p1, p2] + vecinos_p1 + vecinos_p2))
    nodos_set = set(nodos)

    aristas = [
        {"source": u, "target": v, "weight": w,
         "es_maxima": (u==p1 and v==p2) or (u==p2 and v==p1)}
        for u, v, w in interacciones
        if u in nodos_set and v in nodos_set
    ]

    return {
        "algoritmo": "Divide y Vencerás",
        "resultado": {"protein1": p1, "protein2": p2, "peso": peso},
        "nodos": nodos,
        "aristas": aristas
    }

# ==========================================
# PRE-CÁLCULO 2: DFS
# ==========================================

def precalc_dfs():
    # Grafo simple (sin pesos) para DFS
    g = defaultdict(list)
    for u, v, _ in interacciones:
        g[u].append(v)
        g[v].append(u)

    inicio = "MYC" if "MYC" in g else list(g.keys())[0]

    visitados = []
    pila      = [inicio]
    vistos    = set()
    while pila:
        nodo = pila.pop()
        if nodo not in vistos:
            vistos.add(nodo)
            visitados.append(nodo)
            for vecino in g[nodo]:
                if vecino not in vistos:
                    pila.append(vecino)

    sub   = visitados[:25]
    s_set = set(sub)
    aristas = [
        {"source": u, "target": v}
        for u, v, _ in interacciones
        if u in s_set and v in s_set
    ]

    return {
        "algoritmo": "DFS",
        "inicio": inicio,
        "total_recorridos": len(visitados),
        "nodos": sub,
        "aristas": aristas
    }

# ==========================================
# PRE-CÁLCULO 3: FUERZA BRUTA
# ==========================================

def precalc_fuerza_bruta():
    t0     = time.time()
    nodos  = set()
    aristas = []

    filas = list(zip(
        df['protein1'].head(300).tolist(),
        df['protein2'].head(300).tolist()
    ))

    for p1, p2 in filas:
        p1, p2   = str(p1), str(p2)
        longitud = min(len(p1), len(p2))
        if longitud == 0:
            continue
        coincidencias = sum(1 for a, b in zip(p1, p2) if a == b)
        sim = coincidencias / longitud * 100
        if sim >= 50:
            nodos.add(p1); nodos.add(p2)
            aristas.append({"source": p1, "target": p2,
                            "similitud": round(sim, 2)})

    return {
        "algoritmo": "Fuerza Bruta",
        "tiempo_segundos": round(time.time() - t0, 4),
        "nodos": list(nodos),
        "aristas": aristas,
        "total_nodos": len(nodos),
        "total_aristas": len(aristas)
    }

# ==========================================
# PRE-CÁLCULO 4: SCC (TARJAN iterativo)
# ==========================================
# Se usa versión ITERATIVA para evitar
# RecursionError en Python con grafos grandes

def precalc_scc():
    adj = defaultdict(list)
    for u, v, _ in interacciones:
        adj[u].append(v)

    nodos_scc = list(adj.keys())
    indices   = {n: -1  for n in nodos_scc}
    lowlink   = {n: -1  for n in nodos_scc}
    on_stack  = {n: False for n in nodos_scc}
    stack     = []
    resultado = []
    counter   = [0]

    # Tarjan iterativo con pila explícita
    def tarjan_iter(raiz):
        call_stack = [(raiz, iter(adj[raiz]), False)]
        indices[raiz] = lowlink[raiz] = counter[0]
        counter[0] += 1
        stack.append(raiz)
        on_stack[raiz] = True

        while call_stack:
            v, vecinos_iter, _ = call_stack[-1]
            try:
                w = next(vecinos_iter)
                if indices[w] == -1:
                    indices[w] = lowlink[w] = counter[0]
                    counter[0] += 1
                    stack.append(w)
                    on_stack[w] = True
                    call_stack.append((w, iter(adj[w]), False))
                elif on_stack[w]:
                    lowlink[v] = min(lowlink[v], indices[w])
            except StopIteration:
                call_stack.pop()
                if call_stack:
                    parent = call_stack[-1][0]
                    lowlink[parent] = min(lowlink[parent], lowlink[v])
                if lowlink[v] == indices[v]:
                    comp = []
                    while True:
                        nodo = stack.pop()
                        on_stack[nodo] = False
                        comp.append(nodo)
                        if nodo == v:
                            break
                    resultado.append(comp)

    for n in nodos_scc:
        if indices[n] == -1:
            tarjan_iter(n)

    ciclos    = [s for s in resultado if len(s) > 1]
    nodos_vis = []
    aristas_vis = []

    if ciclos:
        scc_mayor = max(ciclos, key=len)[:20]
        s_set     = set(scc_mayor)
        nodos_vis = scc_mayor
        aristas_vis = [
            {"source": u, "target": v}
            for u, v, _ in interacciones
            if u in s_set and v in s_set
        ]

    return {
        "algoritmo": "SCC - Tarjan",
        "total_componentes": len(resultado),
        "ciclos_biologicos": len(ciclos),
        "nodos": nodos_vis,
        "aristas": aristas_vis
    }

# ==========================================
# PRE-CÁLCULO 5: UFSD
# ==========================================

def precalc_ufsd():
    proteinas = list(set(p1_col + p2_col))
    ids       = {p: i for i, p in enumerate(proteinas)}
    parent    = list(range(len(proteinas)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        pa, pb = find(a), find(b)
        if pa != pb:
            parent[pa] = pb

    for u, v, _ in interacciones:
        union(ids[u], ids[v])

    grupos = defaultdict(list)
    for p in proteinas:
        grupos[find(ids[p])].append(p)

    grupo_mayor = max(grupos.values(), key=len)
    sub         = grupo_mayor[:25]
    s_set       = set(sub)

    aristas = [
        {"source": u, "target": v}
        for u, v, _ in interacciones
        if u in s_set and v in s_set
    ]

    return {
        "algoritmo": "UFSD - Union Find",
        "total_grupos": len(grupos),
        "grupo_mayor_size": len(grupo_mayor),
        "nodos": sub,
        "aristas": aristas
    }

# ==========================================
# PRE-CÁLCULO 6: BACKTRACKING
# ==========================================

def precalc_backtracking():
    nodos   = []
    aristas = []
    cnt     = [0]

    def bt(seq1, seq2, i, j, a1, a2, padre, prof, max_p):
        if prof > max_p:
            return
        nid = cnt[0]; cnt[0] += 1
        nodos.append({"id": nid, "label": f"{a1}|{a2}", "profundidad": prof})
        if padre is not None:
            aristas.append({"source": padre, "target": nid})
        if i == len(seq1) and j == len(seq2):
            return
        if i < len(seq1) and j < len(seq2):
            bt(seq1, seq2, i+1, j+1, a1+seq1[i], a2+seq2[j], nid, prof+1, max_p)
        if i < len(seq1):
            bt(seq1, seq2, i+1, j, a1+seq1[i], a2+"-", nid, prof+1, max_p)
        if j < len(seq2):
            bt(seq1, seq2, i, j+1, a1+"-", a2+seq2[j], nid, prof+1, max_p)

    bt("RFC2", "RFC4", 0, 0, "", "", None, 0, 3)

    return {
        "algoritmo": "Backtracking",
        "secuencia1": "RFC2", "secuencia2": "RFC4",
        "nodos": nodos, "aristas": aristas
    }

# ==========================================
# PRE-CÁLCULO 7: MST (KRUSKAL)
# ==========================================

def precalc_mst():
    nodos_u = list(set(p1_col + p2_col))
    parent  = {n: n for n in nodos_u}
    rank    = {n: 0 for n in nodos_u}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry: return False
        if rank[rx] < rank[ry]: rx, ry = ry, rx
        parent[ry] = rx
        if rank[rx] == rank[ry]: rank[rx] += 1
        return True

    aristas_ord = sorted(interacciones, key=lambda x: x[2])
    mst         = []
    peso_total  = 0.0

    for u, v, w in aristas_ord:
        if union(u, v):
            mst.append((u, v, w))
            peso_total += w
            if len(mst) == len(nodos_u) - 1:
                break

    sub      = mst[:25]
    sub_nods = list(set([u for u,v,w in sub] + [v for u,v,w in sub]))

    return {
        "algoritmo": "MST — Kruskal",
        "total_aristas_mst": len(mst),
        "peso_total": round(peso_total, 4),
        "nodos": sub_nods,
        "aristas": [{"source": u, "target": v, "weight": round(w,4)}
                    for u, v, w in sub]
    }

# ==========================================
# PRE-CÁLCULO 8: FLUJO MÁXIMO
# ==========================================

def precalc_flujo_maximo():
    SOURCE = top_nodos[0]
    SINK   = top_nodos[1]

    cap = defaultdict(lambda: defaultdict(float))
    ady = defaultdict(set)
    for u, v, w in interacciones:
        cap[u][v] += w; cap[v][u] += w
        ady[u].add(v);  ady[v].add(u)

    def bfs(src, snk, padre, c):
        vis = {src}; q = deque([src])
        while q:
            u = q.popleft()
            for v in ady[u]:
                if v not in vis and c[u][v] > 0:
                    vis.add(v); padre[v] = u
                    if v == snk: return True
                    q.append(v)
        return False

    cap_r = defaultdict(lambda: defaultdict(float))
    for u in cap:
        for v in cap[u]: cap_r[u][v] = cap[u][v]

    flujo_total = 0.0
    rutas       = []

    for _ in range(8):
        padre = {}
        if not bfs(SOURCE, SINK, padre, cap_r): break
        f = float('inf'); v = SINK; cam = []
        while v != SOURCE:
            u = padre[v]; f = min(f, cap_r[u][v])
            cam.append(v); v = u
        cam.append(SOURCE); cam.reverse()
        v = SINK
        while v != SOURCE:
            u = padre[v]; cap_r[u][v] -= f; cap_r[v][u] += f; v = u
        flujo_total += f
        rutas.append((cam, round(f, 4)))

    nodos_v = set(); aristas_v = []
    for cam, f in rutas:
        for n in cam: nodos_v.add(n)
        for i in range(len(cam)-1):
            aristas_v.append({"source": cam[i], "target": cam[i+1], "flujo": f})

    return {
        "algoritmo": "Flujo Máximo — Ford-Fulkerson",
        "source": SOURCE, "sink": SINK,
        "flujo_maximo": round(flujo_total, 4),
        "rutas": len(rutas),
        "nodos": list(nodos_v),
        "aristas": aristas_v
    }

# ==========================================
# PRE-CÁLCULO 9: VORAZ
# ==========================================

def precalc_voraz():
    MATCH=2; MISMATCH=-1; GAP=-2

    def voraz(s1, s2):
        a1,a2,sc,ops=[],[],0,[]
        i=j=0
        while i<len(s1) and j<len(s2):
            if s1[i]==s2[j]: a1.append(s1[i]);a2.append(s2[j]);sc+=MATCH;ops.append('M')
            else: a1.append(s1[i]);a2.append(s2[j]);sc+=MISMATCH;ops.append('X')
            i+=1;j+=1
        while i<len(s1): a1.append(s1[i]);a2.append('-');sc+=GAP;ops.append('G');i+=1
        while j<len(s2): a1.append('-');a2.append(s2[j]);sc+=GAP;ops.append('G');j+=1
        return ''.join(a1),''.join(a2),sc,ops

    resultados=[]; nodos_s=set(); aristas=[]
    for p1,p2 in zip(p1_col[:50], p2_col[:50]):
        p1,p2=str(p1),str(p2)
        a1,a2,sc,ops=voraz(p1,p2)
        m=ops.count('M'); lg=max(len(ops),1)
        ide=round(m/lg*100,2)
        resultados.append({"p1":p1,"p2":p2,"alin1":a1,"alin2":a2,
                           "score":sc,"matches":m,
                           "mismatches":ops.count('X'),
                           "gaps":ops.count('G'),"identidad":ide})
        if sc>0:
            nodos_s.add(p1);nodos_s.add(p2)
            aristas.append({"source":p1,"target":p2,"score":sc,"identidad":ide})

    top10=sorted(resultados,key=lambda x:x['score'],reverse=True)[:10]
    return {"algoritmo":"Voraz — Alineamiento Heurístico",
            "total_pares":len(resultados),"top_alineamientos":top10,
            "nodos":list(nodos_s),"aristas":aristas}

# ==========================================
# PRE-CÁLCULO 10: DP — NEEDLEMAN-WUNSCH
# ==========================================

def precalc_dp():
    MATCH=2; MISMATCH=-1; GAP=-2

    def nw(s1,s2):
        n,m=len(s1),len(s2)
        dp=[[0]*(m+1) for _ in range(n+1)]
        for i in range(n+1): dp[i][0]=i*GAP
        for j in range(m+1): dp[0][j]=j*GAP
        for i in range(1,n+1):
            for j in range(1,m+1):
                d=dp[i-1][j-1]+(MATCH if s1[i-1]==s2[j-1] else MISMATCH)
                dp[i][j]=max(d,dp[i-1][j]+GAP,dp[i][j-1]+GAP)
        a1,a2=[],[];i,j=n,m
        while i>0 or j>0:
            if i>0 and j>0:
                d=dp[i-1][j-1]+(MATCH if s1[i-1]==s2[j-1] else MISMATCH)
                if dp[i][j]==d: a1.append(s1[i-1]);a2.append(s2[j-1]);i-=1;j-=1
                elif dp[i][j]==dp[i-1][j]+GAP: a1.append(s1[i-1]);a2.append('-');i-=1
                else: a1.append('-');a2.append(s2[j-1]);j-=1
            elif i>0: a1.append(s1[i-1]);a2.append('-');i-=1
            else: a1.append('-');a2.append(s2[j-1]);j-=1
        a1.reverse();a2.reverse()
        return dp,''.join(a1),''.join(a2),dp[n][m]

    resultados=[]; nodos_s=set(); aristas=[]
    for p1,p2 in zip(p1_col[:20], p2_col[:20]):
        p1,p2=str(p1),str(p2)
        tabla,a1,a2,sc=nw(p1,p2)
        m=sum(1 for x,y in zip(a1,a2) if x==y and x!='-')
        ide=round(m/max(len(a1),1)*100,2)
        resultados.append({"p1":p1,"p2":p2,"alin1":a1,"alin2":a2,
                           "score":sc,"matches":m,
                           "gaps":a1.count('-')+a2.count('-'),
                           "identidad":ide,"tabla":tabla})
        nodos_s.add(p1);nodos_s.add(p2)
        aristas.append({"source":p1,"target":p2,"score":sc,"identidad":ide})

    top=sorted(resultados,key=lambda x:x['score'],reverse=True)
    return {"algoritmo":"DP — Needleman-Wunsch",
            "total_pares":len(resultados),
            "mejor_score":top[0]['score'] if top else 0,
            "mejor_par":{"p1":top[0]['p1'],"p2":top[0]['p2']} if top else {},
            "top_alineamientos":top[:10],
            "nodos":list(nodos_s),"aristas":aristas}

# ==========================================
# PRE-CÁLCULO 11: DP EN GRAFO
# ==========================================

def precalc_dp_en_grafo():
    FUENTE  = top_nodos[0]
    DESTINO = top_nodos[2]
    nodos_t = set(top_nodos[:60])
    nodos_t.add(FUENTE); nodos_t.add(DESTINO)

    dist  = {n: float('-inf') for n in nodos_t}
    padre = {n: None for n in nodos_t}
    dist[FUENTE] = 0.0

    for _ in range(len(nodos_t)-1):
        upd=False
        for u in nodos_t:
            if dist[u]==float('-inf'): continue
            for v,w in grafo_ady.get(u,[]):
                if v in nodos_t and dist[u]+w>dist[v]:
                    dist[v]=dist[u]+w; padre[v]=u; upd=True
        if not upd: break

    camino=[]; actual=DESTINO; vistos=set()
    while actual is not None and actual not in vistos:
        vistos.add(actual); camino.append(actual); actual=padre[actual]
    camino.reverse()

    peso_opt=round(dist[DESTINO],4) if dist[DESTINO]!=float('-inf') else 0
    aristas_c=[{"source":camino[i],"target":camino[i+1]}
               for i in range(len(camino)-1)]

    return {"algoritmo":"DP en Grafos — Bellman-Ford",
            "fuente":FUENTE,"destino":DESTINO,
            "peso_optimo":peso_opt,
            "longitud_camino":len(camino),
            "camino":camino,
            "nodos":camino if camino else [FUENTE,DESTINO],
            "aristas":aristas_c}

# ==========================================
# PRE-CALCULAR TODO AL ARRANCAR
# ==========================================

def precalcular_todo():
    tareas = [
        ("dyv",          precalc_dyv),
        ("dfs",          precalc_dfs),
        ("fuerza_bruta", precalc_fuerza_bruta),
        ("scc",          precalc_scc),
        ("ufsd",         precalc_ufsd),
        ("backtracking", precalc_backtracking),
        ("mst",          precalc_mst),
        ("flujo_maximo", precalc_flujo_maximo),
        ("voraz",        precalc_voraz),
        ("dp",           precalc_dp),
        ("dp_en_grafo",  precalc_dp_en_grafo),
    ]

    for nombre, fn in tareas:
        t0 = time.time()
        try:
            CACHE[nombre] = fn()
            print(f"[BioNet] ✓ {nombre:15s} {round(time.time()-t0,2)}s")
        except Exception as e:
            print(f"[BioNet] ✗ {nombre:15s} ERROR: {e}")
            CACHE[nombre] = {"algoritmo": nombre, "error": str(e),
                             "nodos": [], "aristas": []}

    print("[BioNet] Pre-cálculo completo. Servidor listo.")

# ==========================================
# RUTA PRINCIPAL
# ==========================================

@app.route("/")
def index():
    return render_template("index.html")

# ==========================================
# ENDPOINTS — SOLO DEVUELVEN CACHÉ
# ==========================================

@app.route("/api/dyv")
def api_dyv():
    return jsonify(CACHE.get("dyv", {}))

@app.route("/api/dfs")
def api_dfs():
    return jsonify(CACHE.get("dfs", {}))

@app.route("/api/fuerza_bruta")
def api_fuerza_bruta():
    return jsonify(CACHE.get("fuerza_bruta", {}))

@app.route("/api/scc")
def api_scc():
    return jsonify(CACHE.get("scc", {}))

@app.route("/api/ufsd")
def api_ufsd():
    return jsonify(CACHE.get("ufsd", {}))

@app.route("/api/backtracking")
def api_backtracking():
    return jsonify(CACHE.get("backtracking", {}))

@app.route("/api/mst")
def api_mst():
    return jsonify(CACHE.get("mst", {}))

@app.route("/api/flujo_maximo")
def api_flujo_maximo():
    return jsonify(CACHE.get("flujo_maximo", {}))

@app.route("/api/voraz")
def api_voraz():
    return jsonify(CACHE.get("voraz", {}))

@app.route("/api/dp")
def api_dp():
    return jsonify(CACHE.get("dp", {}))

@app.route("/api/dp_en_grafo")
def api_dp_en_grafo():
    return jsonify(CACHE.get("dp_en_grafo", {}))

# ==========================================
# ARRANCAR
# ==========================================

if __name__ == "__main__":
    precalcular_todo()
    app.run(debug=False)